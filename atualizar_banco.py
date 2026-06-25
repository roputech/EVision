import requests
import firebase_admin
from firebase_admin import credentials, db

# 1. AS TUAS CHAVES
ODDS_API_KEY = '181385d79b4261cfadcfd292c806644f'
FIREBASE_URL = 'https://evision-5dafd-default-rtdb.firebaseio.com/'

cred = credentials.Certificate("firebase-key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})

def atualizar_dados_copa_ao_vivo():
    print("🌍 Reconfigurando base de dados para a Copa do Mundo de 2026...")
    
    # Buscando apenas as Odds da Copa do Mundo (Mercado Principal H2H)
    url_odds = f"https://api.the-odds-api.com/v4/sports/soccer_fifa_world_cup/odds/?apiKey={ODDS_API_KEY}&regions=eu,uk,us,au&markets=h2h"
    
    try:
        print("\n➔ Capturando Mercado de Odds da Copa...")
        res_odds = requests.get(url_odds)
        if res_odds.status_code == 200:
            dados_odds = res_odds.json()
            
            # Voltamos a salvar na pasta padrão da Copa
            db.reference('mercado_copa_do_mundo').set(dados_odds)
            print(f"✅ Odds de {len(dados_odds)} partidas salvas com sucesso no Firebase.")
            print("\n🚀 Base de dados atualizada! Pronta para o Motor de Momentum Ao Vivo.")
        else:
            print(f"❌ Erro nas Odds: {res_odds.status_code}")
    except Exception as e:
        print(f"❌ Erro fatal nas Odds: {e}")

atualizar_dados_copa_ao_vivo()