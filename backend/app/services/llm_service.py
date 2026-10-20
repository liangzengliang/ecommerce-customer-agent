"""
LLM 服务
优先从数据库读取默认模型配置，否则用 .env 配置。
演示模式下若未配置 API Key 或调用失败，自动降级为规则回复。
"""

from langchain_openai import ChatOpenAI
from app.core.config import settings
from app.services.model_config_service import model_config_service
import logging

logger = logging.getLogger(__name__)


async def is_llm_available() -> bool:
    """
    判断 LLM 是否可用：
    1. 数据库存在启用的默认对话模型配置（网友在模型配置页面配置的）→ 可用
    2. 否则 .env 配置了 OPENAI_API_KEY → 可用
    3. 否则不可用（走离线规则回复）
    """
    # 1. 数据库有带 API Key 的默认模型配置（网友配置的）→ 可用
    try:
        db_config = await model_config_service.get_default_chat_model()
        if db_config:
            logger.info("LLM 可用：数据库默认模型配置 %s (%s)", db_config['name'], db_config['model'])
            return True
    except Exception as e:
        logger.error("检查数据库模型配置失败: %s", e)

    # 2. .env 有 API Key → 可用
    return bool(settings.OPENAI_API_KEY)


async def get_llm_async(
    streaming: bool = False,
    temperature: float | None = None,
) -> ChatOpenAI:
    """
    异步获取 LLM：优先数据库默认模型，回退到 .env
    参数：streaming - 是否流式
          temperature - 覆盖温度（None 时用配置里的）
    """
    # 1. 尝试从数据库读默认模型
    db_config = await model_config_service.get_default_chat_model()

    if db_config:
        logger.info(f"使用数据库默认模型: {db_config['name']} ({db_config['model']})")
        return ChatOpenAI(
            model=db_config["model"],
            api_key=db_config["api_key"],
            base_url=db_config["base_url"],
            temperature=temperature if temperature is not None else db_config["temperature"],
            max_tokens=db_config["max_tokens"],
            streaming=streaming,
        )

    # 2. 回退到 .env
    logger.info(f"使用 .env 默认模型: {settings.LLM_MODEL}")
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        temperature=temperature if temperature is not None else 0.3,
        streaming=streaming,
    )


def get_llm(streaming: bool = False) -> ChatOpenAI:
    """
    同步版本（向后兼容），不查数据库，直接用 .env
    建议改用 get_llm_async
    """
    return ChatOpenAI(
        model=settings.LLM_MODEL,
        api_key=settings.OPENAI_API_KEY,
        base_url=settings.OPENAI_BASE_URL,
        temperature=0.3,
        streaming=streaming,
    )
