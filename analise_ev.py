import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

# 1. Conectando ao Banco de Dados (reaproveitando a mesma chave)
cred = credentials.Certificate("firebase-key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        # ATENÇÃO: Cole o seu link do Firebase aqui novamente
        'databaseURL': 'https://evision-5dafd-default-rtdb.firebaseio.com/' 
    })

print("🧠 EVision: Iniciando Motor de Análise Matemática...\n")

# 2. Lendo os 26 jogos da Copa que o outro script salvou
ref = db.reference('mercado_copa_do_mundo')
jogos = ref.get()

# 3. Processando e dissecando jogo a jogo
for jogo in jogos:
    time_casa = jogo.get('home_team')
    time_fora = jogo.get('away_team')
    
    # Vamos pegar a primeira casa de aposta que a API encontrou para este jogo
    casas_aposta = jogo.get('bookmakers', [])
    
    if casas_aposta:
        primeira_casa = casas_aposta[0]
        nome_casa = primeira_casa.get('title')
        mercados = primeira_casa.get('markets', [])
        
        if mercados:
            # Pegamos as odds do mercado h2h (Vencedor da Partida)
            odds = mercados[0].get('outcomes', [])
            
            print(f"⚽ {time_casa} vs {time_fora} (Referência: {nome_casa})")
            
            for opcao in odds:
                nome_selecao = opcao['name']
                valor_odd = opcao['price']
                
                # O Cérebro aplicando a fórmula de Probabilidade Implícita
                prob_implicita = (1 / valor_odd) * 100
                
                print(f"   ➔ {nome_selecao}: Odd {valor_odd} | A casa calcula: {prob_implicita:.1f}% de chance")
            print("-" * 50)