from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Advertisement(BaseModel):
    title: str
    description: str
    price: float
    author: str
    created_at: datetime = datetime.now()
    updated_at: Optional[datetime] = None
    id: Optional[int] = None

    model_config = {
        "from_attributes": True
    }

advertisements = []
next_id = 1

@app.post("/advertisement/")
async def create_advertisement(advertisement: Advertisement):
    global next_id
    advertisement.id = next_id
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
    raise HTTPException(status_code=404, detail="Announcement not found")

@app.patch("/advertisement/{advertisement_id}", response_model=Advertisement | None)
async def update_advertisement(advertisement_id: int, request: Request):
    for index, advertisement in enumerate(advertisements):
        if advertisement.id == advertisement_id:
            try:
                request_body = await request.json()
            except Exception as e:
                raise HTTPException(status_code=400, detail="Invalid JSON format")

            if not isinstance(request_body, dict):
                raise HTTPException(status_code=400, detail="Request body should be a dictionary")

            advertisement_data = advertisement.model_dump()

            if "title" in request_body:
                advertisement_data["title"] = request_body["title"]
            if "description" in request_body:
                advertisement_data["description"] = request_body["description"]
            if "price" in request_body:
                advertisement_data["price"] = request_body["price"]
            if "author" in request_body:
                advertisement_data["author"] = request_body["author"]

            updated_advertisement = Advertisement.model_validate(advertisement_data)
            updated_advertisement.updated_at = datetime.now()

            advertisements[index] = updated_advertisement
            return updated_advertisement

    raise HTTPException(status_code=404, detail="Announcement not found")

@app.delete("/advertisement/{advertisement_id}")
async def delete_advertisement(advertisement_id: int):
    for index, advertisement in enumerate(advertisements):
        if advertisement.id == advertisement_id:
            del advertisements[index]
            return {"message": "Announcement deleted successfully"}
    raise HTTPException(status_code=404, detail="Announcement not found")

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