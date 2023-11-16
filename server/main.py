from fastapi import Request, Response, FastAPI
from equipment_interface import InterfaceEquipment
import logging
import re
from pydantic import BaseModel
import json
import asyncio, asyncssh, sys

formato = "%(asctime)s: %(message)s"
logging.basicConfig(format=formato)
# logger = logging.getLogger("asyncssh").setLevel(logging.DEBUG)
logging.getLogger("asyncssh").setLevel(logging.DEBUG)
# logger.setLevel(logging.INFO)

app = FastAPI()


class PayloadModel(BaseModel):
    IP: str
    CMD: str
    REGEX: str


@app.post("/logar/")
async def logar(request: PayloadModel):
    try:
        payload = request.model_dump()
        logging.info(
            "Enviando comando no equipamento "
            + payload["IP"]
            + " Comando: "
            + payload["CMD"]
        )
        async with asyncssh.connect(
            host=payload["IP"],
            username="admin",
            password="1234",
            encryption_algs=(["aes128-cbc", "3des-cbc", "aes192-cbc", "aes256-cbc"]),
            public_key_auth=False,
        ) as conn:
            output = await conn.run(payload["CMD"])
            print(output.stdout)
            status = 200
            saida = output.stdout
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
            # saida = saida.replace("'", " ")
            # regex = re.compile(payload["REGEX"])
            # reg_match = regex.match(saida)
            # if not saida:
            #     status = 502
            # elif reg_match:
            #     saida = reg_match.group(1)
            # else:
            #     status = 503

            # conexao.disconnect()
    except Exception as e:
        status = 500
        saida = "Erro"
        logging.error(
            "req_id-" + str(payload["IP"]) + "Erro na funcao principal: " + str(e)
        )

    resposta = {"RESPONSE": saida}

    return Response(
        content=json.dumps(obj=resposta),
        status_code=status,
        media_type="application/json",
    )
