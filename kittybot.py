import logging
import os
import requests

from logging.handlers import RotatingFileHandler
from telegram import ReplyKeyboardMarkup
from telegram.ext import CommandHandler, Filters, MessageHandler, Updater

from dotenv import load_dotenv


load_dotenv()

# Взяли переменную TOKEN из пространства переменных окружения
secret_token = os.getenv('TOKEN')

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
)

# создании отдельного логгера
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s - '
                              + '%(funcName)s')
# Хэндлер для управления лог-файлами
handler = RotatingFileHandler(
    'main.log',
    maxBytes=50000000,
    backupCount=2,
)
handler.setFormatter(formatter)
logger.addHandler(handler)

URL = 'https://api.thecatapi.com/v1/images/search'


def get_new_image():
    try:
        response = requests.get(URL)
    except Exception as error:
        # Печатать информацию в консоль теперь не нужно:
        # всё необходимое будет в логах
        logger.error(f'Ошибка при запросе к основному API: {error}')
        new_url = 'https://api.thedogapi.com/v1/images/search'
        response = requests.get(new_url)
    
    response = response.json()
    random_cat = response[0].get('url')
    logger.info('В функции get_new_image запрошено фото random_cat - '
                + f'{random_cat}.')
    return random_cat 

def new_cat(update, context):
    chat = update.effective_chat
    name = update.message.chat.first_name
    button = ReplyKeyboardMarkup(
        [['/newcat']],
        resize_keyboard=True
    )
    context.bot.send_message(
        chat_id=chat.id, 
        text=f'Привет, {name}. Посмотри, какого котика я тебе нашёл',
        reply_markup=button
    )
    context.bot.send_photo(chat.id, get_new_image())
    logger.info(f'Фото отправлено пользователю в ид чата - {chat.id}. Имя пользователя - {name}.')
    logger.info(f'Состав объекта context - {context}.')

def wake_up(update, context):
    # В ответ на команду /start 
    # будет отправлено сообщение 'Спасибо, что включили меня'
    chat = update.effective_chat
    name = update.message.chat.first_name
    # Вот она, наша кнопка.
    # Обратите внимание: в класс передаётся список, вложенный в список, 
    # даже если кнопка всего одна.
    button = ReplyKeyboardMarkup(
        [['/newcat']],
        resize_keyboard=True
    )
    
    context.bot.send_message(
        chat_id=chat.id, 
        text=f'Привет, {name}. Посмотри, какого котика я тебе нашёл',
        reply_markup=button
    )
    context.bot.send_photo(chat.id, get_new_image())
    logger.info(f'Состав объекта context - {context}.')

def say_hi(update, context):  # say_hi готова принять update и context неявно
    # Получаем информацию о чате, из которого пришло сообщение,
    # и сохраняем в переменную chat
    chat = update.effective_chat
    # В ответ на любое текстовое сообщение 
    # будет отправлено 'Привет, я KittyBot!'
    context.bot.send_message(chat_id=chat.id, text='Привет, я KittyBot!')
    logger.info(f'Состав объекта context - {context}.')

def main():
    try:
        updater = Updater(token=secret_token)
        logger.info(f'Создан объект updater - {updater}.')
    except Exception as error:
        logger.error(f'Ошибка при создании объекта updater - {error}.')
    else:
        # Регистрируется обработчик CommandHandler;
        # он будет отфильтровывать только сообщения с содержимым '/start'
        # и передавать их в функцию wake_up()
        updater.dispatcher.add_handler(CommandHandler('start', wake_up))
        updater.dispatcher.add_handler(CommandHandler('newcat', new_cat))

        # Регистрируется обработчик MessageHandler;
        # из всех полученных сообщений он будет выбирать только текстовые сообщения
        # и передавать их в функцию say_hi()
        updater.dispatcher.add_handler(MessageHandler(Filters.text, say_hi))

        # Метод start_polling() запускает процесс polling, 
        # приложение начнёт отправлять регулярные запросы для получения обновлений.
        updater.start_polling()  # задержка обновления poll_interval=20.0
        # Бот будет работать до тех пор, пока не нажмете Ctrl-C
        updater.idle()

if __name__ == '__main__':
    main()
