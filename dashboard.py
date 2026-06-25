import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time
import json
import os

# --- CONFIGURAÇÃO DA TELA ---
st.set_page_config(page_title="EVision Premium", page_icon="🎯", layout="wide")

# --- CSS PREMIUM E BARRAS DE PRESSÃO ---
st.markdown("""
    <style>
    .ev-card-monitor {
        background-color: #1a1a1a;
        border-left: 5px solid #444;
        border-radius: 10px; padding: 20px; margin-bottom: 20px;
        color: #888;
    }
    
    .ev-card-alerta {
        background-color: #121212;
        border-left: 5px solid #00ff88;
        border-radius: 10px; padding: 20px; margin-bottom: 20px;
        box-shadow: 0 0 20px rgba(0, 255, 136, 0.4);
        color: #ffffff;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { box-shadow: 0 0 10px rgba(0, 255, 136, 0.2); }
        50% { box-shadow: 0 0 25px rgba(0, 255, 136, 0.6); }
        100% { box-shadow: 0 0 10px rgba(0, 255, 136, 0.2); }
    }

    .ev-header {
        display: flex; justify-content: space-between; align-items: center;
        border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 15px;
    }
    .ev-title { font-size: 1.5rem; font-weight: bold; margin: 0; }
    .ev-minuto { color: #ff4b4b; font-weight: bold; font-size: 1.2rem; }
    .ev-destaque { color: #00ff88; font-size: 2rem; font-weight: 900; }
    
    .barra-fundo { background-color: #333; border-radius: 5px; width: 100%; height: 12px; margin-top: 8px; }
    .barra-pressao { height: 12px; border-radius: 5px; transition: width 0.5s ease-in-out; }
    
    .btn-apostar {
        background-color: #00ff88;
        color: #000 !important;
        padding: 8px 15px;
        text-decoration: none;
        border-radius: 5px;
        font-weight: bold;
        display: inline-block;
        margin-top: 10px;
        transition: 0.3s;
        text-align: center;
    }
    .btn-apostar:hover { background-color: #00cc6a; box-shadow: 0 0 10px #00ff88; }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO ROPUTECH ---
FIREBASE_URL = 'https://evision-5dafd-default-rtdb.firebaseio.com/'

if not firebase_admin._apps:
    if os.path.exists("firebase-key.json"):
        cred = credentials.Certificate("firebase-key.json")
    else:
        chave_nuvem = json.loads(st.secrets["FIREBASE_JSON"])
        chave_nuvem["private_key"] = chave_nuvem["private_key"].replace('\\n', '\n').replace('\r', '').strip()
        cred = credentials.Certificate(chave_nuvem)
        
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})

# --- MENU LATERAL (SIDEBAR) ---
st.sidebar.title("⚙️ Painel de Controle")
st.sidebar.markdown("---")
if st.sidebar.button("🎯 Forçar Varredura Agora", use_container_width=True):
    db.reference('sistema/controle/forcar_varredura').set(True)
    st.sidebar.success("Comando enviado ao motor de fundo!")

# --- O NOVO INDICADOR DE RASTREAMENTO DO SATÉLITE ---
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛰️ Satélite: Captura Bruta")
jogos_rastreados = db.reference('sistema/jogos_detectados').get()

if jogos_rastreados:
    for jogo_nome in jogos_rastreados:
        st.sidebar.caption(f"🟢 {jogo_nome}")
else:
    st.sidebar.caption("⏳ Aguardando leitura do motor...")

# --- CABEÇALHO PRINCIPAL ---
st.title("🎯 EVision: Terminal Quantitativo")
st.markdown("**Copa do Mundo 2026** | Motor de Momentum Multivariável Ativo")

placeholder = st.empty()

# --- LOOP VISUAL ---
while True:
    with placeholder.container():
        jogos_vivo = db.reference('alertas_ao_vivo').get()

        if jogos_vivo:
            jogos_ordenados = sorted(jogos_vivo, key=lambda x: x.get('vantagem_porcentagem', 0), reverse=True)
            st.write(f"### 📡 {len(jogos_ordenados)} Jogo(s) com Vantagem no Radar")
            
            for jogo in jogos_ordenados:
                partida = jogo.get('partida', 'Desconhecido')
                placar = jogo.get('placar', '0x0')
                minuto = jogo.get('minuto', '0')
                selecao = jogo.get('selecao', 'N/A')
                odd = jogo.get('odd_oferecida', '0.0')
                casa = jogo.get('casa_aposta', 'Bet365')
                v_ev = jogo.get('vantagem_porcentagem', 0)
                p_real = jogo.get('probabilidade_real', 0)
                p_casa = jogo.get('probabilidade_casa', 0)
                link_casa = jogo.get('link_casa', 'https://www.bet365.com')
                
                is_alerta = v_ev > 5.0
                classe_css = "ev-card-alerta" if is_alerta else "ev-card-monitor"
                cor_barra = "#00ff88" if is_alerta else "#ffb703"
                texto_ev = f"+{v_ev}%" if v_ev > 0 else f"{v_ev}%"
                preenchimento_barra = min((v_ev / 15.0) * 100, 100) if v_ev > 0 else 0
                
                botao_html = f'<a href="{link_casa}" target="_blank" class="btn-apostar">🎯 Abrir {casa}</a>' if is_alerta else ''

                html_card = f"""
<div class="{classe_css}">
    <div class="ev-header">
        <p class="ev-title">⚽ {partida} <span style="color:#888;">| Placar: {placar}</span></p>
        <p class="ev-minuto">⏱️ {minuto}' min</p>
    </div>
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="flex: 1;">
            <p style="margin: 0; color: #aaa;">Entrada Tática (+EV):</p>
            <p class="ev-title" style="color: #fff;">{selecao} @ {odd}</p>
            <p style="margin: 5px 0 0 0; color: #888;">🏦 Operar na: <strong>{casa}</strong></p>
            {botao_html}
        </div>
        <div style="flex: 1; padding: 0 20px;">
            <p style="margin: 0; color: #aaa; text-align: center;">Termômetro de Pressão (IPM)</p>
            <div class="barra-fundo">
                <div class="barra-pressao" style="width: {preenchimento_barra}%; background-color: {cor_barra};"></div>
            </div>
        </div>
        <div style="flex: 1; text-align: right;">
            <p style="margin: 0; color: #aaa;">Vantagem Matemática</p>
            <p class="ev-destaque" style="color: {cor_barra};">{texto_ev}</p>
            <p style="margin: 5px 0 0 0; font-size: 0.85rem; color: #666;">Linha Justa: {p_real}% | Linha da Casa: {p_casa}%</p>
        </div>
    </div>
</div>
"""
                st.markdown(html_card, unsafe_allow_html=True)
        else:
            st.info("📡 Escaneando satélites da FIFA... O algoritmo está a analisar escanteios, cartões e pressão.")

    time.sleep(10)
    st.rerun()