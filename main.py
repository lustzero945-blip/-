import traceback
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    CallbackQueryHandler, ContextTypes,
    MessageHandler, filters
)

from config import TOKEN, XP_COURSE, XP_QUIZ_GOOD, XP_QUIZ_BAD
from database import get_user, add_xp, add_quiz_score, leaderboard, get_rank
from ai import generate_course, generate_quiz, correct_code

QUIZ_CACHE = {}

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
    await update.message.reply_text("🔥 FUTURE DEV SCHOOL\nChoisis un langage :", reply_markup=menu())

# ===== HANDLE =====
async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        name = query.from_user.first_name
        data = query.data

        if data == "menu":
            await query.message.reply_text("📋 Menu", reply_markup=menu())

        elif data.endswith("_lvl"):
            topic = data.replace("_lvl","")
            await query.message.reply_text(f"Niveau {topic}", reply_markup=level_menu(topic))

        elif "_beginner" in data or "_advanced" in data:
            topic, level = data.split("_")
            full = f"{topic} {level}"

            course = await generate_course(full)
            add_xp(user_id, name, XP_COURSE)

            await query.message.reply_text(
                f"📚 {full.upper()}\n\n{course[:3500]}",
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("📝 Quiz", callback_data=f"quiz_{topic}")],
                    [InlineKeyboardButton("🔙 Menu", callback_data="menu")]
                ])
            )

        elif data.startswith("quiz_"):
            topic = data.split("_")[1]
            quiz = await generate_quiz(topic)

            correct = "A"
            for l in quiz.split("\n"):
                if "Réponse" in l:
                    correct = l.split(":")[1].strip()

            QUIZ_CACHE[user_id] = correct

            await query.message.reply_text(
                quiz[:3500],
                reply_markup=InlineKeyboardMarkup([
                    [InlineKeyboardButton("A", callback_data="answer_A"),
                     InlineKeyboardButton("B", callback_data="answer_B"),
                     InlineKeyboardButton("C", callback_data="answer_C")]
                ])
            )

        elif data.startswith("answer_"):
            answer = data.split("_")[1]
            correct = QUIZ_CACHE.get(user_id)

            if answer == correct:
                add_xp(user_id, name, XP_QUIZ_GOOD)
                add_quiz_score(user_id, 1)
                text = "✅ Bonne réponse +XP"
            else:
                add_xp(user_id, name, XP_QUIZ_BAD)
                text = f"❌ Mauvaise (correct: {correct})"

            await query.message.reply_text(text, reply_markup=menu())

        elif data == "profile":
            user = get_user(user_id, name)
            rank = get_rank(user["level"])

            await query.message.reply_text(
                f"👤 {name}\nLevel: {user['level']}\nXP: {user['xp']}\nRank: {rank}\nQuiz: {user['quiz_score']}",
                reply_markup=menu()
            )

        elif data == "leader":
            top = leaderboard()
            text = "🏆 TOP DEVELOPERS\n\n"
            for i, u in enumerate(top, 1):
                text += f"{i}. {u['name']} | Lv{u['level']}\n"

            await query.message.reply_text(text, reply_markup=menu())

    except Exception as e:
        print("ERREUR:", e)
        traceback.print_exc()

# ===== CODE AI =====
async def handle_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text
    if len(code) > 10:
        reply = await correct_code(code)
        await update.message.reply_text(reply[:4000])

# ===== MAIN =====
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CallbackQueryHandler(handle))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_code))

print("🔥 BOT ONLINE")

app.run_polling()
