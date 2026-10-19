"""
槽位填充模块
定义每个意图的必需槽位，判断是否缺失，生成澄清问题。
"""

from typing import Dict, List, Any

# 各意图的必需槽位配置
REQUIRED_SLOTS = {
    "ORD_001": ["order_no"],   # 订单查询需要订单号
    "ORD_002": ["order_no"],   # 订单修改
    "ORD_003": ["order_no"],   # 取消订单
    "ORD_004": ["order_no"],   # 物流追踪
    "ORD_005": ["order_no"],   # 催促发货
    "ORD_006": ["order_no"],   # 修改地址
    "PAY_002": ["order_no"],   # 申请退款
}

def check_missing_slots(intent_code: str, slots: Dict[str, Any]) -> List[str]:
    """
    检查意图需要的槽位是否齐全
    参数：intent_code - 意图编码
          slots - 已填充的槽位
    返回：缺失的槽位列表
    """
    required = REQUIRED_SLOTS.get(intent_code, [])
    return [s for s in required if not slots.get(s)]

def build_clarification_question(missing: List[str]) -> str:
    """
    根据缺失槽位生成澄清问句
    参数：missing - 缺失的槽位列表
    返回：向用户追问的话术
    """
    if not missing:
        return ""
    mapping = {
        "order_no": "请提供您的订单号",
        "phone": "请提供您的手机号",
    }
    parts = [mapping.get(m, f"请提供{m}") for m in missing]
    return "，".join(parts) + "，我来帮您处理。"