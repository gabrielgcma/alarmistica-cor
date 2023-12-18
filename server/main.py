from fastapi import Request, Response, FastAPI
from fastapi.responses import JSONResponse
from equipment_interface import InterfaceEquipment
import logging
import re
from pydantic import BaseModel
import json
import asyncio, asyncssh, sys
import concurrent.futures
from netmiko import ConnectHandler

formato = "%(asctime)s: %(message)s"
logging.basicConfig(format=formato)
logging.getLogger("asyncssh").setLevel(logging.DEBUG)

app = FastAPI()


class PayloadModel(BaseModel):
    IP: str
    CMD: str
    REGEX: str


request_buffer = []
responses = []


@app.post("/logar/")
async def logar(request: PayloadModel):
    payload = request.model_dump()
    request_buffer.append(payload)

    if len(request_buffer) >= 10:
        buffer_responses = await process_requests()
        return JSONResponse(content=buffer_responses, status_code=200)

    return JSONResponse(
        content={
            "message": f"Request recebido e bufferizado. Buffer: {len(request_buffer)}/10"
        },
        status_code=200,
    )


async def process_requests():
    responses.clear()

    # sem threads:
    # while request_buffer:
    #     request_payload = request_buffer.pop(0)
    #     response = await handle_request(request_payload)
    #     responses.append(response)

    # com threads:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        for response in executor.map(handle_request, request_buffer):
            responses.append(response)

    request_buffer.clear()
    print(responses)
    return responses


def handle_request(payload):
    try:
        logging.info(
            "Enviando comando no equipamento "
            + payload["IP"]
            + " Comando: "
            + payload["CMD"]
        )
        # com async ssh:

        # async with asyncssh.connect(
        #     host=payload["IP"],
        #     username="admin",
        #     password="1234",
        #     encryption_algs=(["aes128-cbc", "3des-cbc", "aes192-cbc", "aes256-cbc"]),
        #     public_key_auth=False,
        # ) as conn:
        #     output = await conn.run(payload["CMD"])
        #     print(output.stdout)
        #     status = 200
        #     saida = output.stdout

        # com paramiko:

        # conexao = InterfaceEquipment(ip=payload["IP"], user="admin", password="1234")
        # tem_conexao = conexao.connect()
        # if not tem_conexao:
        #     status = 501
        #     saida = str(conexao.cod_error)
        #     logging.error(
        #         "Erro ao logar no equipamento da req "
        #         + str(payload["IP"])
        #         + ": "
        #         + saida
        #     )
        # else:
        #     status = 200
        #     saida = conexao.send_command_default(payload["CMD"])
        #     # saida = saida.replace("'", " ")
        #     # regex = re.compile(payload["REGEX"])
        #     # reg_match = regex.match(saida)
        #     # if not saida:
        #     #     status = 502
        #     # elif reg_match:
        #     #     saida = reg_match.group(1)
        #     # else:
        #     #     status = 503

        #     conexao.disconnect()

        # com netmiko:
        device = {
            "device_type": "cisco_ios",
            "host": payload["IP"],
            "username": "admin",
            "password": "1234",
        }

        conn = ConnectHandler(**device)
        conn.banner_timeout = 40
        saida = conn.send_command(payload["CMD"])
        status = 200

        conn.disconnect()

    except Exception as e:
        status = 500
        saida = "Erro"
        logging.error(
            "req_id-"
            + str(payload["IP"])
            + "Erro em main2.handle_requests(): "
            + str(e)
        )

    resposta = {"IP": payload["IP"], "STATUS": status, "OUTPUT": saida}

    return resposta
