import telebot
import Constants
import json
import datetime
from telegramcalendar import create_calendar

# Ипорт json файла расписания
def load_json(filetoopen):
    with open(filetoopen, 'r', encoding='utf-8') as f:
        jsonfile = json.load(f)
    print('Opened {0}'.format(filetoopen))
    return jsonfile

#Внести данные в json файл
def dump_json(datatowrite, filetoopen):
    with open(filetoopen, 'w', encoding='utf-8') as f:
        json.dump(datatowrite, f)

"""
Объявление переменных и объектовdatetime
"""
c = Constants  #Файл констант
bot = telebot.TeleBot(c.token)  #Объект бота
schedule = load_json(c.scheduleFile)  #Json файл расписания
currentShownDates = {}  #Показываемые в данный момент даты
firstDay = datetime.datetime(datetime.datetime.now().year, 9, 1, 0, 0, 0).timetuple().tm_yday  #Первый день учёбы
groupChatID = 0 #ИД группового чата
groupChatON = False

"""
Изменения в расписании
"""
changes = load_json(c.changesFile) #Json файл изменений
changesList = {}  #Словарь временного хранения введённого изменения
isGettingChanges = False  #Настраиваются ли изменения в данный момент
changesText = ''  #Хранение сообщения с изменениями

"""
Главная страница кастомной клавиатуры
"""
userMarkup = telebot.types.ReplyKeyboardMarkup(True, False)
userMarkup.row('Расписание', 'Информация')
userMarkup.row('Календарь', 'Чётность недели')
userMarkup.row('Расписание на завтра')
userMarkup.row('Расписание на сегодня')

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

print(bot.get_me())  #Вывод Log информации о боте


#Функция вывода расписания
def show_schedule(first, second, var1, var2, date):
    return "Расписание на {0}, {1}, {7}: \n1. {2} \n2. {3} \n3. {4} \n4. {5} \n5. {6}".format(
            c.weekdayList[date.weekday()], "{0}.{1}".format(date.day, date.month),
            var2[first][second]["1"], var2[first][second]["2"],
            var2[first][second]["3"], var2[first][second]["4"],
            var2[first][second]["5"], var1)


#Функция вывода расписания по дате
def show_schedule_by_date(date):
    evenStr = check_even(date)
    if "{0}{1}{2}".format(date.day, date.month, date.year) in changes:
        return show_schedule("{0}{1}{2}".format(date.day, date.month, date.year), 0, evenStr, changes, date)
    else:
        return show_schedule(evenStr, date.weekday(), evenStr, schedule, date)


#Возврат словаря с изменениями
def changes_text(var1, var2, var3, var4, var5):
    return [{'1': var1, '2': var2,
             '3': var3, '4': var4,
             '5': var5}]


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

"""
# Команда "/stop"
@bot.message_handler(commands=["stop"])
def handle_start(message):
    hide_markup = telebot.types.ReplyKeyboardRemove()
    bot.send_message(message.chat.id, 'Дотвидания(9(', reply_markup=hide_markup)
"""

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
        #Показать расписание на следующий день
        now = datetime.datetime.now()
        if message.text == 'Клавиатура':
            bot.send_message(message.chat.id, 'Чем могу помочь?', reply_markup=userMarkup)
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
            answer = "Расписание на {0}, {6}: \n1. {1} \n2. {2} \n3. {3} \n4. {4} \n5. {5}".format(
                message.text,
                schedule[c.evenList[markupEven]][c.weekdayList.index(message.text)]["1"],
                schedule[c.evenList[markupEven]][c.weekdayList.index(message.text)]["2"],
                schedule[c.evenList[markupEven]][c.weekdayList.index(message.text)]["3"],
                schedule[c.evenList[markupEven]][c.weekdayList.index(message.text)]["4"],
                schedule[c.evenList[markupEven]][c.weekdayList.index(message.text)]["5"],
                c.evenList[markupEven])
            bot.send_message(message.chat.id, answer)
            log(message, answer)
            bot.send_message(message.chat.id, 'Чем ещё помочь?', reply_markup=userMarkup)

        #Показать календарь
        if message.text == 'Календарь':
            changes = load_json(c.changesFile)
            show_calendar(message)

        #Вывести чётность текущей недели
        if message.text == 'Чётность недели':
            answer = "Сейчас {0} неделя".format(check_even(datetime.datetime.now()))
            bot.send_message(message.chat.id, answer)
            log(message, answer)
            bot.send_message(message.chat.id, 'Чем ещё помочь?', reply_markup=userMarkup)

        #Внести изменения в расписание
        if "!ИЗМЕНЕНИЯ" in message.text and (message.from_user.id == 246495886 or message.from_user.id == 110455487):
            changes = load_json(c.changesFile)
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
                changesList["{0}{1}{2}".format(date.day, date.month, date.year)] = changes_text(changesText[1],
                                                                                                changesText[2],
                                                                                                changesText[3],
                                                                                                changesText[4],
                                                                                                changesText[5])
                dump_json(changesList, c.changesFile)
                bot.send_message(chatID, 'Успешно')
                isGettingChanges = False
                bot.answer_callback_query(call.id, text="")
            except IndexError:
                changesList["{0}{1}{2}".format(date.day, date.month, date.year)] = changes_text('-', '-',
                                                                                                '-', '-',
                                                                                                '-')
                dump_json(changesList, c.changesFile)
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