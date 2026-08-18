from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote
from urllib.request import Request, urlopen
import xml.etree.ElementTree as ET

from orbit.models import Claim, ResearchBrief, Source


@dataclass(frozen=True)
class ResearchResult:
    title: str
    url: str
    publisher: str
    summary: str


class ResearchAgent:
    """Zero-cost research bootstrap using public RSS feeds.

    This deliberately avoids scraping private systems or paid search APIs.
    A richer provider can be added later behind the same interface.
    """

    RSS_TEMPLATE = "https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"

    def search(self, query: str, limit: int = 8) -> list[ResearchResult]:
        url = self.RSS_TEMPLATE.format(query=quote(query))
        request = Request(url, headers={"User-Agent": "ORBIT/0.1"})
        with urlopen(request, timeout=15) as response:
            root = ET.fromstring(response.read())

        results: list[ResearchResult] = []
        for item in root.findall("./channel/item")[:limit]:
            title = (item.findtext("title") or "").strip()
            link = (item.findtext("link") or "").strip()
            source = item.find("source")
            publisher = (source.text or "").strip() if source is not None else ""
            description = (item.findtext("description") or "").strip()
            if title and link:
                results.append(ResearchResult(title, link, publisher, description))
        return results

    def build_brief(self, topic: str, results: list[ResearchResult]) -> ResearchBrief:
        claims = [
            Claim(
                text=result.title,
                sources=[Source(title=result.title, url=result.url, publisher=result.publisher, reliability=0.5)],
                confidence="low",
            )
            for result in results
        ]
        summary = "\n".join(f"- {r.title} ({r.publisher})" for r in results)
        questions = [
            "What primary source supports the most important claim?",
            "What evidence would change the story's conclusion?",
            "What is genuinely new or surprising for the viewer?",
        ]
        return ResearchBrief(topic=topic, summary=summary, claims=claims, open_questions=questions)
