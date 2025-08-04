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
bot.send_message(chat_id=CHAT_ID, text="✅ Bot Macro Trader iniciado com sucesso. Teste completo em andamento...")

# ==== 2. Enviar agenda econômica 3 touros ====
try:
    enviar_agenda_macro()
    bot.send_message(chat_id=CHAT_ID, text="🗓️ Agenda macroeconômica enviada.")
except Exception as e:
    bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Erro ao enviar agenda macroeconômica: {e}")

# ==== 3. Enviar panorama de mercado ====
try:
    dados = coletar_todos_os_dados()
    mensagem = gerar_mensagem_mercado(dados)
    bot.send_message(chat_id=CHAT_ID, text=mensagem)
except Exception as e:
    bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Erro ao gerar panorama de mercado: {e}")
