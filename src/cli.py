#!/usr/bin/env python3
"""CLI-утилита для биометрической мультипрофильной аутентификации."""

import sys
import os
import json
import argparse
import logging
import re
import numpy as np
import cv2

# Разрешаем реальный путь, даже если запущен через symlink (/usr/local/bin/bioauth)
_REAL_DIR = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(_REAL_DIR, "..")))

from src.capture import VideoCaptureHandler
from src.detector import FaceDetector
from src.recognizer import FaceRecognizer
from src.storage import private_dir, save_embedding, load_embedding

BASE_SYS_DIR = "/var/lib/bioauth"
BASE_USER_DIR = os.path.expanduser("~/.config/bioauth/users")

def validate_username(username: str) -> str:
    if not re.fullmatch(r"[a-z_][a-z0-9_-]{0,31}", username):
        raise ValueError("Invalid Linux username")
    return username

def get_user_dir(username: str) -> str:
    username = validate_username(username)
    # Приоритет: системный каталог при наличии прав, иначе локальный конфиг
    if os.path.exists(BASE_SYS_DIR) and os.access(BASE_SYS_DIR, os.W_OK):
        path = os.path.join(BASE_SYS_DIR, username)
    elif os.path.exists(os.path.join(BASE_SYS_DIR, username)):
        path = os.path.join(BASE_SYS_DIR, username)
    else:
        path = os.path.join(BASE_USER_DIR, username)
    return str(private_dir(path))

def load_user_vectors(username: str) -> list[tuple[str, np.ndarray]]:
    username = validate_username(username)
    """Загружает все зарегистрированные векторы пользователя (primary, alternative, mask)."""
    vectors = []
    # Проверяем оба пути (системный и пользовательский)
    search_dirs = [
        os.path.join(BASE_SYS_DIR, username),
        os.path.join(BASE_USER_DIR, username),
        os.path.expanduser("~/.config/bioauth/enrollment") # обратная совместимость
    ]
    
    seen_slots = set()
    for s_dir in search_dirs:
        if not os.path.exists(s_dir):
            continue
        for slot in ["primary", "alternative", "mask"]:
            f_path = os.path.join(s_dir, f"{slot}.npy")
            if os.path.exists(f_path) and slot not in seen_slots:
                try:
                    vec = load_embedding(f_path)
                    vectors.append((slot, vec))
                    seen_slots.add(slot)
                except Exception:
                    pass
        # Совместимость со старым форматом <username>.npy
        legacy_path = os.path.join(s_dir, f"{username}.npy")
        if os.path.exists(legacy_path) and "primary" not in seen_slots:
            try:
                vec = load_embedding(legacy_path)
                vectors.append(("primary", vec))
                seen_slots.add("primary")
            except Exception:
                pass
                
    return vectors

def cmd_enroll(args):
    user_dir = get_user_dir(args.username)
    slot = args.slot
    target_vec_path = os.path.join(user_dir, f"{slot}.npy")

    print(f"[*] Сканирование лица ({slot}) для пользователя {args.username}...")
    handler = VideoCaptureHandler(device_index=args.device, warmup_frames=5)
    frame = handler.capture_frame()
    if frame is None:
        print("[-] Ошибка: Камера недоступна")
        return 2

    detector = FaceDetector()
    recognizer = FaceRecognizer()

    faces = detector.detect(frame)
    if len(faces) == 0:
        print("[-] Лицо не обнаружено в кадре")
        return 1
    if len(faces) > 1:
        print(f"[-] Обнаружено несколько лиц ({len(faces)}). Должно быть ровно одно.")
        return 1

    feature = recognizer.extract_feature(frame, faces[0])
    save_embedding(target_vec_path, feature)
    # Raw camera frames are deliberately NOT retained by default.

    # Обновление meta.json
    meta_path = os.path.join(user_dir, "meta.json")
    meta = {}
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r") as f:
                meta = json.load(f)
        except Exception:
            pass
    meta[slot] = {
        "updated_at": cv2.getTickCount(),
        "vector_file": f"{slot}.npy",
        "image_file": None
    }
    with open(meta_path, "w") as f:
        json.dump(meta, f, indent=2)
    os.chmod(meta_path, 0o600)

    print(f"[+] Профиль [{slot}] успешно сохранён для пользователя {args.username}")
    return 0

def cmd_verify(args):
    vectors = load_user_vectors(args.username)
    if not vectors:
        if not args.quiet:
            print(f"[-] Биометрические профили не найдены для пользователя {args.username}")
        return 1

    if args.frame:
        frame = cv2.imread(args.frame)
        if frame is None:
            return 2
    else:
        handler = VideoCaptureHandler(device_index=args.device, warmup_frames=3, timeout=1.5)
        frame = handler.capture_frame()
        if frame is None:
            return 2

    detector = FaceDetector()
    recognizer = FaceRecognizer()

    faces = detector.detect(frame)
    if len(faces) == 0:
        if not args.quiet:
            print("[-] Лицо не обнаружено")
        return 1

    # Fail closed: never authenticate when more than one face is visible.
    if len(faces) != 1:
        if not args.quiet:
            print("[-] Expected exactly one face")
        return 1
    for face in faces:
        cand_feature = recognizer.extract_feature(frame, face)
        for slot, ref_feature in vectors:
            is_match, score = recognizer.match(ref_feature, cand_feature)
            if is_match:
                if not args.quiet:
                    print(f"[+] УСПЕХ: Личность подтверждена (Слот: {slot}, Сходство: {score:.3f})")
                return 0

    if not args.quiet:
        print("[-] ОТКАЗ: Лицо не совпадает ни с одним профилем")
    return 1

def cmd_status(args):
    vectors = load_user_vectors(args.username)
    status_data = {
        "username": args.username,
        "enrolled": len(vectors) > 0,
        "slots": [slot for slot, _ in vectors]
    }
    print(json.dumps(status_data, indent=2))
    return 0

def cmd_reset(args):
    user_dir = get_user_dir(args.username)
    if args.slot:
        slots = [args.slot]
    else:
        slots = ["primary", "alternative", "mask"]
    for s in slots:
        for ext in [".npy", ".jpg"]:
            f = os.path.join(user_dir, f"{s}{ext}")
            if os.path.exists(f):
                os.remove(f)
    print(f"[+] Сброшены профили {slots} для {args.username}")
    return 0

def main():
    parser = argparse.ArgumentParser(description="BioAuth Multi-profile Face Authentication")
    parser.add_argument("--device", type=int, default=0)
    parser.add_argument("-q", "--quiet", action="store_true")

    subparsers = parser.add_subparsers(dest="command")

    # enroll
    enroll_p = subparsers.add_parser("enroll")
    enroll_p.add_argument("username", nargs="?", default=os.environ.get("USER", "unknown"))
    enroll_p.add_argument("--slot", choices=["primary", "alternative", "mask"], default="primary")

    # verify
    verify_p = subparsers.add_parser("verify")
    verify_p.add_argument("username", nargs="?", default=os.environ.get("USER", "unknown"))
    verify_p.add_argument("--frame", type=str)

    # status
    status_p = subparsers.add_parser("status")
    status_p.add_argument("username", nargs="?", default=os.environ.get("USER", "unknown"))

    # reset
    reset_p = subparsers.add_parser("reset")
    reset_p.add_argument("username", nargs="?", default=os.environ.get("USER", "unknown"))
    reset_p.add_argument("--slot", choices=["primary", "alternative", "mask"])

    args = parser.parse_args()
    if args.command == "enroll":
        sys.exit(cmd_enroll(args))
    elif args.command == "verify":
        sys.exit(cmd_verify(args))
    elif args.command == "status":
        sys.exit(cmd_status(args))
    elif args.command == "reset":
        sys.exit(cmd_reset(args))
    else:
        parser.print_help()
        sys.exit(0)

if __name__ == "__main__":
    main()
