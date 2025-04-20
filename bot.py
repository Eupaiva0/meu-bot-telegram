import telebot
import requests
import os
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from flask import Flask, request
import threading

# Configurações
TOKEN = '8043403236:AAHsAYj3W99KjXXXryUEUqjDyY3rTpScgiU'  # Token do bot
PUSHINPAY_TOKEN = "24948|GxFlFi5jtSiZy86r0HUxCRc8BbRAwNFSjctPf1f2ac493a6a"  # Token Pushinpay
WEBHOOK_URL = "https://meu-bot-telegram-2lm9.onrender.com/webhook"  # URL do webhook

# Inicialização do bot
bot = telebot.TeleBot(TOKEN)

# Inicialização do Flask para o webhook
app = Flask(__name__)

# Mapeamento de produtos e preços
PRODUTOS = {
    "Pack Bronze": 19.90,
    "Pack Gold": 39.90,
    "Pack Diamond": 49.90,
    "Assinatura Mensal": 29.90,
    "Acesso Vitalício": 99.90,
    "Chamadinha no Whats": 9.90
}

# Links para entrega após pagamento
LINKS_PRODUTOS = {
    "Pack Bronze": "https://drive.google.com/seu-link-bronze",
    "Pack Gold": "https://drive.google.com/seu-link-gold",
    "Pack Diamond": "https://drive.google.com/seu-link-diamond",
    "Assinatura Mensal": "https://t.me/+seuLinkInviteGrupoVIP",
    "Acesso Vitalício": "https://t.me/+seuLinkInviteGrupoVIP",
    "Chamadinha no Whats": "https://wa.me/5599999999999"
}

# Função para gerar o Pix usando a API da Pushinpay
def gerar_pix(nome_produto, chat_id):
    url = "https://api.pushinpay.com.br/v1/checkout/create"
    headers = {
        "Authorization": f"Bearer {PUSHINPAY_TOKEN}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    valor = PRODUTOS.get(nome_produto, 0)
    
    payload = {
        "product_name": nome_produto,
        "value": valor,
        "custom": str(chat_id),
        "webhook": WEBHOOK_URL
    }
    
    try:
        # Imprime as informações para debug
        print(f"Enviando requisição para: {url}")
        print(f"Payload: {json.dumps(payload)}")
        
        response = requests.post(url, json=payload, headers=headers)
        
        # Imprime a resposta para debug
        print(f"Código de status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        # Verifica se a resposta está vazia
        if not response.text:
            print("Resposta vazia da API")
            return {"error": "Resposta vazia da API. Verifique seu token PushInPay."}
            
        # Verifica o código de status
        if response.status_code != 200:
            print(f"Status de erro: {response.status_code}, Resposta: {response.text}")
            return {"error": f"Status de erro: {response.status_code}. Verifique as credenciais."}
        
        # Tenta fazer o parse do JSON
        try:
            return response.json()
        except ValueError as e:
            print(f"Erro ao parsear JSON: {e}, Resposta: {response.text}")
            return {"error": "Resposta inválida da API. Verifique se a API está funcionando."}
            
    except Exception as e:
        print(f"Erro ao gerar PIX: {e}")
        return {"error": str(e)}

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id

    try:
        with open('modelo.jpg', 'rb') as photo:
            markup = InlineKeyboardMarkup(row_width=1)
            markup.add(
                InlineKeyboardButton("💎 Grupo VIP", callback_data="menu_vip"),
                InlineKeyboardButton("📦 Pacotes", callback_data="menu_packs"),
                InlineKeyboardButton("📲 WhatsApp", callback_data="menu_whatsapp")
            )
            bot.send_photo(
                chat_id,
                photo,
                caption="Oii vidinha, eu estava te esperando, você vai brincar comigo hoje? 😈\n\nEscolha uma opção abaixo:",
                reply_markup=markup
            )
    except FileNotFoundError:
        # Caso não encontre a imagem, envia apenas texto
        markup = InlineKeyboardMarkup(row_width=1)
        markup.add(
            InlineKeyboardButton("💎 Grupo VIP", callback_data="menu_vip"),
            InlineKeyboardButton("📦 Pacotes", callback_data="menu_packs"),
            InlineKeyboardButton("📲 WhatsApp", callback_data="menu_whatsapp")
        )
        bot.send_message(
            chat_id,
            "Oii vidinha, eu estava te esperando, você vai brincar comigo hoje? 😈\n\nEscolha uma opção abaixo:",
            reply_markup=markup
        )

# Tratamento dos botões
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    if call.data == "menu_vip":
        vip_menu(call)
    elif call.data == "menu_packs":
        pack_menu(call)
    elif call.data == "menu_whatsapp":
        whatsapp_menu(call)
    elif call.data == "voltar_menu":
        voltar_menu(call)
    elif call.data.startswith("gerar_pix_"):
        handle_payment_request(call)

# Menus editáveis
def vip_menu(call):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💰 Assinatura Mensal", callback_data="gerar_pix_mensal"),
        InlineKeyboardButton("🔒 Acesso Vitalício", callback_data="gerar_pix_vitalicio"),
        InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_menu")
    )
    try:
        bot.edit_message_caption(
            caption="💎 *Grupo VIP*\n\nEscolha seu acesso abaixo:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Erro ao editar mensagem: {e}")
        # Tentar enviar nova mensagem caso não consiga editar
        bot.send_message(
            call.message.chat.id,
            "💎 *Grupo VIP*\n\nEscolha seu acesso abaixo:",
            reply_markup=markup,
            parse_mode="Markdown"
        )

def pack_menu(call):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📦 Pack (Bronze)", callback_data="gerar_pix_bronze"),
        InlineKeyboardButton("📦 Pack (Gold)", callback_data="gerar_pix_gold"),
        InlineKeyboardButton("📦 Pack (Diamond)", callback_data="gerar_pix_diamond"),
        InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_menu")
    )
    try:
        bot.edit_message_caption(
            caption="📦 *Pacotes Exclusivos*\n\nEscolha o que mais te excita:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Erro ao editar mensagem: {e}")
        bot.send_message(
            call.message.chat.id,
            "📦 *Pacotes Exclusivos*\n\nEscolha o que mais te excita:",
            reply_markup=markup,
            parse_mode="Markdown"
        )

def whatsapp_menu(call):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📞 Chamadinha no Whats", callback_data="gerar_pix_chamada"),
        InlineKeyboardButton("💬 Conversar no Whats", url="https://wa.me/5599999999999"),
        InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_menu")
    )
    try:
        bot.edit_message_caption(
            caption="📲 *WhatsApp*\n\nEscolha como quer falar comigo 😘",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Erro ao editar mensagem: {e}")
        bot.send_message(
            call.message.chat.id,
            "📲 *WhatsApp*\n\nEscolha como quer falar comigo 😘",
            reply_markup=markup,
            parse_mode="Markdown"
        )

def voltar_menu(call):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💎 Grupo VIP", callback_data="menu_vip"),
        InlineKeyboardButton("📦 Pacotes", callback_data="menu_packs"),
        InlineKeyboardButton("📲 WhatsApp", callback_data="menu_whatsapp")
    )
    try:
        bot.edit_message_caption(
            caption="Oii vidinha, eu estava te esperando, você vai brincar comigo hoje? 😈\n\nEscolha uma opção abaixo:",
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            reply_markup=markup
        )
    except Exception as e:
        print(f"Erro ao editar mensagem: {e}")
        bot.send_message(
            call.message.chat.id,
            "Oii vidinha, eu estava te esperando, você vai brincar comigo hoje? 😈\n\nEscolha uma opção abaixo:",
            reply_markup=markup
        )

# Função para lidar com solicitações de pagamento
def handle_payment_request(call):
    produto = None
    if call.data == "gerar_pix_mensal":
        produto = "Assinatura Mensal"
    elif call.data == "gerar_pix_vitalicio":
        produto = "Acesso Vitalício"
    elif call.data == "gerar_pix_bronze":
        produto = "Pack Bronze"  # CORREÇÃO: Removido os parênteses
    elif call.data == "gerar_pix_gold":
        produto = "Pack Gold"  # CORREÇÃO: Removido os parênteses
    elif call.data == "gerar_pix_diamond":
        produto = "Pack Diamond"  # CORREÇÃO: Removido os parênteses
    elif call.data == "gerar_pix_chamada":
        produto = "Chamadinha no Whats"
    
    if produto:
        # Informar o usuário que o pagamento está sendo gerado
        bot.send_message(
            call.message.chat.id,
            f"🔄 Gerando pagamento para *{produto}*... Aguarde um momento.",
            parse_mode="Markdown"
        )
        
        # Gerar PIX
        pix_info = gerar_pix(produto, call.message.chat.id)
        
        if "error" in pix_info:
            bot.send_message(
                call.message.chat.id,
                f"❌ Erro ao gerar pagamento: {pix_info['error']}\n\nTente novamente mais tarde."
            )
        else:
            # Verificar diferentes formatos possíveis de resposta da API
            payment_url = None
            
            # Verificar formato principal esperado
            if "data" in pix_info and isinstance(pix_info["data"], dict):
                if "payment_url" in pix_info["data"]:
                    payment_url = pix_info["data"]["payment_url"]
                elif "checkout_url" in pix_info["data"]:
                    payment_url = pix_info["data"]["checkout_url"]
            
            # Verificar outros formatos possíveis
            if not payment_url:
                # Checar campos comuns que poderiam conter a URL
                for field in ["pix_url", "url", "payment_url", "checkout_url"]:
                    if field in pix_info:
                        payment_url = pix_info[field]
                        break
            
            if payment_url:
                bot.send_message(
                    call.message.chat.id,
                    f"💰 *Pagamento para {produto}*\n\nValor: R$ {PRODUTOS[produto]:.2f}\n\n✅ [Clique aqui para pagar]({payment_url})\n\nApós o pagamento, você receberá seu conteúdo automaticamente!",
                    parse_mode="Markdown"
                )
            else:
                bot.send_message(
                    call.message.chat.id,
                    f"❌ Não foi possível extrair URL de pagamento. Por favor, tente novamente ou contate o suporte.\n\nDetalhes: {json.dumps(pix_info)[:100]}..."
                )
                
                # Registrar resposta completa para debug
                print(f"Debug - Resposta sem URL de pagamento: {json.dumps(pix_info, indent=2)}")

# Webhook para recebimento de notificações de pagamento
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.json or {}
        print(f"Webhook recebido: {data}")
        
        # Verificar se o pagamento foi confirmado
        if data.get('status') == 'confirmed':
            nome_produto = data.get('product_name')
            chat_id = data.get('custom')  # Chat ID armazenado no campo custom
            
            # Buscar o link do produto
            link = LINKS_PRODUTOS.get(nome_produto)
            
            if link and chat_id:
                try:
                    # Enviar o link para o cliente
                    bot.send_message(
                        chat_id,
                        f"💖 *Pagamento confirmado!*\n\nSeu acesso para *{nome_produto}* está pronto:\n\n{link}",
                        parse_mode="Markdown"
                    )
                    
                    # Se for grupo, enviar instruções adicionais
                    if "Grupo VIP" in nome_produto or nome_produto == "Assinatura Mensal" or nome_produto == "Acesso Vitalício":
                        bot.send_message(
                            chat_id,
                            "📝 *Instruções:*\n\n1. Clique no link acima para entrar no grupo\n2. O link é exclusivo e válido por 24 horas\n3. Não compartilhe com ninguém",
                            parse_mode="Markdown"
                        )
                except Exception as e:
                    print(f"Erro ao enviar mensagem após pagamento: {e}")
        
        return {"status": "success"}
    except Exception as e:
        print(f"Erro no webhook: {e}")
        return {"status": "error", "message": str(e)}

# Teste simples para verificar se o servidor está funcionando
@app.route('/', methods=['GET'])
def index():
    return "Bot está online!"

# Comando /debug para testar a integração com a API
@bot.message_handler(commands=['debug'])
def debug_command(message):
    try:
        # Enviar informações de status
        bot.send_message(
            message.chat.id,
            "🔍 *Informações de Debug*\n\n" + 
            "• Bot: Online\n" +
            "• Servidor: Online\n" +
            f"• ID do Chat: {message.chat.id}\n\n" +
            "Para testar a integração com a API de pagamentos, use /testepix",
            parse_mode="Markdown"
        )
    except Exception as e:
        print(f"Erro no comando debug: {e}")

# Comando de teste para pagamento
@bot.message_handler(commands=['testepix'])
def test_pix(message):
    try:
        produto_teste = "Pack Bronze"
        pix_info = gerar_pix(produto_teste, message.chat.id)
        
        bot.send_message(
            message.chat.id,
            f"🧪 *Teste de Integração*\n\n" +
            f"Produto: {produto_teste}\n" +
            f"Resposta da API: {json.dumps(pix_info, indent=2)}",
            parse_mode="Markdown"
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Erro no teste: {str(e)}"
        )

# Função para iniciar o bot de Telegram
def start_bot():
    try:
        bot.remove_webhook()
        bot.polling(none_stop=True)
    except Exception as e:
        print(f"Erro no bot: {e}")
        # Aguardar um pouco antes de tentar reiniciar
        import time
        time.sleep(10)
        start_bot()  # Reiniciar o bot em caso de erro

# Ponto de entrada principal
if __name__ == "__main__":
    # Iniciar o bot em uma thread separada
    bot_thread = threading.Thread(target=start_bot)
    bot_thread.daemon = True
    bot_thread.start()
    
    # Iniciar o servidor Flask para o webhook
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
