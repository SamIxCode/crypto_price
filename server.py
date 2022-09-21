import os

from aiohttp import web
import aiohttp_jinja2
import jinja2

from Backend import MainHandler, ApiHandler
from middlewares import setup_middlewares
from routes import setup_routes
from DBsevice import DbService
from settings import base

def setup_static_routes(app, settings):
    app.router.add_static('/static/', path=settings.STATIC_PATH, name='static')



def main():
    settings = base

    api = web.Application()
    handler = ApiHandler(settings)
    setup_routes(api, handler)
    setup_middlewares(api, api=True)

    app = web.Application()
    app.add_subapp("/api/", api)
    setup_middlewares(app, api=False)
    handler = MainHandler(settings)
    setup_routes(app, handler)

    db_service = DbService(settings)
    db_service.initialize_db()

    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(str(os.path.join(settings.STATIC_PATH, 'templates'))))

    setup_static_routes(app, settings)
    web.run_app(app)


if __name__ == '__main__':
    main()

