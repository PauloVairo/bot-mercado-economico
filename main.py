import os
from telegram import Bot
from macro_scheduler import enviar_agenda_macro
from market_fetcher import gerar_mensagem_mercado, coletar_todos_os_dados
from keep_alive import keep_alive

# ==== PEGANDO VARIÁVEIS DO GITHUB SECRETS ====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TELEGRAM_TOKEN)

# ==== 1. Enviar confirmação de início ====
print("🚀 Iniciando o Bot Macro Trader...")
bot.send_message(chat_id=CHAT_ID, text="✅ Bot Macro Trader iniciado com sucesso. Teste completo em andamento...")

# ==== 2. Enviar agenda econômica 3 touros ====
try:
    print("📅 Enviando agenda macroeconômica...")
    enviar_agenda_macro()
    print("✅ Agenda enviada.")
    bot.send_message(chat_id=CHAT_ID, text="🗓️ Agenda macroeconômica enviada.")
except Exception as e:
    print(f"❌ Erro na agenda: {e}")
    bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Erro ao enviar agenda macroeconômica: {e}")

# ==== 3. Enviar panorama de mercado ====
try:
    print("📥 Coletando dados do mercado...")
    dados = coletar_todos_os_dados()
    print("✅ Dados coletados.")

    print("🧠 Gerando mensagem de panorama de mercado...")
    mensagem = gerar_mensagem_mercado(dados)
    print("📨 Mensagem gerada.")

    print("📤 Enviando mensagem para o Telegram...")
    bot.send_message(chat_id=CHAT_ID, text=mensagem)
    print("✅ Mensagem enviada com sucesso.")
except Exception as e:
    print(f"❌ Erro ao gerar panorama: {e}")
    bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Erro ao gerar panorama de mercado: {e}")
