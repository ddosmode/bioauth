"""Active randomized head-motion challenge. Not certified presentation attack detection."""
import secrets
import time
import cv2

def direction(face, width):
    x, y, w, h = [float(v) for v in face[:4]]
    center = (x + w / 2) / width
    if center < 0.42:
        return "left"
    if center > 0.58:
        return "right"
    return "center"

def challenge(capture, detector, clock=time.monotonic, choose=secrets.choice, deadline=12.0):
    """Require center -> random side -> center, one face throughout, before deadline."""
    side = choose(("left", "right"))
    print(f"[BioAuth] Look straight, then move your HEAD to the {side.upper()}, then return to center.")
    states = ("center", side, "center")
    progress = 0
    start = clock()
    consecutive = 0
    while clock() - start < deadline:
        ok, frame = capture.read()
        if not ok or frame is None:
            return False, None
        faces = detector.detect(frame)
        if len(faces) != 1:
            progress = 0
            consecutive = 0
            continue
        observed = direction(faces[0], frame.shape[1])
        if observed == states[progress]:
            consecutive += 1
            if consecutive >= 3:
                progress += 1
                consecutive = 0
                if progress == len(states):
                    return True, frame
        else:
            consecutive = 0
    return False, None

def capture_with_challenge(device_index, detector, timeout=12.0):
    cap = cv2.VideoCapture(device_index, cv2.CAP_V4L2)
    if not cap.isOpened():
        return None
    try:
        passed, frame = challenge(cap, detector, deadline=timeout)
        return frame if passed else None
    finally:
        cap.release()
