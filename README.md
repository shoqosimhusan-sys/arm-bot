# Axborot-Resurs Markazi (ARM) Telegram Boti

Bu bot talabalar uchun elektron kutubxona xizmatini taqdim etadi.

## Imkoniyatlari:
1. **Kurslar bo'yicha saralash:**
   - 1-kurs, 2-kurs, 3-kurs, 4-kurs va Magistratura darsliklari.
2. **Elektron kutubxona:**
   - Badiiy adabiyotlar, ilmiy maqolalar, dasturlash va chet tili kitoblari.
3. **Qidiruv:**
   - Kitob nomi yoki muallifi bo'yicha tezkor qidiruv.
4. **Kitob so'rash (Buyurtma):**
   - Talaba topolmagan kitobini so'rab xabar qoldirishi mumkin.
5. **Admin Panel:**
   - Yangi PDF kitoblarni bot orqali to'g'ridan-to'g'ri bazaga yuklash.
   - Statistika (foydalanuvchilar, kitoblar, yuklab olishlar soni).

---

## 🚀 Qanday ishga tushiriladi?

### 1-qadam: Python o'rnatish
Agar kompyuteringizda Python bo'lmasa:
- [python.org](https://www.python.org/downloads/) saytiga kiring va yuklab oling.
- O'rnatayotganda **"Add Python to PATH"** katakchasiga belgi qo'yishni unutmang!

### 2-qadam: Bot Tokenini kiritish
1. Telegramda [@BotFather](https://t.me/BotFather) botiga kiring.
2. `/newbot` buyrug'ini bering, botga nom va username tanlang.
3. Sizga berilgan **HTTP API Token**ni nusxalang.
4. `config.py` faylini ochib, `BOT_TOKEN = "SIZNING_TOKENINGIZ"` qatoriga qo'ying.
5. O'zingizning Telegram ID raqamingizni `ADMIN_IDS = [SIZNING_ID]` joyiga yozing (ID ni bilish uchun @userinfobot ga kiring).

### 3-qadam: Ishga tushirish
Shunchaki papkadagi **`ishga_tushirish.bat`** faylini ikki marta bosing!
Bot ishga tushadi va talabalar foydalanishi mumkin bo'ladi.
