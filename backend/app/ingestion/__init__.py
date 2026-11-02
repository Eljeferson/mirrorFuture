"""
Mirror Future - Production Data Ingestion Package (Zero Mocks).
Provides WhatsApp chat parsers (.zip/.txt), lexical/latency profiler,
dense pgvector (384d) embedding engine, live web research engine,
and Google Calendar (.ics) / GitHub activity analyzers.
"""

from app.ingestion.whatsapp_parser import (
    WhatsAppParser,
    ParsedMessage
)
from app.ingestion.contact_profiler import (
    ContactProfiler
)
from app.ingestion.embedding_engine import (
    RealEmbeddingEngine,
    ConversationalEpisode,
    ConversationalChatSegmenter,
    DEFAULT_EMBEDDING_MODEL_NAME,
    VECTOR_DIMENSION
)
from app.ingestion.calendar_github import (
    RealCalendarParser,
    RealCalendarEvent,
    RealGitHubAnalyzer,
    RealProductivityCorrelator
)
from app.ingestion.live_web_research_engine import (
    LiveWebResearchEngine,
    live_web_engine
)

__all__ = [
    "WhatsAppParser",
    "ParsedMessage",
    "ContactProfiler",
    "RealEmbeddingEngine",
    "ConversationalEpisode",
    "ConversationalChatSegmenter",
    "DEFAULT_EMBEDDING_MODEL_NAME",
    "VECTOR_DIMENSION",
    "RealCalendarParser",
    "RealCalendarEvent",
    "RealGitHubAnalyzer",
    "RealProductivityCorrelator",
    "LiveWebResearchEngine",
    "live_web_engine",
]
