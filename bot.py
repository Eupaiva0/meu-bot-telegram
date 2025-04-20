import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '8043403236:AAHsAYj3W99KjXXXryUEUqjDyY3rTpScgiU'
bot = telebot.TeleBot(TOKEN)

# Comando /start
@bot.message_handler(commands=['start'])
def send_welcome(message):
    chat_id = message.chat.id

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

# Menus editáveis (mantendo o layout da mesma mensagem)
def vip_menu(call):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💰 Assinatura Mensal", url="https://pushinpay.com/SEU-LINK-MENSAL"),
        InlineKeyboardButton("🔒 Acesso Vitalício", url="https://pushinpay.com/SEU-LINK-VITALICIO"),
        InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_menu")
    )
    bot.edit_message_caption(
        caption="💎 *Grupo VIP*\n\nEscolha seu acesso abaixo:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )

def pack_menu(call):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📦 Pack (Bronze)", url="https://pushinpay.com/SEU-LINK-PACK01"),
        InlineKeyboardButton("📦 Pack (Gold)", url="https://pushinpay.com/SEU-LINK-PACK02"),
        InlineKeyboardButton("📦 Pack (Diamond)", url="https://pushinpay.com/SEU-LINK-PACK03"),
        InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_menu")
    )
    bot.edit_message_caption(
        caption="📦 *Pacotes Exclusivos*\n\nEscolha o que mais te excita:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )

def whatsapp_menu(call):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("📞 Chamadinha no Whats", url="https://pushinpay.com/SEU-LINK-CHAMADA"),
        InlineKeyboardButton("💬 Conversar no Whats", url="https://wa.me/5599999999999"),
        InlineKeyboardButton("⬅️ Voltar", callback_data="voltar_menu")
    )
    bot.edit_message_caption(
        caption="📲 *WhatsApp*\n\nEscolha como quer falar comigo 😘",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup,
        parse_mode="Markdown"
    )

def voltar_menu(call):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton("💎 Grupo VIP", callback_data="menu_vip"),
        InlineKeyboardButton("📦 Packs Exclusivos", callback_data="menu_packs"),
        InlineKeyboardButton("📲 WhatsApp", callback_data="menu_whatsapp")
    )
    bot.edit_message_caption(
        caption="Oii vidinha, eu estava te esperando, você vai brincar comigo hoje? 😈\n\nEscolha uma opção abaixo:",
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        reply_markup=markup
    )

bot.polling()
