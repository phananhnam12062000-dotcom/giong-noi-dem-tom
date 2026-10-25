import re
import sys
from typing import Optional, Tuple

if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass


DIGIT_WORDS = {
    'không': 0, 'khong': 0, 'zero': 0,
    'một': 1, 'mot': 1, 'mốt': 1, 'mot': 1,
    'hai': 2,
    'ba': 3,
    'bốn': 4, 'bon': 4, 'tư': 4, 'tu': 4,
    'năm': 5, 'nam': 5, 'lăm': 5, 'lam': 5, 'nhăm': 5, 'nham': 5,
    'sáu': 6, 'sau': 6,
    'bảy': 7, 'bay': 7, 'bẩy': 7, 'bey': 7,
    'tám': 8, 'tam': 8,
    'chín': 9, 'chin': 9
}

TENS_WORDS = {
    'mười': 10, 'muoi': 10, 'mươi': 10
}

MULTIPLIERS = {
    'trăm': 100, 'tram': 100,
    'nghìn': 1000, 'nghin': 1000, 'ngàn': 1000, 'ngan': 1000
}

def normalize_text(text: str) -> str:
    """Normalize Vietnamese text for recognition."""
    text = text.lower().strip()
    # Replace common punctuation with space except period/comma in numbers
    text = re.sub(r'[,.](?!\d)', ' ', text)
    text = re.sub(r'[\-_/\\:;!?()\[\]{}"\']', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_spoken_vietnamese_integer(words: list) -> Optional[int]:
    """
    Parse a sequence of Vietnamese words into an integer (0 - 9999).
    Supports standard grammar and common colloquial forms:
    - 'ba mươi lăm' -> 35
    - 'ba lăm' -> 35
    - 'bốn lăm' -> 45
    - 'năm hai' -> 52
    - 'hai tư' -> 24
    - 'mười lăm' -> 15
    - 'một trăm linh năm' -> 105
    """
    if not words:
        return None

    # Filter out empty or filler words like 'con', 'gram', 'gam', 'g', 'cân', 'ký', 'kg'
    cleaned = []
    for w in words:
        if w in ('linh', 'lẻ', 'le'):
            cleaned.append('linh')
        elif w in DIGIT_WORDS or w in TENS_WORDS or w in MULTIPLIERS:
            cleaned.append(w)
        elif w.isdigit():
            # If word itself is digits
            cleaned.append(w)

    if not cleaned:
        return None

    # If already a single digit string
    if len(cleaned) == 1 and cleaned[0].isdigit():
        return int(cleaned[0])

    # Case 1: Check colloquial two-word numbers like "ba lăm" (35), "năm hai" (52), "hai tư" (24)
    if len(cleaned) == 2:
        w1, w2 = cleaned[0], cleaned[1]
        # "mười lăm" (15), "mười một" (11), "mười hai" (12)
        if w1 in ('mười', 'muoi'):
            val2 = DIGIT_WORDS.get(w2)
            if val2 is not None:
                return 10 + val2
        # "hai mươi" (20), "ba mươi" (30)
        if w2 in ('mười', 'muoi', 'mươi'):
            val1 = DIGIT_WORDS.get(w1)
            if val1 is not None:
                return val1 * 10
        # "ba lăm" (35), "bốn lăm" (45), "năm hai" (52), "ba mốt" (31), "hai tư" (24)
        if w1 in DIGIT_WORDS and w2 in DIGIT_WORDS:
            val1 = DIGIT_WORDS[w1]
            val2 = DIGIT_WORDS[w2]
            # When someone says "năm hai", they mean 52, not 5 + 2
            if 1 <= val1 <= 9 and 0 <= val2 <= 9:
                return val1 * 10 + val2

    # Case 2: Standard structured parsing with trăm, mười/mươi, nghìn
    total = 0
    current = 0
    i = 0
    n = len(cleaned)
    while i < n:
        w = cleaned[i]
        if w.isdigit():
            current += int(w)
            i += 1
            continue

        if w in MULTIPLIERS:
            mult = MULTIPLIERS[w]
            if current == 0:
                current = 1
            total += current * mult
            current = 0
            i += 1
        elif w in ('mười', 'muoi', 'mươi'):
            if current == 0:
                current = 10
            else:
                current = current * 10
            i += 1
        elif w == 'linh':
            # 'một trăm linh năm' -> 105
            i += 1
        elif w in DIGIT_WORDS:
            digit = DIGIT_WORDS[w]
            # Check if next word is 'mươi' or 'mười' or 'trăm'
            if i + 1 < n and (cleaned[i+1] in ('mươi', 'mười', 'muoi') or cleaned[i+1] in MULTIPLIERS):
                current += digit
            elif current == 0:
                current = digit
            else:
                # e.g., current is 30, next is 5 -> 35
                if current % 10 == 0:
                    current += digit
                else:
                    # e.g., colloquial "một trăm hai lăm"
                    current = current * 10 + digit
            i += 1
        else:
            i += 1

    total += current
    return total

def parse_vietnamese_number(text: str) -> Optional[float]:
    """
    Parses any number from text, supporting:
    - Direct digits: "35", "35.5", "35,5"
    - Decimal words: "ba mươi lăm phẩy năm" -> 35.5
    - Colloquial words: "ba lăm" -> 35, "bốn lăm" -> 45, "năm hai" -> 52
    """
    text = normalize_text(text)
    
    # 1. Look for direct numbers with decimal: e.g. "35.5" or "35,5" or "35"
    num_match = re.search(r'\b(\d+(?:[.,]\d+)?)\b', text)
    if num_match:
        try:
            val_str = num_match.group(1).replace(',', '.')
            val = float(val_str)
            return int(val) if val.is_integer() else val
        except ValueError:
            pass

    # 2. Check for "phẩy" or "chấm" for decimal spoken text
    if ' phẩy ' in text or ' chấm ' in text:
        parts = re.split(r' phẩy | chấm ', text)
        if len(parts) >= 2:
            int_part = parse_spoken_vietnamese_integer(parts[0].split())
            dec_part = parse_spoken_vietnamese_integer(parts[1].split())
            if int_part is not None and dec_part is not None:
                dec_str = f"0.{dec_part}"
                return float(int_part) + float(dec_str)

    # 3. Spoken integer
    val = parse_spoken_vietnamese_integer(text.split())
    return val

def parse_weighing_and_gender(speech_text: str) -> Tuple[Optional[float], str]:
    """
    Mode 1: Parses weight and gender from speech.
    Syntax: "[Số trọng lượng] + [đực/cái]"
    Examples:
    - "ba mươi lăm đực" -> (35, "Đực")
    - "bốn lăm cái" -> (45, "Cái")
    - "năm hai đực" -> (52, "Đực")
    - "35 đực" -> (35, "Đực")
    - "42.5 cái" -> (42.5, "Cái")
    - "ba lăm" -> (35, "Chưa rõ")
    """
    norm = normalize_text(speech_text)
    
    # Determine gender
    gender = "Chưa rõ"
    # Matches 'đực', 'duc', 'con đực', 'trống'
    if re.search(r'\b(đực|duc|trống|trong)\b', norm):
        gender = "Đực"
    # Matches 'cái', 'cai', 'con cái', 'mái', 'mai'
    elif re.search(r'\b(cái|cai|mái|mai)\b', norm):
        gender = "Cái"

    # Remove gender words and common weight filler words before number parsing
    cleaned_for_num = re.sub(r'\b(đực|duc|trống|cái|cai|mái|con|gram|gam|g|nặng|trọng lượng|kg|ký)\b', ' ', norm)
    cleaned_for_num = re.sub(r'\s+', ' ', cleaned_for_num).strip()
    
    weight = parse_vietnamese_number(cleaned_for_num)
    return weight, gender

def parse_batch_count(speech_text: str) -> Tuple[Optional[str], Optional[int]]:
    """
    Mode 2: Parses batch counting or undo command.
    Returns (action, quantity) where action is 'ADD', 'UNDO', or None.
    Examples:
    - "năm" -> ('ADD', 5)
    - "mười" -> ('ADD', 10)
    - "mười lăm" -> ('ADD', 15)
    - "hai mươi" -> ('ADD', 20)
    - "xóa" / "hủy" -> ('UNDO', None)
    """
    norm = normalize_text(speech_text)
    
    # Check for undo/cancel keywords
    if re.search(r'\b(xóa|xoa|hủy|huy|undo|bỏ|bo|trừ|tru|quay lại|lùi lại)\b', norm):
        return 'UNDO', None
        
    # Remove filler words: 'mẻ', 'thêm', 'cộng', 'con', 'tôm'
    cleaned = re.sub(r'\b(mẻ|me|thêm|them|cộng|cong|con|tôm|tom|bốc|boc)\b', ' ', norm)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    
    val = parse_vietnamese_number(cleaned)
    if val is not None and val > 0:
        return 'ADD', int(val)
        
    return None, None

if __name__ == '__main__':
    test_cases_mode1 = [
        ("ba mươi lăm đực", (35, "Đực")),
        ("bốn lăm cái", (45, "Cái")),
        ("năm hai đực", (52, "Đực")),
        ("ba lăm", (35, "Chưa rõ")),
        ("35 đực", (35, "Đực")),
        ("45 cái", (45, "Cái")),
        ("hai lăm phẩy năm cái", (25.5, "Cái")),
        ("50 gram đực", (50, "Đực")),
        ("mười tám con cái", (18, "Cái")),
        ("một trăm linh năm đực", (105, "Đực")),
        ("hai tư cái", (24, "Cái")),
        ("ba mốt đực", (31, "Đực")),
    ]
    
    print("Testing Mode 1 Parsing:")
    all_passed = True
    for inp, expected in test_cases_mode1:
        res = parse_weighing_and_gender(inp)
        status = "PASS" if res == expected else f"FAIL (Got {res}, expected {expected})"
        if res != expected: all_passed = False
        print(f"  '{inp}' -> {res} [{status}]")
        
    test_cases_mode2 = [
        ("năm", ('ADD', 5)),
        ("mười", ('ADD', 10)),
        ("mười lăm", ('ADD', 15)),
        ("hai mươi", ('ADD', 20)),
        ("hai lăm", ('ADD', 25)),
        ("ba lăm con", ('ADD', 35)),
        ("thêm 10 con", ('ADD', 10)),
        ("xóa", ('UNDO', None)),
        ("hủy", ('UNDO', None)),
        ("hủy mẻ vừa rồi", ('UNDO', None)),
        ("xóa mẻ", ('UNDO', None)),
    ]
    
    print("\nTesting Mode 2 Parsing:")
    for inp, expected in test_cases_mode2:
        res = parse_batch_count(inp)
        status = "PASS" if res == expected else f"FAIL (Got {res}, expected {expected})"
        if res != expected: all_passed = False
        print(f"  '{inp}' -> {res} [{status}]")
        
    print(f"\nAll tests passed: {all_passed}")
