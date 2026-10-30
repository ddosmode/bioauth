"""Minimal private storage for enrolled biometric templates."""
from pathlib import Path
import os
import tempfile
import numpy as np

SLOTS = {"primary", "alternative", "mask"}

def private_dir(path):
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True, mode=0o700)
    if path.is_symlink():
        raise ValueError("Refusing symlinked biometric directory")
    os.chmod(path, 0o700)
    return path

def save_embedding(path, vector):
    path = Path(path)
    private_dir(path.parent)
    if path.is_symlink():
        raise ValueError("Refusing symlinked biometric file")
    fd, temp = tempfile.mkstemp(prefix=".bioauth-", suffix=".npy", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as f:
            np.save(f, vector, allow_pickle=False)
            f.flush()
            os.fsync(f.fileno())
        os.chmod(temp, 0o600)
        os.replace(temp, path)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)

def load_embedding(path):
    path = Path(path)
    if path.is_symlink():
        raise ValueError("Refusing symlinked biometric file")
    vec = np.load(path, allow_pickle=False)
    if vec.shape != (1, 128) or not np.isfinite(vec).all():
        raise ValueError("Invalid biometric vector")
    return vec
