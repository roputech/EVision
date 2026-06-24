import streamlit as st
import firebase_admin
from firebase_admin import credentials, db
import pandas as pd
import time

# 1. Configuração da Página (A estética do App)
st.set_page_config(page_title="EVision - RoPuTech", page_icon="🚀", layout="wide")

# 2. Conexão com o Firebase
cred = credentials.Certificate("firebase-key.json")
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://evision-5dafd-default-rtdb.firebaseio.com/'
    })

# 3. Título e Estilo
st.title("🛡️ EVision: Monitor de Valor Esperado (+EV)")
st.subheader("Copa do Mundo - Inteligência em Tempo Real")

# Criamos um espaço vazio que será atualizado automaticamente
placeholder = st.empty()

while True:
    with placeholder.container():
        # 4. Lendo os alertas ativos que o seu "Cérebro" está gerando
        ref = db.reference('alertas_ativos')
        alertas = ref.get()

        if alertas:
            # Transformando os dados em uma tabela bonita (DataFrame)
            df = pd.DataFrame(alertas)
            
            # Organizando as colunas para o usuário
            df = df[['partida', 'selecao', 'odd_oferecida', 'vantagem_porcentagem', 'probabilidade_casa', 'probabilidade_real']]
            
            # Exibindo métricas de destaque no topo
            col1, col2 = st.columns(2)
            col1.metric("Oportunidades Ativas", len(df))
            col2.metric("Maior Vantagem Encontrada", f"{df['vantagem_porcentagem'].max()}%")

            # Exibindo a tabela com cores
            st.write("### 🚨 Alertas de Apostas Detectados")
            st.dataframe(df.style.highlight_max(axis=0, subset=['vantagem_porcentagem'], color='#2ecc71'))
            
        else:
            st.info("Buscando novas oportunidades no mercado... O radar está operante.")

    # O Dashboard atualiza a tela a cada 10 segundos para mostrar novos alertas
    time.sleep(10)
    st.rerun()