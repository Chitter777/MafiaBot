import json
import os
from typing import Dict

import disnake
from core import Client
from disnake.ext import commands
from dotenv import load_dotenv
from loguru import logger
import re

load_dotenv()

config = {}

bot = Client(intents=disnake.Intents.default(), reload=True)


@logger.catch
def main():
    token_check = re.compile(r"^([A-Za-z0-9-_.]+)\.[A-Za-z0-9-_.]+\.([A-Za-z0-9-_.]+)$")
    try:
        with open("./config.json", "x") as f:
            sets = {
                "extensions": {
                    "ext.commands": ["start_game", "information"],
                    "ext.events": [
                        "on_ready",
                        "on_button_click",
                        "on_dropdown",
                        "on_modal_submit",
                    ],
                },
            }
            json.dump(sets, f, indent=4)
    except FileExistsError:
        pass
    try:
        with open("./.env", "x") as f:
            f.write("TOKEN = YOUR_TOKEN_HERE")
        logger.critical(
            "Первый запуск или .ENV-файл потерян! Укажите новый токен бота!"
        )
        exit(-1)
    except FileExistsError:
        pass

    if os.getenv("TOKEN") in ["YOUR_TOKEN_HERE", None]:
        logger.critical("Вы не заменили токен!")
        exit(-1)
    elif not bool(token_check.match(os.getenv("TOKEN"))):
        logger.critical("Указан синтаксический неверный токен!")
        exit(-1)

    with open("./config.json") as cfg:
        global config
        config = json.load(cfg)


def load_module(group: str, ext_name: str) -> Dict:
    ext_fullname = group + "." + ext_name
    try:
        bot.load_extension(ext_fullname)
        response = {"loaded": True, "fullname": ext_fullname}
    except commands.errors.ExtensionNotFound:
        response = {
            "loaded": False,
            "fullname": ext_fullname,
            "reason": "Расширение не было обнаружено в указанном месте",
        }
    except ModuleNotFoundError:
        response = {
            "loaded": False,
            "fullname": ext_fullname,
            "reason": "Директория, в которой ожидалось расширение, отсутствует",
        }
    except commands.errors.NoEntryPointError:
        response = {
            "loaded": False,
            "fullname": ext_fullname,
            "reason": "Отсутствует точка входа в расширения",
        }
    return response


if __name__ == "__main__":
    main()
    try:
        for key, value in config.get("extensions", {}).items():
            for val in value:
                res = load_module(key, val)
                if res["loaded"]:
                    logger.success(f"Расширение {res['fullname']} успешно загружено!")
                else:
                    logger.warning(
                        f"Расширение {res['fullname']} не было загружено: {res['reason']}"
                    )
        bot.run(os.getenv("TOKEN"), reconnect=True)
    except disnake.LoginFailure:
        logger.critical("Токен не является действительным!")
