import telebot
import Constants
import json
from pprint import pprint

bot = telebot.TeleBot(Constants.token)

print(bot.get_me())

data = ()
weekday =('Понедельник','Вторник','Среда','Четверг','Пятница', 'Суббота','Воскресенье')

def load_schedule():
    with open(Constants.schedule_file) as data_file:
        data = json.load(data_file)

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
    user_markup.row('Расписание', 'Изменения')
    bot.send_message(message.chat.id, 'Дратути)0', reply_markup=user_markup)

@bot.message_handler(commands=["stop"])
def handle_start(message):
    hide_markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 'Дотвидания(9(', reply_markup=hide_markup)


@bot.message_handler(content_types=["text"])
def handle_text(message):
    if message.text == 'Расписание':
        week_markup = telebot.types.ReplyKeyboardMarkup(True, True)
        week_markup.row('Понедельник', 'Вторник')
        week_markup.row('Среда', 'Четверг')
        week_markup.row('Пятница', 'Суббота')
        week_markup.row('Воскресенье')
        bot.send_message(reply_markup=week_markup)
    if any([message.text == i for i in weekday]):
        answer = "Расписание на {0}: \n1. {1} \n2. {2} \n3. {3} \n4. {4} \n5. {5}".format(
            message.text,
            data["Чётная"][weekday.index(message.text)]["1"],
            data["Чётная"][weekday.index(message.text)]["2"],
            data["Чётная"][weekday.index(message.text)]["3"],
            data["Чётная"][weekday.index(message.text)]["4"],
            data["Чётная"][weekday.index(message.text)]["5"])
        bot.send_message(message.chat.id, answer)
        log(message, answer)

bot.polling(none_stop=True, interval=0)
