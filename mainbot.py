import telebot
import Constants

bot = telebot.TeleBot(Constants.token)

print(bot.get_me())

def log(message, answer):
    print("\n ~~~~~~~")
    from datetime import datetime
    print(datetime.now())
    print("Сообщение от {0} {1}. id - {2}. \nТекст - {3}".
          format(message.from_user.first_name, message.from_user.last_name, str(message.from_user.id), message.text)
         )
    print(answer)

@bot.message_handler(commands=["start"])
def handle_start(message):
    user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
    user_markup.row('!Расписание', '!Изменения')
    bot.send_message(message.chat.id, 'Дратути)0', reply_markup=user_markup)

@bot.message_handler(commands=["stop"])
def handle_start(message):
    hide_markup = telebot.types.ReplyKeyboardHide
    bot.send_message(message.chat.id, 'Дотвидания(9(', reply_markup=hide_markup)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    answer = "Ты пидор"
    bot.send_message(message.chat.id, answer)
    log(message, answer)

bot.polling(none_stop=True, interval=0)
