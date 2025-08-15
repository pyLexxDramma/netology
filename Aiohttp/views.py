import json
from datetime import datetime
from typing import List, Optional

import marshmallow
from aiohttp import web
from aiohttp.web_request import Request

from models import Advertisement, AdvertisementSchema

ads: List[Advertisement] = []
next_ad_id = 1

async def create_ad(request: Request) -> web.Response:
    try:
        data = await request.json()
    except json.JSONDecodeError:
        raise web.HTTPBadRequest(text="Invalid JSON")

    try:
        ad = AdvertisementSchema().load(data)
    except marshmallow.exceptions.ValidationError as e:
        raise web.HTTPBadRequest(text=json.dumps(e.messages))

    global next_ad_id
    ad.id = next_ad_id
    next_ad_id += 1
    ads.append(ad)

    return web.json_response({"id": ad.id}, status=201)

async def get_ad(request: Request) -> web.Response:
    ad_id = int(request.match_info['id'])

    for ad in ads:
        if ad.id == ad_id:
            return web.json_response(AdvertisementSchema().dump(ad))

    raise web.HTTPNotFound(text="Ad not found")

async def delete_ad(request: Request) -> web.Response:
    ad_id = int(request.match_info['id'])

    for i, ad in enumerate(ads):
        if ad.id == ad_id:
            del ads[i]
            return web.json_response({"message": "Ad deleted"})

    raise web.HTTPNotFound(text="Ad not found")

async def update_ad(request: Request) -> web.Response:
    ad_id = int(request.match_info['id'])

    try:
        data = await request.json()
    except json.JSONDecodeError:
        raise web.HTTPBadRequest(text="Invalid JSON")
    try:
        updated_ad = AdvertisementSchema().load(data)
    except marshmallow.exceptions.ValidationError as e:
        raise web.HTTPBadRequest(text=json.dumps(e.messages))

    for i, ad in enumerate(ads):
        if ad.id == ad_id:
            updated_ad.id = ad_id
            ads[i] = updated_ad
            return web.json_response({"message": "Ad updated"})

    raise web.HTTPNotFound(text="Ad not found")