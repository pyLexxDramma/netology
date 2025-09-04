# app/routes/user_routes.py
from aiohttp import web
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.user import User
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.db.database import get_db
from app.auth.security import create_access_token, verify_access_token, get_password_hash
from typing import List

async def register_user(request: web.Request):
    try:
        data = await request.json()
        user_data = UserCreate(**data)
    except Exception as e:
        return web.json_response({"detail": f"Invalid input: {e}"}, status=400)

    async for db_session in get_db():
        result = await db_session.execute(select(User).filter(User.email == user_data.email))
        existing_user = result.scalar()
        if existing_user:
            return web.json_response({"detail": "User with this email already registered"}, status=400)

        new_user = User(email=user_data.email)
        new_user.set_password(user_data.password)
        db_session.add(new_user)
        await db_session.commit()
        await db_session.refresh(new_user)
        return web.json_response(UserRead.from_orm(new_user).dict(), status=201)


async def login_user(request: web.Request):
    try:
        data = await request.json()
        login_data = UserRead(**data)
        password = data.get('password')
        if not password:
            return web.json_response({"detail": "Password is required"}, status=400)
    except Exception as e:
        return web.json_response({"detail": f"Invalid input: {e}"}, status=400)

    async for db_session in get_db():
        result = await db_session.execute(select(User).filter(User.email == login_data.email))
        user = result.scalar()

        if not user or not user.verify_password(password):
            return web.json_response({"detail": "Incorrect email or password"}, status=401)

        access_token = create_access_token(data={"sub": user.id})
        return web.json_response({"access_token": access_token, "token_type": "bearer"})


async def get_current_user(request: web.Request, db_session: AsyncSession):
    auth_header = request.headers.get('Authorization')
    if not auth_header:
        return None

    try:
        token_type, token = auth_header.split()
        if token_type.lower() != "bearer":
            return None # Не Bearer токен
    except ValueError:
        return None

    user_info = verify_access_token(token)
    if not user_info:
        return None

    result = await db_session.execute(select(User).filter(User.id == user_info.id))
    user = result.scalar()
    return user


async def get_me(request: web.Request):
    async for db_session in get_db():
        current_user = await get_current_user(request, db_session)
        if not current_user:
            return web.json_response({"detail": "Not authenticated"}, status=401)
        return web.json_response(UserRead.from_orm(current_user).dict())


def setup_user_routes(app: web.Application):
    app.router.add_post('/register', register_user)
    app.router.add_post('/login', login_user)
    app.router.add_get('/me', get_me)
