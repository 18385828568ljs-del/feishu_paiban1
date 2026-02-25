"""
YunGouOs 支付服务模块
"""
import hashlib
import urllib.parse
from typing import Any, Dict, Iterable, List, Tuple
import httpx
import logging
from app.config import settings

logger = logging.getLogger(__name__)


class YunGouOsService:
    """YunGouOs支付服务"""
    
    def __init__(self):
        self.merchant_id = settings.yungouos_merchant_id
        self.secret_key = settings.yungouos_secret_key
        self.api_base = settings.yungouos_api_base
        self.native_pay_url = settings.yungouos_native_pay_url  # 完整的扫码支付URL（可选）
        self.notify_url = settings.yungouos_notify_url

        # 基础配置校验：避免带着空 mch_id/notify_url 去请求第三方，导致排查困难
        missing = []
        if not self.merchant_id:
            missing.append("YUN_GOUOS_MERCHANT_ID")
        if not self.secret_key:
            missing.append("YUN_GOUOS_SECRET_KEY")
        if not self.notify_url:
            missing.append("YUN_GOUOS_NOTIFY_URL")
        if missing:
            raise ValueError(
                "YunGouOS 支付配置缺失："
                + ", ".join(missing)
                + "。请检查 `.env` 是否在后端工作目录（`feishu-print-backend/`）下，且变量名正确。"
            )

        # 归一化：避免出现 /api/api 这类重复前缀（常见于把文档URL当成接口URL）
        self.api_base = (self.api_base or "").strip().rstrip("/")
        # 把文档站域名纠正为接口网关域名（open 是文档站；api 才是接口）
        if "open.pay.yungouos.com" in self.api_base:
            corrected = self.api_base.replace("open.pay.yungouos.com", "api.pay.yungouos.com")
            logger.warning("检测到 YUN_GOUOS_API_BASE 指向文档站域名，已自动纠正: %s -> %s", self.api_base, corrected)
            self.api_base = corrected
        if self.native_pay_url:
            sanitized = self._sanitize_yungouos_url(self.native_pay_url)
            if sanitized != self.native_pay_url:
                logger.warning(
                    "检测到 YUN_GOUOS_NATIVE_PAY_URL 可能包含重复 '/api/api'，已自动归一化: %s -> %s",
                    self.native_pay_url,
                    sanitized,
                )
            self.native_pay_url = sanitized

    @staticmethod
    def _sanitize_yungouos_url(url: str) -> str:
        """修正常见的 URL 拼接/配置错误（例如 /api/api 重复）。"""
        u = (url or "").strip()
        # 文档站域名 -> 接口网关域名
        if "open.pay.yungouos.com" in u:
            u2 = u.replace("open.pay.yungouos.com", "api.pay.yungouos.com")
            if u2 != u:
                logger.warning("检测到 YunGouOS URL 指向文档站域名，已自动纠正: %s -> %s", u, u2)
            u = u2
        # 把连续的 /api/api/... 归一化为 /api/...
        u = u.replace("/api/api/", "/api/")
        # 合并多余的斜杠（保留协议里的 '://')
        if "://" in u:
            scheme, rest = u.split("://", 1)
            while "//" in rest:
                rest = rest.replace("//", "/")
            u = f"{scheme}://{rest}"
        return u.rstrip("/")

    @staticmethod
    def _join_url(base: str, path: str) -> str:
        """安全拼接 base + path，避免出现 // 或 /api/api 重复。"""
        b = (base or "").rstrip("/")
        p = (path or "").lstrip("/")
        url = f"{b}/{p}"
        return YunGouOsService._sanitize_yungouos_url(url)
    
    def _generate_sign(self, params: Dict[str, Any], mandatory_keys: List[str] = None) -> str:
        """
        生成签名
        签名规则：
        1. 如果指定了 mandatory_keys，则只使用这些 key 对应的参数参与签名
        2. 否则使用所有非空参数参与签名
        3. 按key排序，拼接成key=value&key=value格式，最后加上&key=密钥，然后MD5加密
        """
        # 筛选参与签名的参数
        if mandatory_keys:
            # 官方规则：只有文档中的必填参数才参与签名（且值不为空）
            filtered_params = {k: str(v) for k, v in params.items() if k in mandatory_keys and v is not None}
        else:
            # 兼容模式/默认模式：过滤空值和sign参数
            filtered_params = {k: str(v) for k, v in params.items() if v is not None and v != "" and k != 'sign'}
        
        # 按键名排序
        sorted_params = sorted(filtered_params.items())
        
        # 拼接字符串
        sign_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
        sign_str += f"&key={self.secret_key}"
        
        # MD5加密并转大写
        sign = hashlib.md5(sign_str.encode('utf-8')).hexdigest().upper()
        
        logger.debug(f"签名原始字符串: {sign_str}")
        logger.debug(f"签名结果: {sign}")
        
        return sign

    async def create_native_pay(self, order_no: str, amount: int, subject: str) -> Dict:
        """
        创建支付宝扫码支付订单
        """
        # 构造请求参数
        # 注意：amount 是分，但有些接口可能需要元，这里保持原逻辑传分，
        # 如果 feishu1 用的是 total_fee 且单位不明，我们先假设云沟默认是元或分
        # 查看 feishu1: formatted_fee = "{:.2f}".format(total_fee) 说明 feishu1 传的是元字符串
        # 但这里 amount 参数是 int(分)。我们需要确认 YunGouOS `total_fee` 的单位。
        # 通常 total_fee 在支付宝/微信原生是分，但在聚合支付平台有时是元。
        # 让我们再看一眼 feishu1:
        #   native_pay(..., total_fee: float, ...)
        #   formatted_fee = "{:.2f}".format(total_fee)
        # 这说明 feishu1 确实传的是“元”（例如 1.00）。
        # 而我们的 amount 是 int（分）。我们需要转换一下，或者确认接口文档。
        # 常见 YunGouOS 文档：total_fee 字符串类型，单位：元，保留两位小数。
        
        # 将分转为元字符串
        total_fee_str = "{:.2f}".format(amount / 100.0)

        params = {
            'out_trade_no': order_no,
            'total_fee': total_fee_str, 
            'mch_id': self.merchant_id,
            'body': subject,
            # 可选参数
            'type': '2', # 返回二维码链接
            'notify_url': self.notify_url,
        }

        # 核心修正：只对必填参数签名
        # 必填项: out_trade_no, total_fee, mch_id, body
        mandatory_keys = ["out_trade_no", "total_fee", "mch_id", "body"]
        params['sign'] = self._generate_sign(params, mandatory_keys)
        
        logger.info(f"YunGouOS支付请求参数: {params}")
        
        # API地址
        api_url = self._join_url(self.api_base, "/api/pay/alipay/nativePay")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    api_url,
                    data=params,
                    headers={'Content-Type': 'application/x-www-form-urlencoded'}
                )
                
                logger.info(f"YunGouOS 响应状态: {response.status_code}")
                logger.info(f"YunGouOS 响应内容: {response.text}")
                
                result = response.json()
                
                if str(result.get("code")) in ["0", "200"]:
                    # 成功，获取二维码 URL
                    qr_url = result.get("data")
                    
                    # 核心修复：后端代理下载图片并转为 Base64
                    # 这样可以解决飞书安全域名限制和 HTTP/HTTPS 协议冲突问题
                    qr_code_base64 = None
                    try:
                        # 使用独立的 Client 用于下载图片，避免复用连接可能的问题
                        # 设置极短的超时时间，防止卡死
                        async with httpx.AsyncClient(timeout=5.0) as img_client:
                            logger.info(f"开始下载二维码图片: {qr_url}")
                            img_resp = await img_client.get(qr_url)
                            if img_resp.status_code == 200:
                                import base64
                                base64_data = base64.b64encode(img_resp.content).decode('utf-8')
                                qr_code_base64 = f"data:image/png;base64,{base64_data}"
                                logger.info("二维码图片下载并转换成功")
                            else:
                                logger.warning(f"下载二维码图片失败: {img_resp.status_code}")
                    except Exception as img_err:
                        # 捕获所有异常，确保不影响主流程
                        logger.warning(f"转换二维码为 Base64 异常: {str(img_err)}，将退回使用原始 URL")
                    
                    return {
                        "order_no": order_no,
                        "qr_code": qr_code_base64 if qr_code_base64 else qr_url,
                    }
                else:
                    raise Exception(result.get("msg", "创建支付订单失败"))
                    
        except Exception as e:
            logger.error(f"创建支付订单失败: {str(e)}", exc_info=True)
            raise
    
    async def query_order(self, order_no: str) -> Dict:
        """
        查询订单状态
        
        Args:
            order_no: 商户订单号
            
        Returns:
            订单信息字典
        """
        params = {
            'out_trade_no': order_no,
            'mch_id': self.merchant_id,
        }
        
        # 官方规则：只有文或者必填项参与签名
        # 查询订单接口：out_trade_no, mch_id
        mandatory_keys = ["out_trade_no", "mch_id"]
        params['sign'] = self._generate_sign(params, mandatory_keys)
        
        # 注意：feishu1 使用的是 /api/system/order/getPayOrderInfo
        api_url = self._join_url(self.api_base, "/api/system/order/getPayOrderInfo")
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get( # 注意：这个接口通常支持 GET
                    api_url,
                    params=params,
                )
                
                result_text = response.text
                
                # 预解析以决定日志级别
                log_level = logging.INFO
                try:
                    import json
                    pre_res = json.loads(result_text)
                    if str(pre_res.get("code")) == "777":
                        log_level = logging.DEBUG
                except:
                    pass
                
                logger.log(log_level, f"YunGouOs查询订单响应: {result_text}")
                
                if result_text.startswith('{'):
                    import json
                    res = json.loads(result_text)
                    if str(res.get("code")) in ["0", "200"]:
                        data = res.get("data", {})
                        # 这里为了兼容 router 里的检查逻辑
                        # router 检查: status, trade_status, pay_status
                        # YunGouOS 返回 data.payStatus (0=未支付, 1=已支付)
                        pay_status_raw = str(data.get("payStatus", "0"))
                        
                        return {
                            "code": "0",
                            "msg": "suc",
                            "pay_status": "SUCCESS" if pay_status_raw == "1" else "PENDING",
                            "trade_no": data.get("payNo"),
                            # 保留原始数据以便调试
                            "raw_data": data
                        }
                    return res
                else:
                    parsed = urllib.parse.parse_qs(result_text)
                    return {k: v[0] if len(v) == 1 else v for k, v in parsed.items()}
                    
        except Exception as e:
            logger.error(f"查询订单异常: {str(e)}", exc_info=True)
            raise
    
    def verify_notify(self, params: Dict[str, str]) -> bool:
        """
        验证回调通知签名
        
        Args:
            params: 回调参数
            
        Returns:
            签名是否有效
        """
        return self._verify_sign(params.copy())


# 创建全局实例
yungouos_service = YunGouOsService()

