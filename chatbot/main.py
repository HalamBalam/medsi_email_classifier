# модуль для работы с базой данных
import sqlite3 as sl
import pandas as pd
from openpyxl import Workbook
# модуль работы со временем
from datetime import datetime, timezone

import telebot
from telebot import types

from bert_binary_classifier import BertBinaryClassifier
from bert_multiclass_classifier import BertMulticlassClassifier
from distilbert_class import DistilBERTClass

BOT_TOKEN = 'TOKEN'
bot = telebot.TeleBot(BOT_TOKEN)

COMMAND_HELLO = "hello"
COMMAND_START = "start"
COMMAND_HELP = "help"
COMMAND_OUTPUT = "output"
COMMAND_TXT = "TXT"
COMMAND_PDF = "PDF"
COMMAND_DOCX = "DOCX"
MESSAGE_START = "Какой формат документа вы хотите обработать?"

# подключаемся к файлу с базой данных
con = sl.connect('bd_biomind.db')

# открываем файл
with con:
    # получаем количество таблиц с нужным нам именем
    data = con.execute("select count(*) from sqlite_master where type='table' and name='bd_biomind'")
    for row in data:
        # если таких таблиц нет
        if row[0] == 0:
            # создаём таблицу для отчётов
            with con:
                con.execute("""
                    CREATE TABLE bd_biomind (
                        letter_id INTEGER PRIMARY KEY,
                        datetime VARCHAR(40),
                        date VARCHAR(20),
                        user_id   INTEGER,
                        user_name TEXT,
                        text      TEXT,
                        description_service  TEXT,
                        code_service TEXT,
                        class_classification INTEGER
                    );
                    """)


# Функция обработчика команды /hello
@bot.message_handler(commands=[COMMAND_HELLO])
def start(message):
    bot.send_message(message.chat.id, text=f'Привет, {message.from_user.username}!'
                                           f'\nЯ BioMind Bot создан для извлечения текстовой информации из '
                                           f'гарантийных писем.'
                                           f'\n\nУ меня есть следующие команды: '
                                           f'\n\n/help\n\n/reset\n\n/start\n\n/output')


# Функция обработчика команды /help
@bot.message_handler(commands=[COMMAND_HELP])
def cmd_reset(message):
    bot.send_message(message.chat.id,
                     text="Общая цель проекта заключается в создании и развитии системы автоматизированной "
                          "обработки гарантийных писем, обеспечивающей извлечение текстовой информации, "
                          "классификацию услуг."
                          "\nВсю необходимую информацию по реализации проекта можно найти и ознакомиться здесь: "
                          "<a href='https://github.com/HalamBalam/medsi_email_classifier'>ссылка</a>",
                     parse_mode='HTML')
    bot.send_message(message.chat.id, text='Выход в главное меню по команде /hello')


# Функция обработчика команды /stop для разработчика
@bot.message_handler(commands=['stop'])
def stop(message):
    con = sl.connect('bd_biomind.db')
    cur = con.cursor()
    #cur.execute("DELETE FROM bd_biomind")  # Удаляем все записи из таблицы
    cur.execute("DROP TABLE bd_biomind")
    con.commit()  # Подтверждаем изменения
    bot.send_message(message.chat.id,
                     text=f'BioMind завершает свою работу, если хотите снова ко мне обратиться, то напишите мне '
                          f'"/start"!'
                          f'\n\nДо скорых встреч {message.from_user.username}!')
    con.close()  # Закрываем подключение к БД
    bot.stop_polling()


# Функция обработчика команды /reset
@bot.message_handler(commands=["reset"])
def cmd_reset(message):
    con = sl.connect('bd_biomind.db')
    cur = con.cursor()
    # Подставляем значение user_id в запрос для удаления только его записей
    user_id_to_delete = message.from_user.id
    cur.execute("DELETE FROM bd_biomind WHERE user_id=?", (user_id_to_delete,))
    con.commit()
    bot.send_message(message.chat.id, text="Ваши данные были удалены из базы данных"
                                           "\nВыход в главное меню - /hello")
    con.close()
    bot.stop_polling()


# Функция обработчика команды /output
@bot.message_handler(commands=[COMMAND_OUTPUT])
def output_user_data(message):
    user_id = message.from_user.id
    # Подключение к базе данных SQLite
    conn = sl.connect('bd_biomind.db')
    try:
        # Создание объекта cursor для выполнения SQL-запросов
        cursor = conn.cursor()

        # SQL-запрос для получения данных пользователя
        query = """ SELECT date, text, description_service FROM bd_biomind WHERE user_id=? """
        cursor.execute(query, (user_id,))

        # Получение всех строк
        rows = cursor.fetchall()

        # Если строки существуют, отправляем их пользователю
        if rows:
            response = ""
            for i, row in enumerate(rows):
                # Текст обрезается до 50 символов
                text_preview = row[1][:30]
                response += f'[{i}]\nДата: {row[0]};\nТекст: {text_preview}...;\nУслуги: {row[2]};\n\n'

            bot.send_message(message.chat.id, response)
        else:
            # Если строк нет, сообщаем об этом пользователю
            bot.send_message(message.chat.id, "Нет данных для вывода.")

    except sl.Error as e:
        # В случае ошибки выводим сообщение
        bot.send_message(message.chat.id, f"Ошибка при работе с базой данных: {e}")
    finally:
        # Закрываем соединение с базой данных
        if conn:
            conn.close()


# Функция обработчика команды /start
@bot.message_handler(commands=[COMMAND_START])
def main(message):
    # Создаём кнопки
    buttons = types.ReplyKeyboardMarkup(one_time_keyboard=True, row_width=True)
    buttons.add(types.KeyboardButton(COMMAND_TXT), types.KeyboardButton(COMMAND_PDF),
                types.KeyboardButton(COMMAND_DOCX))
    # Отправляем сообщение с кнопками
    msg = bot.send_message(message.chat.id, MESSAGE_START, reply_markup=buttons)
    bot.register_next_step_handler(msg, preprocessing_message)


# Функция обработчика текста
@bot.message_handler(content_types=['text'])
def preprocessing_message(message):
    if message.text == "TXT":
        cid = message.chat.id
        msg = bot.send_message(cid, "Отправьте текст!")
        bot.register_next_step_handler(msg, processing_txt_documents)
    elif message.text == "PDF":
        # cid = message.chat.id
        # msg = bot.send_message(cid, "Отправьте pdf файл!")
        # bot.register_next_step_handler(msg, processing_pdf_documents)
        bot.send_message(message.chat.id, text="(。﹏。*)")
        bot.send_message(message.chat.id, text='Функция "PDF" в разработке'
                                               '\nВоспользуйтесь другим моим функционалом /start')
    elif message.text == "DOCX":
        # cid = message.chat.id
        # msg = bot.send_message(cid, "Отправьте docx файл!")
        # bot.register_next_step_handler(msg, processing_docx_documents)
        bot.send_message(message.chat.id, text='⊙﹏⊙∥')
        bot.send_message(message.chat.id, text='Функция "DOCX" в разработке!'
                                               '\nВоспользуйтесь другим моим функционалом /hello')
    else:
        bot.reply_backend(message.chat.id, text="Я не понимаю вас (┬┬﹏┬┬)"
                                                "\nПерейдите в /help, чтобы познакомиться со мной поближе ╰(*°▽°*)╯")


def processing_txt_documents(message):
    global result
    # Прочитайте данные из Excel-файла в DataFrame
    df = pd.read_excel('Справочник_услуг.xlsx')
    # подключаемся к базе
    con = sl.connect('bd_biomind.db')
    cur = con.cursor()
    # получаем сегодняшнюю дату
    now = datetime.now(timezone.utc)
    date = now.date()
    # получаем user_id
    user_id = message.from_user.id
    # user_name
    user_name = message.from_user.username
    # text
    text = message.text

    sql_count = """
    SELECT COUNT(*) 
    FROM bd_biomind 
    WHERE user_id = ?"""
    # проверяем количество записей для данного user_id
    cur.execute(sql_count, (user_id,))
    count = cur.fetchone()[0]

    sql_limit = """
    DELETE FROM bd_biomind WHERE user_id = ? 
    AND datetime = (SELECT MIN(datetime) 
    FROM bd_biomind WHERE user_id = ?)"""
    # Если количество записей превышает 3, удаляем самую старую
    if count >= 3:
        cur.execute(sql_limit, (user_id, user_id))

    # формируем данные для запроса
    data = [
        (str(now), str(date), int(user_id), str(user_name), str(text))
    ]
    sql_insert = """INSERT INTO bd_biomind (datetime, date, user_id, user_name, text) values(?, ?, ?, ?, ?)"""
    # добавляем новую запись
    cur.executemany(sql_insert, data)
    con.commit()

    # отправляем пользователю сообщение о том, что отчёт принят
    bot.send_message(message.from_user.id, 'Принято, спасибо! Ваше письмо в обработке.', parse_mode='Markdown')

    # Найдем запись с самой поздней датой для данного user_id
    query_latest_text = """
    SELECT text 
    FROM bd_biomind 
    WHERE user_id = ? 
    ORDER BY datetime DESC LIMIT 1"""
    cur.execute(query_latest_text, (user_id,))
    result = cur.fetchone()

    binary_classifier = BertBinaryClassifier()
    class_predict = binary_classifier.predict(result)

    update_table = """
                        UPDATE bd_biomind
                        SET class_classification = ?,
                            code_service = ?,
                            description_service = ?
                        WHERE user_id = ?
                        AND datetime = (
                        SELECT MAX(datetime)
                        FROM bd_biomind
                        WHERE user_id = ?
                                        )"""

    # Если класс письма 1 - есть услуги
    if class_predict == 1:
        multiclass_classifier = BertMulticlassClassifier()
        code_service_predict = multiclass_classifier.predict(str(result))
        # Получение списка индексов услуг, предоставляемых пользователю
        services_provided = [index for index, value in enumerate(code_service_predict) if value]

        if services_provided:
            # Фильтрация DataFrame для получения соответствующих значений ServiceCode и ServiceName
            relevant_services = df[df['service_id'].isin(services_provided)]
            # Создание объединенной строки со значением "ServiceCode ServiceName"
            combined_service_info = relevant_services.apply(
                lambda row: f"{row['ServiceCode']}: {row['ServiceName']}", axis=1
            ).str.cat(sep=';\n')

            # Отправляем пользователю сообщение со списком кодов услуг
            bot.send_message(user_id, f'Предоставляемые услуги:\n{combined_service_info}', parse_mode='Markdown')
            bot.send_message(user_id, text="Выход в главное меню /hello", parse_mode='Markdown')

            # Подготовка значений для обновления
            update_values = (int(class_predict), str(services_provided), combined_service_info)
            # Выполняем запрос с данными: обновляем таблицу
            with con:
                cur.execute(update_table,  (*update_values, user_id, user_id))
                con.commit()

        else:
            class_predict = 0
            combined_service_info = 'Нет услуг'
            bot.send_message(user_id, f'Услуги не найдены: {class_predict}', parse_mode='Markdown')
            bot.send_message(user_id, text="Выход в главное меню /hello", parse_mode='Markdown')

            update_values = (int(class_predict), str(services_provided), combined_service_info)
            with con:
                cur.execute(update_table, (*update_values, user_id, user_id))
                con.commit()

        con.close()

    else:
        class_predict = 0
        bot.send_message(user_id, f'Услуги не найдены: {class_predict}', parse_mode='Markdown')
        bot.send_message(user_id, text="Выход в главное меню /hello", parse_mode='Markdown')

        update_values = (int(class_predict), str(0), str('Нет услуг'))
        with con:
            cur.execute(update_table, (*update_values, user_id, user_id))
            con.commit()

        con.close()


def processing_pdf_documents(message):
    pass


def processing_docx_documents(message):
    pass


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
#bot.infinity_polling()
while True:
    # в бесконечном цикле постоянно опрашиваем бота — есть ли новые сообщения
    try:
        bot.polling(none_stop=True, interval=0)
    # если возникла ошибка — сообщаем про исключение и продолжаем работу
    except Exception as e:
        print('❌❌❌❌❌ Сработало исключение! ❌❌❌❌❌')
