"""
应用配置模块
支持两种配置来源：
1. .env 文件或环境变量 → 通过 pydantic-settings 加载，用于密钥、连接串等敏感配置
2. config/*.yaml 文件   → 通过 PyYAML 加载，用于业务参数（意图、RAG、Agent 等）

其他模块统一通过以下方式使用：
    from app.core.config import settings          # .env 配置
    from app.core.config import llm_config        # YAML 配置
"""

from pathlib import Path
from functools import lru_cache
from typing import Any, Dict
import yaml

from pydantic_settings import BaseSettings


# ============================================================
# 路径常量
# ============================================================

# 当前文件路径：backend/app/core/config.py
# .parent        → backend/app/core
# .parent.parent → backend/app
# .parent x3     → backend/
# .parent x4     → 项目根目录（ecommerce-customer-service/）
PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent

# config/ 目录（存放 4 个 YAML 文件）
CONFIG_DIR = PROJECT_ROOT / "config"

# knowledge_base/ 目录（存放原始知识文件）
KNOWLEDGE_BASE_DIR = PROJECT_ROOT / "knowledge_base"

# logs/ 目录（存放日志文件）
LOGS_DIR = PROJECT_ROOT / "logs"

# ============================================================
# .env 配置（pydantic-settings）
# ============================================================

class Settings(BaseSettings):
    """
    全局配置类
    所有字段优先从环境变量读取，其次从 .env 文件读取，最后使用默认值。
    适合存放敏感信息（密钥、密码）和环境相关的连接串。
    """

    # ----- 应用基础信息 -----
    APP_NAME: str = "电商智能客服"                      # 应用名称
    APP_VERSION: str = "1.0.0"                        # 版本号
    DEBUG: bool = True                                # 调试模式（生产环境设为 False）

    # ----- 数据库配置 -----
    # 默认 SQLite 演示模式（无需安装 MySQL）；真实环境通过 .env 设置 DATABASE_URL 为 MySQL
    DEMO_MODE: bool = True                          # 演示模式：每表上限 10 条 + 每日零点重置
    DATABASE_URL: str = "sqlite+aiosqlite:///./demo.db"

    # ----- Redis 配置（会话记忆、缓存、限流、Celery broker）-----
    REDIS_URL: str = "redis://localhost:6379/0"

    # ----- Milvus 向量数据库配置 -----
    MILVUS_HOST: str = "localhost"                    # Milvus 主机
    MILVUS_PORT: int = 19530                          # Milvus 端口
    MILVUS_COLLECTION: str = "ecommerce_knowledge"    # 集合名称

    # ===== LLM 配置（OpenAI 兼容协议，可用硅基流动/DeepSeek等）=====
    OPENAI_API_KEY: str = ""                          # API Key  ← 这是默认值，只是兜底
    OPENAI_BASE_URL: str = "https://api.siliconflow.cn/v1"  # 接口地址
    LLM_MODEL: str = "Qwen/Qwen2.5-7B-Instruct"       # 默认模型

    # ----- 嵌入模型配置 -----
    EMBEDDING_MODEL: str = "BAAI/bge-m3"              # 嵌入模型名称
    EMBEDDING_DIM: int = 1024                         # 向量维度
    EMBEDDING_API_KEY: str = ""                       # 嵌入 API Key  ← 这是默认值，只是兜底 后面会覆盖
    EMBEDDING_BASE_URL: str = "https://api.siliconflow.cn/v1"                         # 嵌入 API 地址

    # ----- JWT 认证配置 -----
    SECRET_KEY: str = "demo-only-change-me-to-a-random-secret-key"  # 密钥（生产必须更换）
    ALGORITHM: str = "HS256"                          # 签名算法
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440           # Token 有效期（分钟），默认 24 小时

    # ----- CORS 配置 -----
    CORS_ORIGINS: list[str] = ["*"]                   # 允许的来源，生产环境应指定具体域名

    # ----- 限流配置 -----
    RATE_LIMIT_ENABLED: bool = True                   # 是否启用限流
    RATE_LIMIT_MAX_REQUESTS: int = 60                 # 窗口内最大请求数
    RATE_LIMIT_WINDOW_SECONDS: int = 60               # 窗口大小（秒）

    # ----- Celery 配置 -----
    CELERY_TASK_TIME_LIMIT: int = 600                 # 单任务硬超时（秒）
    CELERY_TASK_SOFT_TIME_LIMIT: int = 540            # 软超时（秒）

    class Config:
        """pydantic-settings 配置"""
        env_file = ".env"                             # 从 .env 文件读取
        env_file_encoding = "utf-8"
        case_sensitive = True                         # 环境变量名区分大小写
        extra = "ignore"                              # 忽略 .env 中未定义的变量

@lru_cache
def get_settings() -> Settings:
    """
    获取全局配置单例
    使用 lru_cache 避免重复读取 .env 文件，提升性能。
    返回：Settings 实例
    """
    return Settings()

# 全局配置实例，其他模块直接 from app.core.config import settings 使用
settings = get_settings()

# ============================================================
# YAML 配置加载
# ============================================================

@lru_cache
def load_yaml_config(name: str) -> Dict[str, Any]:
    """
    加载 config/ 目录下的 YAML 配置文件
    参数：name - 文件名（不含 .yaml 后缀），如 'llm_config'、'rag_config'
    返回：解析后的字典，文件不存在或解析失败时返回空字典
    """
    path = CONFIG_DIR / f"{name}.yaml"

    # 文件不存在，返回空字典，避免调用方崩溃
    if not path.exists():
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
            return data if isinstance(data, dict) else {}
    except yaml.YAMLError as e:
        # YAML 语法错误时打印警告，返回空字典
        print(f"[WARN] 解析 {path} 失败: {e}")
        return {}
    except Exception as e:
        # 其他读取错误（权限等）
        print(f"[WARN] 读取 {path} 失败: {e}")
        return {}


# 四个业务 YAML 配置的全局实例
llm_config: Dict[str, Any] = load_yaml_config("llm_config")       # LLM 配置
intent_config: Dict[str, Any] = load_yaml_config("intent_config") # 意图识别配置
rag_config: Dict[str, Any] = load_yaml_config("rag_config")       # RAG 配置
agent_config: Dict[str, Any] = load_yaml_config("agent_config")   # Agent 配置


# ============================================================
# 便捷工具函数
# ============================================================

def get_yaml_value(config: Dict[str, Any], keys: str, default: Any = None) -> Any:
    """
    安全地从嵌套字典中取值
    参数：config - 配置字典
          keys - 点分隔的键路径，如 'default.model'
          default - 取值失败时的默认值
    返回：取到的值，或默认值

    示例：
        get_yaml_value(llm_config, "default.model", "gpt-3.5-turbo")
    """
    current = config
    for key in keys.split("."):
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current


def reload_configs() -> None:
    """
    重新加载所有 YAML 配置
    用于开发环境中配置改动后热更新（清除 lru_cache 后重新读取）。
    """
    load_yaml_config.cache_clear()
    global llm_config, intent_config, rag_config, agent_config
    llm_config = load_yaml_config("llm_config")
    intent_config = load_yaml_config("intent_config")
    rag_config = load_yaml_config("rag_config")
    agent_config = load_yaml_config("agent_config")