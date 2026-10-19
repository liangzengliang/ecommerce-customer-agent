"""
知识库导入脚本
功能：
1. 从 knowledge_base/ 目录读取 txt/md 文件
2. 解析 Q&A 对，写入 MySQL
3. 调用向量化任务写入 Milvus

用法：
    cd backend
    python -m scripts.import_knowledge
    python -m scripts.import_knowledge --category faqs
"""

import asyncio
import argparse
from pathlib import Path
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.knowledge import Knowledge
from app.rag.vector_store import vector_store_manager
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("import_knowledge")

# 知识库根目录（项目根下的 knowledge_base/）
KB_ROOT = Path(__file__).resolve().parent.parent.parent / "knowledge_base"

def parse_qa(text: str) -> list[tuple[str, str]]:
    """
    解析 Q/A 格式文本
    参数：text - 原始文本
    返回：[(question, answer), ...]
    """
    pairs = []
    cur_q = None
    cur_a = []

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.startswith("Q:"):
            if cur_q and cur_a:
                pairs.append((cur_q, "\n".join(cur_a)))
            cur_q = line[2:].strip()
            cur_a = []
        elif line.startswith("A:"):
            cur_a.append(line[2:].strip())
        elif cur_a:
            cur_a.append(line)

    if cur_q and cur_a:
        pairs.append((cur_q, "\n".join(cur_a)))

    return pairs

async def import_file(file_path: Path, category: str) -> int:
    """
    导入单个文件
    参数：file_path - 文件路径
          category - 知识分类
    返回：导入条数
    """
    text = file_path.read_text(encoding="utf-8")
    pairs = parse_qa(text)

    if not pairs:
        logger.warning(f"⚠️  {file_path.name} 未解析到 Q/A 对，跳过")
        return 0

    async with AsyncSessionLocal() as db:
        for q, a in pairs:
            db.add(Knowledge(category=category, question=q, answer=a))
        await db.commit()

    logger.info(f"✅ {file_path.name}: 导入 {len(pairs)} 条")
    return len(pairs)

async def vectorize_all():
    """把所有没有 vector_id 的知识写入 Milvus"""

    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(Knowledge).where(Knowledge.vector_id.is_(None))
        )
        items = result.scalars().all()

        if not items:
            logger.info("⏭️  没有待向量化的知识")
            return

        texts = [f"{i.question}\n{i.answer}" for i in items]
        metadatas = [{"knowledge_id": i.id, "category": i.category} for i in items]
        ids = vector_store_manager.add_texts(texts, metadatas)

        for item, vid in zip(items, ids):
            item.vector_id = str(vid)
        await db.commit()

        logger.info(f"✅ 向量化完成：{len(items)} 条")

async def main(category_filter: str | None):
    """脚本主入口"""
    logger.info(f"=== 开始导入知识库，根目录：{KB_ROOT} ===")

    if not KB_ROOT.exists():
        logger.error(f"❌ 知识库目录不存在：{KB_ROOT}")
        return

    total = 0
    for category_dir in KB_ROOT.iterdir():
        if not category_dir.is_dir():
            continue
        if category_filter and category_dir.name != category_filter:
            continue

        logger.info(f"📁 处理分类：{category_dir.name}")
        for file_path in category_dir.glob("*.txt"):
            total += await import_file(file_path, category_dir.name)
        for file_path in category_dir.glob("*.md"):
            total += await import_file(file_path, category_dir.name)

    logger.info(f"=== 导入完成，共 {total} 条 ===")

    await vectorize_all()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--category", help="只导入指定分类", default=None)
    args = parser.parse_args()
    asyncio.run(main(args.category))