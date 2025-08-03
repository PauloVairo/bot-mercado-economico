import os
from telegram import Bot
from macro_scheduler import enviar_agenda_macro
from market_fetcher import enviar_panorama_mercado
from datetime import datetime

# ==== VARIÁVEIS DE AMBIENTE ====
TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

bot = Bot(token=TOKEN)

# ==== 1. Enviar confirmação de início ====
bot.send_message(chat_id=CHAT_ID, text="✅ Bot Macro Trader iniciado com sucesso. Teste completo em andamento...")

# ==== 2. Enviar agenda econômica 3 touros (agenda do dia seguinte) ====
try:
    enviar_agenda_macro()
    bot.send_message(chat_id=CHAT_ID, text="🗓️ Agenda macroeconômica enviada.")
except Exception as e:
    bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Erro ao enviar agenda macroeconômica: {e}")

# ==== 3. Enviar panorama de mercado ====
try:
    enviar_panorama_mercado()
    bot.send_message(chat_id=CHAT_ID, text="🌍 Panorama de mercado enviado.")
except Exception as e:
    bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Erro ao enviar panorama de mercado: {e}")

# ==== 4. Simular disparo de notícia com palavra-chave ====
try:
    noticia = "Estados Unidos reporta inflação acima do esperado, reforçando apostas em juros mais altos."
    impacto = "🟡 Impacto moderado no dólar (WDO) e futuros americanos (Nasdaq/S&P)."
    recomendacao = "📉 Pressão vendedora no início, possível recuperação no final do dia."

    bot.send_message(
        chat_id=CHAT_ID,
        text=f"📰 *Alerta de Notícia Macro*\n\n{noticia}\n\n{impacto}\n{recomendacao}",
        parse_mode="Markdown"
    )
except Exception as e:
    bot.send_message(chat_id=CHAT_ID, text=f"⚠️ Erro ao simular notícia macro: {e}")
