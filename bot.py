import logging, os, openai
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters, PicklePersistence
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


def set_custom_behavior(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.chat_data['custom_behavior'] = " ".join(context.args)

async def custom_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    custom_behavior = context.chat_data.get('custom_behavior')

    if custom_behavior:
        question = " ".join(context.args)

        answer = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
            {"role": "system", "content": custom_behavior},
            {"role": "user", "content": question}
        ])
        await context.bot.sendMessage(chat_id=update.effective_chat.id, text=answer['choices'][0]['message']['content'])
    else:
        await context.bot.sendMessage(chat_id=update.effective_chat.id, text="Please set a custom behavior first.")

async def message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Please use one of the available commands.")

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="This command does not exist.")

if __name__ == '__main__':
    chat_persistence = PicklePersistence(filepath="nelssistant_data")
    application = ApplicationBuilder().token(os.getenv("BOT_TOKEN")).persistence(chat_persistence).build()

    question_handler = CommandHandler('q', question)
    set_custom_behavior_handler = CommandHandler('p', set_custom_behavior)
    custom_prompt_handler = CommandHandler('c', custom_prompt)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(question_handler)
    application.add_handler(set_custom_behavior_handler)
    application.add_handler(custom_prompt_handler)
    application.add_handler(message_handler)
    application.add_handler(unknown_handler)
    application.run_polling()