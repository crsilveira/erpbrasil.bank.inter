# -*- coding: utf-8 -*-
import json
import requests
from datetime import datetime, timedelta

FILTRAR_POR = [
    'TODOS',
    'VENCIDOSAVENCER',
    'EXPIRADOS',
    'PAGOS',
    'TODOSBAIXADOS',
]

ORDENAR_CONSULTA_POR = [
    'NOSSONUMERO',  # (Default)
    'SEUNUMERO',
    'DATAVENCIMENTO_ASC',
    'DATAVENCIMENTO_DSC',
    'NOMESACADO',
    'VALOR_ASC',
    'VALOR_DSC',
    'STATUS_ASC',
    'STATUS_DSC',
]


class ApiInter(object):
    """ Implementa a Api do Inter"""

    data_do_ultimo_token = None
    token = None

    def __init__(self, cert, conta_corrente, client_id, client_secret, client_environment):
        self._cert = cert
        self.conta_corrente = conta_corrente
        self._client_id = client_id
        self._client_secret = client_secret
        self._client_environment = client_environment
        if self._client_environment == "1":
           self._api = 'https://cdpj.partners.bancointer.com.br/cobranca/v3/'
        else:
           # sandbox
           self._api = 'https://cdpj-sandbox.partners.uatinter.co/cobranca/v3/'

    def _prepare_token(self):
        if self._client_environment == "1":
            URL_OAUTH = "https://cdpj.partners.bancointer.com.br/oauth/v2/token"
        else:
            # sandbox
            URL_OAUTH = "https://cdpj-sandbox.partners.uatinter.co/oauth/v2/token"
        D1 = "client_id={}".format(self._client_id)
        D2 = "client_secret={}".format(self._client_secret)
        D3 = "scope=boleto-cobranca.read boleto-cobranca.write"
        #D3 = "scope=boleto-cobranca.write"
        D4 = "grant_type=client_credentials"
        DADOS = f"{D1}&{D2}&{D3}&{D4}"
        print(f"{D1} - {D2} - {D3}")
        response = requests.post(
            URL_OAUTH,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            data=DADOS,
            cert=self._cert,
            timeout=(10)
        )
        response.raise_for_status()
        # Isola o access_token do JSON recebido
        access_token = response.json().get("access_token")
        if not access_token:
            return
        TOKEN = access_token
        return TOKEN

    def _prepare_headers(self):
        if self.token is not None:
            tempo_token = (datetime.now() - self.data_do_ultimo_token).total_seconds()
            if tempo_token > 3600:
                new_token = self._prepare_token()
                self.data_do_ultimo_token = datetime.now()
                self.token = new_token
        else:
            self.token = self._prepare_token()
            self.data_do_ultimo_token = datetime.now()

        return {
            "Authorization": "Bearer " + self.token,
            "x-conta-corrente": self.conta_corrente,
            "Content-type": "application/json",
        }

    def _call(self, http_request, url, params=None, data=None, **kwargs):
        response = http_request(
            url,
            headers=self._prepare_headers(),
            data=data,
            params=params,
            cert=self._cert,
            verify=True,
            **kwargs
        )
        # response.raise_for_status()
        # print(response.text)
        if response.status_code > 299:
            message = '%s - Código %s' % (
                response.status_code,
                response.text,
            )
            raise Exception(message)
        return response

    def boleto_inclui(self, boleto):
        """ POST
        https://cdpj.partners.bancointer.com.br/cobranca/v3/

        :param boleto:
        :return:
        """
        result = self._call(
            requests.post,
            url=self._api + 'cobrancas',
            data=json.dumps(boleto),
        )
        return result.content and result.json() or result.ok

    def consulta_boleto_detalhado(self, nosso_numero=False):
        """
            GET https://cdpj.partners.bancointer.com.br/cobranca/v3/cobrancas/{codigoSolicitacao}
        """
        if not nosso_numero:
            raise Exception('Nosso número não informado.')

        url = self._api + 'cobrancas'

        # nao consegui fazer consulta por boleto

        # params = {
        #    "codigoSolicitao": nosso_numero
        # }

        dt = datetime.now()
        dt_fim = dt.strftime("%Y-%m-%d")
        dt = dt + timedelta(days=-5)
        dt_ini = dt.strftime("%Y-%m-%d")
        opFiltros = {
          'dataInicial': dt_ini,
          'dataFinal': dt_fim,
          'filtrarDataPor': 'EMISSAO',
          'situacao':'A_RECEBER',
          'tipoOrdenacao':'ASC',
        }

        result = self._call(
            requests.get,
            url=url,
            params=opFiltros
        )
        return result.content and result.json() or result.ok

    def boleto_baixa(self, nosso_numero, codigo_baixa):
        """ POST
        https://cdpj.partners.bancointer.com.br/cobranca/v2/boletos/
        {nossoNumero}/cancelar

        :param nosso_numero:
        :return:
        """
        url = self._api + 'cobrancas/' + nosso_numero + '/cancelar'
        result = self._call(
            requests.post,
            url=url,
            data='{{"motivoCancelamento":"{}"}}'.format(codigo_baixa)

        )
        return result.content and result.json() or result.ok

    def boleto_pdf(self, nosso_numero):
        """ GET
        https://cdpj.partners.bancointer.com.br/cobranca/v2/boletos/
        {nossoNumero}/pdf

        :param nosso_numero:
        :return:
        """
        url = self._api + 'cobrancas/' + nosso_numero + '/pdf'
        result = self._call(
            requests.get,
            url=url,
        )
        return result.content
