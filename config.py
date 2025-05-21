import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")
    OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
    MODEL_NAME =  "gemini-2.0-flash-lite" # "gemini-1.5-flash"
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    @staticmethod
    def validate():
        required = ["GEMINI_API_KEY", "GOOGLE_MAPS_API_KEY", "OPENWEATHERMAP_API_KEY"]
        missing = [key for key in required if not getattr(Config, key)]
        if missing:
            raise ValueError(f"Missing required environment variables: {', '.join(missing)}")