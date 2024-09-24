# -*- coding: utf-8 -*-


# from erpbrasil.febraban.boleto.custom_property import CustomProperty
# from erpbrasil.febraban.entidades import Boleto


class BoletoInter:
    """ Implementa a Api do BancoInter """

    @classmethod
    def convert_to(cls, obj, **kwargs):
        obj.__class__ = cls
        obj.__special_init__()
        for key, value in kwargs.items():
            if hasattr(obj, key):
                obj.__dict__[key] = value

    def __init__(self, sender, amount, payer, issue_date, due_date,
                 identifier, instructions=None, mora=None, multa=None,
                 discount1=None, discount2=None, discount3=None):
        self._sender = sender
        self._amount = amount
        self._payer = payer
        self._issue_date = issue_date.strftime("%Y-%m-%d")
        self._due_date = due_date.strftime("%Y-%m-%d")
        self._identifier = identifier
        self._instructions = instructions or []

        #self.mora = mora or dict(
        #    codigoMora="ISENTO",
        #    valor=0,
        #    taxa=0
        #)
        #self.mora = dict(
        #    taxa=mora or 0,
        #    codigo="TAXAMENSAL",
        #)
        #self.multa = dict(
        #    taxa=multa or 0,
        #    codigo="PERCENTUAL",
        #)
        self.discount1 = discount1 or dict(
            codigoDesconto="NAOTEMDESCONTO",
            taxa=0,
            valor=0,
            data=""
        )
        self.discount2 = discount2 or dict(
            codigoDesconto="NAOTEMDESCONTO",
            taxa=0,
            valor=0,
            data=""
        )
        self.discount3 = discount3 or dict(
            codigoDesconto="NAOTEMDESCONTO",
            taxa=0,
            valor=0,
            data=""
        )

    def _emissao_data(self):
        tipo_pessoa = "FISICA"
        if len(self._payer.identifier) > 11:
            tipo_pessoa = "JURIDICA"
        data = {
            "seuNumero": self._identifier[:15],
            "valorNominal": self._amount,
            "valorAbatimento": 0,
            "dataVencimento": self._due_date,
            "numDiasAgenda": 30,
            "atualizarPagador": "false",
            "pagador": {
                "cpfCnpj": self._payer.identifier,
                "tipoPessoa": tipo_pessoa,
                "nome": self._payer.name,
                "endereco": self._payer.address.streetLine1,
                "cidade": self._payer.address.city,
                "uf": self._payer.address.stateCode,
                "cep": self._payer.address.zipCode,
                "email": "", #self._payer.email,
                "ddd": "", #self._payer.phone[:2],
                "telefone": "", #self._payer.phone[2:],
                "numero": self._payer.address.streetLine2,
                "complemento": "",
                "bairro": self._payer.address.district,
            },
            "desconto1": {
                "codigoDesconto": "PERCENTUALDATAINFORMADA",
                "taxa": 4,
                "valor": self.discount1,
                "data": self._due_date
            },
            "desconto2": {
                "codigoDesconto": "PERCENTUALDATAINFORMADA",
                "taxa": 4,
                "valor": self.discount2,
                "data": self._due_date
            },
            "desconto3": {
                "codigoDesconto": "PERCENTUALDATAINFORMADA",
                "taxa": 4,
                "valor": self.discount3,
                "data": self._due_date
            },
            "beneficiarioFinal": {
                "cpfCnpj": self._sender.identifier,
                "tipoPessoa": "JURIDICA",
                "nome": self._sender.name,
                "endereco": self._sender.address.streetLine1,
                "bairro": self._sender.address.district,
                "cidade": self._sender.address.city,
                "uf": self._sender.address.stateCode,
                "cep": self._sender.address.zipCode,
            }
        }
        #    "multa": self.multa,
        #    "mora": self.mora,
        #    "multa": {
        #        "taxa": self.multa or 0,
        #        "codigo": "PERCENTUAL"
        #    },

        if self._instructions:
            data['mensagem'] = {'linha{}'.format(k + 1): v for k, v in enumerate(self._instructions)}

        return data
