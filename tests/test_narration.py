from __future__ import annotations

import subprocess
import wave

from orbit.production.narration import Narrator


def test_espeak_narration_reads_wav_duration_without_ffprobe(tmp_path, monkeypatch):
    output = tmp_path / "voice.wav"

    def fake_run(command, **kwargs):
        with wave.open(str(output), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(22050)
            wav.writeframes(b"\x00\x00" * 22050 * 3)
        return subprocess.CompletedProcess(command, 0, "", "")

    monkeypatch.setattr("orbit.production.narration.shutil.which", lambda name: "/usr/bin/espeak-ng")
    monkeypatch.setattr("orbit.production.narration.subprocess.run", fake_run)
    result = Narrator(backend="espeak").render("A short test", output)

    assert result.path == output
    assert result.backend == "espeak"
    assert result.duration_seconds == 3.0
