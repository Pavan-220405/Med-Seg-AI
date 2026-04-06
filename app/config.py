from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    JWT_SECRET_KEY : str
    JWT_ALGORITHM : str
    ACCESS_TOKEN_EXPIRY_MINUTES : int
    REFRESH_TOKEN_EXPIRY_DAYS : int 
    DATABASE_URL : str 
    REDIS_HOST : str = "localhost"
    REDIS_PORT : int = 6379
    JTI_EXPIRY : int = 60


    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )
settings = Settings()


if __name__ == "__main__":
    print(settings.DATABASE_URL)
    print(settings.REDIS_HOST)
    print(settings.REDIS_PORT)
    print(settings.JTI_EXPIRY)