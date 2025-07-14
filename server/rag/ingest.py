import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from server.core.config import settings
from langchain_community.embeddings import HuggingFaceEmbeddings

def ingest_documents():
    """
    'documents' 디렉토리의 모든 .txt 파일을 로드하여 청크로 분할하고,
    HuggingFace 임베딩을 사용하여 FAISS 벡터 저장소에 저장합니다.
    """
    source_dir = settings.DOCUMENT_SOURCE_DIR
    if not os.path.exists(source_dir):
        print(f"'{source_dir}' 디렉토리가 존재하지 않아 빈 디렉토리를 생성합니다.")
        os.makedirs(source_dir)
        with open(os.path.join(source_dir, "sample.txt"), "w", encoding="utf-8") as f:
            f.write("AI Assistant 프로젝트에 오신 것을 환영합니다.")
        print(f"'{source_dir}/sample.txt' 예시 파일을 생성했습니다.")

    print(f"'{source_dir}' 디렉토리에서 문서를 로드합니다...")
    loader = DirectoryLoader(
        source_dir,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
        show_progress=True,
        use_multithreading=True
    )
    documents = loader.load()

    if not documents:
        print("로드할 문서가 없습니다. 프로세스를 종료합니다.")
        return

    print(f"{len(documents)}개의 문서를 로드했습니다. 문서를 청크로 분할합니다...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)

    print(f"{len(docs)}개의 청크로 분할되었습니다. 임베딩 및 벡터 저장소 생성을 시작합니다...")
    
    embeddings = HuggingFaceEmbeddings(
        model_name=settings.EMBEDDING_MODEL_NAME,
        model_kwargs={'device': 'cpu'},
        encode_kwargs={'normalize_embeddings': True}
    )

    db = FAISS.from_documents(docs, embeddings)

    if not os.path.exists(settings.VECTOR_STORE_PATH):
        os.makedirs(settings.VECTOR_STORE_PATH)
        
    db.save_local(settings.VECTOR_STORE_PATH)
    print(f"벡터 저장소 생성이 완료되었습니다. 저장 경로: {settings.VECTOR_STORE_PATH}")

if __name__ == "__main__":
    ingest_documents()
