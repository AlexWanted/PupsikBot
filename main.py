import telebot
import Constants
import datetime
from telegramcalendar import create_calendar
from firebase import firebase

"""
Объявление переменных и объектов datetime
"""
db = firebase.FirebaseApplication('https://pupsikbot.firebaseio.com/')
c = Constants  #Файл констант
bot = telebot.TeleBot(c.token)  #Объект бота
currentShownDates = {}  #Показываемые в данный момент даты
firstDay = datetime.datetime(datetime.datetime.now().year-1, 9, 1, 0, 0, 0).timetuple().tm_yday  #Первый день учёбы
groupChatID = 0 #ИД группового чата
groupChatON = False

"""
Изменения в расписании
"""
changes = db.get('Изменения', None)
changesList = {}  #Словарь временного хранения введённого изменения
isGettingChanges = False  #Настраиваются ли изменения в данный момент
changesText = ''  #Хранение сообщения с изменениями

"""
Главная страница кастомной клавиатуры
"""
userMarkup = telebot.types.ReplyKeyboardMarkup(True, False)
userMarkup.row('Расписание', 'Расписание звонков')
userMarkup.row('Календарь', 'Чётность недели')
userMarkup.row('Расписание на завтра')
userMarkup.row('Расписание на сегодня')

print(bot.get_me())  #Вывод Log информации о боте

"""
Чётность недели
"""
markupEven = 0  #Чётность недели для клавиатуры
isEven = False  #Чётная ли неделя
#Проверка чётности недели
def check_even(date):
    try:
        weekend = max(list(range(firstDay, date.timetuple().tm_yday+1, 7)))
    except ValueError:
        weekend = 1
    if weekend-1 < date.timetuple().tm_yday:
        if ((weekend+7) - firstDay) / 7 % 2 == 0:
            return c.evenList[0]
        else:
            return c.evenList[1]
    elif weekend-1 >= date.timetuple().tm_yday:
        if (weekend - firstDay) / 7 % 2 == 0:
            return c.evenList[0]
        else:
            return c.evenList[1]

#Функция вывода расписания
def show_schedule(first, second, var1, var2, date):
    scheduleStr = "Расписание на {0}, {1}, {2}: ".format(c.weekdayList[date.weekday()], "{0}.{1}".format(date.day, date.month), var1)
    for i in range(1, len(var2[first][second])):
        scheduleStr += "\n"+str(i)+". "+str(var2[first][second][i])
    return scheduleStr

#Функция вывода расписания
def show_schedule(var1, var2, date):
    scheduleStr = "Расписание на {0}, {1}, {2}: ".format(c.weekdayList[date.weekday()], "{0}.{1}".format(date.day, date.month), var1)
    for i in range(1, len(var2)):
        scheduleStr += "\n"+str(i)+". "+str(var2[i])
    return scheduleStr

#Функция вывода расписания по дате
def show_schedule_by_date(date):
    evenStr = check_even(date)
    schedule = db.get('Расписание', None)
    changes = db.get("Изменения/", None)
    if "{0}{1}{2}".format(date.day, date.month, date.year) in changes:
        changes = db.get("Изменения/", "{0}{1}{2}".format(date.day, date.month, date.year))
        return show_schedule(evenStr, changes, date)
    else:
        return show_schedule(evenStr, c.weekdayList[date.weekday()], evenStr, schedule, date)

# Функция ведения лога
def log(message, answer):
    print("\n~~~~~~~")
    print(datetime.datetime.now())
    print("Сообщение от {0} {1}. id - {2}. \nТекст - {3}".
          format(message.from_user.first_name, message.from_user.last_name,
                 str(message.from_user.id), message.text))
    print(answer)
    print("\n~~~~~~~")

# Команда "/start"
@bot.message_handler(commands=["start"])
def handle_start(message):
    bot.send_message(message.chat.id, 'Дратути)0', reply_markup=userMarkup)

def get_admin_ids(bot, chat_id):
    return [admin.user.id for admin in bot.get_chat_administrators(chat_id)]

# Обработка текстовых сообщений
@bot.message_handler(content_types=["text"])
def handle_text(message):
    global markupEven
    global changes
    global changesList
    global isGettingChanges
    global changesText
    global groupChatID
    global groupChatON

    if message.chat.id == message.from_user.id:
        now = datetime.datetime.now()
        if message.text == 'Клавиатура':
            bot.send_message(message.chat.id, 'Чем могу помочь?', reply_markup=userMarkup)

        #Показать расписание на следующий день
        if message.text == 'Расписание на завтра':
            try:
                answer = show_schedule_by_date(
                    datetime.datetime(now.year, now.month,
                                      now.day + 1, 0, 0, 0))
            except ValueError:
                if now.day == 31 and now.month == 12:
                    answer = show_schedule_by_date(
                        datetime.datetime(now.year+1, 1,
                                          1, 0, 0, 0))
                else:
                    answer = show_schedule_by_date(
                        datetime.datetime(now.year, now.month + 1,
                                          1, 0, 0, 0))
            bot.send_message(message.chat.id, answer)
            log(message, answer)
            bot.send_message(message.chat.id, 'Чем ещё помочь?', reply_markup=userMarkup)

        #Показать расписание на сегодня
        if message.text == 'Расписание на сегодня':
            answer = show_schedule_by_date(datetime.datetime.now())
            bot.send_message(message.chat.id, answer)
            log(message, answer)
            bot.send_message(message.chat.id, 'Чем ещё помочь?', reply_markup=userMarkup)

        #Показать расписание звонков
        if message.text == 'Расписание звонков':
            for i in range(1,6):
                answer += "{0} пара: {1}".format(i, c.scheduleTime[i])
            bot.send_message(message.chat.id, answer)
            log(message, answer)
            bot.send_message(message.chat.id, 'Чем ещё помочь?', reply_markup=userMarkup)

        #Вывод клавиатуры выброра чётности
        if message.text == 'Расписание':
            even_markup = telebot.types.ReplyKeyboardMarkup(True, True)
            even_markup.row('Чётная', 'Нечётная')
            bot.send_message(message.chat.id, 'Выберите чётность недели', reply_markup=even_markup)

        #Выбор дня недели
        if message.text == 'Чётная' or message.text == 'Нечётная':
            if message.text == 'Чётная':
                markupEven = 0
            if message.text == 'Нечётная':
                markupEven = 1
            weekMarkup = telebot.types.ReplyKeyboardMarkup(True, True)
            weekMarkup.row('Понедельник', 'Вторник')
            weekMarkup.row('Среда', 'Четверг')
            weekMarkup.row('Пятница', 'Суббота')
            weekMarkup.row('Воскресенье')
            bot.send_message(message.chat.id, 'Выберите день', reply_markup=weekMarkup)

        #Вывод расписания на выбранный день недели
        if any([message.text == i for i in c.weekdayList]):
            answer = "Расписание на {0}, {1}: ".format(message.text, c.evenList[markupEven])
            schedule = db.get("Расписание", None)
            for i in range(1, len(schedule[c.evenList[markupEven]][message.text])):
                answer += "\n" + str(i) + ". " + str(schedule[c.evenList[markupEven]][message.text][i])
            bot.send_message(message.chat.id, answer)
            log(message, answer)
            bot.send_message(message.chat.id, 'Чем ещё помочь?', reply_markup=userMarkup)

        #Показать календарь
        if message.text == 'Календарь':
            changes = db.get('Изменения', None)
            show_calendar(message)

        #Вывести чётность текущей недели
        if message.text == 'Чётность недели':
            answer = "Сейчас {0} неделя".format(check_even(datetime.datetime.now()))
            bot.send_message(message.chat.id, answer)
            log(message, answer)
            bot.send_message(message.chat.id, 'Чем ещё помочь?', reply_markup=userMarkup)

        #Внести изменения в расписание
        if "!ИЗМЕНЕНИЯ" in message.text and (message.from_user.id == 246495886 or message.from_user.id == 110455487):
            changes = db.get('Изменения', None)
            changesList = changes
            isGettingChanges = True
            changesText = message.text.splitlines()
            show_calendar(message)
    else:
        if message.text == '!on' and message.from_user.id in get_admin_ids(bot, message.chat.id) and not groupChatON:
            groupChatON = True
            groupChatID = message.chat.id
            print('Успешно')
            start_group()
        if message.text == '!off' and message.from_user.id in get_admin_ids(bot, message.chat.id):
            groupChatON = False
            groupChatID = 0
            print('Отключено')
        if message.text == '!Расписание на завтра' and message.from_user.id in get_admin_ids(bot, message.chat.id):
            try:
                answer = show_schedule_by_date(
                    datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month,
                                      datetime.datetime.now().day + 1, 0, 0, 0))
            except ValueError:
                if datetime.now().day == 31 and datetime.date().month == 12:
                    answer = show_schedule_by_date(
                        datetime.datetime(datetime.datetime.now().year+1, 1,
                                          1, 0, 0, 0))
                else:
                    answer = show_schedule_by_date(
                        datetime.datetime(datetime.datetime.now().year, datetime.datetime.now().month + 1,
                                          1, 0, 0, 0))
            bot.send_message(message.chat.id, answer)
        if message.text == '!Расписание' and message.from_user.id in get_admin_ids(bot, message.chat.id):
            answer = show_schedule_by_date(datetime.datetime.now())
            bot.send_message(message.chat.id, answer)

def start_group():
    global groupChatID
    global groupChatON
    isSended = False
    now = datetime.datetime.now()
    
    while groupChatON:
        if (now.hour == 7) and (now.minute == 0) and (now.second == 0) and not isSended:
            answer = show_schedule_by_date(datetime.datetime.now())
            bot.send_message(groupChatID, answer)
            isSended = True
        if (now.hour == 7) and (now.minute == 0) and (now.second == 2) and isSended:
            isSended = False
        if ((now.hour == 18) or (now.hour == 23)) and (now.minute == 0) and (now.second == 0) and not isSended:
            try:
                answer = show_schedule_by_date(datetime.datetime(now.year, now.month, now.day + 1, 0, 0, 0))
            except ValueError:
                if now.day == 31 and now.month == 12:
                    answer = show_schedule_by_date(datetime.datetime(now.year + 1, 1, 1, 0, 0, 0))
                else:
                    answer = show_schedule_by_date( datetime.datetime(now.year, now.month + 1, 1, 0, 0, 0))
            bot.send_message(groupChatID, answer)

#Функция вызова календаря
def show_calendar(message):
    chat_id = message.chat.id
    date = (datetime.datetime.now().year, datetime.datetime.now().month)
    currentShownDates[chat_id] = date
    markup = create_calendar(datetime.datetime.now().year, datetime.datetime.now().month)
    bot.send_message(message.chat.id, "Выберите дату", reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data[0:13] == 'calendar-day-')
#Выбор дня в календаре
def get_day(call):
    global changesList
    global isGettingChanges
    chatID = call.message.chat.id
    savedDate = currentShownDates.get(chatID)

    if savedDate is not None:
        day = call.data[13:]
        date = datetime.datetime(int(savedDate[0]),int(savedDate[1]),int(day),0,0,0)
        if not isGettingChanges:
            if date.month >= 9 or (date.month <= 6 and not date.year  <= 2017):
                bot.send_message(chatID, show_schedule_by_date(date))
                bot.answer_callback_query(call.id, text="")
            else:
                bot.send_message(chatID, 'Ошибочка')
                bot.answer_callback_query(call.id, text="")
        else:
            try:
                print(len(changesText))
                changesDict = {}
                for i in range(1, len(changesText)):
                    changesDict[i] = changesText[i]
                db.put('Изменения', "{0}{1}{2}".format(date.day, date.month, date.year), changesDict)
                bot.send_message(chatID, 'Успешно')
                isGettingChanges = False
                bot.answer_callback_query(call.id, text="")
            except IndexError:
                changesDict = {}
                for i in range(1, 5):
                    changesDict[i] = "-"
                db.put('Изменения', "{0}{1}{2}".format(date.day, date.month, date.year), changesDict)
                bot.send_message(chatID, 'Успешно')
                isGettingChanges = False
                bot.answer_callback_query(call.id, text="")
    else:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'next-month')
#Перейти на следующий месяц
def next_month(call):
    chatID = call.message.chat.id
    savedDate = currentShownDates.get(chatID)

    if savedDate is not None:
        year, month = savedDate
        month += 1
        if month > 12:
            month = 1
            year += 1
        date = (year,month)
        currentShownDates[chatID] = date
        markup = create_calendar(year,month)
        bot.edit_message_text("Выберите дату", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        pass

@bot.callback_query_handler(func=lambda call: call.data == 'previous-month')
#Перейти на предыдущий месяц
def previous_month(call):
    chatID = call.message.chat.id
    savedDate = currentShownDates.get(chatID)

    if savedDate is not None:
        year, month = savedDate
        month -= 1
        if month < 1:
            month = 12
            year -= 1
        date = (year, month)
        currentShownDates[chatID] = date
        markup = create_calendar(year, month)
        bot.edit_message_text("Выберите дату", call.from_user.id, call.message.message_id, reply_markup=markup)
        bot.answer_callback_query(call.id, text="")
    else:
        pass

bot.polling(none_stop=True, interval=0)