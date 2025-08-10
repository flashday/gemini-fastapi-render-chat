import os
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
 
 
class Settings(BaseSettings):
    """
    应用的配置类，继承自 Pydantic 的 BaseSettings。
    它会自动从环境变量或 .env 文件中加载配置。
    """
    GEMINI_API_KEY: str
 
    model_config = SettingsConfigDict(
        env_file=os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env'),
        env_file_encoding='utf-8'
    )
 
 
@lru_cache
def get_settings() -> Settings:
    """
    返回一个缓存的 Settings 实例。
    使用 lru_cache 装饰器可以确保 Settings 对象只被创建一次，
    避免了每次 API 请求都重新读取 .env 文件，这是一个重要的性能优化。
    """
    return Settings()
