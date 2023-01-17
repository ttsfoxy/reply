import telebot
import logging
import traceback
import time
import sqlite3
from settings_win import start_dir, id_bot, lg_file, database_db, my_id


def connectsql():                # коннект к базе
    try:
        db_path = start_dir + database_db
        conn_to_base = sqlite3.connect(db_path, timeout=15)
        return (conn_to_base)
    except Exception:
        conn_to_base.close()
        logging.error('CONNECTSQL ERROR ' + db_path + ' ' + str(traceback.format_exc()))


def create_table():
    conn = connectsql()
    conn.execute("CREATE TABLE IF NOT EXIST messages(id_user integer, id_message_from integer,\
                 id_to integer)")
    conn.commit()
    conn.close()


def write_to_base(message, x_id):
    try:
        id_user = message.chat.id
        id_message_from = message.message_id
        id_to = x_id
        conn = connectsql()
        conn.execute("INSERT INTO messages(id_user, id_message_from, id_to) values(?,?,?)",
                     (id_user, id_message_from, id_to))
        conn.commit()
        conn.close()
    except Exception:
        logging.error('у меня ошибка в write_to_base ' + str(traceback.format_exc()))


def get_base(reply):
    try:
        conn = connectsql()
        info = conn.execute("SELECT * FROM messages WHERE id_to=?", (reply,))
        date = info.fetchone()
        conn.close()
        return (date)
    except Exception:
        logging.error('у меня ошибка в get_base ' + str(traceback.format_exc()))


bot = telebot.TeleBot(id_bot)
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, filename=(start_dir + lg_file), format="%(asctime)s \
        - %(levelname)s - %(funcName)s: %(lineno)d - %(message)s")

    logging.info('Started')

    @bot.message_handler(content_types=["photo", "text"])
    def start_handler(message):

        if message.from_user.id != my_id:
            x = bot.forward_message(my_id, message.chat.id, message.message_id)
            write_to_base(message, x.message_id)
        if message.from_user.id == my_id and message.reply_to_message is not None:
            id_user, id_message_from, id_to = get_base(message.reply_to_message.message_id)
            bot.send_message(id_user, message.text, reply_to_message_id=id_message_from)

    while True:
        try:

            bot.polling(none_stop=True, interval=1, allowed_updates='chat_member')

            # Предполагаю, что бот может мирно завершить работу, поэтому
            # даем выйти из цикла

        except Exception:
            logging.error('у меня ошибка внутренняя' + str(traceback.format_exc()))
            bot.stop_polling()
            time.sleep(10)
