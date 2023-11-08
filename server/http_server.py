from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import json
import re
from equipment_interface import *
import sys


class RequestHandler(BaseHTTPRequestHandler):
    def _set_response(self, code):
        self.send_response(code)
        self.send_header("Content-type", "text/html")
        self.send_header("charset", "utf-8")
        self.end_headers()

    def do_GET(self):
        logging.info(
            "GET request,\nPath: %s\nHeaders:\n%s\n", str(self.path), str(self.headers)
        )
        self._set_response()
        self.wfile.write("GET request for {}".format(self.path).encode("utf-8"))

    def do_POST(self):
        content_length = int(
            self.headers["Content-Length"]
        )  # <--- Gets the size of data
        post_data = self.rfile.read(content_length)  # <--- Gets the data itself
        logging.info(
            "POST request,\nPath: %s\nHeaders:\n%s\n\nBody:\n%s\n",
            str(self.path),
            str(self.headers),
            post_data.decode("utf-8"),
        )
        #
        try:
            req_data = json.loads(post_data)
            logging.info(
                "Enviando comando no equipemento "
                + req_data["IP"]
                + " Comando: "
                + req_data["CMD"]
            )
            conexao = InterfaceEquipment(
                ip=req_data["IP"], user="<USER>", password="<PASS>"
            )
            tem_conexao = conexao.connect()
            if not tem_conexao:
                status = 501
                saida = str(conexao.cod_error)
                logging.error(
                    "Erro ao logar no equipamento da req "
                    + str(req_data["IP"])
                    + ": "
                    + saida
                )
            else:
                status = 200
                saida = conexao.send_command_default(req_data["CMD"])
                saida = saida.replace("'", " ")
                regex = re.compile(req_data["REGEX"])
                reg_match = regex.match(saida)
                if not saida:
                    status = 502
                elif reg_match:
                    saida = reg_match.group(1)
                else:
                    status = 503

                conexao.disconnect()
        except Exception as e:
            status = 500
            logging.error(
                "req_id-" + str(req_data["IP"]) + "Erro na funcao principal: " + str(e)
            )
        #
        self._set_response(status)
        resposta = {"RESPONSE": saida}

        # self.wfile.write(saida.encode("utf8"))
        return resposta


def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    formato = "%(asctime)s: %(message)s"
    # logging.basicConfig(
    #    format=formato, level=logging.INFO, filename="CoraNetworkManager.log"
    # )
    logging.basicConfig(format=formato, level=logging.INFO)
    server_address = ("", port)
    httpd = server_class(server_address, handler_class)
    logging.info("Starting httpd...\n")
    print(httpd)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("Stopping httpd...\n")
        httpd.server_close()


if __name__ == "__main__":
    from sys import argv

    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        run()
