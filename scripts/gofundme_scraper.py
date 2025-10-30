import re
import sys
import time
from typing import List

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter, Retry


URL = "https://gofund.me/ff8591f9f"

def get_session() -> requests.Session:
    """Create a requests session with retries and a desktop User-Agent."""
    sess = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=["GET", "HEAD", "OPTIONS"]
    )
    sess.mount("https://", HTTPAdapter(max_retries=retries))
    sess.headers.update({
        # A realistic UA helps avoid being blocked by simple bot filters.
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/127.0.0.0 Safari/537.36"
        ),
        "Accept-Language": "en-US,en;q=0.9",
    })
    return sess


def fetch_html(url: str, timeout: int = 20) -> str:
    """Fetch raw HTML with minimal politeness (retries + tiny delay)."""
    session = get_session()
    resp = session.get(url, timeout=timeout)
    resp.raise_for_status()
    # Small delay to be polite (and avoid triggering rate limits).
    time.sleep(0.3)
    return resp.text


def extract_dollar_values(html):
    """Extract numbers between '$' and 'r' in the target class elements."""
    soup = BeautifulSoup(html, "html.parser")
    elems = soup.select(".hrt-text-body-lg.hrt-font-bold.hrt-mb-0")
    texts = [e.get_text(strip=True) for e in elems]

    # Regex: match dollar amount before an 'r' (e.g., "$5,342 r")
    pattern = re.compile(r"\$(.*?)r", re.IGNORECASE)

    results = []
    for text in texts:
        match = pattern.search(text)
        if match:
            # Clean up commas and convert to number if desired
            raw_num = match.group(1).strip().replace(",", "")
            results.append(raw_num)
    return results


def main():
    html = fetch_html(URL)
    numbers = extract_dollar_values(html)
    if numbers:
        return(numbers[0])
        # for n in numbers:
            # print(n)
    else:
        print("No matches found. The content may be rendered dynamically with JavaScript.")


if __name__ == "__main__":
   result =  main()

print(result)