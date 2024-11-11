from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import os

# Anime va maxfiy kanal havolalari ro'yxati
anime_links = {
    "Naruto": "https://t.me/your_channel_username/1",
    "One Piece": "https://t.me/your_channel_username/2"
}

# Majburiy obuna kanali username'si
mandatory_subscription_channel = "Aniplayuzb"  # Kanal username'ini faqat username ko'rinishida kiritish kerak

# Faqat admin qo'sha olishi uchun admin ID
ADMIN_USER_ID = 7027097722  # Bu yerda o'zingizning Telegram ID'nizni kiriting

# /start komanda funksiyasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Salom! Anime ro‘yxatini ko‘rish uchun /anime yozing.")

# Obuna bo‘lishni tekshiruvchi funksiya
async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_member = await context.bot.get_chat_member(f"@{mandatory_subscription_channel}", user_id)
        return chat_member.status in ["member", "administrator", "creator"]
    except Exception as e:
        print(f"Error in check_subscription: {e}")
        return False

# /anime komanda funksiyasi - Anime ro'yxatini yuboradi, agar obuna bo'lmagan bo'lsa, ogohlantiradi
async def show_anime_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not await check_subscription(user_id, context):
        await update.message.reply_text(
            f"Botdan foydalanish uchun kanalimizga obuna bo'ling: https://t.me/{mandatory_subscription_channel}"
        )
        return

    keyboard = []
    for anime_name in anime_links.keys():
        keyboard.append([InlineKeyboardButton(anime_name, callback_data=anime_name)])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("Qaysi animeni ko‘rmoqchisiz?", reply_markup=reply_markup)

# Tanlangan animening maxfiy kanaldagi havolasini yuborish
async def anime_link_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    anime_name = query.data
    if anime_name in anime_links:
        link = anime_links[anime_name]
        await query.edit_message_text(f"{anime_name}ni ko‘rish uchun shu yerga o'ting: {link}")
    else:
        await query.edit_message_text("Tanlangan anime topilmadi.")

# Admin uchun - yangi anime havolasini qo'shish yoki olib tashlash
async def add_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_USER_ID:
        if len(context.args) >= 2:
            anime_name = context.args[0]
            link = context.args[1]
            anime_links[anime_name] = link
            await update.message.reply_text(f"{anime_name} anime uchun havola qo‘shildi.")
        else:
            await update.message.reply_text("To‘g‘ri format: /add_link <anime_nomi> <havola>")
    else:
        await update.message.reply_text("Bu komanda faqat admin uchun.")

async def remove_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == ADMIN_USER_ID:
        if context.args:
            anime_name = context.args[0]
            if anime_name in anime_links:
                del anime_links[anime_name]
                await update.message.reply_text(f"{anime_name} anime uchun havola olib tashlandi.")
            else:
                await update.message.reply_text("Anime topilmadi.")
        else:
            await update.message.reply_text("To‘g‘ri format: /remove_link <anime_nomi>")
    else:
        await update.message.reply_text("Bu komanda faqat admin uchun.")

# Botni ishga tushirish
if __name__ == '__main__':
    app = ApplicationBuilder().token("7708556164:AAGm4I9IrIf9T9RZkRJ1irwiKoRnSqi9Ydc").build()  # API tokenni kiriting

    # Komandalarni qo'shish
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("anime", show_anime_list))
    app.add_handler(CommandHandler("add_link", add_link))
    app.add_handler(CommandHandler("remove_link", remove_link))
    app.add_handler(CallbackQueryHandler(anime_link_callback))

    print("Bot ishga tushdi...")
    app.run_polling()