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
