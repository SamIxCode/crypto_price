import logging

import aiohttp_jinja2
from aiohttp import web

from exceptions import UnknownCurrencyException
logging.basicConfig(filename='logs/app.log', filemode='a',
                    format='%(asctime)s - %(levelname)s - %(message)s', level=logging.WARNING)


@web.middleware
async def api_error_middleware(request, handler):
    try:
        return await handler(request)
    except web.HTTPException as ex:
        if ex.status == 404:
            return web.json_response({"error": "Page not found"}, status=404)
        if ex.status == 500:
            return web.json_response({"error": "Internal error"}, status=500)
        raise
    except UnknownCurrencyException as ex:
        logging.error(f"Unknown currency {ex.args[-1]}")
        return web.json_response({"error": f"Unknown currency {ex.args[-1]}"}, status=400)


    except Exception as ex:
        logging.exception(ex.__traceback__)
        return web.json_response({"error": "Internal error"}, status=500)


@web.middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except web.HTTPException as ex:
        if ex.status == 404:
            return aiohttp_jinja2.render_template('404.html', request, {}, status=404)
        if ex.status == 500:
            return aiohttp_jinja2.render_template('500.html', request, {}, status=500)
        raise
    except UnknownCurrencyException as ex:
        logging.error(f"Unknown currency {ex.args[-1]}")
        return aiohttp_jinja2.render_template('400.html', request, {"message": f"Unknown currency {ex.args[-1]}"},
                                              status=400)



    except Exception as ex:
        logging.exception(ex.__traceback__)
        return aiohttp_jinja2.render_template('500.html', request, {}, status=500)


def setup_middlewares(app, api):
    if api:
        app.middlewares.append(api_error_middleware)
    else:
        app.middlewares.append(error_middleware)
