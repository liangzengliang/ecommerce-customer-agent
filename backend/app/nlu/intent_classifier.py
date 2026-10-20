"""
意图识别模块
"""

from langchain_core.prompts import ChatPromptTemplate
from app.services.llm_service import get_llm_async, is_llm_available
import logging

logger = logging.getLogger(__name__)

INTENT_CODE_MAP = {
    "商品详情": "PRD_001", "促销活动": "PRD_002", "商品推荐": "PRD_003",
    "会员权益": "PRD_004", "配送时效": "PRD_005", "库存查询": "PRD_006",
    "订单查询": "ORD_001", "订单修改": "ORD_002", "取消订单": "ORD_003",
    "物流追踪": "ORD_004", "催促发货": "ORD_005", "修改地址": "ORD_006",
    "支付问题": "PAY_001", "申请退款": "PAY_002", "优惠券使用": "PAY_003",
    "售后政策": "PAY_004", "发票问题": "PAY_005",
    "投诉建议": "CMP_001", "退款退货": "CMP_002", "人工客服": "CMP_003",
    "建议反馈": "CMP_004", "闲聊/未知": "FALLBACK",
}

INTENT_NAMES = list(INTENT_CODE_MAP.keys())
INTENT_LIST_STR = "、".join(INTENT_NAMES)


class IntentClassifier:
    """意图分类器"""

    def __init__(self):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system",
             "你是电商客服意图识别助手。从下面的意图列表中，选出最匹配用户问题的那一个，"
             "只输出意图名称本身，不要标点、不要解释。\n\n"
             f"可选意图（必须严格从这里选）：\n{INTENT_LIST_STR}\n\n"
             "【重要】区分'咨询'和'操作'：\n"
             "- 用户问'**怎么做**'、'**多久**'、'**流程**'、'**政策**'、'**是什么**' → 归到对应知识类意图\n"
             "- 用户说'**我要做**'、'**帮我做**'、'**申请**'、'**取消**' → 归到操作类意图\n\n"
             "示例：\n"
             "用户：退款多久到账 → 支付问题\n"
             "用户：我要退款 → 申请退款\n"
             "用户：电脑保修多久 → 售后政策\n"
             "用户：怎么查订单 → 订单查询\n"
             "用户：帮我查订单 ORDER123 → 订单查询\n"
             "用户：订单 ORDER123 到哪了 → 物流追踪\n"
             "用户：我的快递到哪了 → 物流追踪\n"
             "用户：怎么申请退款 → 售后政策\n"
             "用户：我要投诉 → 投诉建议\n"
             "用户：转人工 → 人工客服\n"
             "用户：你好 → 闲聊/未知"),
            ("human", "{text}\n\n只输出意图名称："),
        ])

    async def classify(self, text: str) -> dict:
        # 演示模式/LLM 不可用时直接走关键词兜底，避免超时
        if not await is_llm_available():
            code, name = self._keyword_fallback(text, "闲聊/未知")
            return {"intent_code": code, "intent_name": name, "confidence": 0.6}

        try:
            llm = await get_llm_async(temperature=0)
            chain = self.prompt | llm
            resp = await chain.ainvoke({"text": text})
            name = (resp.content or "").strip()

            name = name.split("\n")[0].strip()
            name = name.strip("。，、,. \"'：:；;")

            code = INTENT_CODE_MAP.get(name)

            if not code:
                for k, v in INTENT_CODE_MAP.items():
                    if k in name or name in k:
                        code = v
                        name = k
                        break

            if not code:
                code, name = self._keyword_fallback(text, name)

            logger.info(f"意图识别: '{text[:30]}' → name='{name}', code={code}")
            return {
                "intent_code": code,
                "intent_name": name,
                "confidence": 0.9 if code != "FALLBACK" else 0.3,
            }
        except Exception as e:
            logger.error(f"意图识别失败: {e}")
            code, name = self._keyword_fallback(text, "闲聊/未知")
            return {"intent_code": code, "intent_name": name, "confidence": 0.3}

    def _keyword_fallback(self, text: str, name: str) -> tuple:
        """关键词兜底（覆盖高频场景）"""
        t = text.lower()

        # 咨询类 → 政策/知识
        if any(k in text for k in ["多久", "几天", "多长时间", "到账时间"]):
            if "退款" in text or "退" in text:
                return "PAY_001", "支付问题"
            if "发货" in text or "物流" in text:
                return "PRD_005", "配送时效"
            if "保修" in text or "售后" in text:
                return "PAY_004", "售后政策"
            return "PAY_001", "支付问题"

        if any(k in text for k in ["怎么", "如何", "流程", "步骤"]):
            if "退款" in text or "退" in text:
                return "PAY_004", "售后政策"
            if "订单" in text:
                return "ORD_001", "订单查询"
            if "发票" in text:
                return "PAY_005", "发票问题"
            return "PAY_004", "售后政策"

        if "保修" in text or "售后" in text:
            return "PAY_004", "售后政策"

        # 操作类
        if "退款" in text and any(k in text for k in ["我要", "申请", "帮我"]):
            return "PAY_002", "申请退款"
        if "订单" in text or "order" in t:
            if any(k in text for k in ["物流", "快递", "到哪", "在哪", "运输"]):
                return "ORD_004", "物流追踪"
            return "ORD_001", "订单查询"
        if "物流" in text or "快递" in text:
            return "ORD_004", "物流追踪"
        if "投诉" in text:
            return "CMP_001", "投诉建议"
        if "人工" in text:
            return "CMP_003", "人工客服"
        if "发票" in text:
            return "PAY_005", "发票问题"
        if "优惠" in text or "活动" in text or "促销" in text:
            return "PRD_002", "促销活动"
        if "耳机" in text or "手机" in text or "电脑" in text:
            return "PRD_001", "商品详情"

        return "FALLBACK", name or "闲聊/未知"