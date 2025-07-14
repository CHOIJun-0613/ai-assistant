from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """
    애플리케이션의 설정을 관리하는 클래스.
    .env 파일에서 환경 변수를 로드합니다.
    """
    # --- CHANGED: Google 키 대신 Groq 키를 사용하도록 변경 ---
    GROQ_API_KEY: str
    GROQ_MODEL_NAME: str = "llama3-8b-8192"
    
    # --- CHANGED: 임베딩 모델 이름을 HuggingFace 모델로 변경 ---
    EMBEDDING_MODEL_NAME: str = "jhgan/ko-sbert-nli"
    
    VECTOR_STORE_PATH: str = "./vector_store/faiss_index"
    DOCUMENT_SOURCE_DIR: str = "./documents"
    
    # Google Workspace 도구 연동을 위한 설정 (기존과 동일)
    GOOGLE_CREDENTIALS_PATH: str = "./credentials.json"
    TOKEN_PATH: str = "./token.json"
    REDIRECT_URI: str = "http://localhost:8501"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding='utf-8')

settings = Settings()
