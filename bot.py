import logging, os, openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
if not os.getenv("BOT_TOKEN") or not os.getenv("OPENAI_API_KEY"):
    from dotenv import load_dotenv
    load_dotenv() # for local testing purposes

openai.api_key=os.getenv("OPENAI_API_KEY")

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args)

    answer = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
        {"role": "system", "content": "You are a friendly robotic assistant named Nelssistant"},
        {"role": "user", "content": question}
    ])
    
    await context.bot.sendMessage(chat_id=update.effective_chat.id, text=answer['choices'][0]['message']['content'])


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="This command does not exist.")

if __name__ == '__main__':
    application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).build()

    question_handler = CommandHandler('q', question)

    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(question_handler)
    application.add_handler(unknown_handler)
    application.run_polling()