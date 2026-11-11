import io
from pathlib import Path
from PIL import Image
from doc_ingress_hub.config import MAX_IMAGE_WIDTH, JPEG_QUALITY, SUPPORTED_IMAGE_EXTS


def compress_to_blob(file_path: Path) -> tuple[bytes, str, int, int]:
    """
    Сжимает изображение до читаемого для OCR/QR размера (~150-250 КБ).
    Не-изображения (например, PDF) читает в исходном виде.
    Возвращает: (bytes, mime_type, original_size, compressed_size)
    """
    original_size = file_path.stat().st_size
    ext = file_path.suffix.lower()

    if ext not in SUPPORTED_IMAGE_EXTS:
        raw_bytes = file_path.read_bytes()
        mime = "application/pdf" if ext == ".pdf" else "application/octet-stream"
        return raw_bytes, mime, original_size, len(raw_bytes)

    with Image.open(file_path) as img:
        # Конвертируем RGBA / палитру в RGB для корректного сохранения в JPEG
        if img.mode in ("RGBA", "P"):
            img = img.convert("RGB")

        # Пропорциональный ресайз, если ширина превышает лимит из config.py
        if img.width > MAX_IMAGE_WIDTH:
            ratio = MAX_IMAGE_WIDTH / float(img.width)
            new_height = int(float(img.height) * ratio)
            img = img.resize((MAX_IMAGE_WIDTH, new_height), Image.Resampling.LANCZOS)

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
        compressed_bytes = buffer.getvalue()

    return compressed_bytes, "image/jpeg", original_size, len(compressed_bytes)
