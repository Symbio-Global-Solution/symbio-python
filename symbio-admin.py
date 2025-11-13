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

# URL da API de IA (Certifique-se que está no ar no Render)
API_IA_URL = "https://symbio-api-ia.onrender.com"

# --- Funções de Estilização do Terminal ---

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

def pausar_e_limpar():
    '''
    Pausa a execução e limpa o terminal.
    '''
    input("\nPressione Enter para continuar...")
    limpar_terminal()
    titulo_sistema()

# --- Função para o Banco de Dados ---

def getConexao():
    '''
    Estabelece e retorna uma conexão com o banco de dados Oracle.
    '''
    try:
        # [SEGURANÇA] Preencha com suas credenciais
        conn = oracledb.connect(
            user="rm563620",
            password="[SUA_SENHA_AQUI]", 
            host="oracle.fiap.com.br",
            port=1521,
            service_name="ORCL"
        )
        return conn
    except oracledb.Error as e:
        print(
        f"""[ERRO]: Não foi possível conectar ao Oracle: {e}\n
Verifique se:
1. O Oracle Instant Client está instalado e no PATH.
2. A VPN da FIAP está conectada.
3. As credenciais (user, password) estão corretas."""
        )
        return None
    except Exception as e:
        print(f"\n[ERRO]: Ocorreu um erro: {e}")
        return None

def testar_conexao():
    '''
    Tenta conectar ao banco de dados e imprime o status.
    '''
    print("Testando conexão com o Banco de Dados Oracle...")
    
    conn = getConexao()
    
    if conn:
        print(f"Conexão bem-sucedida! \nVersão do Banco de Dados: {conn.version}")
        conn.close()
        return True
    else:
        print("[ERRO]: Falha ao conectar.")
        return False

# --- Funções de Gestão de Cargos ---

def obter_risco_ia(features: list):
    '''
    Chama a API de IA para obter a predição de risco.
    '''
    try:
        url = f"{API_IA_URL}/prever/risco"
        payload = {"features": features}
        
        # [AJUSTE] Timeout aumentado para 20s para aguentar o "cold start" do Render
        response = requests.post(url, json=payload, timeout=20) 
        
        if response.status_code == 200:
            return response.json().get("risco_predito")
        else:
            print(f"[ERRO]: A API de IA teve um erro {response.status_code}: {response.text}")
            return None
            
    except requests.exceptions.ConnectionError:
        print("\n[ERRO DE REDE] Não foi possível conectar à API de IA (Flask).")
        print(f"Verifique se o servidor está rodando em: {API_IA_URL}")
        return None
    except requests.exceptions.ReadTimeout:
        print("\n[ERRO DE TIMEOUT] A API de IA no Render demorou muito para responder (mais de 20s).")
        print("Isto é normal no plano gratuito (Cold Start). Tente novamente em alguns segundos.")
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
    print("│                     [SYMBIO]                     │")
    print("│           Adicionar Novo Cargo com IA            │")
    print("╚═───────────────────────────────────────────────═╝")
    
    # Obter dados do cargo 
    nome = input("Nome do Cargo (ex: Engenheiro de Prompt): ")
    descricao = input("Descrição curta do Cargo: ")
    
    try:
        # Obter as features para a IA
        print("\nAgora, classifique o cargo em porcentagem (0 a 100): ")
        repetitividade = int(input("  % Tarefa Repetitiva (0-100): "))
        criatividade = int(input("  % Exige Criatividade (0-100): "))
        interacao = int(input("  % Interação Humana (0-100): "))
        
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
    Retorna True se houver cargos, False se não houver.
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
                return False # Retorna False se não houver cargos

            print(f"\n{'ID':<6} | {'RISCO':<10} | {'NOME':<30}")
            print("-" * 50)
            for cargo in cargos:
                print(f"{cargo[0]:<6} | {cargo[2]:<10} | {cargo[1]:<30}")
            return True # Retorna True se houver cargos

    except oracledb.Error as e:
        print(f"\n[ERRO]: Ao listar cargos: {e}")
    except Exception as e:
        print(f"\n[ERRO]: Erro inesperado {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return False # Retorna False em caso de erro

def atualizar_cargo():
    '''
    Atualiza um cargo existente no banco de dados.
    '''
    # [AJUSTE 3] Mostra a lista (e o título da lista) primeiro
    if not listar_cargos(): # Mostra os cargos para o usuário escolher
        print("\nNão há cargos para atualizar.")
        return
    
    # [AJUSTE 3] Agora mostra o título da *ação*
    print("\n╔═───────────────────────────────────────────────═╗")
    print("│                     [SYMBIO]                     │")
    print("│                Atualizar Cargo                   │")
    print("╚═───────────────────────────────────────────────═╝")
    
    try:
        id_cargo_att = int(input("\nDigite o ID do cargo que deseja ATUALIZAR (ou 0 para cancelar): "))
        if id_cargo_att == 0:
            print("Operação cancelada.")
            return
    except ValueError:
        print("\n[ERRO]: ID inválido. Deve ser um número.")
        return

    conn = None
    cursor = None
    try:
        conn = getConexao()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Buscar dados antigos
        cursor.execute("SELECT nm_cargo, ds_cargo FROM T_SYM_CARGO WHERE id_cargo = :1", [id_cargo_att])
        cargo_antigo = cursor.fetchone()
        
        if not cargo_antigo:
            print("\n[ERRO]: Cargo não encontrado.")
            return

        print(f"\nAtualizando cargo: {cargo_antigo[0]}")
        nome = input(f"Novo Nome (Deixe em branco para manter '{cargo_antigo[0]}'): ") or cargo_antigo[0]
        descricao = input(f"Nova Descrição (Deixe em branco para manter '{cargo_antigo[1]}'): ") or cargo_antigo[1]
        
        # Atualizar o Risco de IA (obrigatório ao atualizar)
        print("\nÉ necessário reavaliar o risco do cargo:")
        repetitividade = int(input("  % Tarefa Repetitiva (0-100): "))
        criatividade = int(input("  % Exige Criatividade (0-100): "))
        interacao = int(input("  % Interação Humana (0-100): "))
        
        print(f"\nAnalisando cargo com a IA...")
        features_ia = [repetitividade, criatividade, interacao]
        risco_calculado = obter_risco_ia(features_ia)

        if risco_calculado is None:
            print("Não foi possível calcular o risco. A atualização NÃO será salva.")
            return
        
        print(f"IA calculou o novo risco como: {risco_calculado}")

        # Executar Update
        sql = """
            UPDATE T_SYM_CARGO
            SET nm_cargo = :1, ds_cargo = :2, nivel_risco_ia = :3
            WHERE id_cargo = :4
        """
        cursor.execute(sql, [nome, descricao, risco_calculado, id_cargo_att])
        conn.commit()
        
        print(f"\n[SUCESSO] Cargo ID {id_cargo_att} atualizado com sucesso!")

    except oracledb.Error as e:
        print(f"\n[ERRO]: Ao atualizar cargo: {e}")
    except ValueError:
        print("\n[ERRO]: Valores inválidos. As percentagens devem ser números.")
    except Exception as e:
        print(f"\n[ERRO]: Erro inesperado {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def apagar_cargo():
    '''
    Apaga um cargo existente no banco de dados.
    '''
    # [AJUSTE 3] Mostra a lista (e o título da lista) primeiro
    if not listar_cargos():
        print("\nNão há cargos para apagar.")
        return
    
    # [AJUSTE 3] Agora mostra o título da *ação*
    print("\n╔═───────────────────────────────────────────────═╗")
    print("│                     [SYMBIO]                     │")
    print("│                   Apagar Cargo                   │")
    print("╚═───────────────────────────────────────────────═╝")
    
    try:
        id_cargo_del = int(input("\nDigite o ID do cargo que deseja APAGAR (ou 0 para cancelar): "))
        if id_cargo_del == 0:
            print("Operação cancelada.")
            return
    except ValueError:
        print("\n[ERRO]: ID inválido. Deve ser um número.")
        return

    conn = None
    cursor = None
    try:
        conn = getConexao()
        if not conn:
            return
            
        cursor = conn.cursor()
        
        # [AJUSTE 1] Confirmação removida.
        
        # Executar Delete
        cursor.execute("DELETE FROM T_SYM_CARGO WHERE id_cargo = :1", [id_cargo_del])
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"\n[SUCESSO] Cargo ID {id_cargo_del} apagado com sucesso!")
        else:
            print("\n[AVISO] Nenhum cargo foi apagado (ID não encontrado).")

    except oracledb.Error as e:
        # Erro ORA-02292: child record found (Foreign Key)
        if 'ORA-02292' in str(e):
            print("\n[ERRO]: Este cargo não pode ser apagado pois está sendo usado por colaboradores.")
            print("Primeiro, realoque os colaboradores para outros cargos.")
        else:
            print(f"\n[ERRO]: Ao apagar cargo: {e}")
    except Exception as e:
        print(f"\n[ERRO]: Erro inesperado {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Funções de Gestão de Skills ---

def adicionar_skill():
    '''
    Solicita ao administrador os dados de uma nova skill e
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
        conn = getConexao()
        if conn:
            cursor = conn.cursor()
            
            sql = """
                INSERT INTO T_SYM_SKILL (nm_skill, tp_skill, ds_skill)
                VALUES (:1, :2, :3)
                RETURNING id_skill INTO :4
            """
            
            id_gerado_var = cursor.var(int)
            
            cursor.execute(sql, [nome, tipo, descricao, id_gerado_var])
            
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

def listar_skills():
    '''
    Busca e exibe todas as skills cadastradas no banco de dados.
    Retorna True se houver skills, False se não houver.
    '''
    print("\n╔═───────────────────────────────────────────────═╗")
    # Corrigido SYMBBIO -> SYMBIO
    print("│                     [SYMBIO]                     │") 
    print("│           Lista de Skills Cadastradas            │")
    print("╚═───────────────────────────────────────────────═╝")
    conn = None
    cursor = None
    try:
        conn = getConexao()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id_skill, nm_skill, tp_skill FROM T_SYM_SKILL ORDER BY tp_skill, nm_skill")
            
            skills = cursor.fetchall()
            
            if not skills:
                print("Nenhuma skill encontrada.")
                return False # Retorna False se não houver skills

            print(f"\n{'ID':<6} | {'TIPO':<10} | {'NOME':<30}")
            print("-" * 50)
            for skill in skills:
                print(f"{skill[0]:<6} | {skill[2]:<10} | {skill[1]:<30}")
            return True # Retorna True se houver skills

    except oracledb.Error as e:
        print(f"\n[ERRO DE BANCO DE DADOS] ao listar Skills: {e}")
    except Exception as e:
        print(f"\n[ERRO INESPERADO]: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
    return False # Retorna False em caso de erro

def atualizar_skill():
    '''
    Atualiza uma skill existente no banco de dados.
    '''
    # [AJUSTE] Mostra lista primeiro
    if not listar_skills():
        print("\nNão há skills para atualizar.")
        return
    
    # [AJUSTE] Título depois
    print("\n╔═───────────────────────────────────────────────═╗")
    print("│                     [SYMBIO]                     │")
    print("│                 Atualizar Skill                  │")
    print("╚═───────────────────────────────────────────────═╝")
    
    try:
        id_skill_att = int(input("\nDigite o ID da skill que deseja ATUALIZAR (ou 0 para cancelar): "))
        if id_skill_att == 0:
            print("Operação cancelada.")
            return
    except ValueError:
        print("\n[ERRO]: ID inválido. Deve ser um número.")
        return

    conn = None
    cursor = None
    try:
        conn = getConexao()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # Buscar dados antigos
        cursor.execute("SELECT nm_skill, tp_skill, ds_skill FROM T_SYM_SKILL WHERE id_skill = :1", [id_skill_att])
        skill_antiga = cursor.fetchone()
        
        if not skill_antiga:
            print("\n[ERRO]: Skill não encontrada.")
            return

        print(f"\nAtualizando skill: {skill_antiga[0]}")
        nome = input(f"Novo Nome (Deixe em branco para manter '{skill_antiga[0]}'): ") or skill_antiga[0]
        
        tipo = ""
        while tipo not in ['SOFT', 'HARD', '']:
            tipo = input(f"Novo Tipo (SOFT ou HARD) (Deixe em branco para manter '{skill_antiga[1]}'): ").upper()
            if tipo not in ['SOFT', 'HARD', '']:
                print("[ERRO] Tipo inválido. Use 'SOFT', 'HARD' ou deixe em branco.")
        if tipo == '':
            tipo = skill_antiga[1]
            
        descricao = input(f"Nova Descrição (Deixe em branco para manter '{skill_antiga[2]}'): ") or skill_antiga[2]
        
        # Executar Update
        sql = """
            UPDATE T_SYM_SKILL
            SET nm_skill = :1, tp_skill = :2, ds_skill = :3
            WHERE id_skill = :4
        """
        cursor.execute(sql, [nome, tipo, descricao, id_skill_att])
        conn.commit()
        
        print(f"\n[SUCESSO] Skill ID {id_skill_att} atualizada com sucesso!")

    except oracledb.Error as e:
        print(f"\n[ERRO]: Ao atualizar skill: {e}")
    except Exception as e:
        print(f"\n[ERRO]: Erro inesperado {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def apagar_skill():
    '''
    Apaga uma skill existente no banco de dados.
    '''
    # [AJUSTE] Mostra lista primeiro
    if not listar_skills():
        print("\nNão há skills para apagar.")
        return
    
    # [AJUSTE] Título depois
    print("\n╔═───────────────────────────────────────────────═╗")
    print("│                     [SYMBIO]                     │")
    print("│                   Apagar Skill                   │")
    print("╚═───────────────────────────────────────────────═╝")
    
    try:
        id_skill_del = int(input("\nDigite o ID da skill que deseja APAGAR (ou 0 para cancelar): "))
        if id_skill_del == 0:
            print("Operação cancelada.")
            return
    except ValueError:
        print("\n[ERRO]: ID inválido. Deve ser um número.")
        return

    conn = None
    cursor = None
    try:
        conn = getConexao()
        if not conn:
            return
            
        cursor = conn.cursor()
        
        # [AJUSTE 1] Confirmação removida (delete direto)

        # Executar Delete
        cursor.execute("DELETE FROM T_SYM_SKILL WHERE id_skill = :1", [id_skill_del])
        conn.commit()
        
        if cursor.rowcount > 0:
            print(f"\n[SUCESSO] Skill ID {id_skill_del} apagada com sucesso!")
        else:
            print("\n[AVISO] Nenhuma skill foi apagada (ID não encontrado).")

    except oracledb.Error as e:
        if 'ORA-02292' in str(e):
            print("\n[ERRO]: Esta skill não pode ser apagada pois está em uso por um colaborador ou vaga.")
        else:
            print(f"\n[ERRO]: Ao apagar skill: {e}")
    except Exception as e:
        print(f"\n[ERRO]: Erro inesperado {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Funções de Exportação ---

def json_converter(o):
    '''
    Converte tipos de dados não serializáveis (como data) para JSON.
    '''
    if isinstance(o, datetime.datetime) or isinstance(o, datetime.date):
        return o.isoformat()

def exportar_relatorios_json():
    '''
    Executa 3 consultas diferentes e exporta os resultados para arquivos JSON.
    '''
    print("\n╔═───────────────────────────────────────────────═╗")
    print("│                     [SYMBIO]                     │")
    print("│            Exportar Relatórios JSON              │")
    print("╚═───────────────────────────────────────────────═╝")
    
    conn = None
    cursor = None
    try:
        conn = getConexao()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # [AJUSTE 2] Mensagem única de processamento
        print("\nProcessando relatórios...") 

        # --- Consulta 1: Cargos em Alto Risco ---
        sql1 = """
            SELECT C.nm_colaborador, CG.nm_cargo, CG.nivel_risco_ia
            FROM T_SYM_COLABORADOR C
            INNER JOIN T_SYM_CARGO CG ON C.id_cargo = CG.id_cargo
            WHERE CG.nivel_risco_ia = 'ALTO'
            ORDER BY C.nm_colaborador
        """
        cursor.execute(sql1)
        colunas = [col[0].lower() for col in cursor.description]
        resultado1 = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        
        with open('export_1_cargos_alto_risco.json', 'w', encoding='utf-8') as f:
            json.dump(resultado1, f, ensure_ascii=False, indent=4, default=json_converter)
        

        # --- Consulta 2: Contagem de funcionários por Risco ---
        sql2 = """
            SELECT CG.nivel_risco_ia, COUNT(C.id_colaborador) AS total_funcionarios
            FROM T_SYM_CARGO CG
            LEFT JOIN T_SYM_COLABORADOR C ON CG.id_cargo = C.id_cargo
            GROUP BY CG.nivel_risco_ia
            ORDER BY total_funcionarios DESC
        """
        cursor.execute(sql2)
        colunas = [col[0].lower() for col in cursor.description]
        resultado2 = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        
        with open('export_2_contagem_por_risco.json', 'w', encoding='utf-8') as f:
            json.dump(resultado2, f, ensure_ascii=False, indent=4, default=json_converter)
        
        
        # --- Consulta 3: Lista de Skills por Tipo ---
        sql3 = "SELECT tp_skill, nm_skill, ds_skill FROM T_SYM_SKILL ORDER BY tp_skill, nm_skill"
        cursor.execute(sql3)
        colunas = [col[0].lower() for col in cursor.description]
        resultado3 = [dict(zip(colunas, row)) for row in cursor.fetchall()]
        
        with open('export_3_lista_de_skills.json', 'w', encoding='utf-8') as f:
            json.dump(resultado3, f, ensure_ascii=False, indent=4, default=json_converter)
        
        
        # [AJUSTE 2] Mensagem de confirmação única no final
        print("\n[SUCESSO] 3 relatórios JSON foram gerados com sucesso:")
        print("  - export_1_cargos_alto_risco.json")
        print("  - export_2_contagem_por_risco.json")
        print("  - export_3_lista_de_skills.json")

    except oracledb.Error as e:
        print(f"\n[ERRO DE BANCO DE DADOS] ao exportar JSON: {e}")
    except Exception as e:
        print(f"\n[ERRO INESPERADO]: {e}")
    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

# --- Funções de Menu ---

def menu_cargos():
    '''
    Menu de Gerenciamento de Cargos.
    '''
    while True:
        limpar_terminal()
        titulo_sistema()
        print(f"\nGestão de Cargos\n")
        print("1. Adicionar Novo Cargo (com IA)")
        print("2. Listar Cargos")
        print("3. Atualizar Cargo (com IA)")
        print("4. Apagar Cargo")
        print("0. Voltar ao Menu Principal")
        
        escolha = input("Digite a sua opção: ")
        
        if escolha == '1':
            adicionar_cargo()
            pausar_e_limpar()
        elif escolha == '2':
            listar_cargos()
            pausar_e_limpar()
        elif escolha == '3':
            atualizar_cargo()
            pausar_e_limpar()
        elif escolha == '4':
            apagar_cargo()
            pausar_e_limpar()
        elif escolha == '0':
            print("Voltando ao menu principal...")
            break # Sai do loop e volta ao menu_principal
        else:
            print("\n[ERRO] Opção inválida.")
            pausar_e_limpar()


def menu_skills():
    '''
    Menu de Gerenciamento de Skills.
    '''
    while True:
        limpar_terminal()
        titulo_sistema()
        print("\n--- Gestão de Skills ---")
        print("1. Adicionar Nova Skill")
        print("2. Listar Skills")
        print("3. Atualizar Skill")
        print("4. Apagar Skill")
        print("0. Voltar ao Menu Principal") # Padronizado para '0'
        
        escolha = input("Digite a sua opção: ")
        
        if escolha == '1':
            adicionar_skill()
            pausar_e_limpar()
        elif escolha == '2':
            listar_skills()
            pausar_e_limpar()
        elif escolha == '3':
            atualizar_skill()
            pausar_e_limpar()
        elif escolha == '4': # Corrigido de '4S' para '4'
            apagar_skill()
            pausar_e_limpar()
        elif escolha == '0': # Corrigido de '9' para '0'
            print("Voltando ao menu principal...")
            break # Sai do loop e volta ao menu_principal
        else:
            print("\n[ERRO] Opção inválida.")
            pausar_e_limpar()

def menu_principal():
    '''
    Exibe o menu principal interativo para o utilizador.
    '''
    limpar_terminal()
    titulo_sistema()
    
    while True:
        print(f"\nMenu de Opções\n")
        print("1. Gerenciar Cargos")
        print("2. Gerenciar Skills")
        print("3. Exportar Relatórios (JSON)")
        print("0. Sair")
        
        escolha = input("Digite a sua opção: ")
        
        if escolha == '1':
            menu_cargos()
            # Quando o menu_cargos() terminar (break), limpa e remostra o título
            limpar_terminal() 
            titulo_sistema()  
        elif escolha == '2':
            menu_skills()
            # Quando o menu_skills() terminar (break), limpa e remostra o título
            limpar_terminal() 
            titulo_sistema()  
        elif escolha == '3':
            exportar_relatorios_json()
            pausar_e_limpar()
        elif escolha == '0':
            limpar_terminal()
            print("Encerrando programa...")
            break
        else:
            print("\n[ERRO] Opção inválida. Por favor, tente novamente.")
            pausar_e_limpar()

# --- Ponto de Entrada Principal ---

if __name__ == "__main__":
    if testar_conexao(): # Testa a conexão antes de iniciar o menu
        pausar_e_limpar()
        menu_principal()
    else:
        print("\n[ERRO FATAL] Não foi possível iniciar o sistema. Verifique a conexão com o banco.")
        input("Pressione Enter para sair...")