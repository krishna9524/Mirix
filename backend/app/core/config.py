#from pydantic_settings import BaseSettings

#class Settings(BaseSettings):
 #   OPENROUTER_API_KEY: str  # <-- ADD THIS
    
    # Remove or comment out the old keys if you're not using them
    # GEMINI_API_KEY: str
    # GPT_API_KEY: str
    
    # Define the path to your SQLite database
  #  DATABASE_URL: str = "sqlite:///./app/db/mirix_local.db"

   # class Config:
    #    env_file = ".env"

#settings = Settings()

from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    OPENROUTER_API_KEY: str
    
    # --- MySQL Settings ---
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    
    # --- THIS IS THE FIX ---
    # The connection string format was wrong.
    # It should be: "mysql+pymysql://USER:PASSWORD@HOST:PORT/DB_NAME"
    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+pymysql://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"
    # --- END OF FIX ---

    class Config:
        env_file = ".env"

settings = Settings()