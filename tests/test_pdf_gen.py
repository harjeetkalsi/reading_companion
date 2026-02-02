import re
import reading_companion.core.utils.pdf_gen as pdf_gen

def _is_pdf(pdf: bytes) -> bool:
    # Minimal sanity checks for a PDF byte stream
    return pdf.startswith(b"%PDF") and b"%%EOF" in pdf


def _page_count(pdf: bytes) -> int:
    # Heuristic: count page objects
    # (ReportLab generates /Type /Page entries for each page)
    return len(re.findall(rb"/Type\s*/Page\b", pdf))


def test_pdf_generation_bytes_and_header():
    text = "Line 1\nLine 2\nLine 3"
    pdf = pdf_gen.data_for_pdf(text)
    assert isinstance(pdf, (bytes, bytearray))
    assert len(pdf) > 100      
    assert _is_pdf(pdf)


def test_pdf_generation_empty_input():
    pdf = pdf_gen.data_for_pdf("")
    assert _is_pdf(pdf)
    assert len(pdf) > 100

    def test_pdf_generation_unicode_text():
        text = "Café — π≈3.14159\nRésumé\nnaïve façade"
        pdf = pdf_gen.data_for_pdf(text)
        assert _is_pdf(pdf)
        assert len(pdf) > 100


def test_pdf_generation_multiple_pages():
    long_text = "\n".join(f"Line {i}: This is a reasonably long line for wrapping tests."
                          for i in range(800))
    pdf = pdf_gen.data_for_pdf(long_text)
    assert _is_pdf(pdf)
    assert _page_count(pdf) >= 2