"""
系统模板导入脚本
包含20个实用模板：10个传统样式 + 10个现代设计样式
"""
import argparse
import json
import urllib.error
import urllib.request


def _post_json(url: str, payload: dict, timeout: int) -> tuple[int, str]:
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = urllib.request.Request(
        url=url,
        data=data,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            return resp.status, body
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace")
        return e.code, body


# ============================================================
# 传统样式模板（10个）- 黑白表格风格，适合正式办公场景
# ============================================================

def template_leave_application() -> dict:
    """请假申请单"""
    return {
        "name": "请假申请单",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 267mm; padding: 15mm; box-sizing: border-box; font-family: SimSun, serif; font-size: 14px; background: white;">
<p style="text-align:center;margin-bottom:20px;"><span style="font-size:24px;font-family:方正小标宋简体;font-weight:bold;">请 假 申 请 单</span></p>
<p style="text-align:right;margin-bottom:15px;font-family:仿宋;">编号：<span class="template-field field-block" data-fieldname="编号">{$编号}</span>　填表日期：<span class="template-field field-block" data-fieldname="日期">{$日期}</span></p>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;" border="1">
<tbody>
<tr style="height:45px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">申请人</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="姓名">{$姓名}</span></td>
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">部门</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="部门">{$部门}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">职位</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="职位">{$职位}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">联系电话</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="电话">{$电话}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">请假类型</td>
<td colspan="3" style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="请假类型">{$请假类型}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">开始时间</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="开始时间">{$开始时间}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">结束时间</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="结束时间">{$结束时间}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">请假天数</td>
<td colspan="3" style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="请假天数">{$请假天数}</span> 天</td>
</tr>
<tr style="height:100px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">请假事由</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;"><span class="template-field field-block" data-fieldname="请假事由">{$请假事由}</span></td>
</tr>
<tr style="height:80px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">部门意见</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;"></td>
</tr>
<tr style="height:80px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">人事意见</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;"></td>
</tr>
</tbody>
</table>
<div style="margin-top:30px;display:flex;justify-content:space-between;font-family:仿宋;">
<div>申请人签名：________________</div>
<div>审批人签名：________________</div>
<div>日期：________________</div>
</div>
</div>"""
    }


def template_expense_claim() -> dict:
    """报销申请单"""
    return {
        "name": "费用报销单",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 267mm; padding: 15mm; box-sizing: border-box; font-family: SimSun, serif; font-size: 14px; background: white;">
<p style="text-align:center;margin-bottom:20px;"><span style="font-size:24px;font-family:方正小标宋简体;font-weight:bold;">费 用 报 销 单</span></p>
<p style="text-align:right;margin-bottom:15px;font-family:仿宋;">单据编号：<span class="template-field field-block" data-fieldname="编号">{$编号}</span>　日期：<span class="template-field field-block" data-fieldname="日期">{$日期}</span></p>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;" border="1">
<tbody>
<tr style="height:40px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">报销人</td>
<td style="width:20%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="姓名">{$姓名}</span></td>
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">部门</td>
<td style="width:20%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="部门">{$部门}</span></td>
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">报销金额</td>
<td style="width:15%;text-align:center;font-family:仿宋;color:#c00;font-weight:bold;">￥<span class="template-field field-block" data-fieldname="总金额">{$总金额}</span></td>
</tr>
</tbody>
</table>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;margin-top:-1px;" border="1">
<thead>
<tr style="height:35px;background:#f5f5f5;">
<th style="width:5%;font-family:仿宋;">序号</th>
<th style="width:15%;font-family:仿宋;">日期</th>
<th style="width:20%;font-family:仿宋;">费用类型</th>
<th style="width:35%;font-family:仿宋;">费用说明</th>
<th style="width:12%;font-family:仿宋;">金额(元)</th>
<th style="width:13%;font-family:仿宋;">附件张数</th>
</tr>
</thead>
<tbody>
<tr style="height:40px;"><td style="text-align:center;">1</td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:40px;"><td style="text-align:center;">2</td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:40px;"><td style="text-align:center;">3</td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:40px;"><td style="text-align:center;">4</td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:40px;"><td style="text-align:center;">5</td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:35px;background:#f5f5f5;">
<td colspan="4" style="text-align:right;padding-right:20px;font-family:仿宋;font-weight:bold;">合计金额：</td>
<td style="text-align:center;font-family:仿宋;color:#c00;font-weight:bold;">￥<span class="template-field field-block" data-fieldname="总金额">{$总金额}</span></td>
<td></td>
</tr>
</tbody>
</table>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;margin-top:-1px;" border="1">
<tbody>
<tr style="height:40px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">金额大写</td>
<td colspan="5" style="padding-left:15px;font-family:仿宋;"><span class="template-field field-block" data-fieldname="金额大写">{$金额大写}</span></td>
</tr>
<tr style="height:80px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">备注说明</td>
<td colspan="5" style="padding:10px;font-family:仿宋;vertical-align:top;"><span class="template-field field-block" data-fieldname="备注">{$备注}</span></td>
</tr>
</tbody>
</table>
<div style="margin-top:25px;display:flex;justify-content:space-between;font-family:仿宋;font-size:13px;">
<div>报销人：____________</div>
<div>部门负责人：____________</div>
<div>财务审核：____________</div>
<div>总经理：____________</div>
</div>
</div>"""
    }


def template_business_trip() -> dict:
    """出差申请单"""
    return {
        "name": "出差申请单",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 267mm; padding: 15mm; box-sizing: border-box; font-family: SimSun, serif; font-size: 14px; background: white;">
<p style="text-align:center;margin-bottom:20px;"><span style="font-size:24px;font-family:方正小标宋简体;font-weight:bold;">出 差 申 请 单</span></p>
<p style="text-align:right;margin-bottom:15px;font-family:仿宋;">编号：<span class="template-field field-block" data-fieldname="编号">{$编号}</span>　申请日期：<span class="template-field field-block" data-fieldname="申请日期">{$申请日期}</span></p>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;" border="1">
<tbody>
<tr style="height:45px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">申请人</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="姓名">{$姓名}</span></td>
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">部门</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="部门">{$部门}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">出差地点</td>
<td colspan="3" style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="出差地点">{$出差地点}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">出发日期</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="出发日期">{$出发日期}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">返回日期</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="返回日期">{$返回日期}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">出差天数</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="出差天数">{$出差天数}</span> 天</td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">交通方式</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="交通方式">{$交通方式}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">预计费用</td>
<td colspan="3" style="text-align:center;font-family:仿宋;">￥<span class="template-field field-block" data-fieldname="预计费用">{$预计费用}</span> 元</td>
</tr>
<tr style="height:120px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">出差事由</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;"><span class="template-field field-block" data-fieldname="出差事由">{$出差事由}</span></td>
</tr>
<tr style="height:80px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">部门审批</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;"></td>
</tr>
<tr style="height:80px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">领导审批</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;"></td>
</tr>
</tbody>
</table>
<div style="margin-top:25px;font-family:仿宋;font-size:12px;color:#666;">
<p>注：1. 出差前须填写此表，经批准后方可出差；2. 出差返回后三日内办理报销手续。</p>
</div>
</div>"""
    }


def template_work_handover() -> dict:
    """工作交接单"""
    return {
        "name": "工作交接单",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 267mm; padding: 15mm; box-sizing: border-box; font-family: SimSun, serif; font-size: 14px; background: white;">
<p style="text-align:center;margin-bottom:20px;"><span style="font-size:24px;font-family:方正小标宋简体;font-weight:bold;">工 作 交 接 单</span></p>
<p style="text-align:right;margin-bottom:15px;font-family:仿宋;">编号：<span class="template-field field-block" data-fieldname="编号">{$编号}</span>　日期：<span class="template-field field-block" data-fieldname="日期">{$日期}</span></p>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;" border="1">
<tbody>
<tr style="height:45px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">移交人</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="移交人">{$移交人}</span></td>
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">接收人</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="接收人">{$接收人}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">原部门</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="原部门">{$原部门}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">新部门</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="新部门">{$新部门}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">交接原因</td>
<td colspan="3" style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="交接原因">{$交接原因}</span></td>
</tr>
</tbody>
</table>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;margin-top:-1px;" border="1">
<thead>
<tr style="height:35px;background:#f5f5f5;">
<th style="width:8%;font-family:仿宋;">序号</th>
<th style="width:25%;font-family:仿宋;">交接事项</th>
<th style="width:37%;font-family:仿宋;">具体内容</th>
<th style="width:15%;font-family:仿宋;">数量/状态</th>
<th style="width:15%;font-family:仿宋;">备注</th>
</tr>
</thead>
<tbody>
<tr style="height:45px;"><td style="text-align:center;">1</td><td style="padding:5px;">文件资料</td><td></td><td></td><td></td></tr>
<tr style="height:45px;"><td style="text-align:center;">2</td><td style="padding:5px;">办公设备</td><td></td><td></td><td></td></tr>
<tr style="height:45px;"><td style="text-align:center;">3</td><td style="padding:5px;">工作账号</td><td></td><td></td><td></td></tr>
<tr style="height:45px;"><td style="text-align:center;">4</td><td style="padding:5px;">进行中项目</td><td></td><td></td><td></td></tr>
<tr style="height:45px;"><td style="text-align:center;">5</td><td style="padding:5px;">客户资源</td><td></td><td></td><td></td></tr>
<tr style="height:45px;"><td style="text-align:center;">6</td><td style="padding:5px;">其他事项</td><td></td><td></td><td></td></tr>
</tbody>
</table>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;margin-top:-1px;" border="1">
<tbody>
<tr style="height:80px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">备注说明</td>
<td style="padding:10px;font-family:仿宋;vertical-align:top;"><span class="template-field field-block" data-fieldname="备注">{$备注}</span></td>
</tr>
</tbody>
</table>
<div style="margin-top:30px;display:flex;justify-content:space-between;font-family:仿宋;">
<div>移交人签字：____________</div>
<div>接收人签字：____________</div>
<div>监交人签字：____________</div>
</div>
<div style="margin-top:15px;display:flex;justify-content:space-between;font-family:仿宋;">
<div>日期：____________</div>
<div>日期：____________</div>
<div>日期：____________</div>
</div>
</div>"""
    }


def template_meeting_minutes() -> dict:
    """会议纪要"""
    return {
        "name": "会议纪要",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 267mm; padding: 15mm; box-sizing: border-box; font-family: SimSun, serif; font-size: 14px; background: white;">
<p style="text-align:center;margin-bottom:5px;"><span style="font-size:24px;font-family:方正小标宋简体;font-weight:bold;">会 议 纪 要</span></p>
<p style="text-align:center;margin-bottom:20px;font-family:仿宋;color:#666;">（<span class="template-field field-block" data-fieldname="会议主题">{$会议主题}</span>）</p>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;" border="1">
<tbody>
<tr style="height:40px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">会议时间</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="会议时间">{$会议时间}</span></td>
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">会议地点</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="会议地点">{$会议地点}</span></td>
</tr>
<tr style="height:40px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">主持人</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="主持人">{$主持人}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">记录人</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="记录人">{$记录人}</span></td>
</tr>
<tr style="height:50px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">参会人员</td>
<td colspan="3" style="padding:10px;font-family:仿宋;"><span class="template-field field-block" data-fieldname="参会人员">{$参会人员}</span></td>
</tr>
<tr style="height:50px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">缺席人员</td>
<td colspan="3" style="padding:10px;font-family:仿宋;"><span class="template-field field-block" data-fieldname="缺席人员">{$缺席人员}</span></td>
</tr>
</tbody>
</table>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;margin-top:-1px;" border="1">
<tbody>
<tr style="height:180px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;vertical-align:top;padding-top:15px;">会议内容</td>
<td style="padding:15px;font-family:仿宋;vertical-align:top;line-height:1.8;"><span class="template-field field-block" data-fieldname="会议内容">{$会议内容}</span></td>
</tr>
<tr style="height:120px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;vertical-align:top;padding-top:15px;">会议决议</td>
<td style="padding:15px;font-family:仿宋;vertical-align:top;line-height:1.8;"><span class="template-field field-block" data-fieldname="会议决议">{$会议决议}</span></td>
</tr>
<tr style="height:80px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;vertical-align:top;padding-top:15px;">待办事项</td>
<td style="padding:15px;font-family:仿宋;vertical-align:top;line-height:1.8;"><span class="template-field field-block" data-fieldname="待办事项">{$待办事项}</span></td>
</tr>
</tbody>
</table>
<div style="margin-top:25px;text-align:right;font-family:仿宋;">
<p>记录人：<span class="template-field field-block" data-fieldname="记录人">{$记录人}</span></p>
<p>日期：<span class="template-field field-block" data-fieldname="日期">{$日期}</span></p>
</div>
</div>"""
    }


def template_purchase_request() -> dict:
    """采购申请单"""
    return {
        "name": "采购申请单",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 267mm; padding: 15mm; box-sizing: border-box; font-family: SimSun, serif; font-size: 14px; background: white;">
<p style="text-align:center;margin-bottom:20px;"><span style="font-size:24px;font-family:方正小标宋简体;font-weight:bold;">采 购 申 请 单</span></p>
<p style="text-align:right;margin-bottom:15px;font-family:仿宋;">编号：<span class="template-field field-block" data-fieldname="编号">{$编号}</span>　日期：<span class="template-field field-block" data-fieldname="日期">{$日期}</span></p>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;" border="1">
<tbody>
<tr style="height:40px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">申请部门</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="部门">{$部门}</span></td>
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">申请人</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="申请人">{$申请人}</span></td>
</tr>
<tr style="height:40px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">采购类型</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="采购类型">{$采购类型}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">期望到货</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="期望到货日期">{$期望到货日期}</span></td>
</tr>
</tbody>
</table>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;margin-top:-1px;" border="1">
<thead>
<tr style="height:35px;background:#f5f5f5;">
<th style="width:6%;font-family:仿宋;">序号</th>
<th style="width:24%;font-family:仿宋;">物品名称</th>
<th style="width:15%;font-family:仿宋;">规格型号</th>
<th style="width:8%;font-family:仿宋;">单位</th>
<th style="width:8%;font-family:仿宋;">数量</th>
<th style="width:12%;font-family:仿宋;">预估单价</th>
<th style="width:12%;font-family:仿宋;">预估金额</th>
<th style="width:15%;font-family:仿宋;">备注</th>
</tr>
</thead>
<tbody>
<tr style="height:40px;"><td style="text-align:center;">1</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:40px;"><td style="text-align:center;">2</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:40px;"><td style="text-align:center;">3</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:40px;"><td style="text-align:center;">4</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:40px;"><td style="text-align:center;">5</td><td></td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:35px;background:#f5f5f5;">
<td colspan="6" style="text-align:right;padding-right:15px;font-family:仿宋;font-weight:bold;">合计金额：</td>
<td style="text-align:center;font-family:仿宋;color:#c00;font-weight:bold;">￥<span class="template-field field-block" data-fieldname="总金额">{$总金额}</span></td>
<td></td>
</tr>
</tbody>
</table>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;margin-top:-1px;" border="1">
<tbody>
<tr style="height:80px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">采购理由</td>
<td style="padding:10px;font-family:仿宋;vertical-align:top;"><span class="template-field field-block" data-fieldname="采购理由">{$采购理由}</span></td>
</tr>
</tbody>
</table>
<div style="margin-top:20px;display:flex;justify-content:space-between;font-family:仿宋;font-size:13px;">
<div>申请人：____________</div>
<div>部门负责人：____________</div>
<div>采购部：____________</div>
<div>财务部：____________</div>
</div>
</div>"""
    }


def template_contract_approval() -> dict:
    """合同审批单"""
    return {
        "name": "合同审批单",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 267mm; padding: 15mm; box-sizing: border-box; font-family: SimSun, serif; font-size: 14px; background: white;">
<p style="text-align:center;margin-bottom:20px;"><span style="font-size:24px;font-family:方正小标宋简体;font-weight:bold;">合 同 审 批 单</span></p>
<p style="text-align:right;margin-bottom:15px;font-family:仿宋;">编号：<span class="template-field field-block" data-fieldname="编号">{$编号}</span>　日期：<span class="template-field field-block" data-fieldname="日期">{$日期}</span></p>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;" border="1">
<tbody>
<tr style="height:45px;">
<td style="width:18%;text-align:center;font-family:仿宋;background:#f5f5f5;">合同名称</td>
<td colspan="3" style="padding:10px;font-family:仿宋;"><span class="template-field field-block" data-fieldname="合同名称">{$合同名称}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">合同编号</td>
<td style="width:32%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="合同编号">{$合同编号}</span></td>
<td style="width:18%;text-align:center;font-family:仿宋;background:#f5f5f5;">合同类型</td>
<td style="width:32%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="合同类型">{$合同类型}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">对方单位</td>
<td colspan="3" style="padding:10px;font-family:仿宋;"><span class="template-field field-block" data-fieldname="对方单位">{$对方单位}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">合同金额</td>
<td style="text-align:center;font-family:仿宋;color:#c00;font-weight:bold;">￥<span class="template-field field-block" data-fieldname="合同金额">{$合同金额}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">付款方式</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="付款方式">{$付款方式}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">签订日期</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="签订日期">{$签订日期}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">有效期至</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="有效期">{$有效期}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">经办部门</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="经办部门">{$经办部门}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">经办人</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="经办人">{$经办人}</span></td>
</tr>
<tr style="height:100px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">合同摘要</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;line-height:1.8;"><span class="template-field field-block" data-fieldname="合同摘要">{$合同摘要}</span></td>
</tr>
<tr style="height:70px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">法务意见</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;"></td>
</tr>
<tr style="height:70px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">财务意见</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;"></td>
</tr>
<tr style="height:70px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">领导审批</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;"></td>
</tr>
</tbody>
</table>
</div>"""
    }


def template_employee_info() -> dict:
    """员工信息登记表"""
    return {
        "name": "员工信息登记表",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 267mm; padding: 15mm; box-sizing: border-box; font-family: SimSun, serif; font-size: 14px; background: white;">
<p style="text-align:center;margin-bottom:20px;"><span style="font-size:24px;font-family:方正小标宋简体;font-weight:bold;">员 工 信 息 登 记 表</span></p>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;" border="1">
<tbody>
<tr style="height:45px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">姓名</td>
<td style="width:20%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="姓名">{$姓名}</span></td>
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">性别</td>
<td style="width:15%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="性别">{$性别}</span></td>
<td rowspan="4" style="width:20%;text-align:center;font-family:仿宋;padding:10px;">照片<br/><br/>(一寸免冠照)</td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">出生日期</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="出生日期">{$出生日期}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">民族</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="民族">{$民族}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">身份证号</td>
<td colspan="3" style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="身份证号">{$身份证号}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">联系电话</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="电话">{$电话}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">邮箱</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="邮箱">{$邮箱}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">学历</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="学历">{$学历}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">毕业院校</td>
<td colspan="2" style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="毕业院校">{$毕业院校}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">专业</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="专业">{$专业}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">毕业时间</td>
<td colspan="2" style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="毕业时间">{$毕业时间}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">入职部门</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="部门">{$部门}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">职位</td>
<td colspan="2" style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="职位">{$职位}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">入职日期</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="入职日期">{$入职日期}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">工号</td>
<td colspan="2" style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="工号">{$工号}</span></td>
</tr>
<tr style="height:60px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">家庭住址</td>
<td colspan="4" style="padding:10px;font-family:仿宋;"><span class="template-field field-block" data-fieldname="家庭住址">{$家庭住址}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">紧急联系人</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="紧急联系人">{$紧急联系人}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">联系电话</td>
<td colspan="2" style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="紧急联系电话">{$紧急联系电话}</span></td>
</tr>
<tr style="height:100px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">备注</td>
<td colspan="4" style="padding:10px;font-family:仿宋;vertical-align:top;"><span class="template-field field-block" data-fieldname="备注">{$备注}</span></td>
</tr>
</tbody>
</table>
<div style="margin-top:25px;display:flex;justify-content:space-between;font-family:仿宋;">
<div>本人签名：________________</div>
<div>人事确认：________________</div>
<div>日期：________________</div>
</div>
</div>"""
    }


def template_overtime_application() -> dict:
    """加班申请单"""
    return {
        "name": "加班申请单",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 267mm; padding: 15mm; box-sizing: border-box; font-family: SimSun, serif; font-size: 14px; background: white;">
<p style="text-align:center;margin-bottom:20px;"><span style="font-size:24px;font-family:方正小标宋简体;font-weight:bold;">加 班 申 请 单</span></p>
<p style="text-align:right;margin-bottom:15px;font-family:仿宋;">编号：<span class="template-field field-block" data-fieldname="编号">{$编号}</span>　申请日期：<span class="template-field field-block" data-fieldname="申请日期">{$申请日期}</span></p>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;" border="1">
<tbody>
<tr style="height:45px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">申请人</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="姓名">{$姓名}</span></td>
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">部门</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="部门">{$部门}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">加班类型</td>
<td colspan="3" style="text-align:center;font-family:仿宋;">
□ 工作日加班　□ 周末加班　□ 节假日加班
</td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">加班日期</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="加班日期">{$加班日期}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">加班时长</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="加班时长">{$加班时长}</span> 小时</td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">开始时间</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="开始时间">{$开始时间}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">结束时间</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="结束时间">{$结束时间}</span></td>
</tr>
<tr style="height:120px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">加班事由</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;line-height:1.8;"><span class="template-field field-block" data-fieldname="加班事由">{$加班事由}</span></td>
</tr>
<tr style="height:80px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">部门审批</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;"></td>
</tr>
<tr style="height:80px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">人事审批</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;"></td>
</tr>
</tbody>
</table>
<div style="margin-top:25px;font-family:仿宋;font-size:12px;color:#666;">
<p>注：1. 加班需提前申请，经批准后方可加班；2. 加班完成后需在考勤系统中确认。</p>
</div>
</div>"""
    }


def template_visitor_registration() -> dict:
    """访客登记表"""
    return {
        "name": "访客登记表",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 267mm; padding: 15mm; box-sizing: border-box; font-family: SimSun, serif; font-size: 14px; background: white;">
<p style="text-align:center;margin-bottom:20px;"><span style="font-size:24px;font-family:方正小标宋简体;font-weight:bold;">访 客 登 记 表</span></p>
<p style="text-align:right;margin-bottom:15px;font-family:仿宋;">日期：<span class="template-field field-block" data-fieldname="日期">{$日期}</span></p>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;" border="1">
<tbody>
<tr style="height:45px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">访客姓名</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="访客姓名">{$访客姓名}</span></td>
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">证件号码</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="证件号码">{$证件号码}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">所属单位</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="所属单位">{$所属单位}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">联系电话</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="联系电话">{$联系电话}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">被访部门</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="被访部门">{$被访部门}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">被访人</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="被访人">{$被访人}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">来访时间</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="来访时间">{$来访时间}</span></td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">离开时间</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="离开时间">{$离开时间}</span></td>
</tr>
<tr style="height:45px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">随行人数</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="随行人数">{$随行人数}</span> 人</td>
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">车牌号码</td>
<td style="text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="车牌号码">{$车牌号码}</span></td>
</tr>
<tr style="height:80px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">来访事由</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;"><span class="template-field field-block" data-fieldname="来访事由">{$来访事由}</span></td>
</tr>
<tr style="height:60px;">
<td style="text-align:center;font-family:仿宋;background:#f5f5f5;">携带物品</td>
<td colspan="3" style="padding:10px;font-family:仿宋;vertical-align:top;"><span class="template-field field-block" data-fieldname="携带物品">{$携带物品}</span></td>
</tr>
</tbody>
</table>
<div style="margin-top:25px;display:flex;justify-content:space-between;font-family:仿宋;">
<div>访客签名：________________</div>
<div>被访人确认：________________</div>
<div>门卫签字：________________</div>
</div>
<div style="margin-top:20px;font-family:仿宋;font-size:12px;color:#666;">
<p>注：1. 访客须出示有效证件登记；2. 离开时请在门卫处签退。</p>
</div>
</div>"""
    }


def template_asset_requisition() -> dict:
    """物资领用单"""
    return {
        "name": "物资领用单",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 267mm; padding: 15mm; box-sizing: border-box; font-family: SimSun, serif; font-size: 14px; background: white;">
<p style="text-align:center;margin-bottom:20px;"><span style="font-size:24px;font-family:方正小标宋简体;font-weight:bold;">物 资 领 用 单</span></p>
<p style="text-align:right;margin-bottom:15px;font-family:仿宋;">编号：<span class="template-field field-block" data-fieldname="编号">{$编号}</span>　日期：<span class="template-field field-block" data-fieldname="日期">{$日期}</span></p>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;" border="1">
<tbody>
<tr style="height:40px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">领用部门</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="部门">{$部门}</span></td>
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">领用人</td>
<td style="width:35%;text-align:center;font-family:仿宋;"><span class="template-field field-block" data-fieldname="领用人">{$领用人}</span></td>
</tr>
</tbody>
</table>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;margin-top:-1px;" border="1">
<thead>
<tr style="height:35px;background:#f5f5f5;">
<th style="width:8%;font-family:仿宋;">序号</th>
<th style="width:25%;font-family:仿宋;">物资名称</th>
<th style="width:17%;font-family:仿宋;">规格型号</th>
<th style="width:10%;font-family:仿宋;">单位</th>
<th style="width:10%;font-family:仿宋;">申请数量</th>
<th style="width:10%;font-family:仿宋;">实发数量</th>
<th style="width:20%;font-family:仿宋;">备注</th>
</tr>
</thead>
<tbody>
<tr style="height:40px;"><td style="text-align:center;">1</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:40px;"><td style="text-align:center;">2</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:40px;"><td style="text-align:center;">3</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:40px;"><td style="text-align:center;">4</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:40px;"><td style="text-align:center;">5</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
<tr style="height:40px;"><td style="text-align:center;">6</td><td></td><td></td><td></td><td></td><td></td><td></td></tr>
</tbody>
</table>
<table style="border-collapse:collapse;width:100%;border:1px solid #000;margin-top:-1px;" border="1">
<tbody>
<tr style="height:70px;">
<td style="width:15%;text-align:center;font-family:仿宋;background:#f5f5f5;">领用事由</td>
<td style="padding:10px;font-family:仿宋;vertical-align:top;"><span class="template-field field-block" data-fieldname="领用事由">{$领用事由}</span></td>
</tr>
</tbody>
</table>
<div style="margin-top:25px;display:flex;justify-content:space-between;font-family:仿宋;font-size:13px;">
<div>领用人：____________</div>
<div>部门负责人：____________</div>
<div>仓库管理员：____________</div>
<div>行政审批：____________</div>
</div>
</div>"""
    }


# ============================================================
# 现代设计模板（10个）- 彩色卡片风格，适合现代办公场景
# ============================================================

def template_modern_project_report() -> dict:
    """项目进度报告（现代风格）"""
    return {
        "name": "项目进度报告",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 297mm; padding: 15mm; box-sizing: border-box; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 14px; background: #fff;">
<div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px 25px; border-radius: 12px; margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<div style="font-size: 24px; font-weight: 700;">项目进度报告</div>
<div style="font-size: 13px; opacity: 0.9; margin-top: 5px;"><span class="template-field field-block" data-fieldname="项目名称">{$项目名称}</span></div>
</div>
<div style="text-align: right; font-size: 12px;">
<div>报告日期：<span class="template-field field-block" data-fieldname="日期">{$日期}</span></div>
<div style="margin-top: 3px;">编号：<span class="template-field field-block" data-fieldname="编号">{$编号}</span></div>
</div>
</div>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
<div style="background: #f8fafc; border-left: 4px solid #667eea; padding: 15px; border-radius: 8px;">
<div style="font-size: 12px; color: #64748b; margin-bottom: 6px;">项目负责人</div>
<div style="font-size: 16px; font-weight: 600; color: #1e293b;"><span class="template-field field-block" data-fieldname="负责人">{$负责人}</span></div>
</div>
<div style="background: #f8fafc; border-left: 4px solid #22c55e; padding: 15px; border-radius: 8px;">
<div style="font-size: 12px; color: #64748b; margin-bottom: 6px;">当前进度</div>
<div style="font-size: 16px; font-weight: 600; color: #22c55e;"><span class="template-field field-block" data-fieldname="进度">{$进度}</span>%</div>
</div>
<div style="background: #f8fafc; border-left: 4px solid #f59e0b; padding: 15px; border-radius: 8px;">
<div style="font-size: 12px; color: #64748b; margin-bottom: 6px;">开始日期</div>
<div style="font-size: 16px; font-weight: 600; color: #1e293b;"><span class="template-field field-block" data-fieldname="开始日期">{$开始日期}</span></div>
</div>
<div style="background: #f8fafc; border-left: 4px solid #ef4444; padding: 15px; border-radius: 8px;">
<div style="font-size: 12px; color: #64748b; margin-bottom: 6px;">截止日期</div>
<div style="font-size: 16px; font-weight: 600; color: #1e293b;"><span class="template-field field-block" data-fieldname="截止日期">{$截止日期}</span></div>
</div>
</div>

<div style="background: #f8fafc; border-radius: 10px; padding: 20px; margin-bottom: 15px;">
<div style="font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 12px; display: flex; align-items: center;">
<span style="width: 4px; height: 18px; background: #667eea; border-radius: 2px; margin-right: 10px;"></span>
本周完成工作
</div>
<div style="color: #475569; line-height: 1.8;"><span class="template-field field-block" data-fieldname="本周完成">{$本周完成}</span></div>
</div>

<div style="background: #f8fafc; border-radius: 10px; padding: 20px; margin-bottom: 15px;">
<div style="font-size: 16px; font-weight: 600; color: #334155; margin-bottom: 12px; display: flex; align-items: center;">
<span style="width: 4px; height: 18px; background: #22c55e; border-radius: 2px; margin-right: 10px;"></span>
下周工作计划
</div>
<div style="color: #475569; line-height: 1.8;"><span class="template-field field-block" data-fieldname="下周计划">{$下周计划}</span></div>
</div>

<div style="background: #fef3c7; border-radius: 10px; padding: 20px; margin-bottom: 15px;">
<div style="font-size: 16px; font-weight: 600; color: #92400e; margin-bottom: 12px; display: flex; align-items: center;">
<span style="width: 4px; height: 18px; background: #f59e0b; border-radius: 2px; margin-right: 10px;"></span>
风险与问题
</div>
<div style="color: #78350f; line-height: 1.8;"><span class="template-field field-block" data-fieldname="风险问题">{$风险问题}</span></div>
</div>

<div style="display: flex; justify-content: space-between; margin-top: 25px; padding-top: 15px; border-top: 1px solid #e2e8f0;">
<div style="text-align: center;">
<div style="font-size: 12px; color: #94a3b8; margin-bottom: 8px;">项目负责人</div>
<div style="width: 100px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 12px; color: #94a3b8; margin-bottom: 8px;">部门经理</div>
<div style="width: 100px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 12px; color: #94a3b8; margin-bottom: 8px;">日期</div>
<div style="width: 100px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
</div>
</div>"""
    }


def template_modern_quotation() -> dict:
    """报价单（现代风格）"""
    return {
        "name": "商业报价单",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 297mm; padding: 15mm; box-sizing: border-box; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 14px; background: #fff;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 25px;">
<div>
<div style="font-size: 28px; font-weight: 700; color: #0f172a;">报 价 单</div>
<div style="font-size: 13px; color: #64748b; margin-top: 5px;">QUOTATION</div>
</div>
<div style="text-align: right;">
<div style="font-size: 12px; color: #64748b;">报价编号</div>
<div style="font-size: 18px; font-weight: 600; color: #3b82f6;"><span class="template-field field-block" data-fieldname="编号">{$编号}</span></div>
<div style="font-size: 12px; color: #64748b; margin-top: 8px;">报价日期：<span class="template-field field-block" data-fieldname="日期">{$日期}</span></div>
</div>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 25px;">
<div style="background: #f1f5f9; border-radius: 10px; padding: 18px;">
<div style="font-size: 13px; font-weight: 600; color: #3b82f6; margin-bottom: 12px;">供应商信息</div>
<div style="font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 6px;"><span class="template-field field-block" data-fieldname="供应商">{$供应商}</span></div>
<div style="font-size: 13px; color: #64748b; line-height: 1.6;">
联系人：<span class="template-field field-block" data-fieldname="联系人">{$联系人}</span><br/>
电话：<span class="template-field field-block" data-fieldname="电话">{$电话}</span>
</div>
</div>
<div style="background: #f1f5f9; border-radius: 10px; padding: 18px;">
<div style="font-size: 13px; font-weight: 600; color: #22c55e; margin-bottom: 12px;">客户信息</div>
<div style="font-size: 15px; font-weight: 600; color: #1e293b; margin-bottom: 6px;"><span class="template-field field-block" data-fieldname="客户名称">{$客户名称}</span></div>
<div style="font-size: 13px; color: #64748b; line-height: 1.6;">
联系人：<span class="template-field field-block" data-fieldname="客户联系人">{$客户联系人}</span><br/>
电话：<span class="template-field field-block" data-fieldname="客户电话">{$客户电话}</span>
</div>
</div>
</div>

<table style="width: 100%; border-collapse: collapse; margin-bottom: 20px;">
<thead>
<tr style="background: #3b82f6; color: white;">
<th style="padding: 12px 10px; text-align: left; font-weight: 500; border-radius: 8px 0 0 0;">序号</th>
<th style="padding: 12px 10px; text-align: left; font-weight: 500;">产品名称</th>
<th style="padding: 12px 10px; text-align: left; font-weight: 500;">规格型号</th>
<th style="padding: 12px 10px; text-align: center; font-weight: 500;">数量</th>
<th style="padding: 12px 10px; text-align: right; font-weight: 500;">单价</th>
<th style="padding: 12px 10px; text-align: right; font-weight: 500; border-radius: 0 8px 0 0;">金额</th>
</tr>
</thead>
<tbody>
<tr style="background: #f8fafc;"><td style="padding: 12px 10px;">1</td><td style="padding: 12px 10px;"></td><td style="padding: 12px 10px;"></td><td style="padding: 12px 10px; text-align: center;"></td><td style="padding: 12px 10px; text-align: right;"></td><td style="padding: 12px 10px; text-align: right;"></td></tr>
<tr><td style="padding: 12px 10px;">2</td><td style="padding: 12px 10px;"></td><td style="padding: 12px 10px;"></td><td style="padding: 12px 10px; text-align: center;"></td><td style="padding: 12px 10px; text-align: right;"></td><td style="padding: 12px 10px; text-align: right;"></td></tr>
<tr style="background: #f8fafc;"><td style="padding: 12px 10px;">3</td><td style="padding: 12px 10px;"></td><td style="padding: 12px 10px;"></td><td style="padding: 12px 10px; text-align: center;"></td><td style="padding: 12px 10px; text-align: right;"></td><td style="padding: 12px 10px; text-align: right;"></td></tr>
<tr><td style="padding: 12px 10px;">4</td><td style="padding: 12px 10px;"></td><td style="padding: 12px 10px;"></td><td style="padding: 12px 10px; text-align: center;"></td><td style="padding: 12px 10px; text-align: right;"></td><td style="padding: 12px 10px; text-align: right;"></td></tr>
<tr style="background: #f8fafc;"><td style="padding: 12px 10px;">5</td><td style="padding: 12px 10px;"></td><td style="padding: 12px 10px;"></td><td style="padding: 12px 10px; text-align: center;"></td><td style="padding: 12px 10px; text-align: right;"></td><td style="padding: 12px 10px; text-align: right;"></td></tr>
</tbody>
</table>

<div style="display: flex; justify-content: flex-end; margin-bottom: 20px;">
<div style="background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%); color: white; padding: 15px 30px; border-radius: 10px;">
<div style="font-size: 13px; opacity: 0.9;">报价总金额</div>
<div style="font-size: 26px; font-weight: 700;">￥<span class="template-field field-block" data-fieldname="总金额">{$总金额}</span></div>
</div>
</div>

<div style="background: #fffbeb; border: 1px solid #fcd34d; border-radius: 8px; padding: 15px; margin-bottom: 20px;">
<div style="font-size: 13px; font-weight: 600; color: #92400e; margin-bottom: 8px;">📋 报价说明</div>
<div style="font-size: 13px; color: #78350f; line-height: 1.7;"><span class="template-field field-block" data-fieldname="备注">{$备注}</span></div>
</div>

<div style="font-size: 12px; color: #94a3b8; line-height: 1.6;">
<p>• 本报价有效期：<span class="template-field field-block" data-fieldname="有效期">{$有效期}</span> 天</p>
<p>• 付款方式：<span class="template-field field-block" data-fieldname="付款方式">{$付款方式}</span></p>
<p>• 交货期：<span class="template-field field-block" data-fieldname="交货期">{$交货期}</span></p>
</div>

<div style="display: flex; justify-content: space-between; margin-top: 30px; padding-top: 20px; border-top: 1px dashed #e2e8f0;">
<div><span style="color: #94a3b8; font-size: 12px;">供应商盖章：</span></div>
<div><span style="color: #94a3b8; font-size: 12px;">客户确认：</span></div>
</div>
</div>"""
    }


def template_modern_invoice() -> dict:
    """收据/发票（现代风格）"""
    return {
        "name": "收款收据",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 297mm; padding: 15mm; box-sizing: border-box; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 14px; background: #fff;">
<div style="border: 2px solid #10b981; border-radius: 15px; padding: 25px; position: relative;">
<div style="position: absolute; top: -12px; left: 30px; background: white; padding: 0 15px;">
<span style="font-size: 20px; font-weight: 700; color: #10b981;">收 款 收 据</span>
</div>

<div style="display: flex; justify-content: space-between; margin-top: 15px; margin-bottom: 25px;">
<div style="font-size: 13px; color: #64748b;">
收据编号：<span style="color: #0f172a; font-weight: 600;"><span class="template-field field-block" data-fieldname="编号">{$编号}</span></span>
</div>
<div style="font-size: 13px; color: #64748b;">
日期：<span style="color: #0f172a; font-weight: 600;"><span class="template-field field-block" data-fieldname="日期">{$日期}</span></span>
</div>
</div>

<div style="background: #f0fdf4; border-radius: 10px; padding: 20px; margin-bottom: 20px;">
<div style="display: grid; grid-template-columns: 100px 1fr; gap: 15px; align-items: center;">
<div style="font-size: 13px; color: #64748b;">付款单位</div>
<div style="font-size: 16px; font-weight: 600; color: #0f172a;"><span class="template-field field-block" data-fieldname="付款单位">{$付款单位}</span></div>
<div style="font-size: 13px; color: #64748b;">收款事由</div>
<div style="font-size: 15px; color: #334155;"><span class="template-field field-block" data-fieldname="收款事由">{$收款事由}</span></div>
</div>
</div>

<div style="text-align: center; padding: 30px 0; border-top: 1px dashed #d1d5db; border-bottom: 1px dashed #d1d5db;">
<div style="font-size: 14px; color: #64748b; margin-bottom: 10px;">收款金额（人民币）</div>
<div style="font-size: 42px; font-weight: 700; color: #10b981;">
￥<span class="template-field field-block" data-fieldname="金额">{$金额}</span>
</div>
<div style="font-size: 14px; color: #64748b; margin-top: 10px;">
大写：<span style="color: #0f172a; font-weight: 500;"><span class="template-field field-block" data-fieldname="金额大写">{$金额大写}</span></span>
</div>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-top: 25px;">
<div>
<div style="font-size: 12px; color: #94a3b8; margin-bottom: 8px;">收款方式</div>
<div style="display: flex; gap: 15px; font-size: 13px; color: #475569;">
<label><input type="checkbox" style="margin-right: 5px;"/>现金</label>
<label><input type="checkbox" style="margin-right: 5px;"/>转账</label>
<label><input type="checkbox" style="margin-right: 5px;"/>支票</label>
</div>
</div>
<div>
<div style="font-size: 12px; color: #94a3b8; margin-bottom: 8px;">收款账户</div>
<div style="font-size: 13px; color: #334155;"><span class="template-field field-block" data-fieldname="收款账户">{$收款账户}</span></div>
</div>
</div>

<div style="background: #fefce8; border-radius: 8px; padding: 12px 15px; margin-top: 20px;">
<div style="font-size: 12px; color: #854d0e;">
备注：<span class="template-field field-block" data-fieldname="备注">{$备注}</span>
</div>
</div>

<div style="display: flex; justify-content: space-between; margin-top: 30px;">
<div style="text-align: center;">
<div style="font-size: 12px; color: #94a3b8; margin-bottom: 30px;">收款单位（盖章）</div>
<div style="width: 120px; border-bottom: 1px solid #d1d5db;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 12px; color: #94a3b8; margin-bottom: 30px;">收款人签字</div>
<div style="width: 120px; border-bottom: 1px solid #d1d5db;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 12px; color: #94a3b8; margin-bottom: 30px;">付款人签字</div>
<div style="width: 120px; border-bottom: 1px solid #d1d5db;"></div>
</div>
</div>
</div>

<div style="text-align: center; margin-top: 15px; font-size: 11px; color: #94a3b8;">
本收据一式两联，第一联存根，第二联交付款方
</div>
</div>"""
    }


def template_modern_work_order() -> dict:
    """工单（现代风格）"""
    return {
        "name": "服务工单",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 297mm; padding: 15mm; box-sizing: border-box; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 14px; background: #fff;">
<div style="display: flex; justify-content: space-between; align-items: center; padding-bottom: 20px; border-bottom: 2px solid #e2e8f0;">
<div>
<div style="font-size: 26px; font-weight: 700; color: #0f172a;">服务工单</div>
<div style="font-size: 12px; color: #64748b; margin-top: 5px;">SERVICE WORK ORDER</div>
</div>
<div style="background: #fee2e2; color: #dc2626; padding: 8px 20px; border-radius: 20px; font-size: 13px; font-weight: 600;">
<span class="template-field field-block" data-fieldname="状态">{$状态}</span>
</div>
</div>

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin: 20px 0;">
<div style="background: #f8fafc; padding: 15px; border-radius: 10px;">
<div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">工单编号</div>
<div style="font-size: 16px; font-weight: 600; color: #0f172a; margin-top: 5px;"><span class="template-field field-block" data-fieldname="编号">{$编号}</span></div>
</div>
<div style="background: #f8fafc; padding: 15px; border-radius: 10px;">
<div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">创建时间</div>
<div style="font-size: 16px; font-weight: 600; color: #0f172a; margin-top: 5px;"><span class="template-field field-block" data-fieldname="创建时间">{$创建时间}</span></div>
</div>
<div style="background: #f8fafc; padding: 15px; border-radius: 10px;">
<div style="font-size: 11px; color: #94a3b8; text-transform: uppercase;">优先级</div>
<div style="font-size: 16px; font-weight: 600; color: #f59e0b; margin-top: 5px;"><span class="template-field field-block" data-fieldname="优先级">{$优先级}</span></div>
</div>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px; margin-bottom: 20px;">
<div style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px;">
<div style="font-size: 13px; font-weight: 600; color: #6366f1; margin-bottom: 12px;">👤 客户信息</div>
<div style="display: grid; gap: 8px; font-size: 13px;">
<div><span style="color: #94a3b8;">客户名称：</span><span class="template-field field-block" data-fieldname="客户名称">{$客户名称}</span></div>
<div><span style="color: #94a3b8;">联系电话：</span><span class="template-field field-block" data-fieldname="联系电话">{$联系电话}</span></div>
<div><span style="color: #94a3b8;">地址：</span><span class="template-field field-block" data-fieldname="地址">{$地址}</span></div>
</div>
</div>
<div style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 18px;">
<div style="font-size: 13px; font-weight: 600; color: #10b981; margin-bottom: 12px;">🔧 服务人员</div>
<div style="display: grid; gap: 8px; font-size: 13px;">
<div><span style="color: #94a3b8;">负责人：</span><span class="template-field field-block" data-fieldname="负责人">{$负责人}</span></div>
<div><span style="color: #94a3b8;">联系电话：</span><span class="template-field field-block" data-fieldname="负责人电话">{$负责人电话}</span></div>
<div><span style="color: #94a3b8;">预约时间：</span><span class="template-field field-block" data-fieldname="预约时间">{$预约时间}</span></div>
</div>
</div>
</div>

<div style="background: #f8fafc; border-radius: 10px; padding: 20px; margin-bottom: 15px;">
<div style="font-size: 14px; font-weight: 600; color: #334155; margin-bottom: 12px;">📋 问题描述</div>
<div style="color: #475569; line-height: 1.8; min-height: 60px;"><span class="template-field field-block" data-fieldname="问题描述">{$问题描述}</span></div>
</div>

<div style="background: #f8fafc; border-radius: 10px; padding: 20px; margin-bottom: 15px;">
<div style="font-size: 14px; font-weight: 600; color: #334155; margin-bottom: 12px;">✅ 处理结果</div>
<div style="color: #475569; line-height: 1.8; min-height: 60px;"><span class="template-field field-block" data-fieldname="处理结果">{$处理结果}</span></div>
</div>

<div style="display: flex; justify-content: space-between; margin-top: 25px; padding-top: 20px; border-top: 1px dashed #e2e8f0;">
<div style="text-align: center;">
<div style="font-size: 12px; color: #94a3b8; margin-bottom: 25px;">客户签字确认</div>
<div style="width: 120px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 12px; color: #94a3b8; margin-bottom: 25px;">服务人员签字</div>
<div style="width: 120px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 12px; color: #94a3b8; margin-bottom: 25px;">完成日期</div>
<div style="width: 120px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
</div>
</div>"""
    }



def template_modern_delivery_note() -> dict:
    """送货单（现代风格）"""
    return {
        "name": "送货单",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 297mm; padding: 15mm; box-sizing: border-box; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 14px; background: #fff;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
<div>
<div style="font-size: 26px; font-weight: 700; color: #0f172a;">送 货 单</div>
<div style="font-size: 12px; color: #64748b; margin-top: 3px;">DELIVERY NOTE</div>
</div>
<div style="text-align: right;">
<div style="background: #dbeafe; color: #1d4ed8; padding: 6px 15px; border-radius: 15px; font-size: 12px; font-weight: 500; display: inline-block;">
单号：<span class="template-field field-block" data-fieldname="编号">{$编号}</span>
</div>
<div style="font-size: 12px; color: #64748b; margin-top: 8px;">日期：<span class="template-field field-block" data-fieldname="日期">{$日期}</span></div>
</div>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
<div style="background: #f0f9ff; border-radius: 10px; padding: 15px;">
<div style="font-size: 12px; color: #0369a1; font-weight: 600; margin-bottom: 10px;">📦 发货方</div>
<div style="font-size: 14px; color: #0f172a; font-weight: 500; margin-bottom: 5px;"><span class="template-field field-block" data-fieldname="发货方">{$发货方}</span></div>
<div style="font-size: 12px; color: #64748b;">联系人：<span class="template-field field-block" data-fieldname="发货联系人">{$发货联系人}</span> | <span class="template-field field-block" data-fieldname="发货电话">{$发货电话}</span></div>
</div>
<div style="background: #f0fdf4; border-radius: 10px; padding: 15px;">
<div style="font-size: 12px; color: #15803d; font-weight: 600; margin-bottom: 10px;">📍 收货方</div>
<div style="font-size: 14px; color: #0f172a; font-weight: 500; margin-bottom: 5px;"><span class="template-field field-block" data-fieldname="收货方">{$收货方}</span></div>
<div style="font-size: 12px; color: #64748b;">联系人：<span class="template-field field-block" data-fieldname="收货联系人">{$收货联系人}</span> | <span class="template-field field-block" data-fieldname="收货电话">{$收货电话}</span></div>
</div>
</div>

<div style="font-size: 12px; color: #64748b; margin-bottom: 10px;">收货地址：<span style="color: #334155;"><span class="template-field field-block" data-fieldname="收货地址">{$收货地址}</span></span></div>

<table style="width: 100%; border-collapse: collapse; margin-bottom: 15px;">
<thead>
<tr style="background: #1e40af; color: white;">
<th style="padding: 10px 8px; text-align: center; font-weight: 500; font-size: 13px; border-radius: 6px 0 0 0;">序号</th>
<th style="padding: 10px 8px; text-align: left; font-weight: 500; font-size: 13px;">商品名称</th>
<th style="padding: 10px 8px; text-align: left; font-weight: 500; font-size: 13px;">规格型号</th>
<th style="padding: 10px 8px; text-align: center; font-weight: 500; font-size: 13px;">单位</th>
<th style="padding: 10px 8px; text-align: center; font-weight: 500; font-size: 13px;">数量</th>
<th style="padding: 10px 8px; text-align: center; font-weight: 500; font-size: 13px; border-radius: 0 6px 0 0;">备注</th>
</tr>
</thead>
<tbody>
<tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 10px 8px; text-align: center;">1</td><td style="padding: 10px 8px;"></td><td style="padding: 10px 8px;"></td><td style="padding: 10px 8px; text-align: center;"></td><td style="padding: 10px 8px; text-align: center;"></td><td style="padding: 10px 8px;"></td></tr>
<tr style="border-bottom: 1px solid #e2e8f0; background: #f8fafc;"><td style="padding: 10px 8px; text-align: center;">2</td><td style="padding: 10px 8px;"></td><td style="padding: 10px 8px;"></td><td style="padding: 10px 8px; text-align: center;"></td><td style="padding: 10px 8px; text-align: center;"></td><td style="padding: 10px 8px;"></td></tr>
<tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 10px 8px; text-align: center;">3</td><td style="padding: 10px 8px;"></td><td style="padding: 10px 8px;"></td><td style="padding: 10px 8px; text-align: center;"></td><td style="padding: 10px 8px; text-align: center;"></td><td style="padding: 10px 8px;"></td></tr>
<tr style="border-bottom: 1px solid #e2e8f0; background: #f8fafc;"><td style="padding: 10px 8px; text-align: center;">4</td><td style="padding: 10px 8px;"></td><td style="padding: 10px 8px;"></td><td style="padding: 10px 8px; text-align: center;"></td><td style="padding: 10px 8px; text-align: center;"></td><td style="padding: 10px 8px;"></td></tr>
<tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 10px 8px; text-align: center;">5</td><td style="padding: 10px 8px;"></td><td style="padding: 10px 8px;"></td><td style="padding: 10px 8px; text-align: center;"></td><td style="padding: 10px 8px; text-align: center;"></td><td style="padding: 10px 8px;"></td></tr>
<tr style="border-bottom: 1px solid #e2e8f0; background: #f8fafc;"><td style="padding: 10px 8px; text-align: center;">6</td><td style="padding: 10px 8px;"></td><td style="padding: 10px 8px;"></td><td style="padding: 10px 8px; text-align: center;"></td><td style="padding: 10px 8px; text-align: center;"></td><td style="padding: 10px 8px;"></td></tr>
</tbody>
</table>

<div style="background: #fffbeb; border-radius: 8px; padding: 12px 15px; margin-bottom: 20px;">
<div style="font-size: 12px; color: #92400e;">
<strong>备注：</strong><span class="template-field field-block" data-fieldname="备注">{$备注}</span>
</div>
</div>

<div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; padding-top: 15px; border-top: 1px dashed #e2e8f0;">
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 20px;">制单人</div>
<div style="border-bottom: 1px solid #d1d5db; width: 80%; margin: 0 auto;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 20px;">发货人</div>
<div style="border-bottom: 1px solid #d1d5db; width: 80%; margin: 0 auto;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 20px;">送货人</div>
<div style="border-bottom: 1px solid #d1d5db; width: 80%; margin: 0 auto;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 20px;">收货人</div>
<div style="border-bottom: 1px solid #d1d5db; width: 80%; margin: 0 auto;"></div>
</div>
</div>
</div>"""
    }


def template_modern_interview_evaluation() -> dict:
    """面试评估表（现代风格）"""
    return {
        "name": "面试评估表",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 297mm; padding: 15mm; box-sizing: border-box; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 14px; background: #fff;">
<div style="background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%); color: white; padding: 20px 25px; border-radius: 12px; margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<div style="font-size: 22px; font-weight: 700;">面试评估表</div>
<div style="font-size: 12px; opacity: 0.9; margin-top: 3px;">INTERVIEW EVALUATION FORM</div>
</div>
<div style="text-align: right; font-size: 12px;">
<div>面试日期：<span class="template-field field-block" data-fieldname="面试日期">{$面试日期}</span></div>
</div>
</div>
</div>

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;">
<div style="background: #f8fafc; padding: 12px 15px; border-radius: 8px;">
<div style="font-size: 11px; color: #94a3b8;">应聘者</div>
<div style="font-size: 15px; font-weight: 600; color: #1e293b; margin-top: 4px;"><span class="template-field field-block" data-fieldname="姓名">{$姓名}</span></div>
</div>
<div style="background: #f8fafc; padding: 12px 15px; border-radius: 8px;">
<div style="font-size: 11px; color: #94a3b8;">应聘职位</div>
<div style="font-size: 15px; font-weight: 600; color: #1e293b; margin-top: 4px;"><span class="template-field field-block" data-fieldname="应聘职位">{$应聘职位}</span></div>
</div>
<div style="background: #f8fafc; padding: 12px 15px; border-radius: 8px;">
<div style="font-size: 11px; color: #94a3b8;">面试官</div>
<div style="font-size: 15px; font-weight: 600; color: #1e293b; margin-top: 4px;"><span class="template-field field-block" data-fieldname="面试官">{$面试官}</span></div>
</div>
</div>

<div style="margin-bottom: 20px;">
<div style="font-size: 14px; font-weight: 600; color: #334155; margin-bottom: 12px; display: flex; align-items: center;">
<span style="width: 4px; height: 16px; background: #6366f1; border-radius: 2px; margin-right: 8px;"></span>
评估项目
</div>
<table style="width: 100%; border-collapse: collapse;">
<thead>
<tr style="background: #f1f5f9;">
<th style="padding: 10px; text-align: left; font-weight: 500; font-size: 13px;">评估维度</th>
<th style="padding: 10px; text-align: center; font-weight: 500; font-size: 13px; width: 60px;">优秀</th>
<th style="padding: 10px; text-align: center; font-weight: 500; font-size: 13px; width: 60px;">良好</th>
<th style="padding: 10px; text-align: center; font-weight: 500; font-size: 13px; width: 60px;">一般</th>
<th style="padding: 10px; text-align: center; font-weight: 500; font-size: 13px; width: 60px;">较差</th>
<th style="padding: 10px; text-align: left; font-weight: 500; font-size: 13px;">备注</th>
</tr>
</thead>
<tbody>
<tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 10px;">专业技能</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px;"></td></tr>
<tr style="border-bottom: 1px solid #e2e8f0; background: #fafafa;"><td style="padding: 10px;">沟通表达</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px;"></td></tr>
<tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 10px;">逻辑思维</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px;"></td></tr>
<tr style="border-bottom: 1px solid #e2e8f0; background: #fafafa;"><td style="padding: 10px;">团队协作</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px;"></td></tr>
<tr style="border-bottom: 1px solid #e2e8f0;"><td style="padding: 10px;">学习能力</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px;"></td></tr>
<tr style="border-bottom: 1px solid #e2e8f0; background: #fafafa;"><td style="padding: 10px;">职业素养</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px; text-align: center;">□</td><td style="padding: 10px;"></td></tr>
</tbody>
</table>
</div>

<div style="background: #f8fafc; border-radius: 10px; padding: 15px; margin-bottom: 15px;">
<div style="font-size: 13px; font-weight: 600; color: #334155; margin-bottom: 8px;">综合评价</div>
<div style="color: #475569; line-height: 1.7; min-height: 50px;"><span class="template-field field-block" data-fieldname="综合评价">{$综合评价}</span></div>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
<div style="background: #f0fdf4; border-radius: 8px; padding: 12px 15px;">
<div style="font-size: 12px; color: #15803d; font-weight: 500; margin-bottom: 6px;">✓ 优势</div>
<div style="font-size: 13px; color: #166534;"><span class="template-field field-block" data-fieldname="优势">{$优势}</span></div>
</div>
<div style="background: #fef2f2; border-radius: 8px; padding: 12px 15px;">
<div style="font-size: 12px; color: #dc2626; font-weight: 500; margin-bottom: 6px;">✗ 不足</div>
<div style="font-size: 13px; color: #991b1b;"><span class="template-field field-block" data-fieldname="不足">{$不足}</span></div>
</div>
</div>

<div style="display: flex; justify-content: space-between; align-items: center; padding: 15px; background: #f1f5f9; border-radius: 10px;">
<div style="font-size: 14px; font-weight: 600; color: #334155;">录用建议</div>
<div style="display: flex; gap: 20px; font-size: 13px;">
<label>□ 强烈推荐</label>
<label>□ 推荐录用</label>
<label>□ 待定</label>
<label>□ 不推荐</label>
</div>
</div>

<div style="display: flex; justify-content: flex-end; margin-top: 20px; gap: 30px;">
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 15px;">面试官签字</div>
<div style="width: 100px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 15px;">日期</div>
<div style="width: 100px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
</div>
</div>"""
    }


def template_modern_training_record() -> dict:
    """培训记录表（现代风格）"""
    return {
        "name": "培训记录表",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 297mm; padding: 15mm; box-sizing: border-box; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 14px; background: #fff;">
<div style="background: linear-gradient(135deg, #059669 0%, #10b981 100%); color: white; padding: 20px 25px; border-radius: 12px; margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<div style="font-size: 22px; font-weight: 700;">培训记录表</div>
<div style="font-size: 12px; opacity: 0.9; margin-top: 3px;">TRAINING RECORD</div>
</div>
<div style="text-align: right; font-size: 12px;">
<div>编号：<span class="template-field field-block" data-fieldname="编号">{$编号}</span></div>
</div>
</div>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
<div style="background: #f8fafc; border-left: 4px solid #059669; padding: 15px; border-radius: 0 8px 8px 0;">
<div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">培训主题</div>
<div style="font-size: 16px; font-weight: 600; color: #0f172a;"><span class="template-field field-block" data-fieldname="培训主题">{$培训主题}</span></div>
</div>
<div style="background: #f8fafc; border-left: 4px solid #0ea5e9; padding: 15px; border-radius: 0 8px 8px 0;">
<div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">培训讲师</div>
<div style="font-size: 16px; font-weight: 600; color: #0f172a;"><span class="template-field field-block" data-fieldname="讲师">{$讲师}</span></div>
</div>
</div>

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;">
<div style="background: #f8fafc; padding: 12px 15px; border-radius: 8px; text-align: center;">
<div style="font-size: 11px; color: #94a3b8;">培训日期</div>
<div style="font-size: 14px; font-weight: 600; color: #1e293b; margin-top: 4px;"><span class="template-field field-block" data-fieldname="培训日期">{$培训日期}</span></div>
</div>
<div style="background: #f8fafc; padding: 12px 15px; border-radius: 8px; text-align: center;">
<div style="font-size: 11px; color: #94a3b8;">培训时长</div>
<div style="font-size: 14px; font-weight: 600; color: #1e293b; margin-top: 4px;"><span class="template-field field-block" data-fieldname="培训时长">{$培训时长}</span></div>
</div>
<div style="background: #f8fafc; padding: 12px 15px; border-radius: 8px; text-align: center;">
<div style="font-size: 11px; color: #94a3b8;">培训地点</div>
<div style="font-size: 14px; font-weight: 600; color: #1e293b; margin-top: 4px;"><span class="template-field field-block" data-fieldname="培训地点">{$培训地点}</span></div>
</div>
</div>

<div style="background: #f8fafc; border-radius: 10px; padding: 18px; margin-bottom: 15px;">
<div style="font-size: 14px; font-weight: 600; color: #334155; margin-bottom: 10px; display: flex; align-items: center;">
<span style="width: 4px; height: 16px; background: #059669; border-radius: 2px; margin-right: 8px;"></span>
培训内容
</div>
<div style="color: #475569; line-height: 1.8;"><span class="template-field field-block" data-fieldname="培训内容">{$培训内容}</span></div>
</div>

<div style="background: #f8fafc; border-radius: 10px; padding: 18px; margin-bottom: 15px;">
<div style="font-size: 14px; font-weight: 600; color: #334155; margin-bottom: 10px; display: flex; align-items: center;">
<span style="width: 4px; height: 16px; background: #0ea5e9; border-radius: 2px; margin-right: 8px;"></span>
参训人员
</div>
<div style="color: #475569; line-height: 1.8;"><span class="template-field field-block" data-fieldname="参训人员">{$参训人员}</span></div>
</div>

<div style="background: #fef3c7; border-radius: 10px; padding: 18px; margin-bottom: 15px;">
<div style="font-size: 14px; font-weight: 600; color: #92400e; margin-bottom: 10px;">📝 培训总结</div>
<div style="color: #78350f; line-height: 1.8;"><span class="template-field field-block" data-fieldname="培训总结">{$培训总结}</span></div>
</div>

<div style="display: flex; justify-content: space-between; margin-top: 25px; padding-top: 15px; border-top: 1px dashed #e2e8f0;">
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 15px;">培训讲师</div>
<div style="width: 100px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 15px;">部门负责人</div>
<div style="width: 100px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 15px;">人事确认</div>
<div style="width: 100px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
</div>
</div>"""
    }


def template_modern_task_assignment() -> dict:
    """任务分配单（现代风格）"""
    return {
        "name": "任务分配单",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 297mm; padding: 15mm; box-sizing: border-box; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 14px; background: #fff;">
<div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 20px;">
<div>
<div style="font-size: 26px; font-weight: 700; color: #0f172a;">任务分配单</div>
<div style="font-size: 12px; color: #64748b; margin-top: 3px;">TASK ASSIGNMENT</div>
</div>
<div style="display: flex; gap: 10px;">
<div style="background: #fef3c7; color: #92400e; padding: 6px 12px; border-radius: 15px; font-size: 12px; font-weight: 500;">
优先级：<span class="template-field field-block" data-fieldname="优先级">{$优先级}</span>
</div>
<div style="background: #dbeafe; color: #1d4ed8; padding: 6px 12px; border-radius: 15px; font-size: 12px; font-weight: 500;">
<span class="template-field field-block" data-fieldname="编号">{$编号}</span>
</div>
</div>
</div>

<div style="background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%); border-radius: 12px; padding: 20px; margin-bottom: 20px;">
<div style="font-size: 18px; font-weight: 600; color: #1e293b; margin-bottom: 8px;"><span class="template-field field-block" data-fieldname="任务名称">{$任务名称}</span></div>
<div style="font-size: 13px; color: #64748b;"><span class="template-field field-block" data-fieldname="任务描述">{$任务描述}</span></div>
</div>

<div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px; margin-bottom: 20px;">
<div style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px;">
<div style="font-size: 12px; color: #f59e0b; font-weight: 600; margin-bottom: 10px;">📤 分配信息</div>
<div style="display: grid; gap: 8px; font-size: 13px;">
<div><span style="color: #94a3b8;">分配人：</span><span class="template-field field-block" data-fieldname="分配人">{$分配人}</span></div>
<div><span style="color: #94a3b8;">分配日期：</span><span class="template-field field-block" data-fieldname="分配日期">{$分配日期}</span></div>
</div>
</div>
<div style="border: 1px solid #e2e8f0; border-radius: 10px; padding: 15px;">
<div style="font-size: 12px; color: #10b981; font-weight: 600; margin-bottom: 10px;">📥 执行信息</div>
<div style="display: grid; gap: 8px; font-size: 13px;">
<div><span style="color: #94a3b8;">负责人：</span><span class="template-field field-block" data-fieldname="负责人">{$负责人}</span></div>
<div><span style="color: #94a3b8;">协作人：</span><span class="template-field field-block" data-fieldname="协作人">{$协作人}</span></div>
</div>
</div>
</div>

<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 12px; margin-bottom: 20px;">
<div style="background: #ecfdf5; padding: 15px; border-radius: 8px; text-align: center;">
<div style="font-size: 11px; color: #059669;">开始日期</div>
<div style="font-size: 15px; font-weight: 600; color: #047857; margin-top: 5px;"><span class="template-field field-block" data-fieldname="开始日期">{$开始日期}</span></div>
</div>
<div style="background: #fef2f2; padding: 15px; border-radius: 8px; text-align: center;">
<div style="font-size: 11px; color: #dc2626;">截止日期</div>
<div style="font-size: 15px; font-weight: 600; color: #b91c1c; margin-top: 5px;"><span class="template-field field-block" data-fieldname="截止日期">{$截止日期}</span></div>
</div>
<div style="background: #f0f9ff; padding: 15px; border-radius: 8px; text-align: center;">
<div style="font-size: 11px; color: #0369a1;">预计工时</div>
<div style="font-size: 15px; font-weight: 600; color: #0c4a6e; margin-top: 5px;"><span class="template-field field-block" data-fieldname="预计工时">{$预计工时}</span></div>
</div>
</div>

<div style="background: #f8fafc; border-radius: 10px; padding: 18px; margin-bottom: 15px;">
<div style="font-size: 14px; font-weight: 600; color: #334155; margin-bottom: 10px;">📋 任务要求</div>
<div style="color: #475569; line-height: 1.8;"><span class="template-field field-block" data-fieldname="任务要求">{$任务要求}</span></div>
</div>

<div style="background: #f8fafc; border-radius: 10px; padding: 18px; margin-bottom: 15px;">
<div style="font-size: 14px; font-weight: 600; color: #334155; margin-bottom: 10px;">🎯 验收标准</div>
<div style="color: #475569; line-height: 1.8;"><span class="template-field field-block" data-fieldname="验收标准">{$验收标准}</span></div>
</div>

<div style="display: flex; justify-content: space-between; margin-top: 20px; padding-top: 15px; border-top: 1px dashed #e2e8f0;">
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 15px;">分配人确认</div>
<div style="width: 100px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 15px;">负责人确认</div>
<div style="width: 100px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 15px;">日期</div>
<div style="width: 100px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
</div>
</div>"""
    }


def template_modern_customer_feedback() -> dict:
    """客户反馈表（现代风格）"""
    return {
        "name": "客户反馈表",
        "is_system": True,
        "content": """<div id="template-root" style="width: 210mm; height: 297mm; padding: 15mm; box-sizing: border-box; font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif; font-size: 14px; background: #fff;">
<div style="background: linear-gradient(135deg, #ec4899 0%, #f472b6 100%); color: white; padding: 20px 25px; border-radius: 12px; margin-bottom: 20px;">
<div style="display: flex; justify-content: space-between; align-items: center;">
<div>
<div style="font-size: 22px; font-weight: 700;">客户反馈表</div>
<div style="font-size: 12px; opacity: 0.9; margin-top: 3px;">CUSTOMER FEEDBACK FORM</div>
</div>
<div style="text-align: right; font-size: 12px;">
<div>编号：<span class="template-field field-block" data-fieldname="编号">{$编号}</span></div>
<div style="margin-top: 3px;">日期：<span class="template-field field-block" data-fieldname="日期">{$日期}</span></div>
</div>
</div>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 20px;">
<div style="background: #fdf2f8; border-radius: 10px; padding: 15px;">
<div style="font-size: 12px; color: #be185d; font-weight: 600; margin-bottom: 10px;">👤 客户信息</div>
<div style="display: grid; gap: 6px; font-size: 13px; color: #1e293b;">
<div>客户名称：<span class="template-field field-block" data-fieldname="客户名称">{$客户名称}</span></div>
<div>联系人：<span class="template-field field-block" data-fieldname="联系人">{$联系人}</span></div>
<div>联系电话：<span class="template-field field-block" data-fieldname="联系电话">{$联系电话}</span></div>
</div>
</div>
<div style="background: #f8fafc; border-radius: 10px; padding: 15px;">
<div style="font-size: 12px; color: #6366f1; font-weight: 600; margin-bottom: 10px;">📦 产品/服务</div>
<div style="display: grid; gap: 6px; font-size: 13px; color: #1e293b;">
<div>产品名称：<span class="template-field field-block" data-fieldname="产品名称">{$产品名称}</span></div>
<div>购买日期：<span class="template-field field-block" data-fieldname="购买日期">{$购买日期}</span></div>
<div>订单编号：<span class="template-field field-block" data-fieldname="订单编号">{$订单编号}</span></div>
</div>
</div>
</div>

<div style="margin-bottom: 20px;">
<div style="font-size: 14px; font-weight: 600; color: #334155; margin-bottom: 12px;">⭐ 满意度评价</div>
<div style="display: grid; grid-template-columns: repeat(5, 1fr); gap: 10px;">
<div style="background: #f8fafc; padding: 12px; border-radius: 8px; text-align: center;">
<div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">产品质量</div>
<div style="font-size: 18px;">□□□□□</div>
</div>
<div style="background: #f8fafc; padding: 12px; border-radius: 8px; text-align: center;">
<div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">服务态度</div>
<div style="font-size: 18px;">□□□□□</div>
</div>
<div style="background: #f8fafc; padding: 12px; border-radius: 8px; text-align: center;">
<div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">响应速度</div>
<div style="font-size: 18px;">□□□□□</div>
</div>
<div style="background: #f8fafc; padding: 12px; border-radius: 8px; text-align: center;">
<div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">性价比</div>
<div style="font-size: 18px;">□□□□□</div>
</div>
<div style="background: #f8fafc; padding: 12px; border-radius: 8px; text-align: center;">
<div style="font-size: 12px; color: #64748b; margin-bottom: 5px;">总体满意度</div>
<div style="font-size: 18px;">□□□□□</div>
</div>
</div>
<div style="font-size: 11px; color: #94a3b8; margin-top: 8px; text-align: right;">评分说明：1星=非常不满意，5星=非常满意</div>
</div>

<div style="background: #f8fafc; border-radius: 10px; padding: 18px; margin-bottom: 15px;">
<div style="font-size: 14px; font-weight: 600; color: #334155; margin-bottom: 10px;">💬 反馈内容</div>
<div style="color: #475569; line-height: 1.8; min-height: 80px;"><span class="template-field field-block" data-fieldname="反馈内容">{$反馈内容}</span></div>
</div>

<div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-bottom: 15px;">
<div style="background: #ecfdf5; border-radius: 8px; padding: 15px;">
<div style="font-size: 13px; color: #059669; font-weight: 500; margin-bottom: 8px;">👍 满意之处</div>
<div style="font-size: 13px; color: #166534; line-height: 1.6;"><span class="template-field field-block" data-fieldname="满意之处">{$满意之处}</span></div>
</div>
<div style="background: #fef2f2; border-radius: 8px; padding: 15px;">
<div style="font-size: 13px; color: #dc2626; font-weight: 500; margin-bottom: 8px;">👎 改进建议</div>
<div style="font-size: 13px; color: #991b1b; line-height: 1.6;"><span class="template-field field-block" data-fieldname="改进建议">{$改进建议}</span></div>
</div>
</div>

<div style="background: #fffbeb; border-radius: 8px; padding: 15px; margin-bottom: 15px;">
<div style="font-size: 13px; color: #92400e; font-weight: 500; margin-bottom: 8px;">📝 处理记录（内部填写）</div>
<div style="font-size: 13px; color: #78350f; line-height: 1.6;"><span class="template-field field-block" data-fieldname="处理记录">{$处理记录}</span></div>
</div>

<div style="display: flex; justify-content: space-between; margin-top: 20px; padding-top: 15px; border-top: 1px dashed #e2e8f0;">
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 15px;">客户签名</div>
<div style="width: 100px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 15px;">客服人员</div>
<div style="width: 100px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
<div style="text-align: center;">
<div style="font-size: 11px; color: #94a3b8; margin-bottom: 15px;">处理日期</div>
<div style="width: 100px; border-bottom: 1px solid #cbd5e1;"></div>
</div>
</div>
</div>"""
    }


# ============================================================
# 获取所有模板
# ============================================================

def get_all_templates() -> list[dict]:
    """获取所有20个系统模板"""
    templates = [
        # 传统样式模板（10个）
        template_leave_application(),
        template_expense_claim(),
        template_business_trip(),
        template_work_handover(),
        template_meeting_minutes(),
        template_purchase_request(),
        template_contract_approval(),
        template_employee_info(),
        template_overtime_application(),
        template_visitor_registration(),
        template_asset_requisition(),
        # 现代设计模板（10个）
        template_modern_project_report(),
        template_modern_quotation(),
        template_modern_invoice(),
        template_modern_work_order(),

        template_modern_delivery_note(),
        template_modern_interview_evaluation(),
        template_modern_training_record(),
        template_modern_task_assignment(),
        template_modern_customer_feedback(),
    ]
    return templates


def main() -> int:
    parser = argparse.ArgumentParser(description="导入20个系统模板（10传统+10现代设计）")
    parser.add_argument(
        "--base-url",
        default="http://localhost:8000",
        help="后端地址，例如 http://localhost:8000",
    )
    parser.add_argument(
        "--endpoint",
        default="/api/templates/",
        help="模板接口路径",
    )
    parser.add_argument("--timeout", type=int, default=15, help="请求超时秒数")
    parser.add_argument(
        "--skip-exists",
        action="store_true",
        default=True,
        help="跳过已存在的模板（默认开启）",
    )
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    endpoint = base_url + args.endpoint

    if not endpoint.endswith("/"):
        endpoint = endpoint + "/"

    print(f"=" * 60)
    print(f"飞书打印模板系统 - 系统模板导入工具")
    print(f"=" * 60)
    print(f"目标接口: {endpoint}")
    print()

    templates = get_all_templates()
    print(f"准备导入 {len(templates)} 个模板...")
    print()

    created = 0
    skipped = 0
    failed = 0

    for idx, t in enumerate(templates, start=1):
        status, body = _post_json(endpoint, t, timeout=args.timeout)

        if status in (200, 201):
            created += 1
            print(f"[{idx:2d}/{len(templates)}] ✅ 创建成功: {t['name']}")
            continue

        if status == 400:
            skipped += 1
            print(f"[{idx:2d}/{len(templates)}] ⏭️  已存在，跳过: {t['name']}")
            continue

        failed += 1
        print(f"[{idx:2d}/{len(templates)}] ❌ 创建失败({status}): {t['name']}")
        print(f"    响应: {body[:200]}...")

    print()
    print(f"=" * 60)
    print(f"导入完成！")
    print(f"  ✅ 成功创建: {created} 个")
    print(f"  ⏭️  跳过已存在: {skipped} 个")
    print(f"  ❌ 失败: {failed} 个")
    print(f"=" * 60)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    exit(main())
