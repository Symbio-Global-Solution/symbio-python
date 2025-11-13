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

# Funções para Estilização do Terminal
def limpar_terminal():
    '''
    Limpa o terminal.
    '''
    os.system('cls' if os.name == 'nt' else 'clear')

def titulo_sistema():
    print('-=≡≣ ------------------ X -------------------- ≣≡=-')
    print('''

░██████╗██╗░░░██╗███╗░░░███╗██████╗░██╗░█████╗░
██╔════╝╚██╗░██╔╝████╗░████║██╔══██╗██║██╔══██╗
╚█████╗░░╚████╔╝░██╔████╔██║██████╦╝██║██║░░██║
░╚═══██╗░░╚██╔╝░░██║╚██╔╝██║██╔══██╗██║██║░░██║
██████╔╝░░░██║░░░██║░╚═╝░██║██████╦╝██║╚█████╔╝
╚═════╝░░░░╚═╝░░░╚═╝░░░░░╚═╝╚═════╝░╚═╝░╚════╝░
''')
    print('-=≡≣ ------------------ X -------------------- ≣≡=-')

# Função para o Banco de Dados
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
    
# Funções de Gestão de Cargos 
def obter_risco_ia(features: list):
    '''
    Chama a API de IA para obter a predição de risco.
    '''
    try:
        url = f"{API_IA_URL}/prever/risco"
        # O JSON que a API espera: {"features": [num1, num2, num3]}
        payload = {"features": features}
        
        response = requests.post(url, json=payload, timeout=5)
        
        if response.status_code == 200:
            return response.json().get("risco_predito")
        else:
            print(f"[ERRO]: A API de IA teve um erro {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n[ERRO DE REDE] Não foi possível conectar à API de IA (Flask).")
        print("Verifique se o servidor 'symbio-app.py' está rodando.")
        return None
    except Exception as e:
        print(f"\n[ERRO INESPERADO API]: {e}")
        return None
    
titulo_sistema()