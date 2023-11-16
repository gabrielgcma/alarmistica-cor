from aiohttp import web
import logging

logger = logging.getLogger()
formato = "%(asctime)s: %(message)s"
logging.basicConfig(format=formato)
logger.setLevel(logging.INFO)


async def handle(req):
    logger.info(req)
    name = req.match_info.get("name", "Anonymous")
    text = "Hello " + name
    return web.Response(text=text)


app = web.Application()
app.add_routes([web.get("/", handle), web.get("/{name}", handle)])

if __name__ == "__main__":
    web.run_app(app)
