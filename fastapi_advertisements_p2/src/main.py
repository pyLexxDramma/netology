from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"],
                   allow_headers=["*"])

SECRET_KEY = os.environ.get("SECRET_KEY", "fdab2c0836a3610b1d4b485478aa50e22ffe7a04c7cd022e80555c7e0ab0308a")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 2880

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


class User(BaseModel):
    id: Optional[int] = None
    username: str = Field(..., min_length=4, max_length=50)
    password: str = Field(..., min_length=8)
    group: str = Field(default="user", enum=["user", "admin"])
    created_at: datetime = Field(default_factory=datetime.now)
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


users: List[User] = []
next_user_id = 1


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def initialize_users():
    global next_user_id
    admin_password_hash = get_password_hash("adminpass")
    admin_user = User(id=next_user_id, username="admin", password=admin_password_hash, group="admin")
    users.append(admin_user)
    next_user_id += 1

    user_password_hash = get_password_hash("userpass")
    regular_user = User(id=next_user_id, username="user", password=user_password_hash, group="user")
    users.append(regular_user)
    next_user_id += 1


initialize_users()


class AdvertisementCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    price: float = Field(..., gt=0)


class Advertisement(BaseModel):
    id: int
    title: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1, max_length=1000)
    price: float = Field(..., gt=0)
    author_id: int
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


advertisements: List[Advertisement] = []
next_id = 1


def find_user_by_username(username: str) -> Optional[User]:
    for user in users:
        if user.username == username:
            return user
    return None


def get_user_by_id(user_id: int) -> Optional[User]:
    for user in users:
        if user.id == user_id:
            return user
    return None


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
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


@app.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = find_user_by_username(form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.verify_password(form_data.password):
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


@app.post("/user/", response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreate):
    global next_user_id
    existing_user = find_user_by_username(user.username)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    hashed_password = get_password_hash(user.password)
    new_user = User(id=next_user_id, username=user.username, password=hashed_password, group=user.group)
    users.append(new_user)
    next_user_id += 1
    return new_user


@app.get("/user/{user_id}", response_model=User)
async def read_user(user_id: int, current_user: User = Depends(get_current_user)):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.id != user_id and current_user.group != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this user")

    return user


@app.patch("/user/{user_id}", response_model=User)
async def update_user(user_id: int, user_update_data: UserCreate, current_user: User = Depends(get_current_user)):
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.id != user_id and current_user.group != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this user")

    if user_update_data.username:
        existing_user = find_user_by_username(user_update_data.username)
        if existing_user and existing_user.id != user_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")
        user.username = user_update_data.username
    if user_update_data.password:
        user.password = get_password_hash(user_update_data.password)
    if user_update_data.group:
        user.group = user_update_data.group

    user.updated_at = datetime.now()

    for index, u in enumerate(users):
        if u.id == user_id:
            users[index] = user
            return user

    raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to update user")


@app.delete("/user/{user_id}")
async def delete_user(user_id: int, current_user: User = Depends(get_current_user)):
    user_to_delete = get_user_by_id(user_id)
    if user_to_delete is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if current_user.id != user_id and current_user.group != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user")

    for index, u in enumerate(users):
        if u.id == user_id:
            del users[index]
            return {"message": "User deleted"}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@app.get("/users/", response_model=List[User])
async def read_users(current_user: User = Depends(get_current_user)):
    if current_user.group != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Forbidden")
    return users


@app.get("/advertisements/", response_model=List[Advertisement])
async def read_all_advertisements(current_user: User = Depends(get_current_user)):
    if current_user.group != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view all advertisements")
    return advertisements


@app.post("/advertisement/", response_model=Advertisement, status_code=status.HTTP_201_CREATED)
async def create_advertisement(
        advertisement_data: AdvertisementCreate,
        current_user: User = Depends(get_current_user)
):
    global next_id

    new_advertisement = Advertisement(
        id=next_id,
        title=advertisement_data.title,
        description=advertisement_data.description,
        price=advertisement_data.price,
        author_id=current_user.id,
        created_at=datetime.now(),
        updated_at=None
    )

    advertisements.append(new_advertisement)
    next_id += 1
    return new_advertisement


@app.get("/advertisement/{advertisement_id}", response_model=Advertisement)
async def read_advertisement(advertisement_id: int, current_user: Optional[User] = Depends(get_current_user)):
    for adv in advertisements:
        if adv.id == advertisement_id:
            return adv
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Advertisement not found")


@app.patch("/advertisement/{advertisement_id}", response_model=Advertisement)
async def update_advertisement(
        advertisement_id: int,
        advertisement_update: Advertisement,
        current_user: User = Depends(get_current_user)
):
    for index, adv in enumerate(advertisements):
        if adv.id == advertisement_id:
            if adv.author_id != current_user.id and current_user.group != "admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Not authorized to update this advertisement")

            update_data = advertisement_update.dict(exclude_unset=True)
            update_data["updated_at"] = datetime.now()

            updated_adv = adv.copy(update=update_data)
            advertisements[index] = updated_adv
            return updated_adv

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Advertisement not found")


@app.delete("/advertisement/{advertisement_id}", response_model=Dict[str, str])
async def delete_advertisement(
        advertisement_id: int,
        current_user: User = Depends(get_current_user)
):
    for index, adv in enumerate(advertisements):
        if adv.id == advertisement_id:
            if adv.author_id != current_user.id and current_user.group != "admin":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                                    detail="Not authorized to delete this advertisement")

            del advertisements[index]
            return {"message": "Advertisement deleted"}

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Advertisement not found")


@app.get("/advertisement/", response_model=List[Advertisement])
async def search_advertisements(
        title: Optional[str] = None,
        description: Optional[str] = None,
        price: Optional[float] = None,
        author_id: Optional[int] = None,
        current_user: Optional[User] = Depends(get_current_user)
):
    results = advertisements

    if title:
        results = [adv for adv in results if title.lower() in adv.title.lower()]
    if description:
        results = [adv for adv in results if description.lower() in adv.description.lower()]
    if price is not None:
        results = [adv for adv in results if adv.price == price]
    if author_id is not None:
        results = [adv for adv in results if adv.author_id == author_id]

    return results