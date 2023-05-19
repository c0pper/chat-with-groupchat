import logging
import os
from time import sleep
import telegram.error
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from chat_with_groupchat import qa_chain, process_llm_response

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)


async def query(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Sto scrivendo...')
    reply = process_llm_response(qa_chain(update.message.text))
    print(reply)
    try:
        await update.message.reply_text(f'{reply}')
    except telegram.error.NetworkError as e:
        sleep(4)
        await update.message.reply_text(f'{reply}')


app = ApplicationBuilder().token(os.environ.get("BOT_TOKEN")).build()

app.add_handler(CommandHandler("domanda", query))

app.run_polling()
