import requests

CHAVE = '31a2db94bb9f359dc818f1ff0fd3e582'

print("📡 Enviando sinal para a API-Football...")

# Testando as duas rotas oficiais ao mesmo tempo
headers = {
    'x-apisports-key': CHAVE,
    'x-rapidapi-key': CHAVE
}

# A rota /status não consome sua cota e diz se a conta está ativa
url = "https://v3.football.api-sports.io/status"

try:
    resposta = requests.get(url, headers=headers)
    dados = resposta.json()
    
    if dados.get('errors'):
        print(f"❌ A API recusou a conexão. Motivo: {dados.get('errors')}")
        print("💡 Solução: Entre no site da API-Football, confirme seu e-mail ou gere uma nova chave no painel.")
    else:
        conta = dados.get('response', {}).get('account', {})
        print(f"✅ CHAVE VÁLIDA E ATIVA!")
        print(f"👤 Nome: {conta.get('firstname')} {conta.get('lastname')}")
        print(f"📧 E-mail: {conta.get('email')}")
        
except Exception as e:
    print(f"❌ Erro na sonda: {e}")