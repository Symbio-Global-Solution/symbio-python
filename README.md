# 🐍 Symbio - Painel Administrativo em Python

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)
![Code Style: Black](https://img.shields.io/badge/code%20style-black-000000.svg)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)

Uma CLI (Command-Line Interface) robusta para o backend administrativo da plataforma **SYMBIO**. Esta ferramenta fornece um terminal interativo e seguro para gerir dados mestres (Cargos e Skills) na base de dados Oracle, integrando-se diretamente com o microserviço de IA para análise preditiva de risco.

Este projeto foi desenvolvido como parte da **Global Solution 2025 da FIAP**, focada no "Futuro do Trabalho".

---

## 🚀 Funcionalidades Principais (Key Features)

* **🤖 Criação de Cargos com IA:** Ao adicionar um novo cargo, o administrador **não precisa de adivinhar** o risco de automação.
    * O sistema solicita métricas-chave do cargo (Repetitividade, Criatividade, Interação).
    * A CLI consome a **API de IA (Flask/Render)** em tempo real.
    * A IA analisa os dados e retorna o risco (`ALTO`, `MEDIO`, `BAIXO`) automaticamente.
    * O cargo é gravado no Oracle já classificado.

* **🛠️ Gestão de Ciclo de Vida (CRUD):**
    * Operações completas de Adicionar, Listar, Atualizar e Apagar para **Cargos** e **Skills**.
    * A atualização de cargos aciona uma reavaliação automática da IA.

* **🛡️ Tratamento Robusto de Erros:**
    * **Banco de Dados:** Captura erros de constraint (ex: `ORA-02292`) para impedir a exclusão de dados em uso (ex: apagar um cargo que ainda tem colaboradores).
    * **API:** Valida o *timeout* da API de IA (essencial para "cold starts" em serviços gratuitos) e falhas de conexão, impedindo o registo de dados incompletos.
    * **Input:** Valida os inputs do utilizador para garantir que os tipos de dados (números, strings) estão corretos.

* **📊 Geração de Relatórios JSON:**
    * Exportação automatizada de 3 relatórios estratégicos para ficheiros `.json`, prontos para análise de dados ou integração com outras ferramentas.

---

## ⚙️ Arquitetura e Stack Tecnológica

Esta CLI é um dos micro-componentes do ecossistema SYMBIO. A sua função é ser a ferramenta de administração de "Nível 0" (data mastering), comunicando-se diretamente com os serviços centrais.

* **Stack Tecnológica:**
    * **`Python 3.10+`**
    * **`oracledb`**: Driver oficial para conectividade de alta performance com o Oracle DB.
    * **`requests`**: Biblioteca padrão para consumo de APIs REST.

* **Fluxo de Dados (Integração):**
    1.  `[Esta CLI]  <--> [Banco de Dados Oracle]` (Para operações CRUD)
    2.  `[Esta CLI]  --->  [API de IA (Flask @ Render)]` (Apenas para `obter_risco_ia`)

---

## 🚀 Começar (Getting Started)

### Pré-requisitos
Para executar este projeto, o seu ambiente precisa de:
1.  **Python 3.10 ou superior.**
2.  **Oracle Instant Client:** A biblioteca `oracledb` requer o Instant Client da Oracle.
    * *Download:* [Oracle Instant Client Downloads](https://www.oracle.com/database/technologies/instant-client/downloads.html)
    * *Instalação:* Descomprima e adicione a pasta ao `PATH` do seu sistema operativo.
3.  **Acesso à Rede:** É necessária uma ligação para aceder ao host `oracle.fiap.com.br`.
4.  **API de IA Online:** A funcionalidade de "Adicionar Cargo" (Opção 1) requer que a nossa API de IA esteja em execução em `https://symbio-api-ia.onrender.com`.

### Instalação
1.  Clone este repositório:
    ```bash
    git clone [https://github.com/Symbio-Global-Solution/symbio-cli-python.git](https://github.com/Symbio-Global-Solution/symbio-cli-python.git)
    cd symbio-cli-python
    ```
2.  (Recomendado) Crie e ative um ambiente virtual:
    ```bash
    python -m venv venv
    .\venv\Scripts\activate  # Windows
    # source venv/bin/activate  # macOS/Linux
    ```
3.  Instale as dependências:
    ```bash
    pip install -r requirements.txt
    ```

### Configuração
As credenciais da base de dados (utilizador/palavra-passe) estão localizadas na função `getConexao()` dentro do `symbio_admin_cli.py`.

```python
# symbio_admin_cli.py
```
...
conn = oracledb.connect(
    user="[SEU_RM_AQUI]",
    password="[SUA_SENHA_AQUI]",
...

---
## 🧪 Como Usar e Testar

Execute o script principal para iniciar o menu interativo:
```bash
python symbio_admin_cli.py
```

### Guia Rápido de Teste (Demonstração para Avaliadores)

Para verificar a funcionalidade principal de IA, siga este fluxo:

1. Execute o script.
2. Selecione a Opção 1 (Gerir Cargos).
3. Selecione a Opção 1 (Adicionar Novo Cargo com IA).
4. Preencha o nome (ex: Engenheiro de Prompt).
5. O sistema pedirá 3 percentagens (0-100).

**Cenário de Teste: Risco ALTO**
- Repetitividade: 90
- Criatividade: 10
- Interação: 20
**Resultado Esperado**: O script irá pausar, mostrar Analisando cargo com a IA... e, após a resposta da API, imprimirá IA calculou o risco como: ALTO, salvando-o no banco.

**Cenário de Teste: Risco BAIXO**
- Repetitividade: 10
- Criatividade: 90
- Interação: 80
**Resultado Esperado:** A IA definirá o risco como BAIXO.

**Nota de Performance:** A API de IA está hospedada no plano gratuito do Render. A primeira requisição do dia pode demorar 15-20 segundos devido ao "cold start" (o servidor a "acordar"). O script está configurado com um timeout de 20 segundos para lidar com isto. As requisições seguintes serão instantâneas.

---

## 🧑‍💻 Autores
Este projeto foi idealizado e desenvolvido por:

- Henrique Martins (RM563620)
GitHub | LinkedIn
- Henrique Teixeira (RM563088)
GitHub | LinkedIn

---

## 📄 Licença
Este projeto é distribuído sob a Licença MIT. Veja o ficheiro LICENSE para mais detalhes.
Copyright (c) 2025 Symbio.
