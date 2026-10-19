"""
文本分块模块
将长文档切分为适合向量化的短块，带重叠。
"""

from langchain_text_splitters import RecursiveCharacterTextSplitter

def split_documents(docs, chunk_size: int = 500, chunk_overlap: int = 50):
    """
    切分文档
    参数：docs - Document 列表
          chunk_size - 每块最大字符数
          chunk_overlap - 块间重叠字符数
    返回：切分后的 Document 列表
    """
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", "。", "！", "？", " ", ""],
    )
    return splitter.split_documents(docs)