import os
from langchain_community.vectorstores import FAISS
from server.core.config import settings
from langchain_community.embeddings import HuggingFaceEmbeddings

def get_rag_retriever():
    """
    FAISS 벡터 저장소에서 RAG 검색기를 로드하고 반환합니다.
    HuggingFace 임베딩 모델을 사용하여 검색기를 초기화합니다.
    """
    if not os.path.exists(settings.VECTOR_STORE_PATH):
        raise FileNotFoundError(
            f"FAISS 벡터 저장소를 찾을 수 없습니다: {settings.VECTOR_STORE_PATH}. "
            "먼저 'python -m server.rag.ingest'를 실행하여 데이터를 인덱싱하세요."
        )

    embeddings = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )
    
    db = FAISS.load_local(
        settings.VECTOR_STORE_PATH,
        embeddings,
        allow_dangerous_deserialization=True
    )
    
    return db.as_retriever()
