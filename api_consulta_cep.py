import re

import requests

class BuscaEndereco:

    def __init__(self, cep):

        self.list_cep = cep

    def __str__(self):
        return self.format_cep()


    def cep_e_valido(self, cep):

        """

            FUNÇÃO PARA VALIDAR O CEP

            # Arguments
                cep        - Required: CEP a ser validado (String)

            # Returns
                validator  - Required: Resultado de validação do CEP (Boolean)

        """

        # FORMATANDO O CEP
        cep = BuscaEndereco.format_cep(cep=cep)

        if len(cep) == 8:
            return True, cep
        else:
            return False, cep

    @staticmethod
    def format_cep(cep):

        # MANTENDO APENAS NÚMEROS
        cep = re.sub(string=cep,
                     pattern="\D",
                     repl="")

        return cep


    def busca_lat_long(self, cep, token):

        """

            REALIZA A CONSULTA DE DADOS
            RELACIONADO AO CEP ENVIADO

            EX DE RESULTADO:
            {'altitude': 760.0,
            'cep': '03069020',
            'latitude': '-23.4214599833',
            'longitude': '-46.4979652344',
            'logradouro': 'Rua Sargento Osvaldo',
            'bairro': 'Vila Zilda (Tatuapé)',
            'cidade': {'ddd': 11,
            'ibge': '3550308',
            'nome': 'São Paulo'},
            'estado': {'sigla': 'SP'}}


            # Arguments
                cep           - Required: CEP desejado (String)

            # Returns
                result_json   - Required: Resultados da API da CEPABERTO (Json)

        """

        try:
            if token is not None:
                # Gerar token particular para consulta do site https://www.cepaberto.com/
                headers = {'Authorization': 'Token token={token}'.format(token=token)}

                # CONSULTANDO LATITUDE E LONGITUDE PARA CADA DADO
                url = "http://www.cepaberto.com/api/v3/cep?cep=" + str(cep)
                response = requests.get(url, headers=headers)
                json = response.json()

                return json
            else:
                print("VOCÊ DEVE POSSUIR UM TOKEN PARA USAR A API DA CEPABERTO")
        except Exception as ex:
            print(ex)

        return None

    def consulta_via_cep(self, cep):

        """

            REALIZA A CONSULTA DE DADOS
            RELACIONADO AO CEP ENVIADO

            EX DE RESULTADO:
            {'cep': '03069-020',
            'logradouro': 'Rua Sargento Osvaldo',
            'complemento': '',
            'bairro': 'Vila Zilda (Tatuapé)',
            'localidade': 'São Paulo',
            'uf': 'SP',
            'ibge': '3550308',
            'gia': '1004',
            'ddd': '11',
            'siafi': '7107'}

            # Arguments
                cep           - Required: CEP desejado (String)

            # Returns
                result_json   - Required: Resultados da API da VIACEP (Json)

        """

        try:
            url = f"https://viacep.com.br/ws/{cep}/json/"
            r = requests.get(url)
            return r.json()
        except Exception as ex:
            print(ex)
            return None

    @staticmethod
    def union_result(result_via_cep, result_lat_long):

        """

            FUNÇÃO RESPONSÁVEL POR UNIR O RESULTADO
            DAS DUAS API'S USADAS

            # Arguments
                result_via_cep        - Required: Resultado obtido da API VIA CEP (Json)
                result_lat_long       - Required: Resultado obtido da API CEPABERTO(Json)

            # Returns
                result_dict           - Required: Resultado após união dos dicts (Json)

        """

        try:
            result_dict = {}

            # UNINDO OS DICTS
            result_via_cep.update(result_lat_long)

            for key, value in result_via_cep.items():
                result_dict[key.upper()] = value

            return result_dict
        except Exception as ex:
            print(ex)
            return None

    def consulta_cep(self, token=None):

        # INICIALIZAND O DICT QUE ARMAZENARÁ O RESULTADO FINAL
        result_consulta = {}

        if isinstance(self.list_cep, (str,)):
            self.list_cep = self.list_cep.split(",")

        if isinstance(self.list_cep, (list, tuple)):

            for cep in self.list_cep:

                print("CONSULTANDO CEP: {}".format(cep))

                # VERIFICANDO SE O CEP É VALIDO
                validator_cep, cep_consulta = self.cep_e_valido(cep)

                if validator_cep:

                    # OBTENDO OS DADOS (API: VIACEP)
                    result_via_cep = BuscaEndereco.consulta_via_cep(self,
                                                                    cep=cep_consulta)

                    # OBTENDO OS DADOS DE LATITUDE E LONGITUDE
                    result_lat_long = BuscaEndereco.busca_lat_long(self,
                                                                   cep=cep_consulta,
                                                                   token=token)

                    # UNINDO OS DOIS RESULTADOS
                    result_consulta[cep] = BuscaEndereco.union_result(result_via_cep,
                                                                      result_lat_long)

                    print("RESULTADO OBTIDO")
                    print(result_consulta[cep])
                    print("-"*50)

                else:
                    print("CEP INVÁLIDO: {}".format(cep))

        return result_consulta