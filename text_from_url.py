import trafilatura
import re
import time

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service

from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from readability import Document

COOKIE_XPATHS = [
    "//button[contains(translate(., 'ACEPT', 'acept'), 'accept')]",
    "//button[contains(translate(., 'ALLOW', 'allow'), 'allow')]",
    "//button[contains(., 'I agree')]",
    "//button[contains(., 'Accept all')]",
    "//button[contains(., 'Accept cookies')]",
    "//button[@id='onetrust-accept-btn-handler']",
]

def _clean_text(text: str) -> str:
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

def extract_main_text_trafilatura(url: str) -> str | None:
    downloaded = trafilatura.fetch_url(url)
    if not downloaded:
        return None
    text = trafilatura.extract(
        downloaded,
        include_comments=False,
        include_tables=False,
        favor_recall=True,  # better at not missing content
    )
    
    return _clean_text(text or "") or None

def extract_main_text_selenium(url: str, headless: bool = True, wait: float = 2.0) -> str | None:
    service = Service()
    options = webdriver.ChromeOptions()
    if headless:
        options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--window-size=1280,1024")
    options.add_argument("--disable-dev-shm-usage")
    driver = webdriver.Chrome(service=service, options=options)

    try:
        driver.get(url)
        time.sleep(wait)

        # Try clicking a cookie/consent button
        for xp in COOKIE_XPATHS:
            try:
                btn = driver.find_element(By.XPATH, xp)
                btn.click()
                time.sleep(1.0)
                break
            except Exception:
                continue

        # Page source after consent
        html = driver.page_source

        # Use readability to isolate the article body
        doc = Document(html)
        main_html = doc.summary(html_partial=True)
        soup = BeautifulSoup(main_html, "html.parser")

        for tag in soup(["script", "style", "noscript", "svg"]):
            tag.decompose()

        text = soup.get_text(separator="\n")
        return _clean_text(text) or None
    finally:
        driver.quit()


def extract_main_text(url: str) -> str:
    """
    High-level function: try fast (trafilatura), fallback to Selenium (+readability) for cookie/JS pages.
    Returns main article text or a friendly message.
    """
    # Fast path
    text = extract_main_text_trafilatura(url)
    if text:
        return text

    # Fallback
    text = extract_main_text_selenium(url)
    if text:
        return text

    return "Sorry — I couldn't extract readable article text from that link."