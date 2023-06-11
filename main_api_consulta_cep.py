from api_consulta_cep import BuscaEndereco

result_consulta_cep = BuscaEndereco(cep="03069020").consulta_cep(token="10c9397802c79fb5a5415edabe9af2be")

print(result_consulta_cep)