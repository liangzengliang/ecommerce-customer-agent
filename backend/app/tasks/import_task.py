"""
知识库文件导入任务
从 txt/md 文件批量导入问答对到 MySQL，并触发向量化。
"""

import asyncio
import os
from app.tasks.celery_app import celery_app
from app.tasks.vectorize_task import _do_vectorize
from app.core.database import AsyncSessionLocal
from app.models.knowledge import Knowledge
from app.rag.document_loader import load_document
from app.rag.text_splitter import split_documents
import logging

logger = logging.getLogger(__name__)

def _parse_qa(text: str) -> list[tuple[str, str]]:
    """
    简单解析：以 'Q:' 开头的行为问题，'A:' 开头的行为答案
    参数：text - 原始文本
    返回：[(question, answer), ...]
    """
    qa_pairs = []
    current_q = None
    current_a_lines = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("Q:"):
            # 遇到新问题，保存上一组
            if current_q and current_a_lines:
                qa_pairs.append((current_q, "\n".join(current_a_lines)))
            current_q = line[2:].strip()
            current_a_lines = []
        elif line.startswith("A:"):
            current_a_lines.append(line[2:].strip())
        elif current_a_lines:
            # 答案续行
            current_a_lines.append(line)

    if current_q and current_a_lines:
        qa_pairs.append((current_q, "\n".join(current_a_lines)))

    return qa_pairs

async def _do_import(file_path: str, category: str):
    """
    实际导入逻辑
    参数：file_path - 文件路径
          category - 知识分类
    返回：导入条数
    """
    docs = load_document(file_path)
    if not docs:
        logger.warning(f"文件为空或加载失败: {file_path}")
        return 0

    # 分块
    chunks = split_documents(docs, chunk_size=500, chunk_overlap=50)

    async with AsyncSessionLocal() as db:
        count = 0
        for chunk in chunks:
            pairs = _parse_qa(chunk.page_content)
            for q, a in pairs:
                if not q or not a:
                    continue
                k = Knowledge(category=category, question=q, answer=a)
                db.add(k)
                count += 1
        await db.commit()

    logger.info(f"导入完成，共 {count} 条")
    # 导入完成后触发向量化
    await _do_vectorize()
    return count

@celery_app.task(name="tasks.import_knowledge_file", bind=True)
def import_knowledge_file(self, file_path: str, category: str = "faqs"):
    """
    Celery 任务入口：导入知识库文件
    参数：file_path - 文件绝对路径
          category - 知识分类
    返回：dict，含 success / count / error
    """
    logger.info(f"[Task {self.request.id}] 导入文件 {file_path}")
    if not os.path.exists(file_path):
        return {"success": False, "error": f"文件不存在: {file_path}"}

    try:
        count = asyncio.run(_do_import(file_path, category))
        return {"success": True, "count": count}
    except Exception as e:
        logger.error(f"导入任务失败: {e}", exc_info=True)
        return {"success": False, "error": str(e)}