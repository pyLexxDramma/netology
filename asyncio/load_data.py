import asyncio
import aiohttp
import databases
import sqlalchemy
import json
import os

db_semaphore = asyncio.Semaphore(5)
metadata = sqlalchemy.MetaData()

people = sqlalchemy.Table(
    "people",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True, index=True),
    sqlalchemy.Column("birth_year", sqlalchemy.String(255)),
    sqlalchemy.Column("eye_color", sqlalchemy.String(255)),
    sqlalchemy.Column("gender", sqlalchemy.String(255)),
    sqlalchemy.Column("hair_color", sqlalchemy.String(255)),
    sqlalchemy.Column("homeworld", sqlalchemy.String(255)),
    sqlalchemy.Column("mass", sqlalchemy.String(255)),
    sqlalchemy.Column("name", sqlalchemy.String(255)),
    sqlalchemy.Column("skin_color", sqlalchemy.String(255)),
)

DATABASE_URL = "sqlite+aiosqlite:///./mydatabase.db"
database = databases.Database(DATABASE_URL)


async def fetch_person(session: aiohttp.ClientSession, person_id: int) -> dict | None:
    url = f"https://www.swapi.tech/api/people/{person_id}/"
    try:
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data
            else:
                print(f"Ошибка при запросе персонажа {person_id}: {response.status}")
                return None
    except aiohttp.ClientError as e:
        print(f"Ошибка сети при запросе персонажа {person_id}: {e}")
        return None


async def insert_person_to_db(person_data: dict):
    if person_data is None:
        return

    try:
        async with db_semaphore:
            person = person_data['result']['properties']
            query = people.insert().values(
                id=int(person_data['result']['uid']),
                birth_year=person.get("birth_year"),
                eye_color=person.get("eye_color"),
                gender=person.get("gender"),
                hair_color=person.get("hair_color"),
                homeworld=person.get("homeworld"),
                mass=person.get("mass"),
                name=person.get("name"),
                skin_color=person.get("skin_color"),
            )
            await database.execute(query)
    except Exception as e:
        print(f"Ошибка при вставке данных в БД: {e}")


async def main():
    await database.connect()

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_person(session, i) for i in range(1, 84)]
        results = await asyncio.gather(*tasks)

        insert_tasks = [insert_person_to_db(person_data) for person_data in results]
        await asyncio.gather(*insert_tasks)

    await database.disconnect()
    print("Загрузка данных завершена.")


if __name__ == "__main__":
    asyncio.run(main())