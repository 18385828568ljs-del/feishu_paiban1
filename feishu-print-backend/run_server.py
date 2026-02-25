"""
Uvicorn 启动脚本 - Windows 优化版本
抑制 reload 模式下的预期异常，提供更清洁的输出
"""
import sys
import os
import logging
import uvicorn
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)],
    force=True
)

class FilteredStderr:
    """过滤 Windows 上 uvicorn reload 的预期错误"""
    def __init__(self, original_stderr):
        self.original_stderr = original_stderr
        self.buffer = []
        self.buffer_size = 50  # 缓存最近 50 行
        
    def write(self, text):
        """写入时过滤预期的错误"""
        if text:
            self.buffer.append(text)
            if len(self.buffer) > self.buffer_size:
                self.buffer.pop(0)
            
            # 检查是否是预期的错误（Windows reload 时的 CancelledError）
            if any(keyword in text for keyword in [
                'CancelledError',
                'Process SpawnProcess',
                'asyncio.exceptions.CancelledError',
                'KeyboardInterrupt',
            ]):
                # 检查上下文，如果是 reload 相关的错误，则抑制
                recent = ''.join(self.buffer[-10:])
                if 'reload' in recent.lower() or 'SpawnProcess' in recent:
                    return  # 抑制输出
            
            # 正常输出
            self.original_stderr.write(text)
    
    def flush(self):
        self.original_stderr.flush()
    
    def __getattr__(self, name):
        return getattr(self.original_stderr, name)

if __name__ == "__main__":
    # 确保在正确的目录下运行
    script_dir = Path(__file__).parent
    os.chdir(script_dir)
    
    print("=" * 60)
    print("Feishu Print Backend - 开发服务器")
    print("=" * 60)
    print(f"工作目录: {script_dir}")
    print("使用 watchfiles 文件监控（Windows 优化）")
    print("访问: http://localhost:8000/docs")
    print("=" * 60)
    print()
    
    # 在 Windows 上过滤 stderr 中的预期错误
    # 可以通过环境变量 SUPPRESS_RELOAD_ERRORS=0 来禁用过滤
    suppress_errors = os.getenv('SUPPRESS_RELOAD_ERRORS', '1') == '1'
    if sys.platform == 'win32' and suppress_errors:
        sys.stderr = FilteredStderr(sys.stderr)
        print("已启用错误过滤（Windows reload 优化）")
        print("设置环境变量 SUPPRESS_RELOAD_ERRORS=0 可禁用过滤")
        print()
    
    try:
        # 使用 watchfiles 引擎，在 Windows 上更稳定
        uvicorn.run(
            "app.main:app",
            host="0.0.0.0",
            port=8000,
            reload=True,
            log_level="info",
            access_log=True,
        )
    except KeyboardInterrupt:
        print("\n服务器已停止")
        sys.exit(0)

