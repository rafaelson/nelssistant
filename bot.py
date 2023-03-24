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

def check_content(content):
    response = openai.Moderation.create(input=content)
    return response['results'][0]['flagged']
        
def prompt(system, user):
    answer = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=[
    {"role": "system", "content": system},
    {"role": "user", "content": user}
    ])
    
    if check_content(answer['choices'][0]['message']['content']):
        return "The answer to your prompt was flagged as inappropriate, you could try rephrasing your prompt and trying again"
    else:
        return answer['choices'][0]['message']['content']


async def question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    question = " ".join(context.args)

    if check_content(question):
        await context.bot.sendMessage(chat_id=update.effective_chat.id, text="Your question was flagged as inappropriate.") 
    else:
        answer = prompt("You are a friendly robotic assistant named Nelssistant", question)
        await context.bot.sendMessage(chat_id=update.effective_chat.id, text=answer)


async def set_custom_behavior(update: Update, context: ContextTypes.DEFAULT_TYPE):
    custom_behavior = " ".join(context.args)

    if check_content(custom_behavior):
        await context.bot.sendMessage(chat_id=update.effective_chat.id, text="Your chosen behavior was flagged as inappropriate.")
    else:
        context.chat_data['custom_behavior'] = custom_behavior


async def print_current_custom_behavior(update: Update, context: ContextTypes.DEFAULT_TYPE):
    custom_behavior = context.chat_data.get('custom_behavior')

    if custom_behavior:
        await context.bot.sendMessage(chat_id=update.effective_chat.id, text=f"The current custom behavior is '{custom_behavior}'")
    else:
        await context.bot.sendMessage(chat_id=update.effective_chat.id, text="You haven't set a custom behavior yet.")


async def custom_prompt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    custom_behavior = context.chat_data.get('custom_behavior')

    if custom_behavior:
        question = " ".join(context.args)

        if check_content(question):
            await context.bot.sendMessage(chat_id=update.effective_chat.id, text="Your prompt was flagged as inappropriate.")
        else:
            answer = prompt(custom_behavior, question)
            await context.bot.sendMessage(chat_id=update.effective_chat.id, text=answer)
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
    set_custom_behavior_handler = CommandHandler('bh', set_custom_behavior)
    print_current_custom_behavior_handler = CommandHandler('cbh', print_current_custom_behavior)
    custom_prompt_handler = CommandHandler('c', custom_prompt)
    message_handler = MessageHandler(filters.TEXT & (~filters.COMMAND), message)
    unknown_handler = MessageHandler(filters.COMMAND, unknown)

    application.add_handler(question_handler)
    application.add_handler(set_custom_behavior_handler)
    application.add_handler(print_current_custom_behavior_handler)
    application.add_handler(custom_prompt_handler)
    application.add_handler(message_handler)
    application.add_handler(unknown_handler)
    application.run_polling()