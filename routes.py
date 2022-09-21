def setup_routes(app, handler):
    router = app.router
    router.add_get('/price/{currency}', handler.handle, name="latest_bid")
