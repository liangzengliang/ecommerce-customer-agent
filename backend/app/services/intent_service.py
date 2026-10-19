"""
意图识别服务
对外暴露意图识别能力。
"""

from app.nlu.intent_classifier import IntentClassifier

class IntentService:
    """意图识别服务类"""

    def __init__(self):
        """初始化意图分类器"""
        self.classifier = IntentClassifier()

    async def classify(self, text: str) -> dict:
        """
        识别用户意图
        参数：text - 用户消息
        返回：dict，含 intent_code / intent_name / confidence
        """
        return await self.classifier.classify(text)

intent_service = IntentService()