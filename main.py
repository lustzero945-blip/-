import traceback
import os

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, ContextTypes,
    MessageHandler, filters
)

from database import get_user, add_xp, add_quiz_score, leaderboard, get_rank
from ai import generate_course, generate_quiz, correct_code

# ⚠️ TOKEN depuis Railway (PAS config.py)
TOKEN = os.getenv("8576498710:AAF9LeBEVTjet9QQjGr8976Mr2IzOLzbBus")

QUIZ_CACHE = {}

START_IMG = "https://i.imgur.com/YhNXsI4.jpeg"
CMD_IMG = "https://i.imgur.com/RbPhQnR.jpeg"

XP_COURSE = 10
XP_QUIZ_GOOD = 5
XP_QUIZ_BAD = 1


# ===== MENU =====
def menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🌐 HTML", callback_data="html_lvl")],
        [InlineKeyboardButton("🎨 CSS", callback_data="css_lvl")],
        [InlineKeyboardButton("⚡ JS", callback_data="js_lvl")],
        [InlineKeyboardButton("🐍 Python", callback_data="python_lvl")],
        [InlineKeyboardButton("📊 Profil", callback_data="profile")],
        [InlineKeyboardButton("🏆 Leaderboard", callback_data="leader")]
    ])


def level_menu(topic):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🔰 Débutant", callback_data=f"{topic}_beginner")],
        [InlineKeyboardButton("⚡ Avancé", callback_data=f"{topic}_advanced")],
        [InlineKeyboardButton("🔙 Menu", callback_data="menu")]
    ])


# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        await update.message.reply_photo(
            photo=START_IMG,
            caption="🚀 FUTURE DEV SCHOOL\n⚡ Powered by LUST DEV\n\nChoisis un langage :",
            reply_markup=menu()
        )
    except Exception as e:
        print("START ERROR:", e)


# ===== HANDLE =====
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        name = query.from_user.first_name
        data = query.data

        # MENU
        if data == "menu":
            await query.message.reply_photo(
                photo=CMD_IMG,
                caption="📋 Menu principal",
                reply_markup=menu()
            )

        # NIVEAU
        elif data.endswith("_lvl"):
            topic = data.replace("_lvl", "")
            await query.message.reply_photo(
                photo=CMD_IMG,
                caption=f"{topic.upper()} - Choisis niveau :",
                reply_markup=level_menu(topic)
            )

        # COURS
        elif "_beginner" in data or "_advanced" in data:
            topic, level = data.split("_")

            try:
                course = await generate_course(f"{topic} {level}")
            except:
                course = "Erreur IA"

            add_xp(user_id, name, XP_COURSE)

            await query.message.reply_photo(
                photo=CMD_IMG,
                caption=f"📚 {topic.upper()} {level}\n\n{course[:3000]}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📝 Quiz", callback_data=f"quiz_{topic}")],
                    [InlineKeyboardButton("🔙 Menu", callback_data="menu")]
                ])
            )

        # QUIZ
        elif data.startswith("quiz_"):
            topic = data.split("_")[1]

            try:
                quiz = await generate_quiz(topic)
            except:
                quiz = "Erreur quiz\nRéponse: A"

            correct = "A"
            for l in quiz.split("\n"):
                if "Réponse" in l:
                    correct = l.split(":")[1].strip()

            QUIZ_CACHE[user_id] = correct

            await query.message.reply_photo(
                photo=CMD_IMG,
                caption=quiz[:3000],
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("A", callback_data="answer_A"),
                     InlineKeyboardButton("B", callback_data="answer_B"),
                     InlineKeyboardButton("C", callback_data="answer_C")]
                ])
            )

        # REPONSE
        elif data.startswith("answer_"):
            answer = data.split("_")[1]
            correct = QUIZ_CACHE.get(user_id, "A")

            if answer == correct:
                add_xp(user_id, name, XP_QUIZ_GOOD)
                add_quiz_score(user_id, 1)
                text = "✅ Bonne réponse"
            else:
                add_xp(user_id, name, XP_QUIZ_BAD)
                text = f"❌ Mauvaise (correct: {correct})"

            await query.message.reply_photo(
                photo=CMD_IMG,
                caption=text,
                reply_markup=menu()
            )

        # PROFIL
        elif data == "profile":
            user = get_user(user_id, name)
            rank = get_rank(user["level"])

            await query.message.reply_text(
                f"👤 {name}\nLevel: {user['level']}\nXP: {user['xp']}\nRank: {rank}"
            )

        # LEADERBOARD
        elif data == "leader":
            top = leaderboard()

            text = "🏆 TOP\n"
            for i, u in enumerate(top, 1):
                text += f"{i}. {u['name']} Lv{u['level']}\n"

            await query.message.reply_text(text)

    except Exception as e:
        print("HANDLE ERROR:", e)
        traceback.print_exc()


# ===== CODE CHECK =====
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        code = update.message.text
        if len(code) > 10:
            reply = await correct_code(code)
            await update.message.reply_text(reply[:3000])
    except Exception as e:
        print("CODE ERROR:", e)


# ===== MAIN =====
if __name__ == "__main__":
    print("🚀 STARTING BOT...")

    if not TOKEN:
        print("❌ TOKEN MANQUANT")
        exit()

    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))

    print("🔥 BOT LUST DEV ONLINE")

    app.run_polling()
