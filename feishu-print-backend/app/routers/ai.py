from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from openai import AsyncOpenAI
from typing import List, Tuple
from ..config import settings
import traceback
import logging
import json
import re
import asyncio
import httpx
import httpcore
from app.database import get_db
from app.models.user import User
from app.routers.user import PLAN_LIMITS, reset_usage_if_needed
from fastapi import Depends
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)

# 常量配置
AI_TEMPERATURE = 0.85  # 提高温度增加多样性
AI_MAX_TOKENS = 4000
STREAM_BUFFER_THRESHOLD = 20
MIN_CONTENT_LENGTH = 800
MAX_RETRY_ATTEMPTS = 2

DEFAULT_MODE = "design"

router = APIRouter(
    prefix="/api/ai",
    tags=["ai"]
)

_ai_client: AsyncOpenAI | None = None

def get_ai_client() -> AsyncOpenAI:
    global _ai_client
    if _ai_client is None:
        from httpx import Timeout
        import httpx
        import os
        
        # 从环境变量读取代理配置，如果未设置则不使用代理
        http_proxy = os.getenv('HTTP_PROXY') or os.getenv('http_proxy')
        https_proxy = os.getenv('HTTPS_PROXY') or os.getenv('https_proxy')
        
        if http_proxy:
            os.environ['HTTP_PROXY'] = http_proxy
            os.environ['http_proxy'] = http_proxy
        if https_proxy:
            os.environ['HTTPS_PROXY'] = https_proxy
            os.environ['https_proxy'] = https_proxy
        
        timeout = Timeout(
            connect=60.0,
            read=max(settings.ai_timeout, 300),
            write=30.0, 
            pool=30.0
        )
        
        http_client = httpx.AsyncClient(
            timeout=timeout,
            http2=False,
            trust_env=True,
        )
        
        _ai_client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            http_client=http_client,
        )
    return _ai_client


class FieldInfo(BaseModel):
    name: str
    id: str
    type: str

class GenerateTemplateRequest(BaseModel):
    description: str
    mode: str = DEFAULT_MODE
    availableFields: List[FieldInfo] = []
    feishu_user_id: str

def extract_colors_from_description(description: str) -> List[str]:
    color_keywords = {
        '红色': '#ef4444', '红': '#ef4444', '赤': '#dc2626',
        '橙色': '#f97316', '橙': '#f97316', '橘色': '#fb923c',
        '黄色': '#eab308', '黄': '#facc15', '金': '#fbbf24',
        '绿色': '#22c55e', '绿': '#4ade80', '青': '#06b6d4',
        '蓝色': '#3b82f6', '蓝': '#60a5fa', '海蓝': '#0ea5e9',
        '紫色': '#a855f7', '紫': '#c084fc',
        '粉色': '#ec4899', '粉': '#f472b6',
        '黑色': '#000000', '黑': '#18181b',
        '白色': '#ffffff', '白': '#f8fafc',
    }
    found_colors = []
    desc_lower = description.lower()
    for key, hex_val in color_keywords.items():
        if key in desc_lower:
            if hex_val not in found_colors:
                found_colors.append(hex_val)
    return found_colors



def extract_html_content(text: str) -> str:
    """从 AI 响应中提取 HTML 内容"""
    if not text:
        return ""
    cleaned_text = text.replace("```html", "").replace("```", "").strip()
    root_match = re.search(r'<div\s+id=["\']template-root["\'][^>]*>', cleaned_text, re.IGNORECASE)
    if root_match:
        start_idx = root_match.start()
        end_idx = _find_matching_closing_tag(cleaned_text, start_idx)
        if end_idx != -1:
            return cleaned_text[start_idx:end_idx + 6]
        else:
            return cleaned_text[start_idx:]
    div_match = re.search(r'<div[^>]*>', cleaned_text, re.IGNORECASE)
    if div_match:
        start_idx = div_match.start()
        end_idx = _find_matching_closing_tag(cleaned_text, start_idx)
        if end_idx != -1:
            return cleaned_text[start_idx:end_idx + 6]
        return cleaned_text[start_idx:]
    return cleaned_text

def _find_matching_closing_tag(html: str, start_idx: int) -> int:
    depth = 1
    i = start_idx
    while i < len(html) and html[i] != '>':
        i += 1
    i += 1
    while i < len(html):
        div_match = re.search(r'</?div[^>]*>', html[i:], re.IGNORECASE)
        if not div_match: break
        match_start = i + div_match.start()
        match_end = i + div_match.end()
        if html[match_start + 1] == '/':
            depth -= 1
            if depth == 0: return match_end
        else:
            depth += 1
        i = match_end
    return -1

def validate_generated_html(html: str) -> Tuple[bool, str]:
    if not html or not html.strip():
        return False, "生成的HTML内容为空"
    if len(html.strip()) < 200:
        return False, "生成的HTML内容过短"
    if not re.search(r'<div\s+id=["\']template-root["\']', html, re.IGNORECASE):
        if not re.search(r'<div[^>]*>', html, re.IGNORECASE):
            return False, "缺少必需的div容器"
    return True, ""

def build_traditional_user_prompt(description: str, available_fields: List[FieldInfo] = None) -> str:
    fields_info = ""
    if available_fields:
        names = ", ".join([f.name for f in available_fields])
        fields_info = f"\n可用字段: {names}"

    # 添加随机元素增加多样性
    import random
    layout_hints = [
        "尝试使用两列、三列或四列布局",
        "可以将相关字段分组显示",
        "适当使用合并单元格增强视觉层次",
        "在重要区域（如标题、签名）使用适当的留白",
        "考虑添加表头背景色区分",
    ]
    selected_hint = random.choice(layout_hints)

    return f"""
请根据以下需求生成一份专业的 A4 办公表格：

【用户需求】
{description}
{fields_info}

【布局建议】
{selected_hint}

【技术要求】
1. 根容器必须使用以下样式（不可修改）：
   id="template-root" style="width: 210mm; height: 267mm; padding: 15mm; box-sizing: border-box; font-family: SimSun, serif; font-size: 14px; background: white;"
2. 使用 <table> 进行核心布局，表格宽度必须是 100%
3. 动态字段格式：<span class="template-field field-block" data-fieldname="字段名">{{$字段名}}</span>
4. 配色限制：黑(#000)、白(#fff)、浅灰(#f5f5f5)
5. **表格内容必须填满页面**，表格高度至少占页面的一半

只输出 HTML 代码，不要任何解释文字。
    """

def build_traditional_system_prompt() -> str:
    return """你是一名资深的办公文档设计专家，擅长设计各类规范的 A4 表格文档。

【核心任务】
根据用户需求，生成一份 **填满整个 A4 页面** 的专业办公表格。

【强制规范】
1. **尺寸约束**：模板宽 210mm、高度固定 267mm（必须填满整个页面）
2. **根容器格式**：必须以此开头：
   <div id="template-root" style="width: 210mm; height: 267mm; padding: 15mm; box-sizing: border-box; font-family: SimSun, serif; font-size: 14px; background: white;">
3. **表格布局**：使用 <table> 且必须设置 width: 100%
4. **配色**：仅黑白灰，表格边框为 1px solid #000
5. **禁止现代布局**：严禁使用 display: flex、display: grid、flexbox、grid-template 等现代 CSS 布局属性
6. **布局方式**：只能使用 <table>、浮动（float）进行多列布局

【占位符规范】
动态字段使用：<span class="template-field field-block" data-fieldname="字段键">{$字段名}</span>

【设计指南 - 必须填满页面】
- 标题居中，字号 20-24px，上下留有适当间距
- **表格行高必须足够大**（50-60px），便于手写填充
- **表格内容区域至少占页面高度的一半**
- 每个输入单元格要有足够的书写空间
- 签名区域放在底部，使用 <table> 实现左右布局，**预留大片空白区域**（至少 80px 高）用于手写签名
- 可以在表格下方添加"备注"或"说明"区域来填充空间
- 根据内容灵活调整列数和布局，**不要每次都用同样的结构**

【输出要求】
直接输出完整 HTML 代码，首行必须是 <div id="template-root"...>，末行必须是 </div>
    """

def build_design_system_prompt() -> str:
    """构建设计模式的系统提示词（现代彩色排版风格）"""
    return """你是一位专业的文档排版设计师，擅长设计现代简洁、有颜色的 A4 办公文档模板。

【核心任务】
设计一份 **210mm × 297mm (A4)** 的现代彩色排版文档模板，风格类似轻量 UI 设计稿，但适合打印。

【强制规范】
1. **尺寸约束**：根容器必须使用：
   <div id="template-root" style="width: 210mm; height: 297mm; padding: 15mm; box-sizing: border-box; font-family: 'PingFang SC', 'Microsoft YaHei', -apple-system, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif; font-size: 14px; background: #fff;">
2. **打印友好**：背景只用浅色（低耗墨），避免大面积深色底
3. **禁止动画**：不使用 animation, transition, keyframes
4. **禁止竖排**：所有文字必须水平排列
5. **禁止现代布局**：严禁使用 display: flex、display: grid、flexbox、grid-template 等现代 CSS 布局属性，因为这会导致编辑器分页功能异常
6. **布局方式**：只能使用 <table>、浮动（float）、内联块（inline-block）进行多列布局

【占位符格式】
动态字段：<span class="template-field field-block" data-fieldname="字段名">{$字段名}</span>

【设计风格（你可自由发挥配色与细节）】
- 现代简洁的彩色排版，不是传统黑白表格
- 配色由你自由选择，保证协调高级（可用商务蓝、活力橙、清新绿、优雅紫等）
- 颜色用于：标题条、分组标题、标签/徽章、表头底色、左侧色条等点缀
- 整体像一张轻量 UI 设计稿，但必须可打印、浅色背景

【布局原则】
1. **顶部标题区**：彩色标题条或浅渐变，包含模板名称、编号、日期
2. **信息卡片区**：使用 <table> 实现 2-3 列布局，每组有小标题（浅底色/左侧色条/分割线）
3. **明细表格区**：表头有底色、隔行斑马纹、关键字段可用 badge 标签强调
4. **底部签名区**：使用 <table> 实现左右签名区布局，浅色边框块，包含审批人、日期、签名等
5. **层次分明**：标题 20-24px、小标题 16px、正文 14px
6. **圆角与阴影**：适当使用圆角 (4-8px) 和轻微阴影增加现代感

【输出要求】
直接输出完整 HTML 代码，首行必须是 <div id="template-root"...>，末行必须是 </div>
    """

def build_user_prompt(request: GenerateTemplateRequest) -> str:
    import random
    
    user_colors = extract_colors_from_description(request.description)
    color_hint = f"参考配色: {user_colors}" if user_colors else "配色：由你自由选择，保证协调高级。"
    
    # 获取可用字段信息
    fields_info = ""
    if request.availableFields:
        names = ", ".join([f.name for f in request.availableFields])
        fields_info = f"\n可用字段: {names}"
    
    # 随机布局提示增加多样性
    layout_hints = [
        "顶部彩色标题条 + 两列信息卡片 + 明细表格 + 底部签名区",
        "左侧色条装饰 + 分组卡片布局 + 斑马纹表格",
        "渐变标题区 + 三列网格信息卡片 + 底部审批流程",
        "简约风格：细线分割 + 左对齐标题 + 清晰的信息层级",
        "卡片式布局：每个信息组用浅色卡片包裹，带轻微阴影",
    ]
    selected_layout = random.choice(layout_hints)

    return f"""
【设计任务】
为以下需求设计一份 A4 纵向可打印的现代彩色排版文档模板：

用户需求: "{request.description}"
{fields_info}
{color_hint}

【布局建议】
{selected_layout}

【核心要求】
1. **现代排版**：不是传统黑白表格，而是有颜色点缀的现代文档风格
2. **打印友好**：背景浅色、低耗墨，适合打印
3. **信息层级**：标题 20-24px、小标题 16px、正文 14px
4. **占位符格式**：<span class="template-field field-block" data-fieldname="字段名">{{$字段名}}</span>

只输出 HTML 代码。
    """

def build_prompts(request: GenerateTemplateRequest) -> Tuple[str, str]:
    if request.mode == "traditional":
        return build_traditional_system_prompt(), build_traditional_user_prompt(request.description, request.availableFields)
    else:
        return build_design_system_prompt(), build_user_prompt(request)

@router.post("/generate-template-stream")
async def generate_template_stream(request: GenerateTemplateRequest, db: Session = Depends(get_db)):
    """生成模板（流式）- 纯 HTML 生成模式"""
    
    # 权限检查与配额扣减
    user = db.query(User).filter(User.feishu_user_id == request.feishu_user_id).first()
    if not user or not user.membership:
        raise HTTPException(status_code=403, detail="用户不存在或未初始化")
        
    membership = user.membership
    reset_usage_if_needed(membership, db)
    
    plan_limits = PLAN_LIMITS.get(membership.plan_type, PLAN_LIMITS["free"])
    limit = plan_limits["ai_generates"]
    
    if limit != -1 and membership.ai_generates_used >= limit:
        raise HTTPException(status_code=403, detail=f"AI生成次数已用完（{limit}次/月），请升级会员")
        
    # 扣减次数（预扣减）
    try:
        membership.ai_generates_used += 1
        membership.ai_generates_total += 1
        db.commit()
    except Exception as e:
        db.rollback()
        logger.error(f"扣减AI次数失败: {e}")
        raise HTTPException(status_code=500, detail="系统繁忙，请重试")

    async def event_generator():
        retry_count = 0
        max_retries = MAX_RETRY_ATTEMPTS
        
        while retry_count <= max_retries:
            buffer = ""
            has_started = False
            full_content = ""
            
            try:
                client = get_ai_client()
                sys_p, usr_p = build_prompts(request)
                
                if retry_count > 0:
                    yield f"data: {json.dumps({'type': 'retry', 'message': f'正在重试生成（第{retry_count}次）...'}, ensure_ascii=False)}\n\n"
                
                stream = await client.chat.completions.create(
                    model=settings.ai_model,
                    messages=[{"role": "system", "content": sys_p}, {"role": "user", "content": usr_p}],
                    temperature=AI_TEMPERATURE,
                    max_tokens=AI_MAX_TOKENS,
                    stream=True
                )
                
                if retry_count == 0:  # 只在第一次尝试时记录
                    logger.debug(f"Stream started")
                
                async for chunk in stream:
                    if chunk.choices and chunk.choices[0].delta.content:
                        content = chunk.choices[0].delta.content
                        if not has_started and content.strip():
                            has_started = True
                        
                        buffer += content
                        if has_started:
                            yield f"data: {json.dumps({'content': content}, ensure_ascii=False)}\n\n"
                            full_content += content
                        elif "<div" in buffer or len(buffer) > STREAM_BUFFER_THRESHOLD:
                            has_started = True
                            yield f"data: {json.dumps({'content': buffer}, ensure_ascii=False)}\n\n"
                            full_content += buffer
                            buffer = ""

                if buffer and not has_started:
                     yield f"data: {json.dumps({'content': buffer}, ensure_ascii=False)}\n\n"
                     full_content += buffer
                
                if full_content:
                    extracted_html = extract_html_content(full_content)
                    if not extracted_html:
                        extracted_html = full_content.replace("```html", "").replace("```", "").strip()
                    
                    is_valid, error_msg = validate_generated_html(extracted_html)
                    if not is_valid:
                        logger.warning(f"Validation failed: {error_msg}")
                    
                    yield "data: [DONE]\n\n"
                    return

                raise Exception("No content received")
                
            except Exception as e:
                logger.error(f"Error: {e}")
                retry_count += 1
                if retry_count > max_retries:
                     yield f"data: {json.dumps({'error': str(e)}, ensure_ascii=False)}\n\n"
                await asyncio.sleep(1)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
