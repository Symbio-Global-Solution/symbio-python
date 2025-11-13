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
    '''
    Exibe titulo personalizado.
    '''
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
    
def adicionar_cargo():
    '''
    Solicita ao admin os dados de um novo cargo, chama a API de IA para calcular o risco
    e insere o cargo completo no banco de dados.
    '''
    print("\n╔═───────────────────────────────────────────────═╗")
    print("│                    [SYMBIO]                     │")
    print("│           Adicionar Novo Cargo com IA           │")
    print("╚═───────────────────────────────────────────────═╝")
    # Obter dados do cargo 
    nome = input("Nome do Cargo (ex: Engenheiro de Prompt): ")
    descricao = input("Descrição curta do Cargo: ")
    
    try:
        # Obter as features para a IA
        print("\nAgora, classifique o cargo em porcentagem (0 a 100): ")
        repetitividade = int(input("Tarefa Repetitiva (0-100%): "))
        criatividade = int(input("Exige Criatividade (0-100%): "))
        interacao = int(input("Interação Humana (0-100%): "))
        
        if not (0 <= repetitividade <= 100 and 0 <= criatividade <= 100 and 0 <= interacao <= 100):
            print("\n[ERRO]: Percentagens devem estar entre 0 e 100. Operação cancelada.")
            return

    except ValueError:
        print("\n[ERRO]: Valores inválidos. As percentagens devem ser números. Operação cancelada.")
        return
    
    if not nome:
        print("\n[ERRO]: Nome é obrigatório. Operação cancelada.")
        return