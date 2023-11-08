import concurrent.futures
import logging
import time

import cx_Oracle
from equipment_interface import *
import datetime
import re


def get_requests_from_oracle():
    cursor = cnx.cursor()
    sql = "SELECT REQUEST_ID, REQUEST_IP, REQUEST_COMMAND FROM AUTOCOR.CNM_COMMANDS_QUEUE " \
          "WHERE STATUS  = 'AGUARDANDO EXECUCAO' ORDER BY REQUEST_ID ASC"
    cursor.execute(sql)
    resultado = cursor.fetchall()
    cursor.close()
    if not resultado:
        return None
    lista_requests = []
    for line in resultado:
        req_id = line[0]
        req_ip = line[1]
        req_command = line[2]
        req = {
            'req_id': req_id,
            'req_ip': req_ip,
            'req_command': req_command
        }
        lista_requests.append(req)
    return lista_requests


def thread_function(request):
    logging.info("Enviando comando no equipemento " + request['req_ip'] + " Comando: " + request['req_command'])
    try:
        conexao = InterfaceEquipment(ip=request['req_ip'], user='caiocor', password='Gto125312!')
        tem_conexao = conexao.connect()
        if not tem_conexao:
            status = 'ERRO'
            saida = str(conexao.cod_error)
            logging.error("Erro ao logar no equipamento da req "+str(request['req_id'])+": " + saida)
        else:
            status = 'EXECUTADO'
            saida = conexao.send_command_default(request['req_command'])
            saida = saida.replace("'", " ")
            if not saida:
                status = 'ERROR'
            conexao.disconnect()
        cursor = cnx.cursor()
        sql = "UPDATE AUTOCOR.CNM_COMMANDS_QUEUE SET " \
              "STATUS='"+status+"', RAW_OUTPUT='"+saida[0:3990]+"' WHERE REQUEST_ID = "+str(request['req_id'])
        cursor.execute(sql)
        cnx.commit()
    except Exception as e:
        logging.error("req_id-" + str(request['req_id']) + "Erro na funcao principal: "+str(e))
        sql = "UPDATE AUTOCOR.CNM_COMMANDS_QUEUE SET STATUS='ERROR', " \
              "RAW_OUTPUT='"+e+"' WHERE REQUEST_ID = " + str(request['req_id'])
        cursor.execute(sql)
        cnx.commit()
    cursor.close()


if __name__ == "__main__":
    formato = "%(asctime)s: %(message)s"
    logging.basicConfig(format=formato, level=logging.INFO, filename='CoraNetworkManager.log')
    #TODO fazer loop aqui
    while True:
        try:
            cnx = cx_Oracle.connect('AUTOCOR', 'N3tC=21rzU', 'exa04-scan-prd.network.ctbc/NCCORPRD', encoding='UTF-8')
            listaRequests = get_requests_from_oracle()
            if listaRequests:
                print(str(len(listaRequests)) + ' objetos recebidos')
                with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                    for request in listaRequests:
                        executor.submit(thread_function, request)
            else:
                print('sem dados')
        except:
            pass
        cnx.close()
        time.sleep(3)

