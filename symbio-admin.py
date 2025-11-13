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
    
    # Chamar a API de IA
    print(f"\nAnalisando cargo com a IA...")
    features_ia = [repetitividade, criatividade, interacao]
    risco_calculado = obter_risco_ia(features_ia)

    if risco_calculado is None:
        print("Não foi possível calcular o risco. O cargo NÃO será salvo.")
        return

    print(f"IA calculou o risco como: {risco_calculado}")
    
    # Inserir no Banco de Dados
    conn = None
    cursor = None
    try:
        conn = getConexao()
        if conn:
            cursor = conn.cursor()
            
            sql = """
                INSERT INTO T_SYM_CARGO (nm_cargo, ds_cargo, nivel_risco_ia)
                VALUES (:1, :2, :3)
                RETURNING id_cargo INTO :4
            """
            
            id_gerado_var = cursor.var(int)
            cursor.execute(sql, [nome, descricao, risco_calculado, id_gerado_var])
            novo_id = id_gerado_var.getvalue()[0]
            
            conn.commit()
            print(f"\n[SUCESSO] Cargo '{nome}' adicionado com sucesso (ID: {novo_id}, Risco: {risco_calculado}).")

    except oracledb.Error as e:
        print(f"\n[ERRO]: Ao inserir cargo: {e}")
    except Exception as e:
        print(f"\n[ERRO]: Erro inesperado {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def listar_cargos():
    '''
    Busca e exibe todos os cargos cadastrados no banco de dados.
    '''
    print("\n╔═───────────────────────────────────────────────═╗")
    print("│                     [SYMBIO]                     │")
    print("│           Lista de Cargos Cadastrados            │")
    print("╚═───────────────────────────────────────────────═╝")
    conn = None
    cursor = None
    try:
        conn = getConexao()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_cargo, nm_cargo, nivel_risco_ia FROM T_SYM_CARGO ORDER BY nivel_risco_ia, nm_cargo")
            
            cargos = cursor.fetchall()
            
            if not cargos:
                print("Nenhum cargo encontrado.")
                return

            print(f"{'ID':<6} | {'RISCO':<10} | {'NOME':<30}")
            print("-" * 50)
            for cargo in cargos:
                print(f"{cargo[0]:<6} | {cargo[2]:<10} | {cargo[1]:<30}")

    except oracledb.Error as e:
        print(f"\n[ERRO]: Ao listar cargos: {e}")
    except Exception as e:
        print(f"\n[ERRO]: Erro inesperado {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# Funções de Gestão de Skills
def adicionar_skill():
    '''
    Solicita ao utilizador os dados de uma nova skill e
    a insere no banco de dados.
    '''
    print("\n╔═───────────────────────────────────────────────═╗")
    print("│                     [SYMBIO]                     │")
    print("│               Adicionar Nova Skill               │")
    print("╚═───────────────────────────────────────────────═╝")
    
    # Obter dados da Skill
    nome = input("Nome da Skill (ex: Python Avançado): ")
    tipo = ""
    while tipo not in ['SOFT', 'HARD']:
        tipo = input("Tipo da Skill (SOFT ou HARD): ").upper()
        if tipo not in ['SOFT', 'HARD']:
            print("[ERRO] Tipo inválido. Use 'SOFT' ou 'HARD'.")
            
    descricao = input("Descrição curta da Skill: ")

    if not nome or not tipo:
        print("\n[ERRO] Nome e Tipo são obrigatórios. Operação cancelada.")
        return

    conn = None
    cursor = None
    try:
        # Obter uma nova conexão
        conn = getConexao()
        if conn:
            cursor = conn.cursor()
            
            # Preparar o SQL 
            sql = """
                INSERT INTO T_SYM_SKILL (nm_skill, tp_skill, ds_skill)
                VALUES (:1, :2, :3)
                RETURNING id_skill INTO :4
            """
            
            id_gerado_var = cursor.var(int)
            
            cursor.execute(sql, [nome, tipo, descricao, id_gerado_var])
            
            # Obter o ID gerado
            novo_id = id_gerado_var.getvalue()[0]

            conn.commit()
            print(f"\n[SUCESSO] Skill '{nome}' adicionada com sucesso (ID gerado: {novo_id}).")

    except oracledb.Error as e:
        print(f"\n[ERRO]: Ao inserir skill: {e}")
    except Exception as e:
        print(f"\n[ERRO] Inesperado: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()