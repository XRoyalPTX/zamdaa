from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings): 
    db_host: str 
    db_port: int
    db_name: str
    db_user: str
    db_pass: str

    secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql+asyncpg://{self.db_user}:{self.db_pass}@{self.db_host}:{self.db_port}/{self.db_name}"

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
settings = Settings()