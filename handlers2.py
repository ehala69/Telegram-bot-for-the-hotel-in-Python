from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from config import SUPERGROUP_ID
from datetime import datetime, timedelta
import random
import string
import sqlite3
import re
from dateutil.relativedelta import relativedelta

GET_ABONEMENT, GET_NAME, GET_PHONE, GET_PREFER_CONTACT = range(4)

# Подключение к базе данных
def get_db_connection():
    conn = sqlite3.connect('abonements.db')
    conn.row_factory = sqlite3.Row  # Чтобы результаты возвращались как словари
    return conn

# Функции для работы с базой данных
def add_abonement(abonement_id, user_id, username, name, phone, abonement, status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO abonements (id, user_id, username, name, phone, abonement, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (abonement_id, user_id, username, name, phone, abonement, status))
    conn.commit()
    conn.close()

def update_abonement_status(abonement_id, new_status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE abonements SET status = ? WHERE id = ?
    ''', (new_status, abonement_id))
    conn.commit()
    conn.close()

def get_abonement_by_id(abonement_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM abonements WHERE id = ?', (abonement_id,))
    abonement = cursor.fetchone()
    conn.close()
    return abonement

def get_abonements_by_status(status):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM abonements WHERE status = ?', (status,))
    abonements = cursor.fetchall()
    conn.close()
    return abonements

# Удаление старых завершенных абонементов
def delete_old_past_abonements():
    conn = get_db_connection()
    cursor = conn.cursor()
    one_week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    # Логируем запрос
    print(f"Deleting abonements with status 'past' and end_date < {one_week_ago}")

    # Получаем количество перед удалением
    cursor.execute('SELECT COUNT(*) FROM abonements WHERE status = "past" AND end_date < ?', (one_week_ago,))
    count = cursor.fetchone()[0]
    print(f"Found {count} abonements to delete")

    # Выполняем удаление
    cursor.execute('''
        DELETE FROM abonements
        WHERE status = 'past' AND end_date < ?
    ''', (one_week_ago,))

    print(f"Deleted {cursor.rowcount} abonements")

    conn.commit()
    conn.close()

# Периодическая задача для удаления старых абонементов
async def periodic_delete_old_abonements(context: ContextTypes.DEFAULT_TYPE):
    delete_old_past_abonements()  # Удаляем старые завершенные абонементы

async def test_notify(update, context):
    await notify_about_ending_abonements(context)

async def notify_about_ending_abonements(context: ContextTypes.DEFAULT_TYPE):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем сегодняшнюю дату в формате YYYY-MM-DD
    today = datetime.now().strftime("%Y-%m-%d")

    # Ищем все абонементы, для которых сегодня должна быть отправка уведомления
    cursor.execute('''
        SELECT * FROM abonements 
        WHERE notification_date = ? AND status = 'active'
    ''', (today,))

    abonements = cursor.fetchall()
    conn.close()

    for abonement in abonements:
        end_date = datetime.strptime(abonement["end_date"], "%Y-%m-%d")
        user_end_date = end_date.strftime("%d.%m.%Y")

        try:
            await context.bot.send_message(
                chat_id=abonement["user_id"],
                text=(
                "😱 Срочные новости! 😱\n"
                "К сожалению, завтра последний рабочий день Вашего абонемента.\n\n"
                
                "📋 Детали:\n"
                f"🆔 ID: `{abonement['id']}`\n"
                f"🏷️ Название: {abonement['abonement']}\n"
                f"📅 Дата окончания: {user_end_date}\n\n"
                
                "Хорошего дня! 🌟"
                )
            )

            # Помечаем уведомление как отправленное
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE abonements 
                SET notification_date = NULL 
                WHERE id = ?
            ''', (abonement['id'],))
            conn.commit()
            conn.close()

        except Exception as e:
            print(f"Ошибка отправки уведомления для {abonement['id']}: {e}")

async def check_and_expire_abonements(context: ContextTypes.DEFAULT_TYPE):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Получаем текущую дату в формате БД
    today = datetime.now().strftime("%Y-%m-%d")

    # Ищем активные абонементы с истекшей датой
    cursor.execute('''
        SELECT * FROM abonements 
        WHERE status = 'active' AND end_date <= ?
    ''', (today,))

    expired_abonements = cursor.fetchall()
    conn.close()

    for abonement in expired_abonements:
        # Обновляем статус
        update_abonement_status(abonement['id'], 'past')

        # Уведомление менеджеру
        await context.bot.send_message(
            chat_id=SUPERGROUP_ID,
            text=(
                f"🚨 Абонемент завершен автоматически\n"
                f"🆔 ID: {abonement['id']}\n"
                f"🙍‍♂️ Пользователь: @{abonement['username']}\n"
                f"📞 Телефон: {abonement['phone']}\n"
                f"📅 Дата окончания: {abonement['end_date']}"
            )
        )

        # Уведомление пользователю
        try:
            await context.bot.send_message(
                chat_id=abonement['user_id'],
                text=(
                    "🔔 *Ваш абонемент завершен* 🔔\n\n"
                    f"🆔 ID: `{abonement['id']}`\n"
                    f"📅 Дата окончания: {datetime.strptime(abonement['end_date'], '%Y-%m-%d').strftime('%d.%m.%Y')}\n\n"
                    "*Спасибо за Ваше проведенное время с нами! Возвращайтесь, мы всегда Вас ждем*❤️\n"
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            print(f"Ошибка отправки уведомления пользователю {abonement['id']}: {e}")

# Словарь для временного хранения данных пользователей
user_data = {}


# 📸 1. Главное меню спортзала
async def sport_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id  # Получаем ID чата

    # Отправка фото с информацией об абонементах по file_id
    photo_file_id = "AgACAgIAAxkBAAIpo2eYqRvw0nZbuRN2WZiApQRxUcXNAAJu6jEbmzDISPJlJGZsSqmJAQADAgADeQADNgQ"
    await context.bot.send_photo(chat_id=chat_id, photo=photo_file_id)

    # Отправка кнопок с выбором действия отдельным сообщением
    keyboard = [
        [InlineKeyboardButton("Продолжить", callback_data="continue_abonement")],
        [InlineKeyboardButton("⬅️ Назад", callback_data="back_to_sport_menu")],
    ]
    await context.bot.send_message(
        chat_id=chat_id,
        text="Выбрали абонемент?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )



# 🔙 2. Вернуться в главное меню
async def back_to_menu_sport(update: Update, context: ContextTypes.DEFAULT_TYPE):
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

    # Редактируем текущее сообщение, заменяя текст и клавиатуру
    await query.message.edit_text(
        "Добро пожаловать в BelonLife!",
        reply_markup=reply_markup
    )


# 📝 3. Ввод абонемента
async def continue_abonement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if query:
        await query.answer()  # Подтверждение нажатия кнопки
        # Редактирование текста сообщения
        await query.message.edit_text(
            "Какой абонемент Вы выбрали?\n\nПример заполнения: Безлимитные карты, взрослый, 6 месяцев"
        )
    return GET_ABONEMENT

# 🎟️ 4. Ввод имени
async def get_abonement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    abonement = update.message.text  # Получаем текст от пользователя

    # Проверяем длину абонемента
    if len(abonement) > 100:
        await update.message.reply_text(
            "Название абонемента слишком длинное. Пожалуйста, введите название не длиннее 100 символов."
        )
        return GET_ABONEMENT  # Повторяем текущий шаг

    # Сохраняем абонемент в user_data
    context.user_data['abonement'] = abonement
    await update.message.reply_text("Отлично! Теперь введите Ваше имя:")
    return GET_NAME

# 🙍 5. Ввод номера
async def get_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text
    if len(name) > 25:
        await update.message.reply_text("Имя слишком длинное. Пожалуйста, введите имя не более 25 символов:")
        return GET_NAME
    context.user_data['name'] = name
    await update.message.reply_text("Теперь введите Ваш номер телефона:")
    return GET_PHONE

# 📱 6. Ввод телефона
async def get_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text
    phone_pattern = r"^[\d\-\+\(\)]{1,20}$"

    if not re.match(phone_pattern, phone):
        await update.message.reply_text("Некорректный номер телефона. Пожалуйста, введите номер, используя только цифры.")
        return GET_PHONE

    context.user_data['phone'] = phone

    # Задаём вопрос о предпочтительном способе связи
    keyboard = [
        [InlineKeyboardButton("Написать", callback_data="contact_write")],
        [InlineKeyboardButton("Позвонить", callback_data="contact_call")],
        [InlineKeyboardButton("Без разницы", callback_data="contact_any")],
    ]

    await update.message.reply_text(
        "Какой способ связи Вы предпочитаете?",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return GET_PREFER_CONTACT

# Получение предпочтительного способа связи
async def get_prefer_contact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    # Сохраняем выбранный способ связи
    contact_preference_map = {
        "contact_write": "Написать",
        "contact_call": "Позвонить",
        "contact_any": "Без разницы",
    }
    context.user_data['prefer_contact'] = contact_preference_map[query.data]

    # Вызов функции для создания текста и клавиатуры
    text, keyboard = create_confirmation_message(context)

    await query.edit_message_text(
        text=text,
        reply_markup=keyboard,
        disable_web_page_preview=True,
        parse_mode='HTML'
    )
    return ConversationHandler.END

# Функция для формирования текста подтверждения и клавиатуры
def create_confirmation_message(context):
    abonement = context.user_data['abonement']
    name = context.user_data['name']
    phone = context.user_data['phone']
    prefer_contact = context.user_data.get('prefer_contact', 'Не указано')

    text = (
        "Ваши данные:\n"
        f"💳 Абонемент: {abonement}\n"
        f"🙍‍♂️ Имя: {name}\n"
        f"📞 Телефон: {phone}\n"
        f"📩 Способ связи: {prefer_contact}\n\n"
        "Всё верно? Нажимая 'Да', Вы даете согласие на <a href='https://docs.google.com/document/d/1n1dVFcS-LrDqbYqkWdWlvWfoUPStZTeQ_Dwcm33HP_c/edit?usp=sharing'>обработку персональных данных</a>"
    )

    keyboard = [
        [InlineKeyboardButton("Да", callback_data="confirm_yes")],
        [InlineKeyboardButton("Нет", callback_data="confirm_no")],
    ]

    return text, InlineKeyboardMarkup(keyboard)

# Проверка, существует ли ID в базе данных
def is_booking_id_exists(abonement_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM abonements WHERE id = ?', (abonement_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

# Функция для генерации уникального ID с проверкой на занятость
def generate_booking_id():
    while True:
        letter = random.choice(string.ascii_uppercase)  # Одна случайная заглавная буква
        digits = ''.join(random.choices(string.digits, k=5))  # Пять случайных цифр
        abonement_id = f"{letter}{digits}"  # Пример: A12345

        # Проверяем, существует ли этот ID в базе данных
        if not is_booking_id_exists(abonement_id):
            return abonement_id  # Если ID не занят, возвращаем его

# Функция для вычисления даты окончания
def calculate_end_date(duration: str):
    current_time = datetime.now()
    # Оставляем логику расчета, но возвращаем объект datetime
    if duration.endswith('m'):
        months = int(duration[:-1])
        return current_time + relativedelta(months=+months)
    elif duration.endswith('w'):
        weeks = int(duration[:-1])
        return datetime.now() + timedelta(weeks=weeks)
    elif duration.endswith('d'):
        days = int(duration[:-1])
        return datetime.now() + timedelta(days=days)
    else:
        raise ValueError("Неверный формат продолжительности.")

# ✅ Подтверждение данных
async def handle_confirmation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_chat.id
    username = update.effective_user.username if update.effective_user.username else "Не указан"

    if query.data == "confirm_yes":
        abonement = context.user_data['abonement']
        name = context.user_data['name']
        phone = context.user_data['phone']
        prefer_contact = context.user_data.get('prefer_contact', 'Не указано')

        # Генерация уникального ID
        abonement_id = generate_booking_id()

        # Добавление в базу данных (только при подтверждении)
        add_abonement(abonement_id, user_id, username, name, phone, abonement, 'waiting')

        text = (
            f"Новая бронь!\n"
            f"🆔 ID: {abonement_id}\n"
            f"💳 Абонемент: {abonement}\n\n"
            f"👾 Username: @{username}\n"
            f"🙍‍♂️ Имя: {name}\n"
            f"📞 Телефон: {phone}\n"
            f"📩 Способ связи: {prefer_contact}\n\n"
            f"Принять: /accept {abonement_id}"
        )

        # Удаляем ключ после его использования
        del context.user_data['prefer_contact']

        await context.bot.send_message(chat_id=SUPERGROUP_ID, text=text)
        await query.answer("Данные отправлены менеджеру. Спасибо!")
        await query.message.edit_text(
            f"🆔 ID: {abonement_id}\nВаши данные успешно отправлены менеджеру. Ожидайте подтверждения ✅ \n\n(Убедитесь, что Вам можно написать в личные сообщения.)"
        )

        context.user_data.clear()
        return ConversationHandler.END
    elif query.data == "confirm_no":
        await query.answer("Вы отменили регистрацию.")

        await back_to_menu_sport(update, context)

        context.user_data.clear()

        return ConversationHandler.END


# 📲 Подтверждение бронирования менеджером
async def accept_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != int(SUPERGROUP_ID):
        await update.message.reply_text("Эту команду может использовать только менеджер.")
        return

    try:
        booking_id = context.args[0]

        # Проверяем, существует ли бронирование
        abonement = get_abonement_by_id(booking_id)
        if not abonement:
            await update.message.reply_text(f"Абонемент с ID {booking_id} не найдено.")
            return

        # Обновляем статус
        update_abonement_status(booking_id, 'not_active')

        await update.message.reply_text(
            f"✅ Абонемент {booking_id} подтвержден и добавлен в список неактивных."
        )

        # Уведомление пользователя
        user_id = abonement['user_id']
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"✅ Ваш абонемент подтвержден, но пока не активен!\n"
                f"🆔 Уникальный номер: {booking_id}\n"
                f"💳 Абонемент: {abonement['abonement']}\n"
                f"🙍‍♂️ Имя: {abonement['name']}\n\n"
                f"📌 Дело осталось за малым! Покажите уникальный номер на кассе."
            )
        )
    except IndexError:
        await update.message.reply_text("Используйте команду в формате: /accept {ID}")


async def activate_booking(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != int(SUPERGROUP_ID):
        await update.message.reply_text("Эту команду может использовать только менеджер.")
        return

    try:
        # Проверка наличия аргументов
        if len(context.args) < 2:
            raise IndexError("Недостаточно аргументов")

        booking_id = context.args[0]
        duration = context.args[1].lower()  # Приводим к нижнему регистру

        # Проверка формата длительности
        if not re.match(r"^\d+[dwm]$", duration):
            raise ValueError("Некорректный формат длительности")

        abonement = get_abonement_by_id(booking_id)
        if not abonement:
            await update.message.reply_text(f"Абонемент с ID {booking_id} не найден.")
            return
        if abonement['status'] != 'not_active':
            await update.message.reply_text(f"Абонемент с ID {booking_id} не в статусе 'неактивный'.")
            return

        # Вычисляем дату окончания
        try:
            end_date = calculate_end_date(duration)
        except ValueError as e:
            await update.message.reply_text(f"Ошибка: {str(e)}")
            return

        # Вычисляем дату уведомления (за день до окончания)
        notification_date = end_date - timedelta(days=1)
        notification_date_str = notification_date.date().isoformat()

        # Форматируем даты
        end_date_str = end_date.date().isoformat()
        start_date_str = datetime.now().date().isoformat()

        # Обновляем данные в базе
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE abonements 
                SET status = 'active', 
                    start_date = ?, 
                    end_date = ?,
                    notification_date = ? 
                WHERE id = ?
            ''', (start_date_str, end_date_str, notification_date_str, booking_id))
            conn.commit()
        except sqlite3.Error as e:
            await update.message.reply_text(f"Ошибка базы данных: {str(e)}")
            return
        finally:
            if conn:
                conn.close()

        # Уведомляем пользователя
        await context.bot.send_message(
            chat_id=abonement['user_id'],
            text=(
                f"🎉 Ваш абонемент (ID: {booking_id}) теперь активен!\n"
                f"📅 Дата окончания: {end_date.strftime('%d.%m.%Y')}\n\n"
                f"Желаем вам удачных тренировок! 💪"
            )
        )
        await update.message.reply_text(f"✅ Абонемент {booking_id} активирован!")

    except IndexError:
        await update.message.reply_text("❌ Используйте команду в формате: /active {ID} {d|w|m}\nПример: /active ABC123 30d")
    except ValueError as e:
        await update.message.reply_text(f"❌ Ошибка: {str(e)}\nИспользуйте формат: число + d/w/m \n1d - 1 день\n1w - 1 неделя\n1m - 1 месяц")


# 📋 Показ всех ожидающих бронирований
async def show_waiting_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != int(SUPERGROUP_ID):
        await update.message.reply_text("Эту команду может использовать только менеджер.")
        return

    # Получаем все ожидающие бронирования
    abonements = get_abonements_by_status('waiting')

    if not abonements:
        await update.message.reply_text("📭 Нет ожидающих бронирований.")
        return

    booking_list = "📋 **Список ожидающих бронирований:**\n\n"
    for abonement in abonements:
        booking_list += (
            f"🆔 **ID:** {abonement['id']}\n"
            f"🙍‍♂️ **Имя:** {abonement['name']}\n"
            f"💳 **Абонемент:** {abonement['abonement']}\n"
            f"👾 **Username:** @{abonement['username']}\n"
            f"📞 **Телефон:** {abonement['phone']}\n\n\n"
        )

    await update.message.reply_text(booking_list, parse_mode="Markdown")


# 📋 Показ всех неактивных бронирований
async def show_not_active_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != int(SUPERGROUP_ID):
        await update.message.reply_text("Эту команду может использовать только менеджер.")
        return

    # Получаем все неактивные бронирования
    abonements = get_abonements_by_status('not_active')

    if not abonements:
        await update.message.reply_text("📭 Нет неактивных абонементов.")
        return

    booking_list = "📋 **Список неактивных абонементов:**\n\n"
    for abonement in abonements:
        booking_list += (
            f"🆔 **ID:** {abonement['id']}\n"
            f"🙍‍♂️ **Имя:** {abonement['name']}\n"
            f"💳 **Абонемент:** {abonement['abonement']}\n"
            f"👾 **Username:** @{abonement['username']}\n"
            f"📞 **Телефон:** {abonement['phone']}\n\n\n"
        )

    await update.message.reply_text(booking_list, parse_mode="Markdown")


# 📋 Показ всех действующих бронирований
async def show_active_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != int(SUPERGROUP_ID):
        await update.message.reply_text("Эту команду может использовать только менеджер.")
        return

    # Получаем все активные бронирования
    abonements = get_abonements_by_status('active')

    if not abonements:
        await update.message.reply_text("📭 Нет активных абонементов.")
        return

    booking_list = "📋 **Список активных абонементов:**\n\n"
    for abonement in abonements:
        booking_list += (
            f"🆔 **ID:** {abonement['id']}\n"
            f"🙍‍♂️ **Имя:** {abonement['name']}\n"
            f"💳 **Абонемент:** {abonement['abonement']}\n"
            f"👾 **Username:** @{abonement['username']}\n"
            f"📞 **Телефон:** {abonement['phone']}\n"
            f"📅 **Дата начала:** {abonement['start_date']}\n"
            f"📅 **Дата окончания:** {abonement['end_date']}\n\n\n"
        )

    await update.message.reply_text(booking_list, parse_mode="Markdown")


# 📋 Показ всех прошедших абонементов
async def show_past_bookings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != int(SUPERGROUP_ID):
        await update.message.reply_text("Эту команду может использовать только менеджер.")
        return

    # Получаем все завершенные бронирования
    abonements = get_abonements_by_status('past')

    if not abonements:
        await update.message.reply_text("📭 Нет прошедших абонементов.")
        return

    booking_list = "📋 **Список прошедших абонементов:**\n\n"
    for abonement in abonements:
        booking_list += (
            f"🆔 **ID:** {abonement['id']}\n"
            f"🙍‍♂️ **Имя:** {abonement['name']}\n"
            f"💳 **Абонемент:** {abonement['abonement']}\n"
            f"👾 **Username:** @{abonement['username']}\n"
            f"📞 **Телефон:** {abonement['phone']}\n"
            f"📅 **Дата начала:** {abonement['start_date']}\n"
            f"📅 **Дата окончания:** {abonement['end_date']}\n\n\n"
        )

    await update.message.reply_text(booking_list, parse_mode="Markdown")

# Завершение абонемента
async def end_abonement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != int(SUPERGROUP_ID):
        await update.message.reply_text("❌ Эту команду может использовать только менеджер.")
        return

    try:
        abonement_id = context.args[0]

        # Проверяем, существует ли абонемент
        abonement = get_abonement_by_id(abonement_id)
        if not abonement or abonement['status'] != 'active':
            await update.message.reply_text(f"❌ Активный абонемент с ID {abonement_id} не найден.")
            return

        # Обновляем статус на "past"
        update_abonement_status(abonement_id, 'past')

        # Уведомление менеджера
        await update.message.reply_text(f"✅ Абонемент с ID {abonement_id} завершён и перемещён в список завершённых.")

        # Уведомление пользователя
        user_id = abonement['user_id']
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"⚠️ Ваш абонемент (ID: {abonement_id}) был завершён менеджером.\n"
                "Если это ошибка, пожалуйста, свяжитесь с администрацией спортзала."
            )
        )
    except IndexError:
        await update.message.reply_text("Используйте команду в формате: /endabon {ID}")

# Удаление абонемента вручную
async def delete_abonement(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != int(SUPERGROUP_ID):
        await update.message.reply_text("❌ Эту команду может использовать только менеджер.")
        return

    try:
        abonement_id = context.args[0]

        # Проверяем, существует ли абонемент
        abonement = get_abonement_by_id(abonement_id)
        if not abonement:
            await update.message.reply_text(f"❌ Абонемент с ID {abonement_id} не найден.")
            return

        # Удаляем абонемент
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM abonements WHERE id = ?', (abonement_id,))
        conn.commit()
        conn.close()

        await update.message.reply_text(f"✅ Абонемент с ID {abonement_id} успешно удалён.")
    except IndexError:
        await update.message.reply_text("Используйте команду в формате: /deleteabon {ID}")

# 📋 Показ списка доступных команд
async def help_abon(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Проверяем, что команда используется в группе
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("Эту команду может использовать только менеджер.")
        return

    commands = (
        "📜 <b>Список доступных команд:</b>\n\n"
        "/accept {ID} - <b>Подтвердить абонемент и добавить в список неактивных.</b>\n"
        "/active {ID} {дата} - <b>Активировать абонемент и добавить в список активных.</b>\n\n"
        "/waitbooks - <b>Показать список ожидающих абонементов.</b>\n"
        "/notactivebooks - <b>Показать список неактивных абонементов.</b>\n"
        "/activebooks - <b>Показать список активных абонементов.</b>\n"
        "/pastbooks - <b>Показать список завершённых абонементов.</b>\n\n"
        "/endabon {ID} - <b>Завершить абонемент и переместить в список завершённых.</b>\n"
        "/deleteabon {ID} - <b>Удалить абонемент.</b>\n\n"
        "/allmessage {сообщение} - <b>Сделать объявление всем, кто имеет абонемент</b>"
    )

    await update.message.reply_text(commands, parse_mode="HTML")

# собрать id всех пользователей для оповещения
def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    # Получаем УНИКАЛЬНЫЕ user_id
    cursor.execute('SELECT DISTINCT user_id FROM abonements WHERE user_id IS NOT NULL')
    users = cursor.fetchall()
    conn.close()
    return [user['user_id'] for user in users]

# функция для /allmessage
async def broadcast_message(update, context):
    if update.effective_chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("Эту команду может использовать только менеджер.")
        return

    if len(context.args) == 0:
        await update.message.reply_text("Пожалуйста, укажите текст сообщения. Пример: /allmessage Всем привет!")
        return

    message_text = ' '.join(context.args)
    user_ids = get_all_users()

    # Дополнительная проверка на уникальность
    unique_users = list(set(user_ids))

    success_count = 0
    errors = []

    for user_id in unique_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message_text)
            success_count += 1
        except Exception as e:
            errors.append(str(e))
            print(f"Ошибка при отправке сообщения пользователю {user_id}: {e}")

    report = (
        f"Рассылка завершена\n"
        f"Успешно: {success_count}\n"
        f"Ошибки: {len(errors)}\n"
        f"Всего уникальных получателей: {len(unique_users)}"
    )

    await update.message.reply_text(report)

# PING FOR PYTHONANYWHERE
async def keep_alive(context: ContextTypes.DEFAULT_TYPE):
    print("Пинг: бот активен")

# Функция для пинга в группу (каждые 12 часов)
async def ping_group(context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=SUPERGROUP_ID, text="Пинг: бот активен!")