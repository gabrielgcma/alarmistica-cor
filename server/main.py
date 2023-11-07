from fastapi import Request, FastAPI

app = FastAPI()


@app.post("/alarmes/")
async def post_alarm(request: Request):
    print("Alarmes recebidos: ")
    alarmes_json = await request.json()
    for alarme in alarmes_json:
        print(alarme)
