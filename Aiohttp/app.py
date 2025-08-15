from aiohttp import web
from views import create_ad, get_ad, delete_ad, update_ad

def setup_routes(app: web.Application) -> None:
    app.router.add_post('/ad', create_ad)
    app.router.add_get('/ad/{id:\d+}', get_ad)
    app.router.add_delete('/ad/{id:\d+}', delete_ad)
    app.router.add_put('/ad/{id:\d+}', update_ad)

async def create_app() -> web.Application:
    app = web.Application()
    setup_routes(app)
    return app

if __name__ == '__main__':
    web.run_app(create_app(), port=8080)