import html
import re
from pathlib import Path
import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md


SCRIPT_RE = re.compile(
    r'self\.__next_f\.push\(\[1,\s*"(?P<payload>(?:\\.|[^"\\])*)"\]\)\s*',
    re.DOTALL,
)


class GranolarParser:
    def __init__(self, source: str):
        self.source = source

    def read_html(self) -> str:
        if self.source.startswith("http://") or self.source.startswith("https://"):
            resp = requests.get(self.source, timeout=30)
            resp.raise_for_status()
            return resp.text
        return Path(self.source).read_text(encoding="utf-8")

    def extract_second_to_last_script(self, html_text: str) -> str:
        soup = BeautifulSoup(html_text, "html.parser")
        scripts = [s for s in soup.find_all("script") if (s.string or s.get_text())]
        if len(scripts) < 2:
            raise ValueError("Expected at least 2 inline <script> tags.")
        return scripts[-2].get_text()

    def decode_payload(self, script_text: str) -> str:
        match = SCRIPT_RE.search(script_text)
        if not match:
            raise ValueError("Could not find __next_f payload in script.")
        raw = match.group("payload")
        decoded = raw.encode("utf-8").decode("unicode_escape")
        return html.unescape(decoded)

    def html_to_markdown(self, html_payload: str) -> str:
        return md(html_payload)
