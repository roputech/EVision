import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import random
import time # Biblioteca para controlar o tempo de repetição (o "Radar")

cred = credentials.Certificate("firebase-key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        # COLE SEU LINK DO FIREBASE AQUI
        'databaseURL': 'https://evision-5dafd-default-rtdb.firebaseio.com/'
    })

print("🧠 EVision: Motor Autônomo de +EV Iniciado (Pressione Ctrl+C para parar)\n")

# O loop infinito transforma o script em um robô que roda 24/7
while True:
    try:
        ref_jogos = db.reference('mercado_copa_do_mundo')
        jogos = ref_jogos.get()
        
        alertas_encontrados = [] # Lista vazia para guardar as oportunidades desta rodada
        
        if jogos:
            for jogo in jogos:
                time_casa = jogo.get('home_team')
                time_fora = jogo.get('away_team')
                casas_aposta = jogo.get('bookmakers', [])
                
                if casas_aposta:
                    primeira_casa = casas_aposta[0]
                    mercados = primeira_casa.get('markets', [])
                    
                    if mercados:
                        odds = mercados[0].get('outcomes', [])
                        
                        for opcao in odds:
                            nome_selecao = opcao['name']
                            valor_odd = opcao['price']
                            
                            prob_implicita = (1 / valor_odd) * 100
                            # Simulação da IA
                            prob_real_evision = prob_implicita + random.uniform(-15, 15)
                            vantagem_ev = prob_real_evision - prob_implicita
                            
                            # Se achou Valor Esperado (+EV), guarda na lista!
                            if vantagem_ev > 2.0:
                                alertas_encontrados.append({
                                    'partida': f"{time_casa} vs {time_fora}",
                                    'selecao': nome_selecao,
                                    'odd_oferecida': valor_odd,
                                    'probabilidade_casa': round(prob_implicita, 1),
                                    'probabilidade_real': round(prob_real_evision, 1),
                                    'vantagem_porcentagem': round(vantagem_ev, 1),
                                    'timestamp': int(time.time())
                                })
            
            # Após varrer todos os jogos, grava a lista de alertas limpa no Firebase
            ref_alertas = db.reference('alertas_ativos')
            ref_alertas.set(alertas_encontrados)
            
            num_alertas = len(alertas_encontrados)
            print(f"📡 Radar concluído: {num_alertas} oportunidades enviadas para a nuvem.")
        
    except Exception as e:
        print(f"❌ Erro na varredura: {e}")
    
    # O robô "dorme" por 60 segundos antes de escanear o mercado de novo
    print("⏳ Aguardando 1 minuto para o próximo ciclo...\n")
    time.sleep(60)