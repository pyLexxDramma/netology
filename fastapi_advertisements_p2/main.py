from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv
from fastapi import Header

load_dotenv()

app = FastAPI()

#@app.get("/test_secret_key")
#async def test_secret_key():
#    return {"secret_key": SECRET_KEY}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SECRET_KEY = os.environ.get("SECRET_KEY", "fdab2c0836a3610b1d4b485478aa50e22ffe7a04c7cd022e80555c7e0ab0308a")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2880

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

from typing import Optional

async def get_token_optional(token: Optional[str] = Depends(oauth2_scheme)) -> Optional[str]:
    return token


async def get_current_user(token: Optional[str] = Depends(get_token_optional)):
    if token is None:
        return None  # No token, no user

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        group: str = payload.get("group")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username, group=group)
    except JWTError:
        raise credentials_exception
    user = find_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

class User(BaseModel):
    id: Optional[int] = None
    username: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=8)
    group: str = Field(default="user", enum=["user", "admin"])
    created_at: datetime = datetime.now()
    updated_at: Optional[datetime] = None

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.password)

class UserCreate(BaseModel):
    username: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=8)
    group: str = Field(default="user", enum=["user", "admin"])

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    username: Optional[str] = None
    group: Optional[str] = None

users = []
next_user_id = 1
advertisements = []
next_id = 1

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def find_user_by_username(username: str):
    for user in users:
        if user.username == username:
            return user
    return None

def get_user(user_id: int):
    for user in users:
        if user.id == user_id:
            return user
    return None

@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = find_user_by_username(form_data.username)
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"username": user.username, "group": user.group}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/user/", response_model=User)
async def create_user(user: UserCreate):
    global next_user_id
    hashed_password = get_password_hash(user.password)
    new_user = User(id=next_user_id, username=user.username, password=hashed_password, group=user.group)
    users.append(new_user)
    next_user_id += 1
    return new_user

from fastapi import Header

@app.get("/user/{user_id}", response_model=User)
async def read_user(user_id: int, authorization: Optional[str] = Header(None)):
    user = get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    if authorization:
        try:
            token = authorization.split(" ")[1]  # Extract token from "Bearer <token>"
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("username")
            group: str = payload.get("group")
            token_data = TokenData(username=username, group=group)
            current_user = find_user_by_username(username=token_data.username)

        except Exception:
            pass
    return user

@app.patch("/user/{user_id}", response_model=User)
async def update_user(user_id: int, request: Request, current_user: User = Depends(get_current_user)):
    user = get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user is None or (current_user.id != user_id and current_user.group != "admin"):
        raise HTTPException(status_code=403, detail="Forbidden")

    try:
        request_body = await request.json()
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid JSON body")

    if not isinstance(request_body, dict):
        raise HTTPException(status_code=400, detail="Request body must be a JSON object")

    user_data = user.dict()

    if "username" in request_body:
        user_data["username"] = request_body["username"]
    if "password" in request_body:
        user_data["password"] = get_password_hash(request_body["password"])
    if "group" in request_body:
        user_data["group"] = request_body["group"]

    updated_user = User(**user_data)
    updated_user.updated_at = datetime.now()

    for index, u in enumerate(users):
        if u.id == user_id:
            users[index] = updated_user
            return updated_user
    raise HTTPException(status_code=404, detail="User not found")

@app.get("/users/", response_model=List[User])
async def read_users(current_user: User = Depends(get_current_user)):
    if current_user is None or current_user.group != "admin":
        raise HTTPException(status_code=403, detail="Forbidden")
    return users

@app.delete("/user/{user_id}")
async def delete_user(user_id: int, request: Request, current_user: User = Depends(get_current_user)):
    user = get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if current_user is None or (current_user.id != user_id and current_user.group != "admin"):
        raise HTTPException(status_code=403, detail="Forbidden")

    for index, u in enumerate(users):
        if u.id == user_id:
            del users[index]
            return {"message": "User deleted"}
    raise HTTPException(status_code=404, detail="User not found")

class Advertisement(BaseModel):
    title: str
    description: str
    price: float
    author: str
    created_at: datetime = datetime.now()
    updated_at: Optional[datetime] = None
    id: Optional[int] = None

    class Config:
        from_attributes = True

@app.post("/advertisement/")
async def create_advertisement(advertisement: Advertisement, current_user: User = Depends(get_current_user)):
    if current_user is None:
         raise HTTPException(status_code=401, detail="Authentication required")
    global next_id
    advertisement.id = next_id
    advertisement.author = current_user.username
    advertisement.created_at = datetime.now()
    advertisement.updated_at = None
    next_id += 1
    advertisements.append(advertisement)
    return advertisement

@app.get("/advertisement/{advertisement_id}")
async def read_advertisement(advertisement_id: int):
    for advertisement in advertisements:
        if advertisement.id == advertisement_id:
            return advertisement
    raise HTTPException(status_code=404, detail="Advertisement not found")

from typing import List

@app.get("/advertisements/", response_model=List[Advertisement])
async def read_advertisements(current_user: User = Depends(get_current_user)):
    if current_user.group != "admin": # Предполагаем, что только админ может видеть все объявления
        raise HTTPException(status_code=403, detail="Not authorized to view all advertisements")
    return advertisements

@app.patch("/advertisement/{advertisement_id}", response_model=Advertisement | None)
async def update_advertisement(advertisement_id: int, request: Request, current_user: User = Depends(get_current_user)):
    if current_user is None:
         raise HTTPException(status_code=401, detail="Authentication required")
    for index, advertisement in enumerate(advertisements):
        if advertisement.id == advertisement_id:
            if advertisement.author != current_user.username and current_user.group != "admin":
                raise HTTPException(status_code=403, detail="Forbidden")
            try:
                request_body = await request.json()
            except Exception as e:
                raise HTTPException(status_code=400, detail="Invalid JSON body")

            if not isinstance(request_body, dict):
                raise HTTPException(status_code=400, detail="Request body must be a JSON object")

            advertisement_data = advertisement.dict()

            if "title" in request_body:
                advertisement_data["title"] = request_body["title"]
            if "description" in request_body:
                advertisement_data["description"] = request_body["description"]
            if "price" in request_body:
                advertisement_data["price"] = request_body["price"]

            updated_advertisement = Advertisement(**advertisement_data)
            updated_advertisement.updated_at = datetime.now()

            advertisements[index] = updated_advertisement
            return updated_advertisement

    raise HTTPException(status_code=404, detail="Advertisement not found")

@app.delete("/advertisement/{advertisement_id}")
async def delete_advertisement(advertisement_id: int, current_user: User = Depends(get_current_user)):
    if current_user is None:
         raise HTTPException(status_code=401, detail="Authentication required")
    for index, advertisement in enumerate(advertisements):
        if advertisement.id == advertisement_id:
            if advertisement.author != current_user.username and current_user.group != "admin":
                raise HTTPException(status_code=403, detail="Forbidden")
            del advertisements[index]
            return {"message": "Advertisement deleted"}
    raise HTTPException(status_code=404, detail="Advertisement not found")

@app.get("/advertisement/")
async def search_advertisements(title: Optional[str] = None, description: Optional[str] = None,
                                price: Optional[float] = None, author: Optional[str] = None):
    results = advertisements[:]

    if title:
        results = [adv for adv in results if title.lower() in adv.title.lower()]
    if description:
        results = [adv for adv in results if description.lower() in adv.description.lower()]
    if price is not None:
        results = [adv for adv in results if adv.price == price]
    if author:
        results = [adv for adv in results if author.lower() in adv.author.lower()]

    return results