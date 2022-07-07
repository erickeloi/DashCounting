import requests
import backoff
import json

import pandas as pd
contador: int = 0
@backoff.on_exception(backoff.expo, requests.exceptions.RequestException, max_tries=10, max_time=150)
def get_api_info(cnpj_id):
    global contador

    api_request = requests.get(f"https://www.receitaws.com.br/v1/cnpj/{cnpj_id}")

    if api_request.status_code == 429:
        contador = contador + 1

        if contador == 10:
            print("Servidor indisponível, por favor tentar novamente mais tarde.")
            contador = 0
            return 'Servidor Indisponivel'

        print(f"Servidor Ocupado! Realizando pedido pela {contador+1}° vez... (Máximo de 10 tentativas)\n")
        raise requests.exceptions.RequestException

    json_infos = api_request.json()
    contador = 0

    if json_infos['status'] == 'ERROR' and json_infos['message'] == 'CNPJ inválido':
        print(f"Erro!\nCnpj informado: {cnpj_id},\nCnpj Inválido.\n")
        return 'CNPJ Invalido'

    return json_infos
