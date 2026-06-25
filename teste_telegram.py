import requests

TELEGRAM_TOKEN = '8727159785:AAHGUBf7bgBzIDVYRI3HVLcX5E8sPSmYl1Y'
TELEGRAM_CHAT_ID = '5796022205'

mensagem = (
    "🤖 *Teste de Sistema EVision*\n\n"
    "Conexão com a central da RoPuTech estabelecida com sucesso! 🚀\n"
    "O seu radar de Valor Esperado (+EV) está ativo e aguardando as partidas."
)

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {
    "chat_id": TELEGRAM_CHAT_ID,
    "text": mensagem,
    "parse_mode": "Markdown"
}

print("📡 Disparando teste para o Telegram...")
try:
    resposta = requests.post(url, json=payload)
    if resposta.status_code == 200:
        print("✅ Mensagem enviada! Verifique o seu celular.")
    else:
        print(f"❌ Erro retornado pelo Telegram: {resposta.text}")
except Exception as e:
    print(f"❌ Erro fatal de conexão: {e}")