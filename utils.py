import re

def parse_message(text: str):
    # Raqamni ajratib olish
    amount_match = re.search(r'(\d+)', text.replace(" ", "").replace(",", ""))
    if not amount_match:
        return None, None, None
    
    amount = float(amount_match.group(1))
    text_lower = text.lower()
    
    # Valyutani aniqlash
    currency = "UZS"
    if "$" in text or "usd" in text_lower: currency = "USD"
    elif "rub" in text_lower: currency = "RUB"
    
    # Aynan nima ekanligini (kategoriyani) aniqlash
    # Masalan "5000 osh" -> "osh" qismini olamiz
    # Raqamlarni matndan olib tashlaymiz va qolgan so'zni kategoriya qilamiz
    category = re.sub(r'\d+', '', text).strip()
    
    # Agar raqamdan keyin hech narsa yozilmagan bo'lsa
    if not category:
        category = "Boshqa"
        
    return amount, currency, category