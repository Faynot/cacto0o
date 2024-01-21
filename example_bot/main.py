from telebot.async_telebot import AsyncTeleBot
import logging
from telebot import types
import asyncio
import json
from dotenv import load_dotenv
import os


BANNED_FILE = 'banned.json'
TOPICS_FILE = 'topics.json'

load_dotenv()

PROXY_URL = "http://proxy.server:3128"
bot = Bot(token=os.environ.get('6032318418:AAE6aMj7lkGmh9SYUmisafAPrhNOJ0dVpEQ'), proxy=PROXY_URL)
dp = Dispatcher(bot)

chat_id = -1002033663463

user_topics = {}  # Хранятся привязанные к пользователю темы(message_thread_id), по которым бот будет пересылать сообщения
user_ids = {}  # Хранятся привязанные к темам айди личных сообщений, по которым можно ответить
banned = []  # Хранятся забаненные айди личных сообщений


def load_banned_users():
    try:
        with open(BANNED_FILE, 'r') as file:
            banned = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        banned = []
    return banned


def save_banned_users(banned):
    with open(BANNED_FILE, 'w') as file:
        json.dump(banned, file)


def load_topics_users():
    try:
        with open(TOPICS_FILE, 'r') as file:
            user_topics = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        user_topics = []
    return user_topics


def save_banned_users(banned):
    with open(BANNED_FILE, 'w') as file:
        json.dump(banned, file)


def save_topics_users(user_topics):
    with open(TOPICS_FILE, 'w') as file:
        json.dump(user_topics, file)


# Загрузка данных при запуске бота
banned = load_banned_users()
user_topics = load_banned_users()


@bot.message_handler(commands=['helps'])  # /helps
async def helps(message: types.Message):
    if message.chat.type == 'private':  # Если личные сообщения
        await bot.reply_to(message, 'поддержка - @faynotobglotish')


@bot.message_handler(commands=['start'])  # /start
async def start(message: types.Message):
    if message.chat.type == 'private':  # Если личные сообщения
        await bot.reply_to(message,
                           '🚨 Чтобы получить вознаграждение (деньги):\n1. Укажите ссылку на видео \n2. Приложите доказательство того, что аккаунт, на котором опубликовано видео, принадлежит вам \n3. Укажите свои реквизиты для получения вознаграждения 💰\n🔴Условия для получения вознаграждения:\n1) от 150.000 просмотров в тт/ютуб шортсы— 700 рублей 💲\n2) от 1.000.000  просмотров в тт/ютуб шортсы —  4000 рублей 💲\n\n❕ВАЖНО❕\n1. Если ваше видео набрало 150к, и в течении 2 недель после момента опубликования добило 1млн, вы можете обратиться за получением ДОПЛАТЫ до 3500 (условно вы набрали 150к -> получили 600руб, и если за 2 недели доберется миллион, я доплачу ещё 2900руб)\n2. Вознаграждение выдается только за видео с участием Cacto0o  (вырезки со стримов, забавные моменты, мемы, эдиты)\nP.S. МОМЕНТЫ С ПЕРСОНАЖАМИ ПО ТИПУ ФУРЫ, СТРУГАНМЕНА МИМО, НУЖНЫ ВИДЕО С ЛИЦОМ cacto0o\n3. ОБЯЗАТЕЛЬНО, чтобы на самом видео или в начале описания к видео было упоминание твич канала (например: twitch: Cacto0o) и  #cacto0o #КостикКакто (второй хештег не обязателен, но было бы славно если бы его тоже писали, что бы было сразу понятно что видео новое)\n4. Вознаграждение выдается только за видео, опубликованные с 15.01.2024 \n5. Модерация имеет право отказать в выдаче вознаграждения')


@bot.callback_query_handler(func=lambda call: call.data.startswith('ban'))  # Обработчик кнопки бана
async def pingall_action(call: types.CallbackQuery):
    global banned, user_topics, user_ids

    user_id = int(call.data.split('_')[1])  # Получения айди пользователя из коллбэка
    thread_id = int(call.data.split('_')[2])  # Получения айди темы из коллбэка

    await bot.send_message(user_ids[thread_id],  # Отправить сообщению о бане в личные сообщения
                           '*ТЕБЯ ЗАБАНИЛИ*',  # Текст о бане ЖИРНЫМ текстом
                           parse_mode='MarkdownV2')  # Режим парсинга, чтобы *текст* работало
    banned.append(user_id)  # Добавить пользователя в список забаненных
    save_banned_users(banned)  # Сохранение нового списка забаненных
    await bot.delete_forum_topic(chat_id, thread_id)  # Удалить тему пользователя(ибо нехуй)


@bot.message_handler(func=lambda message: True,
                     content_types=['text', 'photo', 'animation', 'voice', 'sticker', 'audio',
                                    'document'])  # Главный обработчик
async def main_handler(message: types.Message):
    global user_ids, user_topics, chat_id, banned

    print(message.content_type)

    if message.chat.type == 'private':  # Если личная переписка с ботом
        if message.from_user.id not in banned:  # Проверка не в списке забаненных ли пользователь
            if user_topics.get(message.from_user.id) != None:  # Если к пользователю привязана тема
                await bot.forward_message(chat_id,  # Сообщение отправляется в группу
                                          message.chat.id,  # Айди чата переписки
                                          message.id,  # Айди сообщения
                                          message_thread_id=user_topics[
                                              message.from_user.id])  # Айди темы равно теме извлечённой по этому айди юзера
            else:  # Если к пользователю не привязана тема
                topic = await bot.create_forum_topic(chat_id,  # Создание темы в группе
                                                     f'{message.from_user.full_name} @{message.from_user.username}')  # Название темы в формате "Имя @никнейм, пример - "Sobaka Zlaya @sobaka3laya", на случай если..
                # у кого-то нет имени или никнейма
                user_topics[message.from_user.id] = topic.message_thread_id  # Привязывание айди темы
                user_ids[topic.message_thread_id] = message.chat.id  # Привязывание айди личных сообщений к теме

                markup = types.InlineKeyboardMarkup()
                markup.add(types.InlineKeyboardButton('❌ БАН ❌',
                                                      callback_data=f'ban_{message.from_user.id}_{topic.message_thread_id}'))  # Создание кнопки бана с коллбэком формата ban_айдиюзера_айдитемы
                await bot.send_message(chat_id,
                                       # Отправление сообщения о новом диалоге, по сути существует для прикрепления кнопки бана
                                       f'Сообщение от нового пользователя @{message.from_user.username} {message.from_user.full_name}',
                                       reply_markup=markup,
                                       message_thread_id=topic.message_thread_id)  # Прикрепление кнопки бана
                await bot.forward_message(chat_id,  # Сообщение отправляется в группу
                                          message.chat.id,  # Айди чата переписки
                                          message.id,  # Айди сообщения
                                          message_thread_id=user_topics[
                                              message.from_user.id])  # Айди темы равно теме извлечённой по этому айди юзера
        else:  # Если в списке забаненных
            await bot.send_message(message.chat.id,  # Отправить сообщение о том, что пользователь забанен
                                   '*ТЫ ЗАБАНЕН ШКИЛА*',  # Сообщение о бане ЖИРНЫМ текстом
                                   parse_mode='MarkdownV2')  # Режим парсинга, чтобы *текст* работало
    else:  # Если не личная переписка(обратная связь)
        match message.content_type:  # Проверка типа сообщения
            case 'text':  # Если текст
                await bot.send_message(user_ids[message.message_thread_id],  # Отправление в лс этого юзера
                                       message.text)  # Текст из сообщения
            case 'photo':  # Если картинка
                await bot.send_photo(user_ids[message.message_thread_id],  # Отправление в лс этого юзера
                                     message.photo,  # Картинка из сообщения
                                     message.caption)  # Подпись картинки
            case 'animation':  # Если гифка
                await bot.send_animation(user_ids[message.message_thread_id],  # Отправление в лс этого юзера
                                         message.animation.file_id,  # Гифка из сообщения
                                         caption=message.caption)  # Подпись гифки
            case 'voice':  # Если голосовуха
                await bot.send_voice(user_ids[message.message_thread_id],  # Отправление в лс этого юзера
                                     message.voice.file_id)  # Эта голосовуха
            case 'sticker':  # Если стикер
                await bot.send_sticker(user_ids[message.message_thread_id],  # Отправление в лс этого юзера
                                       message.sticker.file_id)  # Этот стикер
            case 'audio':  # Если аудио
                await bot.send_audio(user_ids[message.message_thread_id],  # Отправление в лс этого юзера
                                     message.audio.file_id,  # Аудио из сообщения
                                     message.caption)  # Подпись из сообщения
            case 'document':  # Документ?
                await bot.send_document(user_ids[message.message_thread_id],  # Отправление в лс этого юзера
                                        message.document.file_id,  # Документ из сообщения
                                        caption=message.caption)  # Подпись из сообщения


asyncio.run(bot.infinity_polling())
