import asyncio
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String

DATABASE_URL = "sqlite:///./mydatabase.db"
metadata = MetaData()

people = Table(
    "people",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("birth_year", String(255)),
    Column("eye_color", String(255)),
    Column("gender", String(255)),
    Column("hair_color", String(255)),
    Column("homeworld", String(255)),
    Column("mass", String(255)),
    Column("name", String(255)),
    Column("skin_color", String(255)),
)

async def create_tables():
    engine = create_engine(DATABASE_URL)
    metadata.create_all(engine)

if __name__ == "__main__":
    asyncio.run(create_tables())
    print("Таблицы созданы")