"""
文档加载模块
直接从文件系统读取 txt / md 文件，不依赖 langchain_community。
"""

from pathlib import Path
from typing import List
from langchain_core.documents import Document
import logging

logger = logging.getLogger(__name__)

def load_document(file_path: str) -> List[Document]:
    """
    加载单个文档
    参数：file_path - 文件路径（支持 .txt / .md / .markdown）
    返回：Document 列表（每个文件对应一个 Document）
    """
    path = Path(file_path)

    if not path.exists():
        logger.warning(f"文件不存在: {file_path}")
        return []

    if path.suffix.lower() not in (".txt", ".md", ".markdown"):
        logger.warning(f"暂不支持的文件类型: {path.suffix}")
        return []

    try:
        content = path.read_text(encoding="utf-8")
        return [
            Document(
                page_content=content,
                metadata={"source": str(path), "filename": path.name},
            )
        ]
    except Exception as e:
        logger.error(f"读取文件失败 {file_path}: {e}")
        return []