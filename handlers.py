from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CallbackContext, ContextTypes, ConversationHandler
from config import CATEGORY_DATA, ROOM_DATA, SUPERGROUP_ID

import re
import asyncio

# Стадии диалога
NAME, PHONE, CHECK_IN, CHECK_OUT, PERSONS, CONTACT_PREF, CONFIRM = range(7)

# Регулярные выражения для проверки
def is_valid_number(text: str) -> bool:
    return bool(re.match(r'^[0-9+]+$', text))

# КОМАНДЫ

# Добавление функции для обработки команды /book
async def book_room_by_manager(update: Update, context: CallbackContext):
    # Проверяем, что команда была вызвана в супергруппе
    if update.effective_chat.id != int(SUPERGROUP_ID):
        await update.message.reply_text("Эту команду можно использовать только менеджер в группе.")
        return

    # Парсим аргументы команды
    try:
        args = context.args
        room_id, start_date, end_date = args[0], args[1], args[2]

        # Проверяем, что номер существует
        if room_id not in ROOM_DATA:
            await update.message.reply_text(f"Номер с ID {room_id} не найден.")
            return

        # Обновляем статус номера
        current_description = ROOM_DATA[room_id]["description"]
        updated_description = re.sub(
            r"Статус: .*$",
            f"Статус: Номер занят с {start_date} по {end_date} число ❌",
            current_description,
            flags=re.MULTILINE
        )
        ROOM_DATA[room_id]["description"] = updated_description
        await update.message.reply_text(f"Статус номера {room_id} успешно обновлён.")
    except (IndexError, ValueError):
        await update.message.reply_text(
            "Неверный формат команды. Используйте: /book {айди номера} {с какого числа} {до какого числа}.\n"
            "Например: /book 02 21.12 25.12"
        )

# Добавление функции для проверки доступности номера
async def check_room_status(update: Update, context: CallbackContext):
    try:
        room_id = context.args[0]

        # Проверяем, что команда была вызвана менеджером
        if update.effective_chat.id != int(SUPERGROUP_ID):
            await update.message.reply_text("Эту команду можно использовать только менеджер в группе.")
            return

        # Проверяем, что номер существует
        if room_id not in ROOM_DATA:
            await update.message.reply_text(f"Номер с ID {room_id} не найден.")
            return

        # Отображаем текущее описание номера
        description = ROOM_DATA[room_id]["description"]
        await update.message.reply_text(f"Статус номера {room_id}: {description}")
    except IndexError:
        await update.message.reply_text("Укажите ID номера. Используйте: /status {айди номера}.")

# Добавление функции для обработки команды /status all
async def statusall(update: Update, context: CallbackContext):
    # Проверяем, что команда была вызвана менеджером
    if update.effective_chat.id != int(SUPERGROUP_ID):
        await update.message.reply_text("Эту команду можно использовать только менеджер в группе.")
        return

    # Формируем список статусов всех номеров
    status_message = "Статусы всех номеров:\n\n"
    for room_id, room_data in ROOM_DATA.items():
        status = room_data["description"]  # Статус из описания номера
        status_message += f"{status}\n\n"

    # Отправляем сообщение менеджеру
    await update.message.reply_text(status_message)

# Добавление функции для обработки команды /unbook
async def unbook_room_by_manager(update: Update, context: CallbackContext):
    # Проверяем, что команда была вызвана в супергруппе
    if update.effective_chat.id != int(SUPERGROUP_ID):
        await update.message.reply_text("Эту команду можно использовать только менеджер в группе.")
        return

    try:
        # Парсим аргументы команды
        room_id = context.args[0]

        # Проверяем, что номер существует
        if room_id not in ROOM_DATA:
            await update.message.reply_text(f"Номер с ID {room_id} не найден.")
            return

        # Обновляем статус номера
        current_description = ROOM_DATA[room_id]["description"]
        updated_description = re.sub(
            r"Статус: .*$",
            "Статус: Номер свободен ✅",
            current_description,
            flags=re.MULTILINE
        )
        ROOM_DATA[room_id]["description"] = updated_description
        await update.message.reply_text(f"Статус номера {room_id} успешно обновлён на 'Номер свободен'.")
    except IndexError:
        await update.message.reply_text("Укажите ID номера. Используйте: /unbook {айди номера}.\nПример: /unbook 02")

# Функция для изменения цены номера
async def set_room_price(update: Update, context: CallbackContext):
    # Проверяем, что команду использует менеджер
    if update.effective_chat.id != int(SUPERGROUP_ID):
        await update.message.reply_text("Эту команду может использовать только менеджер.")
        return

    try:
        # Парсим аргументы команды
        args = context.args
        room_id, new_price = args[0], args[1]

        # Проверяем, что номер существует
        if room_id not in ROOM_DATA:
            await update.message.reply_text(f"Номер с ID {room_id} не найден.")
            return

        # Проверяем, что цена является числом
        if not new_price.isdigit():
            await update.message.reply_text("Цена должна быть числом. Пример: /price 02 28000")
            return

        # Обновляем цену в описании номера
        current_description = ROOM_DATA[room_id]["description"]
        updated_description = re.sub(
            r"Цена: \d+тг",
            f"Цена: {new_price}тг",
            current_description
        )
        ROOM_DATA[room_id]["description"] = updated_description

        await update.message.reply_text(f"Цена номера {room_id} успешно обновлена до {new_price}тг.")
    except (IndexError, ValueError):
        await update.message.reply_text(
            "Неверный формат команды. Используйте: /price {айди номера} {новая цена}.\n"
            "Например: /price 02 28000"
        )

# Функция для отображения всех доступных команд
async def show_help(update: Update, context: CallbackContext):
    # Проверяем, что команду использует менеджер
    if update.effective_chat.id != int(SUPERGROUP_ID):
        await update.message.reply_text("Эту команду может использовать только менеджер.")
        return

    help_text = (
        "📜 <b>Список доступных команд:</b>\n\n"
        "/book {ID} {с какого числа} {до какого числа} - <b>Забронировать номер</b>\n"
        "/unbook {ID} - <b>Освободить номер</b>\n"
        "/status {ID} - <b>Проверить статус номера</b>\n"
        "/statusall - <b>Показать статусы всех номеров</b>\n"
        "/price {ID} {цена} - <b>Изменить цену номера</b>\n"
        "/helpabon - <b>Показать список команд (фитнес)</b>\n"
    )

    await update.message.reply_text(help_text, parse_mode="HTML")

# Функция для обработки команды /start
async def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("Фитнес клуб", callback_data="sport"),
         InlineKeyboardButton("Контакты", callback_data="manager")],
        [InlineKeyboardButton("Посмотреть/Забронировать номер", callback_data="book_room")],
        [InlineKeyboardButton("Основная информация", callback_data="faq")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.message:
        await update.message.reply_text(
            "Добро пожаловать в BelonLife!",
            reply_markup=reply_markup
        )
    elif update.callback_query:
        await update.callback_query.edit_message_text(
            "Добро пожаловать в BelonLife!",
            reply_markup=reply_markup
        )

# Функция для обработки кнопки "Менеджер"
async def manager(update: Update, context):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main_menu")]
    ]

    # Обновляем текущее сообщение, заменяя текст и клавиатуру
    await query.message.edit_text(
        "<b>Контактный номер менеджера:</b> \n+7-747-415-85-75 - сотовый\n+7-7172-56-20-20 - городской",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )

# Функция для обработки кнопки "Ответы на вопросы"
async def faq(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    keyboard = [
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Объединяем весь текст в одну строку
    long_text = (
        "1️⃣ <b>Адрес:</b> \n<a href='https://go.2gis.com/Y3Gsl'>просп. Абылай Хана, 24/1</a>\n\n"
        "2️⃣ <b>Рабочие номера:</b>\n+7-747-415-85-75 - сотовый\n+7-7172-56-20-20 - городской \n\n"
        "3️⃣ <b>Сайт:</b> belon.kz\n\n"
        "4️⃣ Заезд после <b>14:00</b>, выезд до <b>12:00</b>\n\n"
        "5️⃣ <b>На территории отеля есть:</b> \n🛜 Бесплатный Wi-Fi \n🏋️‍♂️ Тренажёрный зал \n🏊 Бассейн \n🧖 Cауна \n🚗 Парковка \n🍷 Ресторан \n🧺 Прачечная \n❄️ Кондиционер в номере\n\n"
        "6️⃣ <b>Отзывы:</b>\n<a href='https://yandex.kz/profile/-/CHUyZL9S'>Яндекс.карты: </a>4,6/5\n<a href='https://go.2gis.com/TgofV'>2GIS: </a>4,4/5\n\n"
        "7️⃣ <b>Популярные вопросы:</b> \n1) Как отменить бронирование?\nСвяжитесь с менеджером и объясните ситуацию.\n\n"
        "2) Можно ли с животными?\nК сожалению, с животными запрещено.\n\n3) Можно ли заказать такси/трансфер до аэропорта?\nДа, мы предоставляем трансфер.\n\n"
        "4) Требуется ли предоплата для бронирования?\nПредоплата не требуется.\n\n5) Каковы условия оплаты?\nОплата производится по прибытии."
    )

    await query.message.edit_text(
        long_text,
        parse_mode="HTML",
        disable_web_page_preview=True,
        reply_markup=reply_markup
    )

# Функция для обработки кнопки "Посмотреть/Забронировать номер"
async def book_room(update: Update, context):
    query = update.callback_query
    await query.answer()
    await menu(update, context)

# Функция для отправки сообщения с выбором категории
async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query

    # Формируем клавиатуру выбора категории
    reply_markup = create_category_keyboard()

    # Редактируем текущее сообщение
    await query.message.edit_text(
        "Выберите категорию:",
        reply_markup=reply_markup
    )

# Обработчик выбора категории
async def category_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()

        # Удаляем текущее сообщение (выбор категории)
        try:
            await query.message.delete()
        except Exception:
            pass  # Игнорируем ошибки при удалении

        # Получаем ключ категории
        category_key = query.data.split("_")[1]
        category = CATEGORY_DATA.get(category_key)

        if not category:
            await query.message.reply_text("Ошибка: категория не найдена.")
            return

        # Сохраняем данные о выбранной категории в `context.user_data`
        context.user_data["room_indices"] = category["rooms"]
        context.user_data["current_room"] = 0

        # Отправляем фотографии первой комнаты
        first_room_index = category["rooms"][0]
        context.user_data["previous_messages"] = await send_room_photos(
            query.message.chat_id, first_room_index, context
        )

# Функция для создания клавиатуры категорий
def create_category_keyboard():
    keyboard = [
        [
            InlineKeyboardButton(f"в сутки от {data['price']}", callback_data=f"category_{key}")
        ] for key, data in CATEGORY_DATA.items()
    ]
    # Добавляем кнопку "Назад" в отдельный ряд
    keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_main_menu")])

    return InlineKeyboardMarkup(keyboard)

# Функция для возврата в главное меню
async def back_to_main_menu(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Определяем клавиатуру главного меню
    keyboard = [
        [InlineKeyboardButton("Фитнес клуб", callback_data="sport"),
         InlineKeyboardButton("Контакты", callback_data="manager")],
        [InlineKeyboardButton("Посмотреть/Забронировать номер", callback_data="book_room")],
        [InlineKeyboardButton("Основная информация", callback_data="faq")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Редактируем текущее сообщение для возврата в главное меню
    await query.message.edit_text(
        "Добро пожаловать в BelonLife!",
        reply_markup=reply_markup
    )

# Функция для удаления сообщений и возврата к выбору категорий
async def back_to_categories(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()

    # Удаляем старые сообщения
    previous_messages = context.user_data.get('previous_messages', [])
    for msg_id in previous_messages:
        try:
            await context.bot.delete_message(chat_id=query.message.chat_id, message_id=msg_id)
        except Exception:
            pass  # Игнорируем ошибки при удалении

    # Отправляем новое сообщение с клавиатурой категорий
    keyboard = create_category_keyboard()
    sent_message = await query.message.reply_text("Выберите категорию: ", reply_markup=keyboard)

    # Сохраняем новое сообщение в user_data
    context.user_data['previous_messages'] = [sent_message.message_id]
    context.user_data['start_message_id'] = sent_message.message_id  # Также обновляем start_message_id

# Функция для создания клавиатуры номеров
def create_room_keyboard(room_index):
    keyboard = [
        [
            InlineKeyboardButton("<", callback_data=f"prev_{room_index}"),
            InlineKeyboardButton(">", callback_data=f"next_{room_index}"),
        ],
        [
            InlineKeyboardButton("Забронировать", callback_data=f"select_{room_index}"),
        ],
        [
            InlineKeyboardButton("⬅️ Назад", callback_data="back_to_categories")
        ]
    ]
    return InlineKeyboardMarkup(keyboard)

# Функция для отправки фотографий номера через file_id
async def send_room_photos(chat_id, room_index, context, previous_messages=None):
    # Удаляем старые сообщения, если они существуют
    if previous_messages:
        for msg_id in previous_messages:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg_id)
                await asyncio.sleep(0.1)  # Задержка в 100 мс
            except Exception:
                pass  # Игнорируем ошибки при удалении

    # Получаем данные номера
    room_data = ROOM_DATA[room_index]
    photo_ids = room_data["photos"]  # Здесь уже должны быть file_id для фото
    description = room_data.get("description", "Описание не указано.")

    # Создаём медиа-группу
    media_group = []
    for i, file_id in enumerate(photo_ids):
        if i == 0:
            media_group.append(InputMediaPhoto(file_id, caption=description))
        else:
            media_group.append(InputMediaPhoto(file_id))

    # Отправляем фотографии как медиа-группу
    await asyncio.sleep(0.1)  # Задержка перед отправкой
    sent_media = await context.bot.send_media_group(chat_id=chat_id, media=media_group)

    # Задержка перед отправкой клавиатуры
    await asyncio.sleep(0.1)

    # Отправляем сообщение с клавиатурой
    sent_buttons = await context.bot.send_message(
        chat_id=chat_id,
        text="Выберите действие:",
        reply_markup=create_room_keyboard(room_index),
    )

    # Возвращаем IDs отправленных сообщений
    return [msg.message_id for msg in sent_media] + [sent_buttons.message_id]


# Обработчик кнопок для номеров
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()  # Подтверждение нажатия кнопки

        # Разделяем данные из callback_data
        data = query.data.split("_")
        action = data[0]
        room_index = data[1]  # Используем индекс как строку, чтобы сохранить ведущие нули

        if action == "select":
            # Изменяем текст сообщения
            await query.message.edit_text(
                f"Вы выбрали номер {room_index}. Пожалуйста, предоставьте необходимую информацию для бронирования."
            )

            # Сохраняем выбранный номер в данных пользователя
            context.user_data['selected_room'] = room_index

            # Запрашиваем имя пользователя для бронирования
            await query.message.reply_text("Введите ваше имя:")

            # Переходим к следующему состоянию
            return NAME  # Например, состояние для ввода имени

        # Логика для кнопок "prev" и "next" (перелистывание номеров)
        if action == "prev":
            context.user_data["current_room"] = (context.user_data["current_room"] - 1) % len(context.user_data["room_indices"])
        elif action == "next":
            context.user_data["current_room"] = (context.user_data["current_room"] + 1) % len(context.user_data["room_indices"])

        # Отправляем новые фотографии номера
        new_room_index = context.user_data["room_indices"][context.user_data["current_room"]]
        context.user_data["previous_messages"] = await send_room_photos(
            query.message.chat_id, new_room_index, context, context.user_data.get("previous_messages", [])
        )


# Определение этапов для опроса
async def ask_name(update: Update, context):
    if len(update.message.text) > 30:
        await update.message.reply_text(
            "Имя не должно превышать 30 символов. Пожалуйста, введите имя снова:"
        )
        return NAME

    context.user_data['name'] = update.message.text
    await update.message.reply_text(
        f"Спасибо, {context.user_data['name']}! Теперь введите ваш номер телефона:"
    )
    return PHONE

async def ask_phone(update: Update, context):
    if len(update.message.text) > 40:
        await update.message.reply_text(
            "Номер телефона не должен превышать 45 символов. Введите номер снова:"
        )
        return PHONE

    if not is_valid_number(update.message.text):
        await update.message.reply_text(
            "Пожалуйста, введите действительный номер телефона, не используйте пробелы и буквы. "
            "Введите ваш номер телефона:"
        )
        return PHONE

    context.user_data['phone'] = update.message.text
    await update.message.reply_text("Какого числа вы планируете заселяться в отель?")
    return CHECK_IN

async def ask_check_in(update: Update, context):
    if len(update.message.text) > 45:
        await update.message.reply_text(
            "Текст не должна превышать 45 символов. Введите дату снова:"
        )
        return CHECK_IN

    context.user_data['check_in'] = update.message.text
    await update.message.reply_text("До какого числа вы планируете пробыть в отеле?")
    return CHECK_OUT

async def ask_check_out(update: Update, context):
    if len(update.message.text) > 45:
        await update.message.reply_text(
            "Дата выезда не должна превышать 45 символов. Введите дату снова:"
        )
        return CHECK_OUT

    context.user_data['check_out'] = update.message.text
    await update.message.reply_text("Сколько человек будут проживать? Будут ли дети? (до 14 лет)")
    return PERSONS

async def ask_persons(update: Update, context):
    if re.search(r'666|52|777', (update.message.text or '')):
        await update.message.reply_text("🤡")
    if len(update.message.text) > 45:
        await update.message.reply_text(
            "Описание количества проживающих не должно превышать 45 символов. Введите данные снова:"
        )
        return PERSONS

    context.user_data['persons'] = update.message.text

    keyboard = [
        [InlineKeyboardButton("Написать", callback_data='write')],
        [InlineKeyboardButton("Позвонить", callback_data='call')],
        [InlineKeyboardButton("Без разницы", callback_data='any')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "Как вы хотите, чтобы мы с вами связались?",
        reply_markup=reply_markup
    )
    return CONTACT_PREF

async def ask_contact_pref(update: Update, context):
    query = update.callback_query
    if query:
        contact_methods = {
            'write': 'Написать',
            'call': 'Позвонить',
            'any': 'Без разницы'
        }
        context.user_data['contact_pref'] = contact_methods[query.data]

        # Формируем информацию о бронировании с учетом выбранного способа связи
        booking_info = (
            f"Ваши данные:\n"
            f"🛏️ Выбранный номер: {context.user_data['selected_room']}\n\n"
            f"🙍‍♂️ Имя: {context.user_data['name']}\n"
            f"📞 Телефон: {context.user_data['phone']}\n"
            f"👥 Количество человек: {context.user_data['persons']}\n"
            f"Предпочтительный способ связи: {context.user_data['contact_pref']}\n\n"
            f"Дата заселения: {context.user_data['check_in']}\n"
            f"Дата выезда: {context.user_data['check_out']}\n\n"
            "Всё верно? Нажимая 'Да', Вы даете согласие на "
            "<a href='https://docs.google.com/document/d/1n1dVFcS-LrDqbYqkWdWlvWfoUPStZTeQ_Dwcm33HP_c/edit?usp=sharing'>обработку персональных данных</a>"
        )

        # Клавиатура с кнопками
        keyboard = [
            [InlineKeyboardButton("Да", callback_data='confirm_yes')],
            [InlineKeyboardButton("Нет", callback_data='confirm_no')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        # Обновляем сообщение с новыми данными и кнопками
        await query.message.edit_text(
            booking_info,
            reply_markup=reply_markup,
            parse_mode='HTML',
            disable_web_page_preview=True
        )

        return CONFIRM

async def confirm_booking(update: Update, context):
    query = update.callback_query
    if query:
        if query.data == "confirm_yes":
            username = update.effective_user.username if update.effective_user and update.effective_user.username else "Не указан"
            booking_info = (
                f"❗Новая бронь❗\n"
                f"🛏️ Выбранный номер: {context.user_data['selected_room']}\n\n"
                f"👾 Username: @{username}\n"
                f"🙍‍♂️ Имя: {context.user_data['name']}\n"
                f"📞 Телефон: {context.user_data['phone']}\n"
                f"👥 Количество человек: {context.user_data['persons']}\n"
                f"Предпочтительный способ связи: {context.user_data['contact_pref']}\n\n"
                f"Дата заселения: {context.user_data['check_in']}\n"
                f"Дата выезда: {context.user_data['check_out']}\n"
                f"Команда: /book {context.user_data['selected_room']} (дата въезда) (дата выезда)"
            )

            if query.message:  # Проверяем, что сообщение доступно

                # Изменяем текст сообщения с подтверждением
                await query.answer("Спасибо, что выбрали нас!")

            # Отправляем информацию менеджеру
            await context.bot.send_message(SUPERGROUP_ID, booking_info)

            # Возвращаем пользователя в главное меню
            await start(update, context)

        elif query.data == "confirm_no":
            # Очищаем сохраненные данные о бронировании
            context.user_data.clear()
            if query.message:  # Проверяем, что сообщение доступно

                # объявление
                await query.answer("Вы отменили регистрацию.")

            # Возвращаем в главное меню
            await start(update, context)

    return ConversationHandler.END

# Обработчик команды /cancel
async def cancel(update: Update, context):
    pass