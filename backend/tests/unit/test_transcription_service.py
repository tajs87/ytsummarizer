import asyncio
from pathlib import Path
from types import SimpleNamespace

import pytest

from src.services.transcription_service import TranscriptionService


@pytest.mark.asyncio
async def test_transcribe_audio_success(tmp_path):
    audio_file = tmp_path / "audio.mp3"
    audio_file.write_bytes(b"fake-audio")

    service = TranscriptionService(api_key="test-key")

    fake_response = SimpleNamespace(
        text="hello world",
        segments=[SimpleNamespace(start=0.0, end=1.0, text=" hello world ")],
        language="en",
    )

    async def fake_create(**kwargs):
        return fake_response

    service.client = SimpleNamespace(
        audio=SimpleNamespace(
            transcriptions=SimpleNamespace(create=fake_create)
        )
    )

    result = await service.transcribe_audio(audio_file)

    assert result["full_text"] == "hello world"
    assert result["language"] == "en"
    assert result["word_count"] == 2
    assert result["segments"][0]["text"] == "hello world"


def test_validate_audio_checks_size_and_extension(tmp_path):
    service = TranscriptionService(api_key="test-key")

    valid = tmp_path / "ok.mp3"
    valid.write_bytes(b"x" * 1024)
    assert asyncio.run(service.validate_audio(valid)) is True

    invalid_ext = tmp_path / "bad.txt"
    invalid_ext.write_text("text")
    assert asyncio.run(service.validate_audio(invalid_ext)) is False
