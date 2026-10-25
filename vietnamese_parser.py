# -*- coding: utf-8 -*-
"""
Module: vietnamese_parser.py
Chức năng: Xử lý và chuyển đổi ngôn ngữ giọng nói tiếng Việt thành số và phân loại dữ liệu:
- Chế độ 1: Cân trọng lượng & Phân loại giới tính ("[Số trọng lượng] + [đực/cái]")
- Chế độ 2: Đếm số lượng cộng dồn tốc độ cao ("[Số lượng mẻ]" hoặc "Xóa"/"Hủy")
"""

import re
from typing import Optional, Tuple, Dict, Any

# Bảng từ số đơn vị cơ bản
DIGIT_WORDS = {
    'không': 0, 'khong': 0, 'zero': 0,
    'một': 1, 'mot': 1, 'mốt': 1,
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
    'nghìn': 1000, 'nghin': 1000, 'ngàn': 1000, 'ngan': 1000, 'k': 1000
}

def normalize_vietnamese_text(text: str) -> str:
    """Chuẩn hóa văn bản tiếng Việt từ âm thanh."""
    if not text:
        return ""
    text = text.lower().strip()
    # Loại bỏ dấu câu không cần thiết trừ dấu phân cách số
    text = re.sub(r'[,.](?!\d)', ' ', text)
    text = re.sub(r'[\-_/\\:;!?()\[\]{}"\'~`@#$%^&*+=|]', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def parse_spoken_vietnamese_integer(words: list) -> Optional[int]:
    """
    Chuyển đổi danh sách từ tiếng Việt thành số nguyên (0 - 99999).
    Hỗ trợ văn nói dân dã miền Tây & thực tế tại ao tôm:
    - 'ba mươi lăm' -> 35
    - 'ba lăm' -> 35
    - 'bốn lăm' -> 45
    - 'năm hai' -> 52
    - 'ba mốt' -> 31
    - 'hai tư' -> 24
    - 'mười lăm' -> 15
    - 'mười một' -> 11
    - 'một trăm linh năm' -> 105
    - 'một trăm hai lăm' -> 125
    """
    if not words:
        return None

    cleaned = []
    for w in words:
        if w in ('linh', 'lẻ', 'le'):
            cleaned.append('linh')
        elif w in DIGIT_WORDS or w in TENS_WORDS or w in MULTIPLIERS:
            cleaned.append(w)
        elif w.isdigit():
            cleaned.append(w)

    if not cleaned:
        return None

    # Nếu chỉ có 1 từ và từ đó là chữ số viết sẵn (Google STT nhận diện dạng số)
    if len(cleaned) == 1:
        if cleaned[0].isdigit():
            return int(cleaned[0])
        if cleaned[0] in DIGIT_WORDS:
            return DIGIT_WORDS[cleaned[0]]
        if cleaned[0] in TENS_WORDS:
            return 10

    # Trường hợp 2 từ nói tắt thông dụng: "ba lăm" (35), "năm hai" (52), "mười lăm" (15)
    if len(cleaned) == 2:
        w1, w2 = cleaned[0], cleaned[1]
        # "mười lăm", "mười một", "mười hai"
        if w1 in ('mười', 'muoi'):
            val2 = DIGIT_WORDS.get(w2)
            if val2 is not None:
                return 10 + val2
        # "hai mươi", "ba mươi"
        if w2 in ('mười', 'muoi', 'mươi'):
            val1 = DIGIT_WORDS.get(w1)
            if val1 is not None:
                return val1 * 10
        # Nói tắt kiểu "ba lăm", "bốn lăm", "năm hai", "bảy tám", "chín chín"
        if w1 in DIGIT_WORDS and w2 in DIGIT_WORDS:
            val1 = DIGIT_WORDS[w1]
            val2 = DIGIT_WORDS[w2]
            if 1 <= val1 <= 9 and 0 <= val2 <= 9:
                return val1 * 10 + val2

    # Trường hợp ngữ pháp chuẩn đầy đủ (trăm, mươi, nghìn)
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
            # Ví dụ: một trăm linh năm -> 105
            i += 1
        elif w in DIGIT_WORDS:
            digit = DIGIT_WORDS[w]
            # Nếu từ tiếp theo là hàng chục/trăm (ví dụ: ba mươi, hai trăm)
            if i + 1 < n and (cleaned[i+1] in ('mươi', 'mười', 'muoi') or cleaned[i+1] in MULTIPLIERS):
                current += digit
            elif current == 0:
                current = digit
            else:
                # Đang có số tròn chục (30) + 5 -> 35
                if current % 10 == 0:
                    current += digit
                else:
                    current = current * 10 + digit
            i += 1
        else:
            i += 1

    total += current
    return total

def parse_vietnamese_number(text: str) -> Optional[float]:
    """
    Trích xuất số từ chuỗi văn bản (hỗ trợ số thực có phần thập phân).
    Ví dụ:
    - '35' -> 35
    - '35.5' -> 35.5
    - 'ba mươi lăm' -> 35
    - 'hai lăm phẩy năm' -> 25.5
    - 'bốn mươi chấm hai' -> 40.2
    """
    text = normalize_vietnamese_text(text)
    if not text:
        return None

    # 1. Tìm số dạng ký tự số trực tiếp (35, 35.5, 35,5)
    num_match = re.search(r'\b(\d+(?:[.,]\d+)?)\b', text)
    if num_match:
        try:
            val_str = num_match.group(1).replace(',', '.')
            val = float(val_str)
            return int(val) if val.is_integer() else round(val, 2)
        except ValueError:
            pass

    # 2. Xử lý số nói có phần thập phân (phẩy, chấm)
    if ' phẩy ' in text or ' phay ' in text or ' chấm ' in text or ' cham ' in text:
        parts = re.split(r' phẩy | phay | chấm | cham ', text)
        if len(parts) >= 2:
            int_part = parse_spoken_vietnamese_integer(parts[0].split())
            dec_part = parse_spoken_vietnamese_integer(parts[1].split())
            if int_part is not None and dec_part is not None:
                dec_val = float(f"0.{dec_part}")
                return round(float(int_part) + dec_val, 2)

    # 3. Xử lý số nguyên nói
    val = parse_spoken_vietnamese_integer(text.split())
    return val

def parse_mode1_weighing_and_gender(speech_text: str) -> Tuple[Optional[float], str]:
    """
    MỤC 2: CHẾ ĐỘ 1 - CÂN TRỌNG LƯỢNG & PHÂN LOẠI GIỚI TÍNH
    Cú pháp: "[Số trọng lượng] + [đực/cái]"
    Ví dụ:
    - "ba mươi lăm đực" -> (35, "Đực")
    - "bốn lăm cái" -> (45, "Cái")
    - "năm hai đực" -> (52, "Đực")
    - "ba lăm" -> (35, "Chưa rõ") (không nghe thấy đực/cái thì mặc định "Chưa rõ")
    - "hai lăm phẩy năm cái" -> (25.5, "Cái")
    """
    norm = normalize_vietnamese_text(speech_text)
    if not norm:
        return None, "Chưa rõ"

    # Phân loại giới tính: trai, chai, đực, tai -> Male; cái, gái, ái -> Female
    gender = "Chưa rõ"
    # 1. Tìm từ khóa Giới tính Cái: cái, gái, ái (female...)
    if re.search(r'\b(cái|cai|gái|gai|ái|female|phi\s*meo|phimeo|pheme|femail|phi|mái|mai)\b', norm):
        gender = "Female"
    # 2. Tìm từ khóa Giới tính Đực: trai, chai, đực, tai (male...)
    elif re.search(r'\b(trai|chai|đực|duc|tai|male|mail|meo|mê|mel|trống|trong)\b', norm):
        gender = "Male"

    # Lọc bỏ từ khóa giới tính và các từ đệm liên quan để trích xuất số trọng lượng
    cleaned_for_num = re.sub(
        r'\b(cái|cai|gái|gai|ái|female|phi\s*meo|phimeo|pheme|femail|phi|mái|mai|trai|chai|đực|duc|tai|male|mail|meo|mê|mel|trống|trong|con|gram|gam|g|nặng|nang|trọng lượng|trong luong|kg|ký|ky)\b',
        ' ',
        norm
    )
    cleaned_for_num = re.sub(r'\s+', ' ', cleaned_for_num).strip()

    weight = parse_vietnamese_number(cleaned_for_num)
    return weight, gender

def parse_mode2_batch_count(speech_text: str) -> Tuple[Optional[str], Optional[int]]:
    """
    MỤC 3: CHẾ ĐỘ 2 - ĐẾM SỐ LƯỢNG CỘNG DỒN TỐC ĐỘ CAO
    Cú pháp người dùng bốc tôm theo mẻ:
    - Đọc số lượng: "năm", "mười", "mười lăm", "hai mươi", "15" -> ('ADD', số)
    - Cơ chế sửa sai rảnh tay (Undo): "Xóa" hoặc "Hủy" -> ('UNDO', None)
    """
    norm = normalize_vietnamese_text(speech_text)
    if not norm:
        return None, None

    # Kiểm tra từ khóa Xóa sạch toàn bộ / Reset
    if re.search(r'\b(xóa hết|xoa het|xóa tất cả|xoa tat ca|xóa toàn bộ|xoa toan bo|reset)\b', norm):
        return 'RESET', None

    # Kiểm tra từ khóa sửa sai / Xóa dòng cuối / Undo
    if re.search(r'\b(xóa dòng|xoa dong|hủy dòng|huy dong|xóa|xoa|hủy|huy|undo|bỏ|bo|trừ|tru|quay lại|lùi|lui|nhầm|nham)\b', norm):
        return 'UNDO', None

    # Lọc các từ đệm thông thường: 'mẻ', 'thêm', 'cộng', 'con', 'tôm', 'bốc'
    cleaned = re.sub(r'\b(mẻ|me|thêm|them|cộng|cong|con|tôm|tom|bốc|boc|đợt|dot)\b', ' ', norm)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()

    val = parse_vietnamese_number(cleaned)
    if val is not None and val > 0:
        return 'ADD', int(val)

    return None, None
