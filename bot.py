from sqlighter import SQLighter
import config_loader as cfg

import logging
from datetime import datetime
import pytz
import asyncio
from aiogram import Bot, Dispatcher, executor, types

logging.basicConfig(level=logging.INFO)

token = cfg.get_token()
bot = Bot(token)
dp = Dispatcher(bot)
db = SQLighter(cfg.get_DB())

# Запускается при первом запуске бота в ЛС.
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer("Привет, " + message.from_user.first_name + ".\nЯ менеджер релизов - бот, созданный для контроля за релизами. Для получения информации по моей настройке наберите /help.")

# Вывод справки. Содержит описание и список доступных команд.
@dp.message_handler(commands=["help"])
async def help(message: types.Message):
    if (int(message.chat.id) > 0):
        await message.answer(f.get_help())
    else:
        await message.answer("Справка работает только в личных сообщениях.")

# Создание нового релиза.
@dp.message_handler(commands=["new"])
async def new(message: types.Message):
    # message.chat.id < 0 (отрицательный ID) в том случае, если сообщение пришло из чата. Если больше нуля - это ЛС.
    if (int(message.chat.id) < 0):
        activeReleases = SQLighter.get_all_releases(db)
        releaseToken = str(message.chat.id)
        releaseName = f.get_key_by_value(activeReleases, releaseToken)
        # releaseName = None - если не удалось найти имя уже созданного релиза.
        if (releaseName != None):
            await message.answer("Для этого чата релиза уже создан релиз \"{}\".".format(releaseName))
        else:
            parameters = message.text.replace("/new", '').replace("@AL_RM_Bot", "").strip().split(" ")
            # Принимаем не менее 2-х параметров (первый - короткое название релиза, остальные - полное название).
            if (len(parameters) >= 2):
                i = 2
                while (i < len(parameters)):
                    parameters[1] += " {}".format(parameters[i])
                    i += 1
                # Нулевой параметр - короткое название релиза на английском языке (его id). Сразу проверяем его на правильность:
                if (f.check_valid_string(parameters[0])):
                    # Регистр здесь важен, приводим его к нижнему.
                    parameters[0] = parameters[0].lower()
                    SQLighter.add_release(db, message.chat.id, parameters[0], parameters[1])
                    await message.answer("Создан новый релиз \"{}\".\nСписок активных релизов можно посмотреть командой /active_releases в личных сообщениях.".format(parameters[1]))
                else:
                    await message.answer("Короткое имя релиза не может содержать кириллицу, пробелы или спецсимволы. Для справки наберите команду /help в личных сообщениях.")
            else:
                await message.answer("Неверно введены параметры для нового релиза. Для справки наберите команду /help в личных сообщениях.")
    else:
        await message.answer("Для создания нового релиза добавьте бота в чат релиза и вызовите эту команду там.")



# Функция (шедулер) для ежедневной отправки статуса по активным релизам. Активна постоянно, проверятся раз в секунду.
async def scheduler(wait_for):
    while True:
        await asyncio.sleep(wait_for)
        now = datetime.strftime(datetime.now(pytz.timezone('Europe/Moscow')), "%X")
        if (now == "20:00:00"):
            print("20:00")
            # activeReleases = SQLighter.get_all_releases(db)
            # for Release in activeReleases:
            #     releaseStatus = f.get_status(db, activeReleases[Release])
            #     releaseLongName = f.get_long_name(db, activeReleases[Release])
            #     today = int(str(SQLighter.get_status(db, activeReleases[Release])[0]).replace("(", "").replace(")", "").split(", ")[4])
            #     if (today > 0):
            #         await bot.send_message(activeReleases[Release], releaseLongName + "\n\n" + releaseStatus, disable_notification=True)
        if (now == "00:00:00"):
            print("00:00")
            # activeReleases = SQLighter.get_all_releases(db)
            # for Release in activeReleases:
            #     f.increase_day(db, activeReleases[Release])

# Стартовая функция для запуска бота.
if __name__ == "__main__":
    # Создаём новый циклический ивент для запуска шедулера.
    loop = asyncio.get_event_loop()
    loop.create_task(scheduler(1))
    # Начало прослушки и готовности ботом принимать команды (long polling).
    executor.start_polling(dp, skip_updates=True)