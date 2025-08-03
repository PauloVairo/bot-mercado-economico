import datetime
import pytz
import schedule
from telegram import Bot

# ==== CONFIGURAÇÕES ====
TELEGRAM_TOKEN = "8294596491:AAGyzS8sVFhFmR4wOyS__jD_iGBEEjzF-go"
CHAT_ID = "1040590608"
bot = Bot(token=TELEGRAM_TOKEN)

def obter_eventos_tres_touros():
    return [
        {
            "nome": "Payroll (Relatório de Emprego EUA)",
            "hora": "09:30",
            "data": "2025-08-02",
            "moeda": "USD",
            "anterior": "150K",
            "previsao": "170K",
            "resultado": None
        },
        {
            "nome": "IPCA Brasil",
            "hora": "08:00",
            "data": "2025-08-02",
            "moeda": "BRL",
            "anterior": "0,45%",
            "previsao": "0,52%",
            "resultado": None
        }
    ]

def enviar_agenda_macro():
    eventos = obter_eventos_tres_touros()
    hoje = datetime.datetime.now(pytz.timezone("America/Sao_Paulo")).strftime("%d/%m/%Y")
    mensagem = f"📆 *Agenda econômica de alto impacto (3 touros)*\n📅 {hoje}\n\n"
    for ev in eventos:
        if ev['moeda'] in ["USD", "BRL"]:
            mensagem += f"🕒 {ev['hora']} - {ev['nome']} ({ev['moeda']})\n"
    bot.send_message(chat_id=CHAT_ID, text=mensagem, parse_mode='Markdown')

def alerta_pre_evento(evento):
    msg = f"⏰ *Alerta Pré-Evento*\n{evento['nome']} ({evento['moeda']})\nPrevisto: {evento['previsao']} | Anterior: {evento['anterior']}\nHorário: {evento['hora']}"
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

def alerta_divulgacao(evento):
    resultado = "0,55%" if evento['moeda'] == "BRL" else "180K"
    evento['resultado'] = resultado
    msg = f"📊 *Resultado Divulgado*\n{evento['nome']} ({evento['moeda']})\nAnterior: {evento['anterior']} | Previsão: {evento['previsao']} | Resultado: *{evento['resultado']}*\n\n🎯 Recomendação: {gerar_recomendacao(evento)}"
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

def alerta_pos_evento(evento):
    msg = f"🧠 *Pós-Análise*\n{evento['nome']} ({evento['moeda']})\nImpacto analisado: {gerar_impacto(evento)}"
    bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')

def gerar_recomendacao(evento):
    try:
        if evento['moeda'] == "USD":
            return "🟢 Compra WDO" if int(evento['resultado'].replace("K", "")) > int(evento['previsao'].replace("K", "")) else "🔴 Venda WDO"
        elif evento['moeda'] == "BRL":
            return "🔴 Venda WIN" if float(evento['resultado'].replace("%", "").replace(",", ".")) > float(evento['previsao'].replace("%", "").replace(",", ".")) else "🟢 Compra WIN"
    except:
        return "⚪ Neutro"

def gerar_impacto(evento):
    if evento['moeda'] == "USD":
        return "Alta no dólar futuro (WDO), possível queda nos índices (NQ, ES)."
    elif evento['moeda'] == "BRL":
        return "Volatilidade no índice futuro brasileiro (WIN)."
    else:
        return "Impacto indefinido."

def agendar_eventos_diarios():
    eventos = obter_eventos_tres_touros()
    for ev in eventos:
        data_hora_evento = f"{ev['data']} {ev['hora']}"
        dt_evento = datetime.datetime.strptime(data_hora_evento, "%Y-%m-%d %H:%M")
        dt_evento = pytz.timezone("America/Sao_Paulo").localize(dt_evento)

        antes = dt_evento - datetime.timedelta(minutes=10)
        depois = dt_evento + datetime.timedelta(minutes=5)

        schedule.every().day.at(antes.strftime("%H:%M")).do(alerta_pre_evento, evento=ev)
        schedule.every().day.at(dt_evento.strftime("%H:%M")).do(alerta_divulgacao, evento=ev)
        schedule.every().day.at(depois.strftime("%H:%M")).do(alerta_pos_evento, evento=ev)
