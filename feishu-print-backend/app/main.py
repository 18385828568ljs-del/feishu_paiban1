from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
import sys
from .database import engine, Base
from .routers import templates, ai, signature, user, team, admin, feedback, payment, promo
from .config import settings

# 配置日志（Windows 兼容性优化）
# 避免 uvicorn reload 模式下的日志配置冲突
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True  # 强制重新配置，避免重载时的冲突
)
logger = logging.getLogger(__name__)

# 创建数据库表
Base.metadata.create_all(bind=engine)

# 启动时记录配置信息
logger.info(f"应用启动 - 环境: {settings.environment}")

app = FastAPI(
    title="智能排版 API",
    description="智能排版模板管理系统 API",
    version="1.0.0"
)

# CORS 配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(templates.router)
app.include_router(ai.router)
app.include_router(signature.router)
app.include_router(user.router)
app.include_router(team.router)
app.include_router(admin.router)
app.include_router(feedback.router)
app.include_router(payment.router)
app.include_router(promo.router)

@app.get("/")
def root():
    return {"message": "Feishu Print API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
