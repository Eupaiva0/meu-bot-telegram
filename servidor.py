from flask import Flask, request
import telebot

# Token do seu bot Telegram
BOT_TOKEN = '8043403236:AAHsAYj3W99KjXXXryUEUqjDyY3rTpScgiU'
bot = telebot.TeleBot(BOT_TOKEN)

# Cria o app Flask
app = Flask(__name__)

# Mapear nomes de produto para links do Google Drive
LINKS_PRODUTOS = {
    "Pack Bronze":        "https://drive.google.com/seu-link-bronze",
    "Pack Gold":          "https://drive.google.com/seu-link-gold",
    "Pack Diamond":       "https://drive.google.com/seu-link-diamond",
    "Assinatura Mensal":  "https://drive.google.com/seu-link-mensal",
    "Acesso Vitalício":   "https://drive.google.com/seu-link-vitalicio",
    "Chamadinha no Whats": "https://drive.google.com/seu-link-chamada"
}

@app.route('/webhook', methods=['POST'])
def receber_pagamento():
    data = request.json or {}
    # Só processa pagamentos confirmados
    if data.get('status') == 'confirmed':
        nome = data.get('product_name')
        chat_id = data.get('custom')  # deve conter o chat_id do lead
        link = LINKS_PRODUTOS.get(nome)
        if link:
            bot.send_message(
                chat_id,
                f"💖 Obrigada pela compra de *{nome}*!\n\nAqui está seu conteúdo:\n{link}",
                parse_mode="Markdown"
            )
        else:
            print("Produto não cadastrado:", nome)
    return {'ok': True}

if __name__ == '__main__':
    # Inicia o Flask para desenvolvimento local
    app.run(host='0.0.0.0', port=5000)
