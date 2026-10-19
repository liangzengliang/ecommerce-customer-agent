"""
日志工具
提供统一的 logger 获取函数。
"""

import logging

def get_logger(name: str) -> logging.Logger:
    """
    获取指定名称的 logger
    参数：name - logger 名称，通常传 __name__
    返回：Logger 实例
    """
    return logging.getLogger(name)