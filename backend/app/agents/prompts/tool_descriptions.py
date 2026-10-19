"""
工具描述
供 LLM 理解每个工具的用途（如接入 Function Calling 时使用）。
"""

TOOL_DESCRIPTIONS = {
    "query_order": "根据订单号查询订单状态",
    "query_product": "根据关键词查询商品信息",
    "create_ticket": "创建工单，用于投诉、退款等需要人工处理的事项",
    "transfer_human": "转接人工客服",
    "search_knowledge": "检索知识库，回答商品政策等问题",
    "request_refund": "提交退款申请",
}