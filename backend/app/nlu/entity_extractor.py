"""
实体抽取模块
基于正则规则抽取订单号、手机号等高置信度实体。
可后续扩展为 LLM 抽取商品名、地址等。
"""

import re
from typing import List, Dict, Any

# 订单号规则：ORDER + 数字，或 2 位大写字母 + 数字，或 12 位以上数字
# ORDER_NO_PATTERN = re.compile(r"\b(ORDER\d{10,}|[A-Z]{2}\d{10,}|\d{12,})\b", re.IGNORECASE)
ORDER_NO_PATTERN = re.compile(r"(ORDER\d{10,}|[A-Z]{2}\d{10,}|\d{12,})", re.IGNORECASE)
# 中国大陆手机号
# PHONE_PATTERN = re.compile(r"\b1[3-9]\d{9}\b")
PHONE_PATTERN = re.compile(r"(1[3-9]\d{9})")

class EntityExtractor:
    """实体抽取器：基于规则快速召回高频实体"""

    def extract(self, text: str) -> List[Dict[str, Any]]:
        """
        从文本中抽取实体
        参数：text - 用户原始消息
        返回：实体列表，每项含 type/value/normalized/start/end/confidence/slot
        """
        entities = []
        for m in ORDER_NO_PATTERN.finditer(text):
            entities.append({
                "type": "order_no",
                "value": m.group(),
                "normalized": m.group().upper(),   # 订单号统一大写
                "start": m.start(),
                "end": m.end(),
                "confidence": 0.95,
                "slot": "order_no",
            })
        for m in PHONE_PATTERN.finditer(text):
            entities.append({
                "type": "phone",
                "value": m.group(),
                "normalized": m.group(),
                "start": m.start(),
                "end": m.end(),
                "confidence": 0.98,
                "slot": "phone",
            })
        return entities

    def build_slots(self, entities: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        将实体列表转换为槽位字典
        参数：entities - 实体列表
        返回：{slot_name: normalized_value}，同名槽位只取第一个
        """
        slots = {}
        for e in entities:
            slot = e.get("slot")
            if slot and slot not in slots:
                slots[slot] = e.get("normalized") or e.get("value")
        return slots