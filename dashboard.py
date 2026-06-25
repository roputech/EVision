import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import time

# --- CONFIGURAÇÃO DA TELA ---
st.set_page_config(page_title="EVision Premium", page_icon="🎯", layout="wide")

# --- CSS PREMIUM E BARRAS DE PRESSÃO ---
st.markdown("""
    <style>
    .ev-card {
        background-color: #121212;
        border-left: 5px solid #00ff88;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 15px rgba(0, 255, 136, 0.1);
        color: #ffffff;
    }
    .ev-header {
        display: flex; justify-content: space-between; align-items: center;
        border-bottom: 1px solid #333; padding-bottom: 10px; margin-bottom: 15px;
    }
    .ev-title { font-size: 1.5rem; font-weight: bold; margin: 0; }
    .ev-minuto { color: #ff4b4b; font-weight: bold; font-size: 1.2rem; }
    .ev-destaque { color: #00ff88; font-size: 2rem; font-weight: 900; }
    
    /* Design do Termômetro */
    .barra-fundo { background-color: #333; border-radius: 5px; width: 100%; height: 12px; margin-top: 8px; }
    .barra-pressao { height: 12px; border-radius: 5px; transition: width 0.5s ease-in-out; }
    </style>
""", unsafe_allow_html=True)

# --- CONEXÃO ROPUTECH ---
FIREBASE_URL = 'https://evision-5dafd-default-rtdb.firebaseio.com/'

if not firebase_admin._apps:
    cred = credentials.Certificate("firebase-key.json")
    firebase_admin.initialize_app(cred, {'databaseURL': FIREBASE_URL})

# --- MENU LATERAL (SIDEBAR) ---
st.sidebar.title("⚙️ Painel de Controle")
st.sidebar.markdown("---")
if st.sidebar.button("🎯 Forçar Varredura Agora", use_container_width=True):
    db.reference('sistema/controle/forcar_varredura').set(True)
    st.sidebar.success("Comando enviado ao motor de fundo!")

# --- CABEÇALHO PRINCIPAL ---
st.title("🎯 EVision: Terminal Quantitativo")
st.markdown("**Copa do Mundo 2026** | Motor de Momentum Multivariável Ativo")

placeholder = st.empty()

# --- LOOP VISUAL ---
while True:
    with placeholder.container():
        alertas_vivo = db.reference('alertas_ao_vivo').get()

        if alertas_vivo:
            # Ordena da maior oportunidade para a menor
            alertas_ordenados = sorted(alertas_vivo, key=lambda x: x.get('vantagem_porcentagem', 0), reverse=True)
            
            st.write(f"### 🚨 {len(alertas_ordenados)} Oportunidade(s) com Pressão de +EV")
            
            for alerta in alertas_ordenados:
                partida = alerta.get('partida')
                placar = alerta.get('placar')
                minuto = alerta.get('minuto')
                selecao = alerta.get('selecao')
                odd = alerta.get('odd_oferecida')
                casa = alerta.get('casa_aposta')
                v_ev = alerta.get('vantagem_porcentagem')
                p_real = alerta.get('probabilidade_real')
                p_casa = alerta.get('probabilidade_casa')
                
                cor_barra = "#00ff88" if v_ev > 5.0 else "#ffb703"
                preenchimento_barra = min((v_ev / 15.0) * 100, 100) if v_ev > 0 else 0

                # O HTML foi encostado à esquerda para não virar código no Streamlit
                html_card = f"""
<div class="ev-card">
    <div class="ev-header">
        <p class="ev-title">⚽ {partida} <span style="color:#888;">| Placar: {placar}</span></p>
        <p class="ev-minuto">⏱️ {minuto}' min</p>
    </div>
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <div style="flex: 1;">
            <p style="margin: 0; color: #aaa;">Entrada Tática (+EV):</p>
            <p class="ev-title" style="color: #fff;">{selecao} @ {odd}</p>
            <p style="margin: 5px 0 0 0; color: #888;">🏦 Operar na: <strong>{casa}</strong></p>
        </div>
        <div style="flex: 1; padding: 0 20px;">
            <p style="margin: 0; color: #aaa; text-align: center;">Termômetro de Pressão (IPM)</p>
            <div class="barra-fundo">
                <div class="barra-pressao" style="width: {preenchimento_barra}%; background-color: {cor_barra};"></div>
            </div>
        </div>
        <div style="flex: 1; text-align: right;">
            <p style="margin: 0; color: #aaa;">Vantagem Matemática</p>
            <p class="ev-destaque" style="color: {cor_barra};">+{v_ev}%</p>
            <p style="margin: 5px 0 0 0; font-size: 0.85rem; color: #666;">Linha Justa: {p_real}% | Linha da Casa: {p_casa}%</p>
        </div>
    </div>
</div>
"""
                st.markdown(html_card, unsafe_allow_html=True)
        else:
            st.info("📡 Escaneando satélites da FIFA... O algoritmo está a analisar escanteios, cartões e pressão.")

    # Atualiza a tela a cada 10 segundos
    time.sleep(10)
    st.rerun()