import requests
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# 1. Configurações direcionadas para a Copa do Mundo
API_KEY = '181385d79b4261cfadcfd292c806644f'
ESPORTE = 'soccer_fifa_world_cup' # Foco total na Copa do Mundo da FIFA
REGIAO = 'eu' # Casas europeias como Bet365 e Betfair
MERCADO = 'h2h' # Mercado de vitória/empate (1X2)

# 2. Conectando ao Firebase
cred = credentials.Certificate("firebase-key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://evision-5dafd-default-rtdb.firebaseio.com/'
    })

print(f"📡 EVision monitorando a Copa do Mundo ({ESPORTE})...")

# 3. Requisição direta para a Copa
url = f'https://api.the-odds-api.com/v4/sports/{ESPORTE}/odds/?apiKey={API_KEY}&regions={REGIAO}&markets={MERCADO}'

try:
    resposta = requests.get(url)
    
    if resposta.status_code == 200:
        dados_jogos = resposta.json()
        num_jogos = len(dados_jogos)
        print(f"✅ Sucesso! {num_jogos} jogos da Copa encontrados. Atualizando banco de dados...")
        
        # Estrutura limpa no banco: mercado_copa_do_mundo -> dados ao vivo
        ref = db.reference('mercado_copa_do_mundo')
        ref.set(dados_jogos)
        
        print("🚀 Dados da Copa do Mundo sincronizados em tempo real no Firebase!")
    else:
        print(f"❌ Erro na API da Copa: {resposta.status_code} - {resposta.text}")
        
except Exception as e:
    print(f"❌ Falha crítica de conexão: {e}")