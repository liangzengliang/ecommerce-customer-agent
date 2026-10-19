"""
路由节点
"""

from app.nlu import IntentClassifier, SentimentAnalyzer, EntityExtractor
from app.agents.graph.state import AgentState
import logging

logger = logging.getLogger(__name__)

_intent_classifier = IntentClassifier()
_sentiment_analyzer = SentimentAnalyzer()
_entity_extractor = EntityExtractor()


async def analyze_and_route(state: AgentState) -> AgentState:
    text = state["user_message"]

    intent_result = await _intent_classifier.classify(text)
    sentiment_result = await _sentiment_analyzer.analyze(text)
    entities = _entity_extractor.extract(text)
    slots = _entity_extractor.build_slots(entities)

    state["intent_code"] = intent_result["intent_code"]
    state["intent_name"] = intent_result["intent_name"]
    state["intent_confidence"] = intent_result["confidence"]
    state["sentiment"] = sentiment_result["sentiment"]
    state["sentiment_score"] = sentiment_result["score"]
    state["entities"] = entities
    state["slots"] = slots

    logger.info(f"NLU: intent={state['intent_code']}, sentiment={state['sentiment']}, slots={slots}")
    return state


def route_decision(state: AgentState) -> str:
    """
    路由规则优先级（从高到低）：
    1. 有订单号/手机号 → 工具
    2. 咨询类词 → RAG
    3. 负面情绪 → 工具（转人工）
    4. 按意图编码走
    """
    code = state["intent_code"]
    text = state["user_message"]
    slots = state.get("slots", {})

    # ========== 规则 0：有订单号/手机号 → 工具 ==========
    if slots.get("order_no") or slots.get("phone"):
        return "tool"

    # ========== 规则 1：咨询类词 → RAG ==========
    # 包含"怎么/如何/多久/流程/政策/是什么/什么是/怎么办/几天"一律 RAG
    consult_keywords = [
        "怎么", "如何", "怎样", "多久", "几天", "多长时间",
        "步骤", "流程", "政策", "是什么", "什么是", "怎么办",
    ]
    if any(k in text for k in consult_keywords):
        return "rag"

    # ========== 规则 2：强烈负面情绪 → 工具 ==========
    if state["sentiment"] == "negative" and state["sentiment_score"] > 0.8:
        return "tool"

    # ========== 规则 3：按意图编码 ==========
    # 订单类：无订单号 → 当咨询（RAG）
    if code.startswith("ORD_"):
        return "rag"

    # 支付类：
    # PAY_001（支付问题）→ RAG（问支付政策）
    # PAY_002（申请退款）→ 需要订单号，无订单号当咨询走 RAG
    # PAY_003/004/005 → RAG
    if code.startswith("PAY_"):
        if code == "PAY_002":
            return "rag"      # 没有订单号，只能讲流程
        return "rag"

    # 商品类：走 RAG
    if code.startswith("PRD_"):
        return "rag"

    # 投诉类：
    # CMP_001（投诉建议）→ 需要用户主动发起，走工具
    # CMP_002（退款退货）→ 需要订单号，无订单号当咨询
    # CMP_003（人工客服）→ 走工具
    # CMP_004（建议反馈）→ 走工具
    if code.startswith("CMP_"):
        if code == "CMP_002":
            return "rag"
        return "tool"

    return "generate"