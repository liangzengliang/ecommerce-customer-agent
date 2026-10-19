"""
日志配置模块
统一项目日志格式，输出到控制台。
"""
import sys
import logging

def setup_logging():
    """初始化日志配置，在 main.py 启动时调用一次即可"""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

# 全局 logger，其他模块可直接 import 使用
logger = logging.getLogger("customer_service")