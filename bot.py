import os
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = "7571267155:AAEDDqLH_EGivgc6z_CHWmo7VmeLxTHwGNk"
LICHESS_USER = "Niginaa"
MINI_APP_URL = "https://tesla2oo2.github.io/chess-bot"

def get_lichess_stats(username):
    response = requests.get(f"https://lichess.org/api/user/{username}")
    data = response.json()
    blitz = data["perfs"]["blitz"]
    rapid = data["perfs"]["rapid"]
    classical = data["perfs"]["classical"]
    puzzles = data["perfs"]["puzzle"]
    return {
        "blitz": blitz["rating"],
        "blitz_games": blitz["games"],
        "rapid": rapid["rating"],
        "rapid_games": rapid["games"],
        "classical": classical["rating"],
        "classical_games": classical["games"],
        "puzzles": puzzles["rating"],
    }

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(
        "♟ Open Dashboard",
        web_app=WebAppInfo(url=f"{MINI_APP_URL}?u={LICHESS_USER}")
    )]]
    await update.message.reply_text(
        "Chess Tracker Bot\n\n/stats — quick stats\n/recent — last 5 games\n/dashboard — full dashboard",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        s = get_lichess_stats(LICHESS_USER)
        text = (
            f"♟ Stats for {LICHESS_USER}\n\n"
            f"Blitz:     {s['blitz']} ({s['blitz_games']} games)\n"
            f"Rapid:     {s['rapid']} ({s['rapid_games']} games)\n"
            f"Classical: {s['classical']} ({s['classical_games']} games)\n"
            f"Puzzles:   {s['puzzles']}"
        )
    except Exception as e:
        text = f"Error fetching stats: {e}"
    await update.message.reply_text(text)

async def recent(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        response = requests.get(
            f"https://lichess.org/api/games/user/{LICHESS_USER}",
            params={"max": 5, "perfType": "blitz"},
            headers={"Accept": "application/x-ndjson"}
        )
        games = [json.loads(line) for line in response.text.strip().split("\n") if line]

        text = f"Last 5 blitz games for {LICHESS_USER}\n\n"
        for g in games:
            white = g["players"]["white"]["user"]["name"]
            black = g["players"]["black"]["user"]["name"]
            winner = g.get("winner", "draw")

            if winner == "draw":
                result = "½"
            elif (winner == "white" and white == LICHESS_USER) or (winner == "black" and black == LICHESS_USER):
                result = "✅"
            else:
                result = "❌"

            opponent = black if white == LICHESS_USER else white
            text += f"{result} vs {opponent}\n"

    except Exception as e:
        text = f"Error: {e}"
    await update.message.reply_text(text)

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(
        "♟ Open Dashboard",
        web_app=WebAppInfo(url=f"{MINI_APP_URL}?u={LICHESS_USER}")
    )]]
    await update.message.reply_text(
        "Tap to open your chess dashboard:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

app = (
    ApplicationBuilder()
    .token(BOT_TOKEN)
    .connect_timeout(30)
    .read_timeout(30)
    .write_timeout(30)
    .build()
)

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("stats", stats))
app.add_handler(CommandHandler("recent", recent))
app.add_handler(CommandHandler("dashboard", dashboard))

print("Bot running...")
app.run_polling()
