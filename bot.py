from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Состояния пользователя
STEP_START = 0
STEP_BUY = 1
STEP_PRODUCTS = 2
STEP_CITY = 3
STEP_DISTRICT = 4

# Админ Telegram ID
ADMIN_ID = 7861733044  

# Хранение состояний и выборов пользователей
user_states = {}
user_choices = {}

# Города и районы
CITIES = {
    "Питер": ["Адмиралтейский", "Василеостровский", "Выборгский", "Калининский", "Кировский",
              "Колпинский", "Красногвардейский", "Красносельский", "Кронштадт", "Курортный"],
    "Нижний Новгород": ["Советский", "Приокский", "Канавинский", "Ленинский", "Московский", "Автозаводский"],
    "Москва": ["Арбат", "Басманный", "Замоскворечье", "Красносельский", "Мещанский", "Пресненский",
               "Таганский", "Тверской"],
    "Екатеринбург": ["Верх-Исетский", "Железнодорожный", "Кировский", "Ленинский", "Октябрьский",
                     "Орджоникидзевский", "Чкаловский"],
    "Самара": ["Куйбышевский", "Самарский", "Ленинский", "Железнодорожный", "Октябрьский", "Советский",
               "Промышленный", "Кировский"],
    "Челябинск": ["Калининский", "Курчатовский", "Ленинский", "Металлургический", "Центральный"],
    "Иркутск": ["Правобережный", "Октябрьский", "Свердловский", "Ленинский"]
}

# Продукты и цены
PRODUCTS = {
    "Марихуана": {"0.5г": "639₽", "1г": "1099₽", "5г": "4499₽"}, 
    "Методон": {"0.5г": "879₽", "1г": "1499₽", "5г": "6699₽"}, 
    "Мефедрон": {"0.5г": "569₽", "1г": "1099₽", "5г": "4199₽"}, 
    "Героин": {"0.5г": "799₽", "1г": "1299₽", "5г": "4999₽"}, 
    "Шмаль": {"0.5г": "439₽", "1г": "799₽", "5г": "3699₽"}, 
    "Канабис": {"0.5г": "599₽", "1г": "999₽", "5г": "4689₽"} 
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_states[user_id] = STEP_START
    keyboard = [['Купить']]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
    await update.message.reply_text("Здравствуйте! Выберите желаемый товар:", reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    username = update.message.from_user.username or update.message.from_user.full_name
    text = update.message.text
    state = user_states.get(user_id, STEP_START)

    if state == STEP_START:
        if text == 'Купить':
            user_states[user_id] = STEP_BUY
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"Пользователь @{username} нажал 'Купить'.")
            keyboard_products = [[p] for p in PRODUCTS.keys()]
            reply_markup_products = ReplyKeyboardMarkup(keyboard_products, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text('Выберите продукт:', reply_markup=reply_markup_products)
        else:
            await update.message.reply_text('Нажмите кнопку "Купить".')

    elif state == STEP_BUY:
        if text in PRODUCTS:
            user_states[user_id] = STEP_PRODUCTS
            user_choices[user_id] = {"product": text}
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"Пользователь @{username} выбрал продукт: {text}")
            weights = list(PRODUCTS[text].keys())
            keyboard_weights = [[f"{w} - {PRODUCTS[text][w]}"] for w in weights]
            reply_markup_weights = ReplyKeyboardMarkup(keyboard_weights, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text('Выберите вес продукта:', reply_markup=reply_markup_weights)
        else:
            await update.message.reply_text('Пожалуйста, выберите продукт из списка.')

    elif state == STEP_PRODUCTS:
        product = user_choices[user_id]["product"]
        selected_weight = next((w for w in PRODUCTS[product] if w in text), None)
        if selected_weight:
            user_choices[user_id]["weight"] = selected_weight
            user_states[user_id] = STEP_CITY
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"Пользователь @{username} выбрал вес: {selected_weight}")
            keyboard_cities = [[city] for city in CITIES.keys()]
            reply_markup_cities = ReplyKeyboardMarkup(keyboard_cities, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text('Выберите город доставки:', reply_markup=reply_markup_cities)
        else:
            await update.message.reply_text('Пожалуйста, выберите вес из списка.')

    elif state == STEP_CITY:
        if text in CITIES:
            user_choices[user_id]["city"] = text
            user_states[user_id] = STEP_DISTRICT
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"Пользователь @{username} выбрал город: {text}")
            districts = CITIES[text]
            keyboard_districts = [[d] for d in districts]
            reply_markup_districts = ReplyKeyboardMarkup(keyboard_districts, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text(f'Выберите район в городе {text}:', reply_markup=reply_markup_districts)
        else:
            await update.message.reply_text('Пожалуйста, выберите город из списка.')

    elif state == STEP_DISTRICT:
        city = user_choices[user_id]["city"]
        if text in CITIES[city]:
            user_choices[user_id]["district"] = text
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"Пользователь @{username} выбрал район: {text} (город {city})")
            product = user_choices[user_id]["product"]
            weight = user_choices[user_id]["weight"]
            await update.message.reply_text(
                f'Спасибо! Вы выбрали {product}, {weight}, город {city}, район {text}.\n'
                f'Реквизиты для оплаты: ... (LTC оплата, сеть LTC, номер LYMgLp92vTjETLodJ8RC8mFSxqNmoiHQMW, после оплаты ждите ответа администратора в течение 6 часов)'
            )
            # Сброс состояния
            user_states[user_id] = STEP_START
            keyboard = [['Купить']]
            reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True)
            await update.message.reply_text('Если хотите сделать новый заказ, нажмите кнопку "Купить".', reply_markup=reply_markup)
        else:
            await update.message.reply_text(f'Пожалуйста, выберите район из списка для города {city}.')

def main():
    TOKEN = '8430561215:AAGRoJjk72yTNwUjmTmPR0vtqJB4IfAtchA'
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    main()
