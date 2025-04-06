from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ConversationHandler
from config import BOT_TOKEN
from handlers import (
    category_handler, button_handler, ask_name, ask_phone, ask_persons,
    ask_check_in, ask_check_out, ask_contact_pref,
    confirm_booking, cancel, start, faq, book_room_by_manager, unbook_room_by_manager,
    check_room_status, manager, book_room, back_to_categories, statusall, set_room_price, show_help, back_to_main_menu,
    NAME, PHONE, CHECK_IN, CHECK_OUT, PERSONS, CONTACT_PREF, CONFIRM
)

from handlers2 import (
    sport_menu, back_to_menu_sport, continue_abonement, get_abonement,
    get_name, get_phone, handle_confirmation, accept_booking, show_waiting_bookings, show_past_bookings,
    show_active_bookings, delete_abonement, activate_booking, show_not_active_bookings, help_abon, end_abonement,
    get_prefer_contact, GET_ABONEMENT, GET_NAME, GET_PHONE, GET_PREFER_CONTACT, broadcast_message, test_notify,
    notify_about_ending_abonements, check_and_expire_abonements, periodic_delete_old_abonements, keep_alive, ping_group
)

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Инициализация job queue
    job_queue = application.job_queue

    # Настройка периодической проверки каждые 12 часов (43200 секунд)
    job_queue.run_repeating(
        notify_about_ending_abonements,
        interval=43200,  # Интервал в секундах
        first=10  # Первый запуск через 10 секунд после старта
    )

    # Настройка периодической проверки каждые 6 часов (21600 секунд)
    job_queue.run_repeating(
        check_and_expire_abonements,
        interval=21600,  # Интервал в секундах
        first=10  # Первый запуск через 10 секунд после старта
    )

    # Настройка периодического удаления старых абонементов каждые 24 часа (86400 секунд)
    job_queue.run_repeating(
        periodic_delete_old_abonements,
        interval=86400,
        first=10
    )

    # Ping каждые 45 минут (print)
    job_queue.run_repeating(
        keep_alive,  # Это синхронная функция, но она будет работать, так как не использует await
        interval=2700,
        first=10
    )

    # ping в группу (message to the group)
    job_queue.run_repeating(
        ping_group,  # Это асинхронная функция
        interval=43200,  # Интервал в 12 часов
        first=10
    )

    # Обработчик бронирования
    booking_conv_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(category_handler, pattern="^category_"),
            CallbackQueryHandler(button_handler, pattern="^(prev|next|select)_[0-9]+$")
        ],
        states={
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_name)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_phone)],
            CHECK_IN: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_check_in)],
            CHECK_OUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_check_out)],
            PERSONS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_persons)],
            CONTACT_PREF: [CallbackQueryHandler(ask_contact_pref)],
            CONFIRM: [CallbackQueryHandler(confirm_booking, pattern="^confirm_(yes|no)$")],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Добавляем основные обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("book", book_room_by_manager))
    application.add_handler(CommandHandler("unbook", unbook_room_by_manager))
    application.add_handler(CommandHandler("status", check_room_status))
    statusall_handler = CommandHandler('statusall', statusall)
    application.add_handler(CommandHandler("price", set_room_price))
    application.add_handler(CommandHandler("help", show_help))

    application.add_handler(CommandHandler("accept", accept_booking))
    application.add_handler(CommandHandler("active", activate_booking))
    application.add_handler(CommandHandler("waitbooks", show_waiting_bookings))
    application.add_handler(CommandHandler("notactivebooks", show_not_active_bookings))
    application.add_handler(CommandHandler("activebooks", show_active_bookings))
    application.add_handler(CommandHandler("pastbooks", show_past_bookings))
    application.add_handler(CommandHandler("deleteabon", delete_abonement))
    application.add_handler(CommandHandler("endabon", end_abonement))
    application.add_handler(CommandHandler("helpabon", help_abon))
    application.add_handler(CommandHandler("allmessage", broadcast_message))

    application.add_handler(CallbackQueryHandler(manager, pattern="^manager$"))
    application.add_handler(CallbackQueryHandler(book_room, pattern="book_room"))
    application.add_handler(CallbackQueryHandler(back_to_categories, pattern='^back_to_categories$'))
    application.add_handler(CallbackQueryHandler(back_to_main_menu, pattern="^back_to_main_menu$"))
    application.add_handler(CallbackQueryHandler(start, pattern='^start$'))
    application.add_handler(CallbackQueryHandler(faq, pattern="^faq$"))
    application.add_handler(statusall_handler)
    application.add_handler(booking_conv_handler)

    # Обработчик для абонементов
    abonement_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(continue_abonement, pattern="continue_abonement")],
        states={
            GET_ABONEMENT: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_abonement)],
            GET_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            GET_PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone)],
            GET_PREFER_CONTACT: [CallbackQueryHandler(get_prefer_contact)]
        },
        fallbacks=[CommandHandler("start", start)]
    )

    application.add_handler(CallbackQueryHandler(sport_menu, pattern="^sport$"))
    application.add_handler(CallbackQueryHandler(back_to_menu_sport, pattern="^back_to_sport_menu$"))
    application.add_handler(CallbackQueryHandler(handle_confirmation, pattern="^confirm_(yes|no)$"))
    application.add_handler(abonement_handler)

    application.add_handler(CommandHandler("testnotify", test_notify))

    application.run_polling()


if __name__ == '__main__':
    main()