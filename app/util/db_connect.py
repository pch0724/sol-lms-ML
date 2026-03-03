from dotenv import load_dotenv
from sqlalchemy import create_engine
import os

def db_connection() :
    load_dotenv()

    DB_URL = (
        f"mysql+pymysql://{os.getenv('DB_USER')}:"
        f"{os.getenv('DB_PASSWORD')}@"
        f"{os.getenv('DB_HOST')}:"
        f"{os.getenv('DB_PORT')}/"
        f"{os.getenv('DB_NAME')}"
    )
    engine = create_engine(DB_URL)

    return engine 