# =================================================
# KODE HATAMOTO BOT v1.0 (Versi Khusus Termux)
# =================================================
import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from telegram.constants import ChatMemberStatus

# --- KONFIGURASI PENTING ---
# Mengambil TOKEN dari Environment Variable di server. Ini lebih aman.
try:
    TOKEN = os.environ.get("BOT_TOKEN")
    if TOKEN is None:
        # Ini akan menghentikan bot jika token tidak ditemukan
        raise ValueError("Error: BOT_TOKEN tidak ditemukan. Pastikan sudah diatur di server.")
except ValueError as e:
    logger.critical(e)
    exit()

# Setup logging untuk melihat error jika terjadi
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

# --- FUNGSI-FUNGSI UTAMA BOT ---

# Fungsi untuk menyambut anggota baru
async def greet_member(update: Update, context):
    """Mengirim pesan sambutan saat ada anggota baru bergabung."""
    try:
        new_members = update.message.new_chat_members
        for member in new_members:
            welcome_message = (
                f"Woy, {member.mention_html()}, met gabung di mari, jir!\n"
                "Biar kaga nyasar, pencet dulu tombol di bawah."
            )

            keyboard = [
                [InlineKeyboardButton("📜 Liat Aturan Main", callback_data="show_rules")],
                [InlineKeyboardButton("😎 Kenalan Sama Admin", callback_data="show_admins")],
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode='HTML')
            logger.info(f"Mengirim sambutan untuk {member.full_name} di grup {update.effective_chat.title}")
    except Exception as e:
        logger.error(f"Error di greet_member: {e}")

# Fungsi untuk menangani saat tombol ditekan
async def button_callback(update: Update, context):
    """Menangani callback dari inline keyboard."""
    query = update.callback_query
    await query.answer()

    try:
        if query.data == "show_rules":
            rules_text = "Aturan Main di Sini Gampang, Jir:\n1. Santuy, jangan toxic.\n2. Gak boleh SARA.\n3. Dilarang jualan apalagi judi.\nUdah gitu doang. Gampang kan?"
            await query.edit_message_text(text=rules_text)
        elif query.data == "show_admins":
            await query.edit_message_text(text="Admin di sini galak-galak, hati-hati aja, wkwk.")
    except Exception as e:
        logger.error(f"Error di button_callback: {e}")

# Fungsi untuk perintah /kick
async def kick_member(update: Update, context):
    """Mengeluarkan anggota dari grup (hanya untuk admin)."""
    user = update.effective_user
    chat = update.effective_chat

    try:
        member = await chat.get_member(user.id)
        if member.status not in [ChatMemberStatus.OWNER, ChatMemberStatus.ADMINISTRATOR]:
            await update.message.reply_text("Cuma admin yang bisa nendang orang, jir!")
            return

        if not update.message.reply_to_message:
            await update.message.reply_text("Caranya salah, cuy. Reply ke pesan orang yang mau ditendang, terus ketik /kick.")
            return

        user_to_kick = update.message.reply_to_message.from_user

        await chat.ban_member(user_to_kick.id)
        await chat.unban_member(user_to_kick.id)
        await update.message.reply_text(f"Berhasil nendang {user_to_kick.mention_html()} keluar angkasa! 🚀", parse_mode='HTML')
        logger.info(f"Admin {user.full_name} mengeluarkan {user_to_kick.full_name}")
    except Exception as e:
        await update.message.reply_text(f"Gagal nendang, jir. Error: {e}")
        logger.error(f"Error di kick_member: {e}")

# --- FUNGSI UTAMA UNTUK MENJALANKAN BOT ---

def main():
    """Fungsi utama untuk menjalankan Hatamoto Bot."""
    application = Application.builder().token(TOKEN).build()

    application.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, greet_member))
    application.add_handler(CommandHandler("kick", kick_member))
    application.add_handler(CallbackQueryHandler(button_callback))

    logger.info("Hatamoto Bot mulai berpatroli...")
    application.run_polling()

if __name__ == "__main__":
    main()