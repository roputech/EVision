import firebase_admin
from firebase_admin import credentials, db

# Sua conexão
FIREBASE_URL = 'https://evision-5dafd-default-rtdb.firebaseio.com/'
if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})

# Criando duas oportunidades fictícias para testar o painel
alertas_falsos = [
    {
        'partida': 'Brasil vs França',
        'placar': '1 - 0',
        'minuto': 85,
        'selecao': 'Brasil',
        'casa_aposta': 'Betano',
        'odd_oferecida': 2.10,
        'probabilidade_casa': 47.6,
        'probabilidade_real': 55.2,
        'vantagem_porcentagem': 7.6 # Vantagem altíssima (Barra Verde Neon)
    },
    {
        'partida': 'Argentina vs Alemanha',
        'placar': '0 - 0',
        'minuto': 32,
        'selecao': 'Alemanha',
        'casa_aposta': 'Bet365',
        'odd_oferecida': 1.85,
        'probabilidade_casa': 54.0,
        'probabilidade_real': 57.5,
        'vantagem_porcentagem': 3.5 # Vantagem normal (Barra Amarela)
    }
]

print("💉 Injetando simulação no banco de dados...")
db.reference('alertas_ao_vivo').set(alertas_falsos)
print("✅ Feito! Olhe para a tela do seu Dashboard agora.")