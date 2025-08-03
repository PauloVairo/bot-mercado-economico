import requests
import time
import datetime
import pytz
from keep_alive import keep_alive
from telegram import Bot
import schedule
from macro_scheduler import enviar_agenda_macro, agendar_eventos_diarios

# ==== CONFIGURAÇÕES ====
TELEGRAM_TOKEN = "8294596491:AAGyzS8sVFhFmR4wOyS__jD_iGBEEjzF-go"
CHAT_ID = "1040590608"

# ==== INICIAR BOT TELEGRAM ====
bot = Bot(token=TELEGRAM_TOKEN)

# ==== ENVIA MENSAGEM DE TESTE ====
def send_startup_message():
    mensagem = "Bot de mercado está funcionando corretamente."
    bot.send_message(chat_id=CHAT_ID, text=mensagem)

# ==== FUNÇÃO PRINCIPAL ====
def main():
    send_startup_message()
    schedule.every().day.at("23:00").do(enviar_agenda_macro)
    agendar_eventos_diarios()

    while True:
        agora = datetime.datetime.now(pytz.timezone("America/Sao_Paulo"))
        hora = agora.time()
        if agora.weekday() < 5 and datetime.time(6, 0) <= hora <= datetime.time(16, 0):
            schedule.run_pending()
        time.sleep(60)

# ==== INICIALIZA ====
keep_alive()
main()
