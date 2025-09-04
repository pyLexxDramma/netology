from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class AdvertisementBase(BaseModel):
    title: str
    description: Optional[str] = None

class AdvertisementCreate(AdvertisementBase):
    pass

class AdvertisementUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None

class AdvertisementRead(AdvertisementBase):
    id: int
    created_at: datetime
    owner_id: int

    class Config:
        orm_mode = True