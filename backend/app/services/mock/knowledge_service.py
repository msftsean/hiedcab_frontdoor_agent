"""
Mock knowledge base service for testing and demo mode.
Uses simple text matching against sample KB articles.
"""

import json
import re
from pathlib import Path
from typing import Optional

from app.models.enums import Department
from app.models.schemas import KnowledgeArticle
from app.services.interfaces import KnowledgeServiceInterface


class MockKnowledgeService(KnowledgeServiceInterface):
    """Mock implementation of knowledge base search."""

    def __init__(self) -> None:
        """Initialize with sample KB articles."""
        self._articles = self._load_articles()

    def _load_articles(self) -> list[dict]:
        """Load articles from mock data file."""
        mock_data_path = Path(__file__).parent.parent.parent.parent / "mock_data" / "sample_kb_articles.json"
        if mock_data_path.exists():
            with open(mock_data_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("articles", [])
        return []

    def _calculate_relevance(self, query: str, article: dict) -> float:
        """Calculate relevance score between query and article."""
        query_lower = query.lower()
        query_words = set(re.findall(r"\w+", query_lower))

        # Get searchable text from article
        title = article.get("title", "").lower()
        content = article.get("content", "").lower()
        tags = " ".join(article.get("tags", [])).lower()
        searchable_text = f"{title} {content} {tags}"
        article_words = set(re.findall(r"\w+", searchable_text))

        # Calculate word overlap
        common_words = query_words & article_words
        if not query_words:
            return 0.0

        # Base score from word overlap
        overlap_score = len(common_words) / len(query_words)

        # Boost for title matches
        title_words = set(re.findall(r"\w+", title))
        title_overlap = len(query_words & title_words)
        title_boost = title_overlap * 0.2

        # Boost for tag matches
        tag_words = set(re.findall(r"\w+", tags))
        tag_overlap = len(query_words & tag_words)
        tag_boost = tag_overlap * 0.15

        # Calculate final score
        score = min(1.0, overlap_score + title_boost + tag_boost)

        return round(score, 2)

    async def search(
        self,
        query: str,
        department: Optional[Department] = None,
        limit: int = 3,
    ) -> list[KnowledgeArticle]:
        """Search articles using text matching."""
        results = []

        for article in self._articles:
            # Filter by department if specified
            if department:
                article_dept = article.get("department")
                if article_dept and article_dept != department.value:
                    continue

            # Calculate relevance score
            score = self._calculate_relevance(query, article)
            if score > 0.1:  # Minimum threshold
                results.append((article, score))

        # Sort by relevance score descending
        results.sort(key=lambda x: x[1], reverse=True)

        # Convert to KnowledgeArticle objects
        articles = []
        for article, score in results[:limit]:
            articles.append(
                KnowledgeArticle(
                    article_id=article["article_id"],
                    title=article["title"],
                    url=article["url"],
                    snippet=article.get("snippet"),
                    relevance_score=score,
                    department=Department(article["department"]) if article.get("department") else None,
                )
            )

        return articles

    async def search_with_content(
        self,
        query: str,
        department: Optional[Department] = None,
        limit: int = 3,
    ) -> tuple[list[KnowledgeArticle], list[dict]]:
        """Search articles and return both metadata and full content."""
        results = []

        for article in self._articles:
            # Filter by department if specified
            if department:
                article_dept = article.get("department")
                if article_dept and article_dept != department.value:
                    continue

            # Calculate relevance score
            score = self._calculate_relevance(query, article)
            if score > 0.1:  # Minimum threshold
                results.append((article, score))

        # Sort by relevance score descending
        results.sort(key=lambda x: x[1], reverse=True)

        # Build both article metadata and full content lists
        articles = []
        contents = []
        for article, score in results[:limit]:
            articles.append(
                KnowledgeArticle(
                    article_id=article["article_id"],
                    title=article["title"],
                    url=article["url"],
                    snippet=article.get("snippet"),
                    relevance_score=score,
                    department=Department(article["department"]) if article.get("department") else None,
                )
            )
            contents.append({
                "article_id": article["article_id"],
                "title": article["title"],
                "content": article.get("content", ""),
                "snippet": article.get("snippet", ""),
                "tags": article.get("tags", []),
            })

        return articles, contents

    async def get_article(
        self,
        article_id: str,
    ) -> Optional[KnowledgeArticle]:
        """Get article by ID."""
        for article in self._articles:
            if article.get("article_id") == article_id:
                return KnowledgeArticle(
                    article_id=article["article_id"],
                    title=article["title"],
                    url=article["url"],
                    snippet=article.get("snippet"),
                    relevance_score=1.0,
                    department=Department(article["department"]) if article.get("department") else None,
                )
        return None

    async def health_check(self) -> tuple[bool, Optional[int], Optional[str]]:
        """Mock health check - always healthy."""
        return True, 15, None
