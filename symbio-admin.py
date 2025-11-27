'''
Global Solution - Computational Thinking Using Python
1TDSPF - Henrique Martins - RM563620
1TDSPF - Henrique Teixeira - RM563088

[SYMBIO] Sistema Administrativo.
Ferramenta administrativa para gestão de Cargos e Skills no banco de dados Oracle.
Inclui integração via API REST para cálculo de risco de automação com IA.
'''

# Importação dos Módulos
import oracledb
import os
import requests
import json
import datetime

# URL da API de IA
API_IA_URL = "https://symbio-api-ia.onrender.com"

# --- UTILITÁRIOS DE SISTEMA ---
def limpar_terminal():
    ''' Detecta o sistema operacional e limpa a tela corretamente '''
    os.system('cls' if os.name == 'nt' else 'clear')

def titulo_sistema():
    ''' Renderiza o cabeçalho ASCII art do sistema '''
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

def pausar_e_limpar():
    ''' Cria uma pausa na execução para leitura do usuário antes de limpar '''
    input("\nPressione Enter para continuar...")
    limpar_terminal()
    titulo_sistema()

# --- CAMADA DE CONEXÃO ---
def get_conexao():
    ''' Estabelece conexão com Oracle retornando objeto de conexão ou None em caso de falha '''
    try:
        conn = oracledb.connect(
            user="rm563620",
            password="200207", 
            host="oracle.fiap.com.br",
            port=1521,
            service_name="ORCL"
        )
        return conn
    except oracledb.Error as e:
        print(f"[ERRO CRÍTICO]: Falha na conexão Oracle: {e}")
        return None
    except Exception as e:
        print(f"[ERRO]: Ocorreu um erro genérico na conexão: {e}")
        return None

def testar_conexao_inicial():
    ''' Verifica a saúde do banco na inicialização do script '''
    print("Verificando disponibilidade do Banco de Dados Oracle...")
    conn = get_conexao()
    if conn:
        print(f"Conexão estabelecida com sucesso! Versão: {conn.version}")
        conn.close()
        return True
    else:
        print("[ERRO]: Não foi possível conectar ao banco de dados.")
        return False

# --- CAMADA DE REGRA DE NEGÓCIO ---
def servico_obter_risco_ia(features: list) -> str:
    ''' Consome a API externa para calcular risco baseado nas features fornecidas
    Retorna a string do risco ou None se houver falha'''
    try:
        url = f"{API_IA_URL}/prever/risco"
        payload = {"features": features}
        
        response = requests.post(url, json=payload, timeout=10) 
        
        if response.status_code == 200:
            return response.json().get("risco_predito")
        else:
            return None
            
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        return None
    except Exception:
        return None

# --- CAMADA DE PERSISTÊNCIA ---

def dao_inserir_cargo(nome, descricao, risco_ia):
    ''' Insere um novo cargo e retorna o ID gerado ou lança exceção '''
    conn = get_conexao()
    if not conn: return None

    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO T_SYM_CARGO (nm_cargo, ds_cargo, nivel_risco_ia)
            VALUES (:1, :2, :3)
            RETURNING id_cargo INTO :4
        """
        id_gerado = cursor.var(int)
        cursor.execute(sql, [nome, descricao, risco_ia, id_gerado])
        novo_id = id_gerado.getvalue()[0]
        conn.commit()
        return novo_id
    except oracledb.Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def dao_listar_cargos():
    ''' Retorna uma lista de dicionários com todos os cargos '''
    conn = get_conexao()
    if not conn: return []

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_cargo, nm_cargo, nivel_risco_ia, ds_cargo FROM T_SYM_CARGO ORDER BY nm_cargo")
        rows = cursor.fetchall()
        cargos = [
            {"id": row[0], "nome": row[1], "risco": row[2], "desc": row[3]} 
            for row in rows
        ]
        return cargos
    finally:
        cursor.close()
        conn.close()

def dao_buscar_cargo_por_id(id_cargo):
    ''' Retorna os dados de um único cargo ou None '''
    conn = get_conexao()
    if not conn: return None

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nm_cargo, ds_cargo, nivel_risco_ia FROM T_SYM_CARGO WHERE id_cargo = :1", [id_cargo])
        row = cursor.fetchone()
        if row:
            return {"nome": row[0], "desc": row[1], "risco": row[2]}
        return None
    finally:
        cursor.close()
        conn.close()

def dao_atualizar_cargo(id_cargo, nome, descricao, risco):
    ''' Atualiza registro e retorna True se afetou alguma linha '''
    conn = get_conexao()
    if not conn: return False

    cursor = conn.cursor()
    try:
        sql = """
            UPDATE T_SYM_CARGO 
            SET nm_cargo = :1, ds_cargo = :2, nivel_risco_ia = :3
            WHERE id_cargo = :4
        """
        cursor.execute(sql, [nome, descricao, risco, id_cargo])
        conn.commit()
        return cursor.rowcount > 0
    except oracledb.Error:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def dao_apagar_cargo(id_cargo):
    ''' Remove cargo e trata integridade referencial '''
    conn = get_conexao()
    if not conn: return False

    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM T_SYM_CARGO WHERE id_cargo = :1", [id_cargo])
        conn.commit()
        return cursor.rowcount > 0
    except oracledb.Error as e:
        if 'ORA-02292' in str(e):
            raise ValueError("Integridade Referencial")
        raise e
    finally:
        cursor.close()
        conn.close()

# --- CAMADA DE PERSISTÊNCIA ---

def dao_inserir_skill(nome, tipo, descricao):
    conn = get_conexao()
    if not conn: return None

    cursor = conn.cursor()
    try:
        sql = """
            INSERT INTO T_SYM_SKILL (nm_skill, tp_skill, ds_skill)
            VALUES (:1, :2, :3)
            RETURNING id_skill INTO :4
        """
        id_gerado = cursor.var(int)
        cursor.execute(sql, [nome, tipo, descricao, id_gerado])
        novo_id = id_gerado.getvalue()[0]
        conn.commit()
        return novo_id
    except oracledb.Error as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def dao_listar_skills():
    ''' Busca todas as skills retornando lista estruturada '''
    conn = get_conexao()
    if not conn: return []

    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id_skill, nm_skill, tp_skill, ds_skill FROM T_SYM_SKILL ORDER BY tp_skill, nm_skill")
        return [{"id": r[0], "nome": r[1], "tipo": r[2], "desc": r[3]} for r in cursor.fetchall()]
    finally:
        cursor.close()
        conn.close()

def dao_buscar_skill_por_id(id_skill):
    ''' Busca skill específica pelo ID '''
    conn = get_conexao()
    if not conn: return None
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nm_skill, tp_skill, ds_skill FROM T_SYM_SKILL WHERE id_skill = :1", [id_skill])
        row = cursor.fetchone()
        return {"nome": row[0], "tipo": row[1], "desc": row[2]} if row else None
    finally:
        cursor.close()
        conn.close()

def dao_atualizar_skill(id_skill, nome, tipo, descricao):
    ''' Atualiza dados da skill '''
    conn = get_conexao()
    if not conn: return False
    cursor = conn.cursor()
    try:
        sql = "UPDATE T_SYM_SKILL SET nm_skill = :1, tp_skill = :2, ds_skill = :3 WHERE id_skill = :4"
        cursor.execute(sql, [nome, tipo, descricao, id_skill])
        conn.commit()
        return cursor.rowcount > 0
    except Exception:
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def dao_apagar_skill(id_skill):
    ''' Remove skill do banco '''
    conn = get_conexao()
    if not conn: return False
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM T_SYM_SKILL WHERE id_skill = :1", [id_skill])
        conn.commit()
        return cursor.rowcount > 0
    except oracledb.Error as e:
        if 'ORA-02292' in str(e): raise ValueError("Integridade Referencial")
        raise e
    finally:
        cursor.close()
        conn.close()

# --- CAMADA DE INTERFACE ---

def ui_adicionar_cargo():
    print("\n--- Adicionar Novo Cargo ---")
    nome = input("Nome do Cargo: ")
    descricao = input("Descrição curta: ")
    
    # Validação simples de entrada
    if not nome:
        print("[AVISO] Nome é obrigatório.")
        return

    try:
        print("\nDefinição de parâmetros para Análise de IA (0-100%):")
        rep = int(input("Nível de Repetitividade: "))
        cri = int(input("Exigência de Criatividade: "))
        hum = int(input("Interação Humana: "))
        
        if not (0 <= rep <= 100 and 0 <= cri <= 100 and 0 <= hum <= 100):
            print("[ERRO] Valores devem ser entre 0 e 100.")
            return

        print("Consultando API de IA...")
        risco = servico_obter_risco_ia([rep, cri, hum])
        
        if risco is None:
            print("[ERRO] Falha na comunicação com a IA. Cadastro abortado.")
            return
            
        print(f"Risco calculado pela IA: {risco}")
        
        novo_id = dao_inserir_cargo(nome, descricao, risco)
        if novo_id:
            print(f"Sucesso! Cargo cadastrado com ID: {novo_id}")
            
    except ValueError:
        print("[ERRO] Entrada inválida. Use apenas números inteiros.")
    except Exception as e:
        print(f"[ERRO] Falha ao salvar: {e}")

def ui_listar_cargos():
    print("\n--- Lista de Cargos ---")
    lista = dao_listar_cargos()
    
    if not lista:
        print("Nenhum cargo encontrado.")
        return False
        
    print(f"{'ID':<5} | {'RISCO':<10} | {'NOME':<30}")
    print("-" * 50)
    for c in lista:
        print(f"{c['id']:<5} | {c['risco']:<10} | {c['nome']:<30}")
    return True

def ui_atualizar_cargo():
    if not ui_listar_cargos(): return
    
    try:
        id_target = int(input("\nID do cargo para atualizar (0 cancela): "))
        if id_target == 0: return
        
        dados_antigos = dao_buscar_cargo_por_id(id_target)
        if not dados_antigos:
            print("[ERRO] Cargo não encontrado.")
            return
            
        print(f"Editando: {dados_antigos['nome']}")
        novo_nome = input(f"Novo Nome [{dados_antigos['nome']}]: ") or dados_antigos['nome']
        nova_desc = input(f"Nova Desc [{dados_antigos['desc']}]: ") or dados_antigos['desc']
        
        print("Recalcular Risco IA (Necessário redigitar parâmetros):")
        rep = int(input("Repetitividade (0-100): "))
        cri = int(input("Criatividade (0-100): "))
        hum = int(input("Interação Humana (0-100): "))
        
        novo_risco = servico_obter_risco_ia([rep, cri, hum])
        if not novo_risco:
            print("Erro na IA. Operação cancelada.")
            return
            
        sucesso = dao_atualizar_cargo(id_target, novo_nome, nova_desc, novo_risco)
        if sucesso:
            print("Cargo atualizado com sucesso!")
        else:
            print("Erro ao atualizar.")
            
    except ValueError:
        print("[ERRO] Digite um ID válido.")

def ui_apagar_cargo():
    if not ui_listar_cargos(): return
    try:
        id_del = int(input("\nID do cargo para apagar (0 cancela): "))
        if id_del == 0: return
        
        if dao_apagar_cargo(id_del):
            print("Cargo removido com sucesso.")
        else:
            print("Cargo não encontrado.")
            
    except ValueError as e:
        if str(e) == "Integridade Referencial":
            print("[ERRO] Não é possível apagar: Cargo em uso por colaboradores.")
        else:
            print("[ERRO] ID Inválido.")

# --- UI FUNÇÕES SKILLS  ---

def ui_adicionar_skill():
    print("\n--- Adicionar Skill ---")
    nome = input("Nome: ")
    tipo = input("Tipo (HARD/SOFT): ").upper()
    desc = input("Descrição: ")
    
    if tipo not in ['HARD', 'SOFT']:
        print("Tipo inválido.")
        return
        
    try:
        nid = dao_inserir_skill(nome, tipo, desc)
        print(f"Skill criada com ID: {nid}")
    except Exception as e:
        print(f"Erro ao inserir: {e}")

def ui_listar_skills():
    lista = dao_listar_skills()
    if not lista:
        print("Nenhuma skill cadastrada.")
        return False
        
    print(f"\n{'ID':<5} | {'TIPO':<6} | {'NOME'}")
    print("-" * 40)
    for s in lista:
        print(f"{s['id']:<5} | {s['tipo']:<6} | {s['nome']}")
    return True

def ui_atualizar_skill():
    if not ui_listar_skills(): return
    try:
        tid = int(input("\nID para atualizar: "))
        antiga = dao_buscar_skill_por_id(tid)
        if not antiga:
            print("Skill não encontrada.")
            return
            
        nm = input(f"Nome [{antiga['nome']}]: ") or antiga['nome']
        tp = input(f"Tipo [{antiga['tipo']}]: ").upper() or antiga['tipo']
        ds = input(f"Desc [{antiga['desc']}]: ") or antiga['desc']
        
        if dao_atualizar_skill(tid, nm, tp, ds):
            print("Skill atualizada.")
    except ValueError:
        print("ID Inválido.")

def ui_apagar_skill():
    if not ui_listar_skills(): return
    try:
        tid = int(input("\nID para apagar: "))
        if dao_apagar_skill(tid):
            print("Skill apagada.")
        else:
            print("Skill não encontrada.")
    except ValueError as e:
        if str(e) == "Integridade Referencial":
            print("Skill em uso, não pode apagar.")
        else:
            print("Entrada inválida.")

# --- EXPORTAÇÃO JSON ---
def json_converter(o):
    ''' Helper para converter objetos datetime em string para o JSON '''
    if isinstance(o, (datetime.date, datetime.datetime)):
        return o.isoformat()

def exportar_relatorios():
    print("\nGerando relatórios JSON...")
    conn = get_conexao()
    if not conn: return
    
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT nm_cargo, nivel_risco_ia FROM T_SYM_CARGO WHERE nivel_risco_ia = 'ALTO'")
        dados = [dict(zip([d[0].lower() for d in cursor.description], row)) for row in cursor.fetchall()]
        
        with open('relatorio_risco_alto.json', 'w', encoding='utf-8') as f:
            json.dump(dados, f, indent=4, ensure_ascii=False)
            
        print("Relatório 'relatorio_risco_alto.json' gerado com sucesso.")
        
    except Exception as e:
        print(f"Erro na exportação: {e}")
    finally:
        cursor.close()
        conn.close()

# --- MENUS ---
def exibir_menu_cargos():
    while True:
        limpar_terminal()
        titulo_sistema()
        print("\n[GESTÃO DE CARGOS]")
        print("1. Adicionar | 2. Listar | 3. Atualizar | 4. Apagar | 0. Voltar")
        op = input("Opção: ")
        
        if op == '1': ui_adicionar_cargo()
        elif op == '2': ui_listar_cargos()
        elif op == '3': ui_atualizar_cargo()
        elif op == '4': ui_apagar_cargo()
        elif op == '0': break
        else: print("Opção inválida.")
        
        if op != '0': pausar_e_limpar()

def exibir_menu_skills():
    while True:
        limpar_terminal()
        titulo_sistema()
        print("\n[GESTÃO DE SKILLS]")
        print("1. Adicionar | 2. Listar | 3. Atualizar | 4. Apagar | 0. Voltar")
        op = input("Opção: ")
        
        if op == '1': ui_adicionar_skill()
        elif op == '2': ui_listar_skills()
        elif op == '3': ui_atualizar_skill()
        elif op == '4': ui_apagar_skill()
        elif op == '0': break
        else: print("Opção inválida.")
        
        if op != '0': pausar_e_limpar()

def main():
    if not testar_conexao_inicial():
        return

    while True:
        limpar_terminal()
        titulo_sistema()
        print("\n[MENU PRINCIPAL]")
        print("1. Cargos")
        print("2. Skills")
        print("3. Exportar Relatórios")
        print("0. Sair")
        
        escolha = input(">> ")
        
        if escolha == '1': exibir_menu_cargos()
        elif escolha == '2': exibir_menu_skills()
        elif escolha == '3': 
            exportar_relatorios()
            pausar_e_limpar()
        elif escolha == '0':
            print("Encerrando sistema...")
            break
        else:
            print("Opção inválida.")
            pausar_e_limpar()

if __name__ == "__main__":
    main()