import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from chat_with_groupchat import qa_chain, process_llm_response

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

async def hello(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reply = process_llm_response(qa_chain(update.message.text))
    print(reply)
    await update.message.reply_text(f'{reply}')


app = ApplicationBuilder().token("6079613795:AAGbtyLGslZxRCGQflcsOy-EaKaZcssbjQs").build()

app.add_handler(CommandHandler("hello", hello))

app.run_polling()