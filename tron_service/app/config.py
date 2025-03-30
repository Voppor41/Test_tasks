from dotenv import load_dotenv
import os

load_dotenv()

database_url = os.getenv("DATABASE_URL")
print("DATABASE_URL:", database_url)  # Проверим, загружается ли строка подключения
