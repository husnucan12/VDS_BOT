import telebot
from telebot import types
import sqlite3
import subprocess
import sys
import os
import threading

TOKEN = "8448809536:AAFtb5MLLGUo9UPCZeu336VITlYsfvuUMXQ"  # vds.py
ADMIN_ID = 8341280215  # Admin ID buraya
bot = telebot.TeleBot(TOKEN)

# ================= ÇEVIRI SİSTEMİ =================
TEXTS = {
    "tr": {
        "welcome": "〽️ Hoş Geldiniz, {name}!\n\n👤 Durumunuz: {status}\n📁 Dosya Sayınız: {count} / {limit}\n\n🤖 Bu bot Python (.py) betiklerini çalıştırmak için tasarlanmıştır.\n\n👇 Butonları kullanın.",
        "premium_status": "⭐ Premium Kullanıcı",
        "free_status": "🆓 Ücretsiz Kullanıcı",
        "unlimited": "Sınırsız",
        "banned": "🚫 Hesabınız yasaklandı.",
        "module_install": "📦 pip modül adı gir:",
        "module_success": "✅ Modül yüklendi.",
        "module_error": "❌ Hata:\n{e}",
        "upload_only_py": "❌ Sadece .py dosya kabul edilir",
        "upload_limit": "❌ Limit dolu. Premium alın.",
        "upload_success": "✅ Dosya yüklendi. Admin onayı bekleniyor.",
        "no_files": "📂 Dosya yok.",
        "waiting": "⏳ Onay Bekliyor",
        "rejected": "❌ Reddedildi",
        "running": "Çalışıyor ✅",
        "stopped": "Duruyor ⏸️",
        "file_not_found": "❌ Dosya bulunamadı.",
        "bot_started": "✅ Bot başlatıldı veya başlatılıyor. Hatalar log'a düşecektir.",
        "bot_stopped_msg": "✅ Bot durduruldu.",
        "file_deleted": "✅ Dosya silindi.",
        "no_logs": "📄 Log bulunamadı.",
        "logs_title": "📄 Loglar:\n",
        "support_prompt": "✍️ Lütfen mesajınızı yazın. Bu mesaj doğrudan admine iletilecek.",
        "support_sent": "✅ Mesajınız iletildi.",
        "send_py": ".py dosyanızı gönderin",
        "pending_info": "Bu dosya admin onayı bekliyor.",
        "not_approved": "❌ Bu dosya admin tarafından onaylanmadı.",
        "file_not_found_cb": "Dosya bulunamadı.",
        "approved_notify": "✅ Dosyanız onaylandı ve çalıştırılmaya hazır: `{filename}`",
        "rejected_notify": "❌ Dosyanız reddedildi: `{filename}`",
        # Menü butonları
        "btn_module": "📦 Modül Yükle",
        "btn_upload": "📂 Dosya Yükle",
        "btn_files": "📂 Dosyalarım",
        "btn_support": "📞 Destek & İletişim",
        "select_lang": "🌐 Lütfen bir dil seçin:\nPlease select a language:",
        "lang_selected": "✅ Türkçe seçildi!",
    },
    "en": {
        "welcome": "〽️ Welcome, {name}!\n\n👤 Status: {status}\n📁 Files: {count} / {limit}\n\n🤖 This bot is designed to run Python (.py) scripts.\n\n👇 Use the buttons below.",
        "premium_status": "⭐ Premium User",
        "free_status": "🆓 Free User",
        "unlimited": "Unlimited",
        "banned": "🚫 Your account has been banned.",
        "module_install": "📦 Enter pip module name:",
        "module_success": "✅ Module installed.",
        "module_error": "❌ Error:\n{e}",
        "upload_only_py": "❌ Only .py files are accepted",
        "upload_limit": "❌ Limit reached. Get Premium.",
        "upload_success": "✅ File uploaded. Waiting for admin approval.",
        "no_files": "📂 No files found.",
        "waiting": "⏳ Waiting for Approval",
        "rejected": "❌ Rejected",
        "running": "Running ✅",
        "stopped": "Stopped ⏸️",
        "file_not_found": "❌ File not found.",
        "bot_started": "✅ Bot started or starting. Errors will appear in the log.",
        "bot_stopped_msg": "✅ Bot stopped.",
        "file_deleted": "✅ File deleted.",
        "no_logs": "📄 No logs found.",
        "logs_title": "📄 Logs:\n",
        "support_prompt": "✍️ Please write your message. It will be forwarded to the admin.",
        "support_sent": "✅ Your message has been sent.",
        "send_py": "Send your .py file",
        "pending_info": "This file is waiting for admin approval.",
        "not_approved": "❌ This file has not been approved by admin.",
        "file_not_found_cb": "File not found.",
        "approved_notify": "✅ Your file has been approved and is ready to run: `{filename}`",
        "rejected_notify": "❌ Your file has been rejected: `{filename}`",
        # Menu buttons
        "btn_module": "📦 Install Module",
        "btn_upload": "📂 Upload File",
        "btn_files": "📂 My Files",
        "btn_support": "📞 Support & Contact",
        "select_lang": "🌐 Lütfen bir dil seçin:\nPlease select a language:",
        "lang_selected": "✅ English selected!",
    }
}

def t(uid, key, **kwargs):
    """Kullanıcının diline göre metin döndürür"""
    lang = get_user_lang(uid)
    text = TEXTS.get(lang, TEXTS["tr"]).get(key, TEXTS["tr"].get(key, key))
    if kwargs:
        text = text.format(**kwargs)
    return text

# ================= DATABASE =================
db = sqlite3.connect("data.db", check_same_thread=False)
sql = db.cursor()

sql.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    premium INTEGER DEFAULT 0,
    banned INTEGER DEFAULT 0,
    lang TEXT DEFAULT 'tr'
)
""")

sql.execute("""
CREATE TABLE IF NOT EXISTS bots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    bot_name TEXT,
    running INTEGER DEFAULT 0,
    status TEXT DEFAULT 'pending'
)
""")

sql.execute("PRAGMA table_info(bots)")
columns = [info[1] for info in sql.fetchall()]
if "status" not in columns:
    sql.execute("ALTER TABLE bots ADD COLUMN status TEXT DEFAULT 'pending'")

sql.execute("PRAGMA table_info(users)")
u_columns = [info[1] for info in sql.fetchall()]
if "lang" not in u_columns:
    sql.execute("ALTER TABLE users ADD COLUMN lang TEXT DEFAULT 'tr'")

db.commit()

running_processes = {}
bot_logs = {}
admin_step = {}
support_wait = {}
announce_wait = {}
lang_wait = {}  # Dil seçimi bekleyen kullanıcılar

# ================= DİL FONKSİYONLARI =================
def get_user_lang(uid):
    sql.execute("SELECT lang FROM users WHERE user_id=?", (uid,))
    row = sql.fetchone()
    return row[0] if row and row[0] else "tr"

def set_user_lang(uid, lang):
    sql.execute("UPDATE users SET lang=? WHERE user_id=?", (lang, uid))
    db.commit()

# ================= MENÜLER =================
def main_menu(uid):
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(t(uid, "btn_module"))
    kb.add(t(uid, "btn_upload"))
    kb.add(t(uid, "btn_files"))
    kb.add(t(uid, "btn_support"))
    return kb

def admin_menu():
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add("⭐ Premium Ver", "👤 Kullanıcı Yasakla / Aç")
    kb.add("🤖 Aktif Botlar")
    kb.add("⛔ Bot Kapat")
    kb.add("🛑 Tüm Botları Kapat")
    kb.add("📢 Duyuru Gönder")
    kb.add("⬅️ Çıkış")
    return kb

def lang_keyboard():
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("🇹🇷 Türkçe", callback_data="lang_tr"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")
    )
    return kb

# ================= LOG =================
def add_log(bot_id, text):
    if bot_id not in bot_logs:
        bot_logs[bot_id] = []
    bot_logs[bot_id].append(text)

# ================= START =================
@bot.message_handler(commands=["start"])
def start(message):
    u = message.from_user
    uid = u.id

    sql.execute("SELECT * FROM users WHERE user_id=?", (uid,))
    existing = sql.fetchone()

    if not existing:
        # Yeni kullanıcı - önce dil seçtir
        sql.execute("INSERT INTO users (user_id, name) VALUES (?, ?)", (uid, u.first_name))
        db.commit()
        bot.send_message(uid, TEXTS["tr"]["select_lang"], reply_markup=lang_keyboard())
        lang_wait[uid] = True
        return

    sql.execute("SELECT premium, banned FROM users WHERE user_id=?", (uid,))
    premium, banned = sql.fetchone()

    if banned:
        bot.send_message(uid, t(uid, "banned"))
        return

    _send_welcome(uid, u, premium)

def _send_welcome(uid, u, premium):
    photos = bot.get_user_profile_photos(uid, limit=1)
    if photos.total_count:
        bot.send_photo(uid, photos.photos[0][0].file_id)

    sql.execute("SELECT COUNT(*) FROM bots WHERE user_id=?", (uid,))
    count = sql.fetchone()[0]

    status_text = t(uid, "premium_status") if premium else t(uid, "free_status")
    limit_text = t(uid, "unlimited") if premium else "1"

    text = t(uid, "welcome", name=u.first_name, status=status_text, count=count, limit=limit_text)
    bot.send_message(uid, text, reply_markup=main_menu(uid))

# ================= DİL DEĞİŞTİR KOMUTU =================
@bot.message_handler(commands=["lang", "language", "dil"])
def change_lang(message):
    bot.send_message(message.chat.id, TEXTS["tr"]["select_lang"], reply_markup=lang_keyboard())

# ================= ADMIN PANEL =================
@bot.message_handler(commands=["adminpanel"])
def adminpanel(message):
    if message.from_user.id != ADMIN_ID:
        return
    bot.send_message(message.chat.id, "👑 Admin Panel", reply_markup=admin_menu())

@bot.message_handler(func=lambda m: m.text == "⬅️ Çıkış" and m.from_user.id == ADMIN_ID)
def exit_admin(message):
    bot.send_message(message.chat.id, "Çıkıldı.", reply_markup=main_menu(message.from_user.id))

# ================= DUYURU =================
@bot.message_handler(func=lambda m: m.text == "📢 Duyuru Gönder" and m.from_user.id == ADMIN_ID)
def announce_prompt(message):
    announce_wait[message.from_user.id] = True
    bot.send_message(message.chat.id, "📢 Göndermek istediğiniz duyuruyu yazın:")

@bot.message_handler(func=lambda m: m.from_user.id in announce_wait)
def announce_send(message):
    try:
        del announce_wait[message.from_user.id]
    except:
        pass

    duyuru_text = message.text
    sql.execute("SELECT user_id FROM users")
    rows = sql.fetchall()
    sent = 0
    for (uid,) in rows:
        try:
            bot.send_message(uid, f"📢 *Duyuru / Announcement*\n\n{duyuru_text}", parse_mode="Markdown")
            sent += 1
        except Exception:
            pass

    bot.send_message(ADMIN_ID, f"📢 Duyuru gönderildi. Toplam gönderim: {sent}")

# ================= PREMIUM VER =================
@bot.message_handler(func=lambda m: m.text == "⭐ Premium Ver" and m.from_user.id == ADMIN_ID)
def premium_prompt(message):
    admin_step[message.from_user.id] = "premium"
    bot.send_message(message.chat.id, "🆔 Kullanıcı ID gir (premium verilecek):")

@bot.message_handler(func=lambda m: admin_step.get(m.from_user.id) == "premium")
def premium_set(message):
    try:
        uid = int(message.text)
        sql.execute("SELECT * FROM users WHERE user_id=?", (uid,))
        if not sql.fetchone():
            bot.send_message(message.chat.id, "❌ Kullanıcı bulunamadı.")
        else:
            sql.execute("UPDATE users SET premium=1 WHERE user_id=?", (uid,))
            db.commit()
            bot.send_message(message.chat.id, f"✅ Kullanıcı {uid} artık Premium.")
            bot.send_message(uid, "⭐ " + ("Tebrikler! Artık Premium kullanıcı oldunuz." if get_user_lang(uid) == "tr" else "Congratulations! You are now a Premium user."))
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Hata: {e}")
    admin_step.clear()

# ================= BAN =================
@bot.message_handler(func=lambda m: m.text == "👤 Kullanıcı Yasakla / Aç" and m.from_user.id == ADMIN_ID)
def ban_prompt(message):
    admin_step[message.from_user.id] = "ban"
    bot.send_message(message.chat.id, "🆔 Kullanıcı ID gönder:")

@bot.message_handler(func=lambda m: admin_step.get(m.from_user.id) == "ban")
def ban_user(message):
    try:
        uid = int(message.text)
        sql.execute("SELECT banned FROM users WHERE user_id=?", (uid,))
        row = sql.fetchone()
        if not row:
            bot.send_message(message.chat.id, "❌ Kullanıcı yok.")
        else:
            new = 0 if row[0] == 1 else 1
            sql.execute("UPDATE users SET banned=? WHERE user_id=?", (new, uid))
            db.commit()
            bot.send_message(message.chat.id, f"✅ Kullanıcı {'açıldı' if new==0 else 'yasaklandı'}.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Hata: {e}")
    admin_step.clear()

# ================= AKTİF BOTLAR =================
@bot.message_handler(func=lambda m: m.text == "🤖 Aktif Botlar" and m.from_user.id == ADMIN_ID)
def active_bots(message):
    sql.execute("SELECT id,user_id,bot_name FROM bots WHERE running=1")
    rows = sql.fetchall()
    if not rows:
        bot.send_message(message.chat.id, "Aktif bot yok.")
        return
    text = "🔥 Aktif Botlar:\n\n"
    for r in rows:
        text += f"Bot ID: {r[0]}\nKullanıcı ID: {r[1]}\nDosya: {r[2]}\n\n"
    bot.send_message(message.chat.id, text)

# ================= BOT KAPAT =================
@bot.message_handler(func=lambda m: m.text == "⛔ Bot Kapat" and m.from_user.id == ADMIN_ID)
def stop_bot_prompt(message):
    admin_step[message.from_user.id] = "stopbot_full"
    bot.send_message(message.chat.id, "🆔 Kullanıcı ID ve Dosya Adı girin (örnek: 12345678 dosya.py)")

@bot.message_handler(func=lambda m: admin_step.get(m.from_user.id) == "stopbot_full")
def stop_bot_full(message):
    try:
        parts = message.text.strip().split()
        if len(parts) != 2:
            return bot.send_message(message.chat.id, "❌ Lütfen KullanıcıID ve DosyaAdı şeklinde girin.")
        uid = int(parts[0])
        filename = parts[1]
        sql.execute("SELECT id FROM bots WHERE user_id=? AND bot_name=?", (uid, filename))
        row = sql.fetchone()
        if not row:
            return bot.send_message(message.chat.id, "❌ Bot bulunamadı.")
        bot_id = row[0]
        proc = running_processes.get(bot_id)
        if proc:
            proc.terminate()
            del running_processes[bot_id]
        sql.execute("UPDATE bots SET running=0 WHERE id=?", (bot_id,))
        db.commit()
        add_log(bot_id, "Bot admin tarafından durduruldu ⏸️")
        bot.send_message(message.chat.id, f"✅ {filename} durduruldu.")
    except Exception as e:
        bot.send_message(message.chat.id, f"❌ Hata: {e}")
    admin_step.clear()

# ================= TÜM BOTLARI KAPAT =================
@bot.message_handler(func=lambda m: m.text == "🛑 Tüm Botları Kapat" and m.from_user.id == ADMIN_ID)
def stop_all(message):
    for p in running_processes.values():
        try:
            p.terminate()
        except:
            pass
    running_processes.clear()
    sql.execute("UPDATE bots SET running=0")
    db.commit()
    bot.send_message(message.chat.id, "✅ Tüm botlar durduruldu.")

# ================= MODÜL YÜKLE =================
@bot.message_handler(func=lambda m: m.text in [TEXTS["tr"]["btn_module"], TEXTS["en"]["btn_module"]])
def mod_prompt(message):
    uid = message.from_user.id
    msg = bot.send_message(message.chat.id, t(uid, "module_install"))
    bot.register_next_step_handler(msg, mod_install)

def mod_install(message):
    uid = message.from_user.id
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", message.text])
        bot.send_message(message.chat.id, t(uid, "module_success"))
    except Exception as e:
        bot.send_message(message.chat.id, t(uid, "module_error", e=e))

# ================= DOSYA YÜKLE =================
@bot.message_handler(func=lambda m: m.text in [TEXTS["tr"]["btn_upload"], TEXTS["en"]["btn_upload"]])
def upload_prompt(message):
    uid = message.from_user.id
    bot.send_message(message.chat.id, t(uid, "send_py"))

@bot.message_handler(content_types=["document"])
def upload(message):
    uid = message.from_user.id
    if not message.document.file_name.endswith(".py"):
        return bot.reply_to(message, t(uid, "upload_only_py"))

    sql.execute("SELECT premium FROM users WHERE user_id=?", (uid,))
    premium = sql.fetchone()[0]
    sql.execute("SELECT COUNT(*) FROM bots WHERE user_id=?", (uid,))
    c = sql.fetchone()[0]

    if not premium and c >= 1:
        return bot.reply_to(message, t(uid, "upload_limit"))

    file = bot.get_file(message.document.file_id)
    data = bot.download_file(file.file_path)
    filename = message.document.file_name

    base, ext = os.path.splitext(filename)
    counter = 1
    while os.path.exists(filename):
        filename = f"{base}_{counter}{ext}"
        counter += 1

    with open(filename, "wb") as f:
        f.write(data)

    sql.execute("INSERT INTO bots (user_id, bot_name, status) VALUES (?, ?, ?)", (uid, filename, 'pending'))
    db.commit()
    bot_id = sql.lastrowid

    bot.reply_to(message, t(uid, "upload_success"))

    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("✅ Onayla", callback_data=f"approve_{bot_id}"),
        types.InlineKeyboardButton("❌ Reddet", callback_data=f"reject_{bot_id}")
    )
    with open(filename, "rb") as f:
        bot.send_document(
            ADMIN_ID,
            f,
            caption=f"📂 Yeni Dosya Yüklendi\n👤 Kullanıcı: {message.from_user.first_name}\n🆔 {uid}\n📄 Dosya: {filename}",
            reply_markup=kb
        )

# ================= DOSYALARIM =================
@bot.message_handler(func=lambda m: m.text in [TEXTS["tr"]["btn_files"], TEXTS["en"]["btn_files"]])
def files(message):
    uid = message.from_user.id
    sql.execute("SELECT id, bot_name, running, status FROM bots WHERE user_id=?", (uid,))
    rows = sql.fetchall()
    if not rows:
        return bot.send_message(uid, t(uid, "no_files"))

    for bot_id, bot_name, running, status in rows:
        if status == 'pending':
            durum = t(uid, "waiting")
        elif status == 'rejected':
            durum = t(uid, "rejected")
        else:
            durum = t(uid, "running") if running else t(uid, "stopped")

        kb = types.InlineKeyboardMarkup()
        if status == 'approved':
            kb.row(
                types.InlineKeyboardButton("▶️ Başlat / Start", callback_data=f"start_{bot_id}"),
                types.InlineKeyboardButton("⛔ Durdur / Stop", callback_data=f"stop_{bot_id}")
            )
            kb.row(
                types.InlineKeyboardButton("❌ Sil / Delete", callback_data=f"delete_{bot_id}"),
                types.InlineKeyboardButton("📄 Log", callback_data=f"log_{bot_id}")
            )
        else:
            kb.row(
                types.InlineKeyboardButton("ℹ️ Onay Bekliyor / Pending", callback_data=f"info_{bot_id}"),
                types.InlineKeyboardButton("❌ Sil / Delete", callback_data=f"delete_{bot_id}")
            )
        bot.send_message(uid, f"📄 {bot_name}\n🆔 ID: {bot_id}\nDurum / Status: {durum}", reply_markup=kb)

# ================= BOT ÇALIŞTIRMA =================
def run_bot_with_log(bot_id, filename):
    def target():
        try:
            proc = subprocess.Popen(
                [sys.executable, filename],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            running_processes[bot_id] = proc
            sql.execute("UPDATE bots SET running=1, status='approved' WHERE id=?", (bot_id,))
            db.commit()
            add_log(bot_id, "Bot başlatıldı ✅")
            for line in proc.stdout:
                add_log(bot_id, line.strip())
            for line in proc.stderr:
                add_log(bot_id, line.strip())
        except ModuleNotFoundError as e:
            missing_module = str(e).split("'")[1]
            add_log(bot_id, f"Başlatılamadı ❌ Eksik modül: {missing_module}")
        except Exception as e:
            add_log(bot_id, f"Hata: {e}")
    threading.Thread(target=target, daemon=True).start()

def get_name(bot_id):
    sql.execute("SELECT bot_name FROM bots WHERE id=?", (bot_id,))
    result = sql.fetchone()
    return result[0] if result else None

# ================= CALLBACK =================
@bot.callback_query_handler(func=lambda c: True)
def cb(call):
    # Dil seçimi callback
    if call.data.startswith("lang_"):
        lang = call.data.split("_")[1]
        uid = call.from_user.id

        # Kullanıcı yoksa ekle
        sql.execute("SELECT * FROM users WHERE user_id=?", (uid,))
        if not sql.fetchone():
            sql.execute("INSERT INTO users (user_id, name, lang) VALUES (?, ?, ?)", (uid, call.from_user.first_name, lang))
            db.commit()
        else:
            set_user_lang(uid, lang)

        lang_wait.pop(uid, None)

        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=TEXTS[lang]["lang_selected"]
        )

        sql.execute("SELECT premium, banned FROM users WHERE user_id=?", (uid,))
        row = sql.fetchone()
        if row:
            premium, banned = row
            if banned:
                bot.send_message(uid, t(uid, "banned"))
                return
            _send_welcome(uid, call.from_user, premium)
        return

    # Diğer callbackler
    try:
        action, bot_id_str = call.data.split("_", 1)
        bot_id = int(bot_id_str)
    except:
        return

    uid = call.from_user.id

    if action == "approve":
        if uid != ADMIN_ID:
            return
        sql.execute("SELECT user_id, bot_name FROM bots WHERE id=? AND status='pending'", (bot_id,))
        row = sql.fetchone()
        if not row:
            bot.answer_callback_query(call.id, "Bu işlem zaten tamamlanmış.", show_alert=True)
            return
        target_uid, filename = row
        sql.execute("UPDATE bots SET status='approved' WHERE id=?", (bot_id,))
        db.commit()
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption="✅ DOSYA ONAYLANDI\n" + call.message.caption.replace("📂 Yeni Dosya Yüklendi", "")
        )
        bot.send_message(target_uid, t(target_uid, "approved_notify", filename=filename), parse_mode="Markdown")

    elif action == "reject":
        if uid != ADMIN_ID:
            return
        sql.execute("SELECT user_id, bot_name FROM bots WHERE id=? AND status='pending'", (bot_id,))
        row = sql.fetchone()
        if not row:
            bot.answer_callback_query(call.id, "Bu işlem zaten tamamlanmış.", show_alert=True)
            return
        target_uid, filename = row
        if os.path.exists(filename):
            os.remove(filename)
        sql.execute("DELETE FROM bots WHERE id=?", (bot_id,))
        db.commit()
        bot.edit_message_caption(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            caption="❌ DOSYA REDDEDİLDİ\n" + call.message.caption.replace("📂 Yeni Dosya Yüklendi", "")
        )
        bot.send_message(target_uid, t(target_uid, "rejected_notify", filename=filename), parse_mode="Markdown")

    elif action == "info":
        bot.answer_callback_query(call.id, t(uid, "pending_info"), show_alert=True)

    else:
        sql.execute("SELECT status FROM bots WHERE id=?", (bot_id,))
        res = sql.fetchone()
        if not res:
            bot.answer_callback_query(call.id, t(uid, "file_not_found_cb"), show_alert=True)
            return
        status = res[0]

        if action in ("start", "stop") and status != "approved":
            bot.answer_callback_query(call.id, t(uid, "not_approved"), show_alert=True)
            return

        if action == "start":
            filename = get_name(bot_id)
            if not filename or not os.path.exists(filename):
                bot.send_message(uid, t(uid, "file_not_found"))
                return
            run_bot_with_log(bot_id, filename)
            bot.send_message(uid, t(uid, "bot_started"))

        elif action == "stop":
            p = running_processes.get(bot_id)
            if p:
                p.terminate()
                del running_processes[bot_id]
            sql.execute("UPDATE bots SET running=0 WHERE id=?", (bot_id,))
            db.commit()
            bot.send_message(uid, t(uid, "bot_stopped_msg"))
            add_log(bot_id, "Bot durduruldu ⏸️")

        elif action == "delete":
            p = running_processes.get(bot_id)
            if p:
                p.terminate()
                del running_processes[bot_id]
            sql.execute("SELECT bot_name FROM bots WHERE id=?", (bot_id,))
            row = sql.fetchone()
            if row:
                filename = row[0]
                if os.path.exists(filename):
                    os.remove(filename)
            sql.execute("DELETE FROM bots WHERE id=?", (bot_id,))
            db.commit()
            bot.send_message(uid, t(uid, "file_deleted"))
            add_log(bot_id, "Dosya silindi ❌")

        elif action == "log":
            logs = bot_logs.get(bot_id, [])
            if not logs:
                bot.send_message(uid, t(uid, "no_logs"))
            else:
                bot.send_message(uid, t(uid, "logs_title") + "\n".join(logs[-50:]))

# ================= DESTEK =================
@bot.message_handler(func=lambda m: m.text in [TEXTS["tr"]["btn_support"], TEXTS["en"]["btn_support"]])
def support(message):
    uid = message.from_user.id
    support_wait[uid] = True
    bot.send_message(message.chat.id, t(uid, "support_prompt"))

@bot.message_handler(func=lambda m: m.from_user.id in support_wait)
def support_msg(message):
    uid = message.from_user.id
    del support_wait[uid]
    bot.send_message(
        ADMIN_ID,
        f"📩 *Destek Mesajı / Support Message*\n\n👤 {message.from_user.first_name}\n🆔 {uid}\n🌐 Dil: {get_user_lang(uid).upper()}\n\n{message.text}",
        parse_mode="Markdown"
    )
    bot.send_message(message.chat.id, t(uid, "support_sent"))

# ================= RUN =================
print("BOT ÇALIŞIYOR...")
bot.infinity_polling()
