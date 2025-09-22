import os
import logging
import openai
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# 🔐 Tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# 🧠 States
SELECT_STANDARD, SELECT_SUBJECT, ASK_QUESTION = range(3)

# 🎓 Options
standards = ["Class 9", "Class 10", "Class 11", "Class 12"]
subjects = ["Science", "Maths", "English", "Social Science"]

# 🧠 Marks Estimation
def estimate_marks(text):
    length = len(text.split())
    if length <= 5:
        return "½ or 1 mark"
    elif length <= 15:
        return "2 marks"
    elif length <= 30:
        return "3 marks"
    elif length <= 50:
        return "4 marks"
    else:
        return "5 marks"

# 🤖 GPT Answer
def get_ai_answer(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Error fetching answer: {str(e)}"

# 🎬 Start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([standards], one_time_keyboard=True)
    await update.message.reply_text("Welcome to EasyBoardPrepBot! 👋\nSelect your standard:", reply_markup=reply_markup)
    return SELECT_STANDARD

# 🎓 Standard
async def select_standard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["standard"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([subjects], one_time_keyboard=True)
    await update.message.reply_text("Now choose your subject:", reply_markup=reply_markup)
    return SELECT_SUBJECT

# 📚 Subject
async def select_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["subject"] = update.message.text
    await update.message.reply_text("Send your question or image 📷")
    return ASK_QUESTION

# ❓ Question
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        await update.message.reply_text("Image received. OCR not implemented yet.")
        question_text = "Image question placeholder"
    else:
        question_text = update.message.text

    marks = estimate_marks(question_text)
    answer = get_ai_answer(question_text)

    sponsored = f"Sponsored: Join XYZ Coaching for Class {context.user_data['standard'][-2:]} {context.user_data['subject']} 🔥"

    await update.message.reply_text(
        f"📘 Standard: {context.user_data['standard']}\n"
        f"📚 Subject: {context.user_data['subject']}\n"
        f"📝 Question: {question_text}\n"
        f"🔍 Estimated Marks: {marks}\n\n"
        f"✅ Step-by-step solution:\n{answer}\n\n"
        f"{sponsored}"
    )
    return ASK_QUESTION

# 🔚 Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Session cancelled. Type /start to begin again.")
    return ConversationHandler.END

# 🚀 Main
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            SELECT_STANDARD: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_standard)],
            SELECT_SUBJECT: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_subject)],
            ASK_QUESTION: [MessageHandler(filters.TEXT | filters.PHOTO, handle_question)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()


