# test_api.py
# Migrated from baassimulator
import requests
import json
import os

# --- CONFIGURAÇÕES ---
# URL base da sua API Django (ajuste conforme seu deploy: http://localhost:8000 ou URL do Cloud Run)
BASE_URL = os.getenv("BANK_API_URL", "http://127.0.0.1:8000/api/v1/bank/")

# >>>>> SUBSTITUA ESTE VALOR COM A API KEY REAL <<<<<
API_KEY = "YOUR-API-KEY-HERE" 

HEADERS = {
    "Content-Type": "application/json",
    "X-API-KEY": API_KEY 
}

print(f"--- Iniciando testes da Bank Service API em {BASE_URL} ---")

# --- TESTE 1: CRIAR UMA NOVA CONTA VIA BAAS ---
print("\n--- Teste 1: Criando uma nova conta para o cliente 'João da Silva' ---")
create_account_endpoint = f"{BASE_URL}accounts/"
account_data = {
    "customer_id_at_fintech": "joao-silva-id-001",
    "owner_name": "João da Silva",
    "initial_balance": "500.00"
}

joao_account_number = None

try:
    response = requests.post(create_account_endpoint, headers=HEADERS, data=json.dumps(account_data))
    response.raise_for_status()
    account_response_data = response.json()
    print("Sucesso ao criar conta:")
    print(json.dumps(account_response_data, indent=2))
    joao_account_number = account_response_data.get('account_number')
    print(f"Número da conta de João: {joao_account_number}")

except Exception as err:
    print(f"Erro ao criar conta: {err}")

# --- TESTE 2: LISTAR CONTAS ---
print("\n--- Teste 2: Listando contas ---")
list_accounts_endpoint = f"{BASE_URL}accounts/"

try:
    response = requests.get(list_accounts_endpoint, headers=HEADERS)
    response.raise_for_status()
    accounts_list = response.json()
    print("Sucesso ao listar contas:")
    print(json.dumps(accounts_list, indent=2))

except Exception as err:
    print(f"Erro ao listar contas: {err}")
