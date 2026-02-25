from aiogram import Bot, Dispatcher
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)

load_dotenv()

bot = Bot(os.getenv('BOT_TOKEN'))
dp = Dispatcher()
