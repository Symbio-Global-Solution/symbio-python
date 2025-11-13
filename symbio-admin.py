'''
Global Solution - Computational Thinking Using Python
1TDSPF - Henrique Martins - RM563620
1TDSPF - Henrique Teixeira - RM563620

[SYMBIO] Sistema Administrativo.
Ferramenta administrativa para gestão de Cargos e Skills no banco de dados Oracle.
Inclui integração via API REST para cálculo de risco de automação com IA.
'''

# Importação dos Módulos
import oracledb
import os
import requests

# URL da API de IA 
API_IA_URL = "https://symbio-api-ia.onrender.com/"

def getConexao():
    '''
    Estabelece e retorna uma conexão com o banco de dados Oracle.
    '''
    try:
        # Tenta estabelecer a conexão
        conn = oracledb.connect(
            user="XXXXXX",
            password="XXXXX",
            host="oracle.fiap.com.br",
            port=1521,
            service_name="ORCL"
        )
        return conn
    except oracledb.Error as e:
        # Captura e exibe erros de conexão
        print(
        f"""[ERRO]: Não foi possível conectar ao Oracle: {e}\n
Verifique se:
1. O Oracle está instalado no sistema.
2. As credenciais (user, password) estão corretas."""
        )
        return None
    except Exception as e:
        print(f"\n[ERRO]: Ocorreu um erro: {e}")
        return None