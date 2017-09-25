import telebot
import Constants
import json
import datetime
from telebot import types
from telegramcalendar import create_calendar
import os
from flask import app

port = int(os.environ.get("PORT", 5000))
app.run(debug=True, host='0.0.0.0', port=port)

# Ипорт json файла расписания
def load_json(filetoopen):
    with open(filetoopen, 'r', encoding='utf-8') as f:
        jsonfile = json.load(f)
    print('Opened {0}'.format(filetoopen))
    return jsonfile

"""
Объявление переменных и объектов
"""
# Объект бота
bot = telebot.TeleBot(Constants.token)
# Json файл расписания
schedule = load_json(Constants.schedule_file)
changes = load_json(Constants.changes_file)
changesList = {}
# Список дней недели
weekday = ('Понедельник', 'Вторник', 'Среда', 'Четверг', 'Пятница', 'Суббота', 'Воскресенье')
evenlist = ('Чётная', 'Нечётная')
# Главная страница кастомной клавиатуры
user_markup = telebot.types.ReplyKeyboardMarkup(True, False)
user_markup.row('Расписание', 'Изменения')
user_markup.row('Календарь', 'Чётность недели')
user_markup.row('Расписание на завтра')
user_markup.row('Расписание на сегодня')
markupeven = 0
current_shown_dates={}

isGettingChanges = False
changesText = ''

isEven = False
firstDay = datetime.datetime(datetime.datetime.now().year, 9, 1, 0, 0, 0).timetuple().tm_yday
# Log информация о боте
print(bot.get_me())
# print(datetime.datetime.now().month)
# print(datetime.datetime(2017, 9, 1, 0, 0, 0).timetuple().tm_yday)
# print(datetime.datetime(2017, 9, 29, 0, 0, 0).timetuple().tm_yday)
# print(datetime.datetime.now().timetuple().tm_yday)

def check_even(date):
    try:
        weekend = max(list(range(firstDay, date.timetuple().tm_yday+1, 7)))
    except ValueError:
        weekend = 1
    if weekend-1 < date.timetuple().tm_yday:
        if ((weekend+7) - firstDay) / 7 % 2 == 0:
            return evenlist[0]
        else:
            return evenlist[1]
    elif weekend-1 >= date.timetuple().tm_yday:
        if (weekend - firstDay) / 7 % 2 == 0:
            return evenlist[0]
        else:
            return evenlist[1]

def show_schedule(first, second, var1, var2, date):
    return "Расписание на {0}, {1}, {7}: \n1. {2} \n2. {3} \n3. {4} \n4. {5} \n5. {6}".format(
            weekday[date.weekday()],
            "{0}.{1}".format(date.day, date.month),
            var2[first][second]["1"],
            var2[first][second]["2"],
            var2[first][second]["3"],
            var2[first][second]["4"],
            var2[first][second]["5"],
            var1)

def show_schedule_by_date(date):
    even_str = check_even(date)
    if "{0}{1}{2}".format(date.day, date.month, date.year) in changes:
        return show_schedule("{0}{1}{2}".format(date.day, date.month, date.year), 0, even_str, changes, date)
    else:
        return show_schedule(even_str, date.weekday(), even_str, schedule, date)

"""
            "Расписание на {0}, {1}, {7}: \n1. {2} \n2. {3} \n3. {4} \n4. {5} \n5. {6}".format(
            weekday[date.weekday()],
            "{0}.{1}".format(date.day, date.month),
            changes["{0}{1}{2}".format(date.day, date.month, date.year)][0]["1"],
            changes["{0}{1}{2}".format(date.day, date.month, date.year)][0]["2"],
            changes["{0}{1}{2}".format(date.day, date.month, date.year)][0]["3"],
            changes["{0}{1}{2}".format(date.day, date.month, date.year)][0]["4"],
            changes["{0}{1}{2}".format(date.day, date.month, date.year)][0]["5"],
            even_str)
"""
"""
            "Расписание на {0}, {1}, {7}: \n1. {2} \n2. {3} \n3. {4} \n4. {5} \n5. {6}".format(
            weekday[date.weekday()],
            "{0}.{1}".format(date.day, date.month),
            schedule[even_str][date.weekday()]["1"],
            schedule[even_str][date.weekday()]["2"],
            schedule[even_str][date.weekday()]["3"],
            schedule[even_str][date.weekday()]["4"],
            schedule[even_str][date.weekday()]["5"],
            even_str)
"""
def heh(var1,var2, var3, var4,var5):
    return [{'1':var1, '2':var2, '3':var3, '4':var4, '5':var5}]

# Функция ведения лога
def log(message, answer):
    print("\n ~~~~~~~")
    from datetime import datetime
    print(datetime.now())
    print("Сообщение от {0} {1}. id - {2}. \nТекст - {3}".
          format(message.from_user.first_name, message.from_user.last_name, str(message.from_user.id), message.text)
         )
    print(answer)

# Команда "/start"
@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id, 'Дратути)0'
                     , reply_markup=user_markup
                     )

"""
# Команда "/stop"
@bot.message_handler(commands=["stop"])
def handle_start(message):
    hide_markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 'Дотвидания(9(', reply_markup=hide_markup)
"""

# Обработка текстовых сообщений
@bot.message_handler(content_types=["text"])
def handle_text(message):
    global markupeven
    global changes
    if message.text == 'Расписание на завтра':
        try:
            answer = show_schedule_by_date(datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month, datetime.datetime.now().day+1, datetime.datetime.now().hour,datetime.datetime.now().minute, datetime.datetime.now().second))
        except ValueError:
            answer = show_schedule_by_date(datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month+1, 1, datetime.datetime.now().hour,datetime.datetime.now().minute, datetime.datetime.now().second))
        bot.send_message(message.chat.id, answer)
        log(message, answer)
        bot.send_message(message.chat.id, 'Чем ещё помочь?', reply_markup=user_markup)
    if message.text == 'Расписание на сегодня':
        answer = show_schedule_by_date(datetime.datetime.now())
        bot.send_message(message.chat.id, answer)
        log(message, answer)
        bot.send_message(message.chat.id, 'Чем ещё помочь?', reply_markup=user_markup)
    if message.text == 'Расписание':
        even_markup = telebot.types.ReplyKeyboardMarkup(True, True)
        even_markup.row('Чётная', 'Нечётная')
        bot.send_message(message.chat.id, 'Выберите чётность недели', reply_markup=even_markup)
    if message.text == 'Чётная' or message.text == 'Нечётная':
        if message.text == 'Чётная':
            markupeven = 0
        if message.text == 'Нечётная':
            markupeven = 1
        week_markup = telebot.types.ReplyKeyboardMarkup(True, True)
        week_markup.row('Понедельник', 'Вторник')
        week_markup.row('Среда', 'Четверг')
        week_markup.row('Пятница', 'Суббота')
        week_markup.row('Воскресенье')
        bot.send_message(message.chat.id, 'Выберите день', reply_markup=week_markup)
    if any([message.text == i for i in weekday]):
        answer = "Расписание на {0}, {6}: \n1. {1} \n2. {2} \n3. {3} \n4. {4} \n5. {5}".format(
            message.text,
            schedule[evenlist[markupeven]][weekday.index(message.text)]["1"],
            schedule[evenlist[markupeven]][weekday.index(message.text)]["2"],
            schedule[evenlist[markupeven]][weekday.index(message.text)]["3"],
            schedule[evenlist[markupeven]][weekday.index(message.text)]["4"],
            schedule[evenlist[markupeven]][weekday.index(message.text)]["5"],
            evenlist[markupeven])
        bot.send_message(message.chat.id, answer)
        log(message, answer)
        bot.send_message(message.chat.id, 'Чем ещё помочь?', reply_markup=user_markup)
    if message.text == 'Календарь':
        changes = load_json(Constants.changes_file)
        now = datetime.datetime.now()  # Current date
        chat_id = message.chat.id
        date = (now.year, now.month)
        current_shown_dates[chat_id] = date  # Saving the current date in a dict
        markup = create_calendar(now.year, now.month)
        bot.send_message(message.chat.id, "Выберите дату", reply_markup=markup)
    if message.text == 'Чётность недели':
        answer = "Сейчас {0} неделя".format(check_even(datetime.datetime.now()))
        bot.send_message(message.chat.id, answer)
        log(message, answer)
        bot.send_message(message.chat.id, 'Чем ещё помочь?', reply_markup=user_markup)
    if "!ИЗМЕНЕНИЯ" in message.text:
        changes = load_json(Constants.changes_file)
        global changesList
        changesList = changes
        global isGettingChanges
        isGettingChanges = True;
        global changesText
        changesText = message.text.splitlines()

        now = datetime.datetime.now()  # Current date
        chat_id = message.chat.id
        date = (now.year, now.month)
        current_shown_dates[chat_id] = date  # Saving the current date in a dict
        markup = create_calendar(now.year, now.month)
        bot.send_message(message.chat.id, "Выберите дату", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data[0:13] == 'calendar-day-')
def get_day(call):
    global changesList
    global isGettingChanges
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        day=call.data[13:]
        date = datetime.datetime(int(saved_date[0]),int(saved_date[1]),int(day),0,0,0)
        if not isGettingChanges:
            if date.month >= 9 or (date.month <= 6 and not date.year  <= 2017):
                bot.send_message(chat_id, show_schedule_by_date(date))
                bot.answer_callback_query(call.id, text="")
            else:
                bot.send_message(chat_id, 'Ошибочка')
                bot.answer_callback_query(call.id, text="")
        else:
            try:
                changesList["{0}{1}{2}".format(date.day, date.month, date.year)] = heh(changesText[1], changesText[2],
                                                                                       changesText[3], changesText[4],
                                                                                       changesText[5])
                with open(Constants.changes_file, 'w', encoding='utf-8') as f:
                    json.dump(changesList, f)
                bot.send_message(chat_id, 'Успешно')
                isGettingChanges = False
                bot.answer_callback_query(call.id, text="")
            except IndexError:
                changesList["{0}{1}{2}".format(date.day, date.month, date.year)] = heh('-', '-',
                                                                                       '-', '-',
                                                                                       '-')
                with open(Constants.changes_file, 'w', encoding='utf-8') as f:
                    json.dump(changesList, f)
                bot.send_message(chat_id, 'Успешно')
                isGettingChanges = False
                bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'next-month')
def next_month(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        year,month = saved_date
        month+=1
        if month>12:
            month=1
            year+=1
        date = (year,month)
        current_shown_dates[chat_id] = date
        markup= create_calendar(year,month)
        bot.edit_message_text("Выберите дату", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'previous-month')
def previous_month(call):
    chat_id = call.message.chat.id
    saved_date = current_shown_dates.get(chat_id)
    if(saved_date is not None):
        year, month = saved_date
        month -= 1
        if month < 9:
            month = 9
            #year-=1
        date = (year, month)
        current_shown_dates[chat_id] = date
        markup = create_calendar(year, month)
        bot.edit_message_text("Выберите дату", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        #Do something to inform of the error
        pass

bot.polling(none_stop=True, interval=0)