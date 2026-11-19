# -*- coding: utf-8 -*-
import os

# Базовая директория проекта
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# --- НАСТРОЙКИ ХОЛСТА И ОБРАБОТКИ ---

# Цвет фона холста (R, G, B)
# (122, 122, 122) — Flat matte gray (#7A7A7A)
BACKGROUND_COLOR = (122, 122, 122)

# Отступ от габаритов кадра (0.10 = 10%)
# Вычисляется автоматически на основе максимальной стороны изображения
# 0.5 хорошо подходит. 0.1 увеличенный.
PADDING_PERCENT = 0.50

# Качество сохранения JPEG (от 1 до 95+)
JPEG_QUALITY = 95

# Поддерживаемые расширения файлов для обработки
VALID_EXTENSIONS = ('.png', '.jpg', '.jpeg', '.webp')

# --- НАСТРОЙКИ ПУТЕЙ ---
INPUT_DIR = os.path.join(BASE_DIR, "input_photos")
OUTPUT_DIR = os.path.join(BASE_DIR, "output_processed")

# === 3 YEARS REPORT - IG 4:5 ===
class R3Config:
    INPUT_DIR = "./input/3_years_report"
    OUTPUT_DIR = "./output/3_years_report"
    BACKGROUND_COLOR = (128, 128, 128) # серый как на твоих фото
    PADDING_PERCENT = 0.15
    JPEG_QUALITY = 95
    VALID_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp")
    TARGET_W = 1080
    TARGET_H = 1350 # 4:5
    FIT_RATIO = 0.80
    BG_THRESHOLD = 25