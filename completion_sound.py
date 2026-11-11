"""Original two-tone microwave-style completion chime for Pomodoro transitions."""
import math
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

_CHIME_PATH = None


def _make_chime():
    global _CHIME_PATH
    if _CHIME_PATH and Path(_CHIME_PATH).is_file():
        return _CHIME_PATH
    rate = 44100
    samples = []
    for note_index, (frequency, duration) in enumerate(((880.0, 0.18), (659.25, 0.27))):
        count = int(rate * duration)
        for index in range(count):
            progress = index / max(1, count - 1)
            envelope = min(1.0, progress * 18.0, (1.0 - progress) * 12.0)
            value = math.sin(2.0 * math.pi * frequency * index / rate)
            samples.append(int(32767 * 0.34 * envelope * value))
        if note_index == 0:
            samples.extend([0] * int(rate * 0.055))
    target = Path(tempfile.gettempdir()) / "examreadytimer-pomodoro-tingtong.wav"
    with wave.open(str(target), "wb") as output:
        output.setnchannels(1)
        output.setsampwidth(2)
        output.setframerate(rate)
        output.writeframes(b"".join(struct.pack("<h", value) for value in samples))
    _CHIME_PATH = str(target)
    return _CHIME_PATH


def play_completion_chime(fallback=None):
    """Play a short high-low two-tone chime asynchronously."""
    try:
        sound_file = _make_chime()
        if sys.platform == "win32":
            import winsound
            winsound.PlaySound(sound_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
            return True
        player = "afplay" if sys.platform == "darwin" else (
            shutil.which("paplay") or shutil.which("aplay") or shutil.which("ffplay")
        )
        if player:
            command = [player, sound_file]
            if Path(player).name == "ffplay":
                command = [player, "-nodisp", "-autoexit", "-loglevel", "quiet", sound_file]
            subprocess.Popen(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
    except (OSError, RuntimeError, wave.Error):
        pass
    if fallback:
        try:
            fallback()
        except Exception:
            pass
    return False
