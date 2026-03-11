from pydantic_settings import BaseSettings


class Settings(BaseSettings):

    DB_HOST: str = "localhost"
    DB_PORT: int = 5432
    DB_NAME: str = "road_network_db"
    DB_USER: str = "postgres"
    DB_PASSWORD: str = "r2omm2550"

    class Config:
        env_file = ".env"


settings = Settings()