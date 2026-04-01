import os
import asyncio
import logging
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, MessageHandler, filters, ContextTypes,
    CommandHandler
)
from telegram.constants import ParseMode

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
CHANNEL_USERNAME = os.environ.get("CHANNEL_USERNAME", "@Random_Group_Chatz")
CHANNEL_LINK = os.environ.get("CHANNEL_LINK", "https://t.me/Random_Group_Chatz")
DEVELOPER = "cooldenji"

# ─── NSFW keyword list ───────────────────────────────────────────────
NSFW_WORDS = [
    "nude", "nudes", "porn", "porno", "xxx", "sexy", "sex", "boobs",
    "dick", "cock", "pussy", "vagina", "penis", "naked", "nsfw",
    "18+", "adult", "horny", "lund", "chut", "bur", "chodna",
    "chodo", "maal", "randi", "gaand", "harami", "bf", "gf video",
    "leaked", "mms", "hot video", "nanga", "nangi"
]

# Blocked sticker pack set names
BLOCKED_STICKER_PACKS = set()

# ─── Bio link/username detection regex ──────────────────────────────
# Detects: http/https links, t.me/ links, @usernames in bio
BIO_LINK_PATTERN = re.compile(
    r'(https?://\S+|t\.me/\S+|@[a-zA-Z0-9_]{4,})',
    re.IGNORECASE
)

# ─── Helper: check channel membership ───────────────────────────────
async def is_member(bot, user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(CHANNEL_USERNAME, user_id)
        return member.status in ["member", "administrator", "creator"]
    except Exception:
        return False

# ─── Helper: delete after delay ─────────────────────────────────────
async def delete_after(context: ContextTypes.DEFAULT_TYPE, chat_id: int, message_id: int, delay: int):
    await asyncio.sleep(delay)
    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=message_id)
    except Exception:
        pass

# ─── Helper: NSFW text check ────────────────────────────────────────
def has_nsfw_text(text: str) -> bool:
    if not text:
        return False
    text_lower = text.lower()
    return any(word in text_lower for word in NSFW_WORDS)

# ─── FEATURE 4: Bio link/username check ─────────────────────────────
async def has_bio_link(bot, user_id: int) -> bool:
    """Returns True if user's bio contains any URL or @username."""
    try:
        user_full = await bot.get_chat(user_id)
        bio = user_full.bio or ""
        if BIO_LINK_PATTERN.search(bio):
            return True
    except Exception:
        pass
    return False

# ─── /start command (DM only) ────────────────────────────────────────
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != "private":
        return

    user = update.effective_user
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔗 Join Community", url=CHANNEL_LINK)]
    ])

    text = (
        f"👋 Hey <b>{user.first_name}</b>!\n\n"
        f"To use this bot in your group, you must join our community first.\n\n"
        f"🔔 <b>Join here:</b> {CHANNEL_LINK}\n\n"
        f"After joining, add me to your group and give me <b>Admin rights</b>.\n\n"
        f"<i>Developer: {DEVELOPER}</i>"
    )
    await update.message.reply_text(text, reply_markup=keyboard, parse_mode=ParseMode.HTML)

# ─── FEATURE 1: Edit detection ───────────────────────────────────────
async def edited_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.edited_message is None:
        return
    if update.effective_chat.type == "private":
        return

    msg = update.edited_message
    user = update.effective_user
    chat_id = update.effective_chat.id

    try:
        await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
    except Exception:
        pass

    username = f"@{user.username}" if user.username else user.first_name
    warn = await context.bot.send_message(
        chat_id=chat_id,
        text=(
            f"⚠️ Hey {username}, editing messages is not allowed due to copyright concerns.\n"
            f"Your message will be deleted in 60 seconds."
        )
    )
    asyncio.create_task(delete_after(context, chat_id, warn.message_id, 60))

# ─── FEATURE 2 + 3 + 4: All group messages ───────────────────────────
async def group_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        return

    msg = update.message
    if msg is None:
        return

    user = update.effective_user
    chat_id = update.effective_chat.id
    username = f"@{user.username}" if user.username else user.first_name

    # ── Channel verification check ──────────────────────────────────
    joined = await is_member(context.bot, user.id)
    if not joined:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        except Exception:
            pass
        notice = await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"🚫 {username}, please join {CHANNEL_LINK} to send messages here.\n"
                f"<i>Developer: {DEVELOPER}</i>"
            ),
            parse_mode=ParseMode.HTML
        )
        asyncio.create_task(delete_after(context, chat_id, notice.message_id, 30))
        return

    # ── FEATURE 4: Bio link/username detection ───────────────────────
    # Applies to everyone — member, admin, owner
    bio_flagged = await has_bio_link(context.bot, user.id)
    if bio_flagged:
        try:
            await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
        except Exception:
            pass
        warn = await context.bot.send_message(
            chat_id=chat_id,
            text=f"⚠️ Your bio contains a link or username, {username}. Message deleted."
        )
        asyncio.create_task(delete_after(context, chat_id, warn.message_id, 20))
        return

    deleted = False
    reason = ""

    # ── NSFW: Sticker ────────────────────────────────────────────────
    if msg.sticker:
        pack_name = msg.sticker.set_name or "unknown_pack"

        if pack_name in BLOCKED_STICKER_PACKS:
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            except Exception:
                pass
            warn = await context.bot.send_message(
                chat_id=chat_id,
                text=f"⚠️ ᗪꫀꪀ𝓳𝓲..!!, the sticker pack \"{pack_name}\" is blocked due to previous NSFW content."
            )
            asyncio.create_task(delete_after(context, chat_id, warn.message_id, 15))
            return

        # All stickers → auto delete in 35s
        asyncio.create_task(delete_after(context, chat_id, msg.message_id, 35))
        return

    # ── NSFW: Animation/GIF ──────────────────────────────────────────
    if msg.animation:
        deleted = True
        reason = "nsfw_media"

    # ── Video ────────────────────────────────────────────────────────
    if msg.video:
        deleted = True
        reason = "media_auto"

    # ── Photo ────────────────────────────────────────────────────────
    if msg.photo:
        deleted = True
        reason = "media_auto"

    # ── Voice note ───────────────────────────────────────────────────
    if msg.voice:
        deleted = True
        reason = "media_auto"

    # ── Video note (circle) ──────────────────────────────────────────
    if msg.video_note:
        deleted = True
        reason = "media_auto"

    # ── Document/File ────────────────────────────────────────────────
    if msg.document:
        mime = msg.document.mime_type or ""
        fname = (msg.document.file_name or "").lower()
        if any(mime.startswith(m) for m in ["video/", "image/"]) or has_nsfw_text(fname):
            deleted = True
            reason = "nsfw_file"

    # ── NSFW text/caption ────────────────────────────────────────────
    if msg.text and has_nsfw_text(msg.text):
        deleted = True
        reason = "nsfw_text"

    if msg.caption and has_nsfw_text(msg.caption):
        deleted = True
        reason = "nsfw_text"

    # ── Execute delete ───────────────────────────────────────────────
    if deleted:
        if reason in ("nsfw_media", "nsfw_text", "nsfw_file"):
            # Instant delete
            try:
                await context.bot.delete_message(chat_id=chat_id, message_id=msg.message_id)
            except Exception:
                pass
        else:
            # 35 sec auto delete
            asyncio.create_task(delete_after(context, chat_id, msg.message_id, 35))

# ─── Admin: /blockpack command ───────────────────────────────────────
async def block_pack_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == "private":
        return
    user = update.effective_user
    admins = await update.effective_chat.get_administrators()
    if user.id not in [a.user.id for a in admins]:
        return
    if not context.args:
        await update.message.reply_text("Usage: /blockpack <pack_name>")
        return
    pack = context.args[0]
    BLOCKED_STICKER_PACKS.add(pack)
    await update.message.reply_text(f"✅ Sticker pack `{pack}` blocked.", parse_mode=ParseMode.MARKDOWN)

# ─── Main ────────────────────────────────────────────────────────────
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("blockpack", block_pack_command))

    # Feature 1 — edit detection
    app.add_handler(MessageHandler(filters.UpdateType.EDITED_MESSAGE, edited_message_handler))

    # Feature 2 + 3 + 4 — group message guard
    app.add_handler(MessageHandler(
        filters.ChatType.GROUPS & (
            filters.TEXT | filters.PHOTO | filters.VIDEO | filters.VOICE |
            filters.ANIMATION | filters.Sticker.ALL | filters.Document.ALL |
            filters.VIDEO_NOTE | filters.AUDIO
        ),
        group_message_handler
    ))

    logger.info("✅ Denji Guard Bot started...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
