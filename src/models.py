"""Pinned, checksum-verified OpenCV Zoo model installer."""
from pathlib import Path
import hashlib
import os
import tempfile
from urllib.request import urlopen

BASE = "https://media.githubusercontent.com/media/opencv/opencv_zoo/main/models"
MODELS = {
    "face_detection_yunet_2023mar.onnx": (
        "face_detection_yunet",
        "8f2383e4dd3cfbb4553ea8718107fc0423210dc964f9f4280604804ed2552fa4",
    ),
    "face_recognition_sface_2021dec.onnx": (
        "face_recognition_sface",
        "0ba9fbfa01b5270c96627c4ef784da859931e02f04419c829e83484087c34e79",
    ),
}

def digest(path):
    h = hashlib.sha256()
    with open(path, "rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()

def install_models(destination=None, opener=urlopen):
    target = Path(destination or Path.home() / ".config/bioauth/models")
    target.mkdir(mode=0o700, parents=True, exist_ok=True)
    if target.is_symlink():
        raise ValueError("Refusing symlinked model directory")
    os.chmod(target, 0o700)
    for filename, (model_dir, expected) in MODELS.items():
        path = target / filename
        if path.is_symlink():
            raise ValueError("Refusing symlinked model file")
        if path.exists() and digest(path) == expected:
            continue
        url = f"{BASE}/{model_dir}/{filename}"
        fd, temp = tempfile.mkstemp(prefix=".download-", dir=target)
        try:
            with os.fdopen(fd, "wb") as out, opener(url, timeout=60) as response:
                while True:
                    chunk = response.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            if digest(temp) != expected:
                raise ValueError(f"SHA256 mismatch for {filename}; refusing installation")
            os.chmod(temp, 0o600)
            os.replace(temp, path)
        finally:
            if os.path.exists(temp):
                os.unlink(temp)
    return target

if __name__ == "__main__":
    print(install_models())
