from fastapi import Request, FastAPI

app = FastAPI()


@app.post("/alarmes/")
async def post_alarm(request: Request):
    print("Alarmes recebidos: ")
    print(await request.body())
