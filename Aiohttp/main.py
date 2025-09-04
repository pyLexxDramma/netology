from dotenv import load_dotenv
load_dotenv()

import asyncio
from aiohttp import web
from app.routes.user_routes import setup_user_routes
from app.routes.advertisement_routes import setup_advertisement_routes
from app.db.database import create_db_and_tables


async def create_app():
    app = web.Application()
    setup_user_routes(app)
    setup_advertisement_routes(app)
    return app


async def main():
    app = await create_app()
    await create_db_and_tables()
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', 8080)
    await site.start()
    print("Server started at http://localhost:8080")
    await asyncio.Event().wait()


if __name__ == "__main__":
    asyncio.run(main())