from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.advertisement import Advertisement
from app.schemas.advertisement import AdvertisementCreate, AdvertisementRead, AdvertisementUpdate
from app.db.database import get_db
from app.routes.user_routes import get_current_user
from typing import List

async def create_advertisement(request: web.Request):
    async for db_session in get_db():
        current_user = await get_current_user(request, db_session)
        if not current_user:
            return web.json_response({"detail": "Not authenticated"}, status=401)

        try:
            data = await request.json()
            advertisement_data = AdvertisementCreate(**data)
        except Exception as e:
            return web.json_response({"detail": f"Invalid input: {e}"}, status=400)

        new_advertisement = Advertisement(
            title=advertisement_data.title,
            description=advertisement_data.description,
            owner_id=current_user.id # Связываем с текущим пользователем
        )
        db_session.add(new_advertisement)
        await db_session.commit()
        await db_session.refresh(new_advertisement)
        return web.json_response(AdvertisementRead.from_orm(new_advertisement).dict(), status=201)

async def get_advertisement(request: web.Request):
    advertisement_id = int(request.match_info["advertisement_id"])
    async for db_session in get_db():
        result = await db_session.execute(select(Advertisement).filter(Advertisement.id == advertisement_id))
        advertisement = result.scalar()
        if not advertisement:
            return web.json_response({"detail": "Advertisement not found"}, status=404)
        return web.json_response(AdvertisementRead.from_orm(advertisement).dict())

async def list_advertisements(request: web.Request):
    async for db_session in get_db():
        result = await db_session.execute(select(Advertisement))
        advertisements = result.scalars().all()
        return web.json_response([AdvertisementRead.from_orm(adv).dict() for adv in advertisements])

async def update_advertisement(request: web.Request):
    advertisement_id = int(request.match_info["advertisement_id"])
    async for db_session in get_db():
        current_user = await get_current_user(request, db_session)
        if not current_user:
            return web.json_response({"detail": "Not authenticated"}, status=401)

        result = await db_session.execute(select(Advertisement).filter(Advertisement.id == advertisement_id))
        advertisement = result.scalar()

        if not advertisement:
            return web.json_response({"detail": "Advertisement not found"}, status=404)

        if advertisement.owner_id != current_user.id:
            return web.json_response({"detail": "Not authorized to update this advertisement"}, status=403)

        try:
            data = await request.json()
            advertisement_data = AdvertisementUpdate(**data)
            for k, v in advertisement_data.dict(exclude_unset=True).items():
                setattr(advertisement, k, v)
            await db_session.commit()
            await db_session.refresh(advertisement)
            return web.json_response(AdvertisementRead.from_orm(advertisement).dict())
        except Exception as e:
            return web.json_response({"detail": f"Failed to update advertisement: {e}"}, status=400)

async def delete_advertisement(request: web.Request):
    advertisement_id = int(request.match_info["advertisement_id"])
    async for db_session in get_db():
        current_user = await get_current_user(request, db_session)
        if not current_user:
            return web.json_response({"detail": "Not authenticated"}, status=401)

        result = await db_session.execute(select(Advertisement).filter(Advertisement.id == advertisement_id))
        advertisement = result.scalar()

        if not advertisement:
            return web.json_response({"detail": "Advertisement not found"}, status=404)

        if advertisement.owner_id != current_user.id:
            return web.json_response({"detail": "Not authorized to delete this advertisement"}, status=403)

        await db_session.delete(advertisement)
        await db_session.commit()
        return web.json_response({"detail": "Advertisement deleted successfully"})

def setup_advertisement_routes(app: web.Application):
    app.router.add_post('/advertisements', create_advertisement)
    app.router.add_get('/advertisements/{advertisement_id}', get_advertisement)
    app.router.add_get('/advertisements', list_advertisements)
    app.router.put('/advertisements/{advertisement_id}', update_advertisement)
    app.router.delete('/advertisements/{advertisement_id}', delete_advertisement)