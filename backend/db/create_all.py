from models import create_database
import asyncio

# Create all tables
if __name__ == "__main__":
    asyncio.run(create_database())