"""
Service for generating AI-powered summaries and highlights from transcriptions.
Uses OpenAI GPT models for intelligent content analysis.
"""

from typing import Any
from openai import AsyncOpenAI

from src.core.config import get_settings
from src.core.errors import TranscriptionFailedError

settings = get_settings()


class SummarizationService:
    """Service for generating video summaries using OpenAI GPT."""

    def __init__(self) -> None:
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-4o-mini"

    async def generate_summary(
        self,
        transcription_text: str,
        summary_type: str = "brief",
    ) -> str:
        """
        Generate summary from transcription text.

        Args:
            transcription_text: Full transcription text
            summary_type: Type of summary (brief, detailed, bullet_points)

        Returns:
            Generated summary text

        Raises:
            TranscriptionFailedError: If summarization fails
        """
        if summary_type == "brief":
            prompt = "Provide a concise 2-3 sentence summary of this video transcription."
        elif summary_type == "detailed":
            prompt = "Provide a comprehensive multi-paragraph summary covering all main topics."
        elif summary_type == "bullet_points":
            prompt = "Provide a bullet-point summary of key insights and takeaways."
        else:
            prompt = "Provide a concise summary of this video transcription."

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert content summarizer. Generate clear, accurate summaries.",
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nTranscription:\n{transcription_text}",
                    },
                ],
                temperature=0.3,
                max_tokens=1000,
            )

            if not response.choices or not response.choices[0].message.content:
                raise TranscriptionFailedError("No summary generated")

            return response.choices[0].message.content.strip()

        except Exception as e:
            raise TranscriptionFailedError(f"Summarization failed: {str(e)}")

    async def extract_highlights(
        self,
        transcription_text: str,
        max_highlights: int = 5,
    ) -> list[dict[str, Any]]:
        """
        Extract key highlights from transcription.

        Args:
            transcription_text: Full transcription text
            max_highlights: Maximum number of highlights to extract

        Returns:
            List of highlight dictionaries with text and importance

        Raises:
            TranscriptionFailedError: If highlight extraction fails
        """
        prompt = f"""
Extract the {max_highlights} most important highlights from this transcription.
Return as JSON array with objects containing:
- text: the key quote or insight
- importance_score: score from 0.0 to 1.0

Focus on actionable insights, key decisions, or main points.
"""

        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "Extract key highlights. Return valid JSON only.",
                    },
                    {
                        "role": "user",
                        "content": f"{prompt}\n\nTranscription:\n{transcription_text}",
                    },
                ],
                temperature=0.2,
                max_tokens=1500,
                response_format={"type": "json_object"},
            )

            if not response.choices or not response.choices[0].message.content:
                return []

            import json
            content = response.choices[0].message.content
            parsed = json.loads(content)
            highlights = parsed.get("highlights", [])

            return highlights if isinstance(highlights, list) else []

        except Exception:
            # Fallback to empty highlights on extraction failure
            return []


# Singleton instance
summarization_service = SummarizationService()
