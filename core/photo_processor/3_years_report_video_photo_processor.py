#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import numpy as np
from PIL import Image
import config

CFG = config.R3Config

def get_detection(image_path):
    with Image.open(image_path) as img:
        small = img.convert("RGB").resize((256, 256))
        arr = np.array(small)
        corners = np.concatenate([
            arr[0:5, 0:5].reshape(-1,3), arr[0:5, -5:].reshape(-1,3),
            arr[-5:, 0:5].reshape(-1,3), arr[-5:, -5:].reshape(-1,3),
        ])
        bg = np.median(corners, axis=0)
        mask = np.linalg.norm(arr.astype(int) - bg, axis=2) > CFG.BG_THRESHOLD
        rows, cols = np.any(mask, axis=1), np.any(mask, axis=0)
        if not np.any(rows): return None
        rmin, rmax = np.where(rows)[0][[0, -1]]
        cmin, cmax = np.where(cols)[0][[0, -1]]
        w, h = Image.open(image_path).size
        return {
            "center": (int((cmin+cmax)/2 * w/256), int((rmin+rmax)/2 * h/256)),
            "box_w": int((cmax-cmin) * w/256),
            "box_h": int((rmax-rmin) * h/256)
        }

def process_image(in_path, out_path):
    print(f"⏳ {os.path.basename(in_path)}...")
    with Image.open(in_path) as img:
        img = img.convert("RGB")
        det = get_detection(in_path)
        if not det:
            cx, cy = img.width//2, img.height//2
            obj_w, obj_h = img.width, img.height
        else:
            cx, cy = det["center"]
            obj_w, obj_h = det["box_w"], det["box_h"]

        # 1. Размер кропа под объект с твоим PADDING_PERCENT
        base_size = int(max(obj_w, obj_h) * (1 + CFG.PADDING_PERCENT * 2 + 0.2))
        
        # 2. Делаем кроп строго 4:5 вокруг центра объекта
        # 4:5 => H = W * 1.25
        crop_w = base_size
        crop_h = int(crop_w * 5 / 4)
        
        # Если объект высокий, считаем от высоты
        if obj_h > obj_w:
            crop_h = int(base_size * 1.1)
            crop_w = int(crop_h * 4 / 5)

        # Центруем кроп на объекте - убирает скачки по X/Y
        left = cx - crop_w // 2
        top = cy - crop_h // 2
        right = left + crop_w
        bottom = top + crop_h

        # Поджимаем чтобы не выйти за границы оригинала
        if left < 0:
            right -= left
            left = 0
        if top < 0:
            bottom -= top
            top = 0
        if right > img.width:
            left -= (right - img.width)
            right = img.width
        if bottom > img.height:
            top -= (bottom - img.height)
            bottom = img.height
        
        left, top, right, bottom = max(0,left), max(0,top), min(img.width,right), min(img.height,bottom)

        cropped = img.crop((left, top, right, bottom))
        
        # 3. Финальный ресайз в 1080x1350 без добавления фона
        final = cropped.resize((CFG.TARGET_W, CFG.TARGET_H), Image.LANCZOS)
        final.save(out_path, "JPEG", quality=CFG.JPEG_QUALITY)
        print(f"✅ Кроп {crop_w}x{crop_h} вокруг [{cx},{cy}] -> 4:5")

def main():
    os.makedirs(CFG.INPUT_DIR, exist_ok=True)
    os.makedirs(CFG.OUTPUT_DIR, exist_ok=True)
    files = [f for f in os.listdir(CFG.INPUT_DIR) if f.lower().endswith(CFG.VALID_EXTENSIONS)]
    for fn in files:
        process_image(os.path.join(CFG.INPUT_DIR, fn), os.path.join(CFG.OUTPUT_DIR, fn.rsplit('.',1)[0]+"_4x5.jpg"))

if __name__ == "__main__":
    main()