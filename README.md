# 🤖 Denji Group Guard Bot

Developer: **cooldenji**  
Community: https://t.me/Random_Group_Chatz

---

## Features

| # | Feature | Details |
|---|---------|---------|
| 1 | ✏️ Edit Detection | Anyone edits → warning shown, deleted in 60s |
| 2 | 🔞 NSFW Auto-Delete | Text, sticker, gif, video, photo, file → instant delete |
| 3 | 📁 Media Auto-Delete | All media, voice, sticker, video → deleted in 35 seconds |
| 4 | 🔗 Bio Link/Username Block | Bio mein link ya @username ho → message instantly deleted |
| 5 | 🔗 Channel Verification | DM /start → must join channel, else messages blocked |
| 6 | 🚫 Sticker Pack Block | Detect & permanently block NSFW sticker packs |

> ✅ All features apply to **everyone** — members, admins, and owners. No exceptions.

---

## Bio Link Feature (New)

Bot automatically checks every sender's Telegram bio before allowing the message.  
If bio contains:
- Any URL (http/https)
- Any `t.me/` link
- Any `@username`

→ Message is **instantly deleted** and user gets:
```
⚠️ Your bio contains a link or username, @username. Message deleted.
```

This warning auto-deletes after 20 seconds.

---

## Deploy on Railway.app (Recommended)

> ⚠️ Netlify and Vercel are serverless — they do NOT support polling bots.  
> Use **Railway.app** — free tier, always-on, GitHub connect.

### Step 1 — Create GitHub Repo
- Go to github.com → New Repository → name: `denji-guard-bot`
- Upload these 3 files: `bot.py`, `requirements.txt`, `README.md`

### Step 2 — Create Bot
- Message @BotFather on Telegram → `/newbot`
- Copy the **BOT_TOKEN**

### Step 3 — Deploy on Railway
1. Go to [railway.app](https://railway.app)
2. Login with GitHub
3. Click **New Project** → **Deploy from GitHub Repo**
4. Select `denji-guard-bot`
5. Go to **Variables** tab → Add:
   ```
   BOT_TOKEN        = your_bot_token_here
   CHANNEL_USERNAME = @Random_Group_Chatz
   CHANNEL_LINK     = https://t.me/Random_Group_Chatz
   ```
6. Go to **Settings** → Start Command:
   ```
   python bot.py
   ```
7. Click **Deploy** ✅

---

## Bot Admin Permissions Required

When adding bot to your group, give it:
- ✅ Delete Messages
- ✅ Read Messages

---

## Commands

| Command | Who Can Use | Action |
|---------|-------------|--------|
| `/start` | Anyone (DM only) | Shows channel join link |
| `/blockpack <name>` | Group Admins only | Permanently blocks a sticker pack |

### How to find sticker pack name:
1. Forward a sticker to [@Stickers](https://t.me/Stickers) bot
2. It will show the pack name
3. Type in your group: `/blockpack PackName`

---

## Notes
- NSFW word list can be expanded in `bot.py` under `NSFW_WORDS`
- Blocked sticker packs reset on bot restart (Railway keeps bot alive 24/7)
- Bio check runs on every single message — no one can bypass it
