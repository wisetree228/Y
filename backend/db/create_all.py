from models import create_database
import asyncio

# Создаём все таблицы
if __name__ == "__main__":
    asyncio.run(create_database())