import requests
import firebase_admin
from firebase_admin import credentials, db
import time
import subprocess # ⚙️ Módulo de automação do sistema operacional
import sys

# --- CREDENCIAIS ROPUTECH ---
FIREBASE_URL = 'https://evision-5dafd-default-rtdb.firebaseio.com/'
ODDS_API_KEY = '181385d79b4261cfadcfd292c806644f'
FOOTBALL_API_KEY = '275321d057f3d8298b7689a3906c616f'

# --- TELEGRAM BOT ---
TELEGRAM_TOKEN = '8727159785:AAHGUBf7bgBzIDVYRI3HVLcX5E8sPSmYl1Y'
TELEGRAM_CHAT_ID = '5796022205' # O teu ID injetado com sucesso!

# --- FILTRO DO MERCADO ---
CASAS_PERMITIDAS = ['betano', 'sportingbet', 'bet365', 'betfair', '1xbet']

cred = credentials.Certificate("firebase-key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})

def enviar_alerta_telegram(mensagem):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": mensagem,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"❌ Erro ao enviar para o Telegram: {e}")

def buscar_estatisticas_ao_vivo():
    url = "https://v3.football.api-sports.io/fixtures?live=all"
    headers = {'x-apisports-key': FOOTBALL_API_KEY}
    try:
        resposta = requests.get(url, headers=headers)
        if resposta.status_code == 200:
            return resposta.json().get('response', [])
        return []
    except Exception:
        return []

def extrair_pressao(jogo_ao_vivo, minuto):
    pressao_casa = 0.0
    pressao_fora = 0.0
    
    estatisticas = jogo_ao_vivo.get('statistics', [])
    
    if len(estatisticas) >= 2:
        # Estatísticas detalhadas de cada equipe
        stats_casa = estatisticas[0].get('statistics', [])
        stats_fora = estatisticas[1].get('statistics', [])
        
        # --- MATRIZ DE PESOS MULTIVARIÁVEL ---
        pesos = {
            'Shots on Goal': 2.0,       # Chute no alvo é quase gol
            'Shots off Goal': 1.0,      # Chute para fora mostra intenção
            'Corner Kicks': 1.2,        # Escanteios geram perigo na área
            'Dangerous Attacks': 0.3,   # Ataques na zona de perigo
            'Ball Possession': 0.05,    # Posse de bola estrutural
            'Red Cards': 5.0            # Expulsão destrói a defesa
        }
        
        # Processando dados do Time da Casa
        for stat in stats_casa:
            tipo = stat.get('type')
            valor = stat.get('value')
            if tipo in pesos and valor is not None:
                # Trata porcentagem de posse limpando o caractere '%' se houver
                val_num = float(str(valor).replace('%', '')) if valor else 0
                pressao_casa += val_num * pesos[tipo]
                
        # Processando dados do Time Visitante
        for stat in stats_fora:
            tipo = stat.get('type')
            valor = stat.get('value')
            if tipo in pesos and valor is not None:
                val_num = float(str(valor).replace('%', '')) if valor else 0
                pressao_fora += val_num * pesos[tipo]

    # --- MULTIPLICADOR DE MOMENTUM TEMPORAL ---
    # Aplica o peso do relógio sobre o saldo de pressão do jogo
    fator_tempo = 1.0
    if minuto >= 80:
        fator_tempo = 1.5  # Abafa final
    elif minuto >= 65:
        fator_tempo = 1.2  # Pressão de segundo tempo
    elif minuto <= 15:
        fator_tempo = 0.5  # Início estudado
        
    # Retornamos a diferença de pressão (Quem está amassando quem)
    pressao_liquida = (pressao_casa - pressao_fora) * fator_tempo
    return pressao_liquida

print("🧠 EVision: Piloto Automático, Telegram e Motor +EV Ativados...\n")

# --- CONTROLADORES DE TEMPO ---
INTERVALO_AUTOMATICO = 900 # 15 minutos para varredura tática ao vivo
INTERVALO_ATUALIZACAO_BANCO = 43200 # 12 horas em segundos para baixar novas odds
ultima_varredura = 0
ultima_atualizacao_banco = 0

while True:
    agora = time.time()
    
    # ==========================================
    # 1. PILOTO AUTOMÁTICO (CARGA DE DADOS)
    # ==========================================
    if agora - ultima_atualizacao_banco >= INTERVALO_ATUALIZACAO_BANCO:
        print("\n⏳ [Automação] Executando carga programada de Odds...")
        try:
            # O Python abre o outro arquivo e manda rodar silenciosamente
            subprocess.run([sys.executable, "atualizar_banco.py"], check=True)
            print("✅ [Automação] Base de dados sincronizada com sucesso!")
        except Exception as e:
            print(f"❌ Erro na automação do banco: {e}")
            
        ultima_atualizacao_banco = agora

    # ==========================================
    # 2. MOTOR DE VARREDURA AO VIVO (+EV)
    # ==========================================
    ref_controle = db.reference('sistema/controle/forcar_varredura')
    forcar = ref_controle.get()
    
    if forcar or (agora - ultima_varredura >= INTERVALO_AUTOMATICO):
        print("\n🚀 Iniciando Varredura Tática Ao Vivo...")
        
        try:
            jogos_ao_vivo_campo = buscar_estatisticas_ao_vivo()
            jogos_odds = db.reference('mercado_copa_do_mundo').get()
            alertas_ao_vivo = []
            
            if jogos_odds and jogos_ao_vivo_campo:
                print("   ➔ Cruzando Pressão Real com as Odds...")
                
                for jogo_campo in jogos_ao_vivo_campo:
                    time_casa_campo = jogo_campo.get('teams', {}).get('home', {}).get('name', '')
                    minuto_jogo = jogo_campo.get('fixture', {}).get('status', {}).get('elapsed', 0)
                    gols_casa = jogo_campo.get('goals', {}).get('home', 0)
                    gols_fora = jogo_campo.get('goals', {}).get('away', 0)
                    
                    for jogo_odd in jogos_odds:
                        time_casa_odd = jogo_odd.get('home_team')
                        
                        if time_casa_odd[:4].lower() in time_casa_campo.lower():
                            casas = jogo_odd.get('bookmakers', [])
                            melhor_odd = 0
                            casa_oferecida = ""
                            selecao_nome = ""
                            
                            for c in casas:
                                nome_casa = c.get('title', '').lower()
                                if any(permitida in nome_casa for permitida in CASAS_PERMITIDAS):
                                    mercados = c.get('markets', [])
                                    if mercados:
                                        odds = mercados[0].get('outcomes', [])
                                        for opcao in odds:
                                            if opcao['name'] == time_casa_odd and opcao['price'] > melhor_odd:
                                                melhor_odd = opcao['price']
                                                casa_oferecida = c.get('title')
                                                selecao_nome = opcao['name']
                            
                            if melhor_odd > 0:
                                prob_implicita = (1 / melhor_odd) * 100
                                pressao_real = extrair_pressao(jogo_campo, minuto_jogo)
                                prob_real_evision = prob_implicita + pressao_real
                                vantagem_ev = prob_real_evision - prob_implicita
                                
                                if vantagem_ev > 3.0:
                                    partida_texto = f"{time_casa_odd} vs {jogo_odd.get('away_team')}"
                                    
                                    alertas_ao_vivo.append({
                                        'partida': partida_texto,
                                        'placar': f"{gols_casa} - {gols_fora}",
                                        'minuto': minuto_jogo,
                                        'selecao': selecao_nome,
                                        'casa_aposta': casa_oferecida,
                                        'odd_oferecida': melhor_odd,
                                        'probabilidade_casa': round(prob_implicita, 1),
                                        'probabilidade_real': round(prob_real_evision, 1),
                                        'vantagem_porcentagem': round(vantagem_ev, 1)
                                    })
                                    
                                    texto_telegram = (
                                        f"🚨 *ALERTA EVISION (+EV)* 🚨\n\n"
                                        f"⚽ *{partida_texto}*\n"
                                        f"⏱️ Minuto: {minuto_jogo}' | Placar: {gols_casa}-{gols_fora}\n\n"
                                        f"💰 *Apostar:* {selecao_nome} @ {melhor_odd}\n"
                                        f"🏦 *Casa:* {casa_oferecida}\n"
                                        f"📈 *Vantagem (+EV):* +{round(vantagem_ev, 1)}%"
                                    )
                                    enviar_alerta_telegram(texto_telegram)
                                break 
            
            db.reference('alertas_ao_vivo').set(alertas_ao_vivo)
            print(f"✅ Feito! Varredura concluída. Painel atualizado.")
            
        except Exception as e:
            print(f"❌ Erro na orquestração: {e}")
            
        ultima_varredura = time.time()
        if forcar:
            ref_controle.set(False)
            print("🛑 Comando manual resetado.")

    time.sleep(5)