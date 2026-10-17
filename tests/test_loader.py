import io

import pytest

from src.loader import UploadError, extract_text, page_for

LONG = "This Agreement is governed by the laws of Illinois. " * 10


def test_txt_ok():
    text, starts = extract_text("a.txt", LONG.encode())
    assert text.startswith("This Agreement") and starts is None


def test_wrong_type_rejected():
    with pytest.raises(UploadError):
        extract_text("a.exe", b"abc")


def test_too_short_rejected():
    with pytest.raises(UploadError):
        extract_text("a.txt", b"hi")


def test_too_big_rejected():
    with pytest.raises(UploadError):
        extract_text("a.txt", b"x" * (15 * 1024 * 1024 + 1))


def test_docx_ok():
    import docx

    d = docx.Document()
    d.add_paragraph(LONG)
    buf = io.BytesIO()
    d.save(buf)
    text, starts = extract_text("a.docx", buf.getvalue())
    assert "Illinois" in text and starts is None


def test_page_for():
    starts = [0, 1500, 3200]
    assert page_for(0, starts) == 1
    assert page_for(1499, starts) == 1
    assert page_for(1500, starts) == 2
    assert page_for(5000, starts) == 3
    assert page_for(5, None) is None