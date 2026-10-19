"""
情感分析服务
对外暴露情感分析能力。
"""

from app.nlu.sentiment_analyzer import SentimentAnalyzer

class SentimentService:
    """情感分析服务类"""

    def __init__(self):
        """初始化情感分析器"""
        self.analyzer = SentimentAnalyzer()

    async def analyze(self, text: str) -> dict:
        """
        分析文本情感
        参数：text - 用户消息
        返回：dict，含 sentiment / score
        """
        return await self.analyzer.analyze(text)

sentiment_service = SentimentService()