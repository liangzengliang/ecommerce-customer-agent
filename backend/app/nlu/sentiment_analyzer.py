"""
情感分析模块
每次请求从数据库获取默认 LLM
"""

from langchain_core.prompts import ChatPromptTemplate
from app.services.llm_service import get_llm_async, is_llm_available
import logging

logger = logging.getLogger(__name__)


class SentimentAnalyzer:
    """情感分析器"""

    def __init__(self):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system",
             "你是情感分析专家。分析用户消息的情感倾向。\n"
             "只输出一个词：positive / neutral / negative\n\n"
             "示例：\n"
             "用户：太好了，谢谢！ → positive\n"
             "用户：你好 → neutral\n"
             "用户：太差了，我要投诉！ → negative"),
            ("human", "{text}\n\n只输出情感标签："),
        ])

    async def analyze(self, text: str) -> dict:
        """分析情感"""
        # 演示模式/LLM 不可用时用规则判断
        if not is_llm_available():
            return self._rule_analyze(text)

        try:
            llm = await get_llm_async(temperature=0)
            chain = self.prompt | llm
            resp = await chain.ainvoke({"text": text})
            result = (resp.content or "").strip().lower()

            # 解析
            if "positive" in result:
                return {"sentiment": "positive", "score": 0.9}
            elif "negative" in result:
                return {"sentiment": "negative", "score": 0.9}
            else:
                return {"sentiment": "neutral", "score": 0.5}

        except Exception as e:
            logger.error(f"情感分析失败: {e}")
            return self._rule_analyze(text)

    def _rule_analyze(self, text: str) -> dict:
        """基于关键词的情感分析降级方案"""
        positive_words = ["谢谢", "感谢", "太好", "满意", "赞", "喜欢", "不错", "棒", "好评", "nice", "great"]
        negative_words = ["差", "垃圾", "投诉", "生气", "愤怒", "失望", "太差", "退货", "退款", "骗子", "可恶", "糟糕", "差评", "bad"]
        t = text.lower()
        pos_hit = any(w in text for w in positive_words)
        neg_hit = any(w in t for w in negative_words)
        if neg_hit and not pos_hit:
            return {"sentiment": "negative", "score": 0.9}
        if pos_hit and not neg_hit:
            return {"sentiment": "positive", "score": 0.8}
        return {"sentiment": "neutral", "score": 0.5}