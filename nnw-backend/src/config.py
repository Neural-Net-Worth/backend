from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "development"
    PG_USER: str
    PG_PASSWORD: str
    PG_HOST: str
    PG_PORT: str
    PG_DB: str
    PG_SSLMODE: str = "require"
    JWT_SECRET: str
    STRIPE_API_KEY: str

    @property
    def database_url(self) -> str:
        return (
            f"postgresql://{self.PG_USER}:{self.PG_PASSWORD}@"
            f"{self.PG_HOST}:{self.PG_PORT}/{self.PG_DB}?sslmode={self.PG_SSLMODE}"
        )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
