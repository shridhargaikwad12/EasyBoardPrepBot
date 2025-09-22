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

# 🔐 Load tokens
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# 🧠 Conversation states
SELECT_STANDARD, SELECT_SUBJECT, ASK_QUESTION = range(3)

# 🎓 Standards and Subjects
standards = ["Class 9", "Class 10", "Class 11", "Class 12"]
subjects = ["Science", "Maths", "English", "Social Science"]

# 🧠 Estimate marks based on question length
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

# 🤖 Get AI-generated answer with error handling
def get_ai_answer(question):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": question}]
        )
        return response['choices'][0]['message']['content']
    except Exception as e:
        return f"❌ Error fetching answer: {str(e)}"

# 🧠 OCR placeholder for image-based questions
def extract_text_from_image(image_file):
    return "Image OCR not implemented yet. Please type your question."

# 🎬 Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = ReplyKeyboardMarkup([standards], one_time_keyboard=True)
    await update.message.reply_text("Welcome to EasyBoardPrepBot! 👋\nPlease select your standard:", reply_markup=reply_markup)
    return SELECT_STANDARD

# 🎓 Standard selected
async def select_standard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["standard"] = update.message.text
    reply_markup = ReplyKeyboardMarkup([subjects], one_time_keyboard=True)
    await update.message.reply_text(f"Selected: {update.message.text}\nNow choose your subject:", reply_markup=reply_markup)
    return SELECT_SUBJECT

# 📚 Subject selected
async def select_subject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["subject"] = update.message.text
    await update.message.reply_text(f"Subject: {update.message.text}\nNow send your question or image 📷")
    return ASK_QUESTION

# ❓ Handle question or image
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.photo:
        await update.message.reply_text("Processing image... 📷")
        image_file = await update.message.photo[-1].get_file()
        question_text = extract_text_from_image(image_file)
    else:
        question_text = update.message.text

    marks = estimate_marks(question_text)
    answer = get_ai_answer(question_text)

    await update.message.reply_text(
        f"📘 Standard: {context.user_data.get('standard')}\n"
        f"📚 Subject: {context.user_data.get('subject')}\n"
        f"📝 Question: {question_text}\n"
        f"🔍 Estimated Marks: {marks}\n\n"
        f"✅ Step-by-step solution:\n{answer}\n\n"
        f"Sponsored: Join XYZ Coaching for Class {context.user_data.get('standard')[-2:]} {context.user_data.get('subject')} 🔥"
    )
    return ASK_QUESTION

# 🔚 Cancel
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Session cancelled. Type /start to begin again.")
    return ConversationHandler.END

# 🚀 Main app
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

