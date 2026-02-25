from pydantic_settings import BaseSettings
from pydantic import AliasChoices, ConfigDict, Field
import os
import warnings

class Settings(BaseSettings):
    database_url: str
    cors_origins: str = "http://localhost:5173,http://localhost:5155,http://localhost:5156,http://localhost:3000"
    dashscope_api_key: str
    jwt_secret_key: str = "your-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_expire_hours: int = 24
    environment: str = "development"  # development, production
    ai_model: str = "qwen-plus"  # AI模型：qwen-turbo(最快), qwen-plus(平衡), qwen-max(最慢但质量最高)
    ai_timeout: int = 300  # AI API超时时间（秒），流式生成需要更长时间，考虑重试机制
    
    # YunGouOs支付配置
    # 兼容两种环境变量命名：
    # - YUNGOOS_*（按字段名 yungouos_* 自动推导，历史/默认）
    # - YUN_GOUOS_*（更直观的命名，你的 .env 当前使用的这一套）
    yungouos_merchant_id: str = Field(
        default="",
        validation_alias=AliasChoices("YUN_GOUOS_MERCHANT_ID", "YUNGOOS_MERCHANT_ID"),
    )  # 商户号
    yungouos_secret_key: str = Field(
        default="",
        validation_alias=AliasChoices("YUN_GOUOS_SECRET_KEY", "YUNGOOS_SECRET_KEY"),
    )  # 密钥
    yungouos_api_base: str = Field(
        # 注意：open.pay.yungouos.com 是文档站点（见 https://open.pay.yungouos.com/#/api/index ）
        # 实际接口网关应使用 api.pay.yungouos.com
        default="https://api.pay.yungouos.com",
        validation_alias=AliasChoices("YUN_GOUOS_API_BASE", "YUNGOOS_API_BASE"),
    )  # API基础URL
    yungouos_native_pay_url: str = Field(
        default="",
        validation_alias=AliasChoices("YUN_GOUOS_NATIVE_PAY_URL", "YUNGOOS_NATIVE_PAY_URL"),
    )  # 扫码支付完整URL（可选，如果设置则直接使用，否则尝试多个路径）
    yungouos_notify_url: str = Field(
        default="",
        validation_alias=AliasChoices("YUN_GOUOS_NOTIFY_URL", "YUNGOOS_NOTIFY_URL"),
    )  # 支付回调地址
    
    model_config = ConfigDict(
        env_file=".env",
        extra="ignore"  # 忽略 .env 文件中未定义的额外字段
    )

settings = Settings()

# 安全性检查：在生产环境中警告使用默认 JWT 密钥
if settings.environment == "production":
    default_key = "your-super-secret-key-change-in-production"
    if settings.jwt_secret_key == default_key:
        raise ValueError(
            "安全错误：生产环境不能使用默认 JWT 密钥！"
            "请在 .env 文件中设置 JWT_SECRET_KEY 为强随机字符串。"
        )
elif settings.jwt_secret_key == "your-super-secret-key-change-in-production":
    warnings.warn(
        "警告：正在使用默认 JWT 密钥。在生产环境中请设置强随机密钥！",
        UserWarning
    )
