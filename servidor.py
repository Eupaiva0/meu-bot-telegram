from flask import Flask, request
import telebot
import requests

# Seu token do bot do Telegram
BOT_TOKEN = '8043403236:AAHsAYj3W99KjXXXryUEUqjDyY3rTpScgiU'
bot = telebot.TeleBot(BOT_TOKEN)

# Cria o app Flask
app = Flask(__name__)

# Dicionário com os links do Google Drive para cada produto
LINKS_PRODUTOS = {
    "Pack Bronze": "https://drive.google.com/seu-link-bronze",
    "Pack Gold": "https://drive.google.com/seu-link-gold",
    "Pack Diamond": "https://drive.google.com/seu-link-diamond",
    "Assinatura Mensal": "https://drive.google.com/seu-link-mensal",
    "Acesso Vitalício": "https://drive.google.com/seu-link-vitalicio",
    "Chamadinha no Whats": "https://drive.google.com/seu-link-chamada"
}

# Webhook da Pushinpay vai mandar POST aqui
@app.route('/webhook', methods=['POST'])
def receber_pagamento():
    data = request.json

    # Verifica se o pagamento foi confirmado
    if data.get('status') == 'confirmed':
        nome_produto = data.get('product_name')
        telegram_id = data.get('custom')  # Aqui você vai colocar o chat_id quando gerar o pagamento

        link_conteudo = LINKS_PRODUTOS.get(nome_produto)

        if link_conteudo:
            try:
                bot.send_message(
                    chat_id=telegram_id,
                    text=f"💖 Obrigada pela compra do *{nome_produto}*!\n\nAcesse seu conteúdo aqui:\n{link_conteudo}",
                    parse_mode="Markdown"
                )
            except Exception as e:
                print("Erro ao enviar link:", e)
        else:
            print(f"Produto não encontrado: {nome_produto}")

    return {'ok': True}

if __name__ == '__main__':
    app.run(port=5000)
