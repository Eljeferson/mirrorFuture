"""
Validation Test Suite for the Mirror Future Real Ingestion Pipeline.
Verifies:
1. whatsapp_parser.py (Android/iOS, 12h/24h, ES/EN, ZIP, Multiline, Unicode)
2. contact_profiler.py (Empirical median, % initiation, 0-23h active hours, top 25 words, top 10 emojis)
3. embedding_engine.py (Segmentation, 384 dimensions, MiniLM-L12-v2)
4. calendar_github.py (Google Calendar .ics and GitHub telemetry metrics)
"""

import io
import os
import sys
import zipfile
from datetime import datetime, timezone, timedelta

# Ensure UTF-8 output encoding on Windows console
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

# Ensure backend directory is in sys.path
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "backend"))
if backend_path not in sys.path:
    sys.path.insert(0, backend_path)

from app.ingestion.whatsapp_parser import WhatsAppParser
from app.ingestion.contact_profiler import ContactProfiler
from app.ingestion.embedding_engine import (
    RealEmbeddingEngine,
    ConversationalChatSegmenter,
    VECTOR_DIMENSION
)
from app.ingestion.calendar_github import (
    RealCalendarParser,
    RealCalendarEvent,
    RealGitHubAnalyzer,
    RealProductivityCorrelator
)
import icalendar


def test_whatsapp_parser_android():
    print("\n--- TEST: WhatsApp Parser (Android Spanish/English 12h/24h + Multiline + Unicode) ---")
    raw_chat = (
        "\u200e12/03/23, 10:00 - Messages and calls are end-to-end encrypted.\n"
        "12/03/23, 10:05\u202fa. m. - Dr. Elena Gomez: Hello, could you review the chapter 3 corrections?\n"
        "12/03/23, 10:15\u202fa. m. - You: Hi Dr., yes, I am running model experiments now.\n"
        "I have a quick question regarding the loss function formulation.\n"
        "12/03/23, 10:20\u202fa. m. - Dr. Elena Gomez: Check the weighted cross-entropy formulation 📊.\n"
        "12/03/23, 10:21\u202fa. m. - Dr. Elena Gomez: <Media omitted>\n"
        "12/03/23, 18:30 - You: Perfect, convergence reached with 384 dimensions 🚀\n"
        "12/03/23, 18:45 - Dr. Elena Gomez: Excellent news! See you tomorrow at the review committee 👏🎉\n"
    )

    parser = WhatsAppParser(user_name="You", contact_name="Dr. Elena Gomez")
    df, meta = parser.parse(raw_chat.encode("utf-8"))

    assert len(df) == 6, f"Expected 6 messages, got {len(df)}"
    assert meta["contact_name"] == "Dr. Elena Gomez"
    assert meta["user_name"] == "You"
    assert meta["user_messages_count"] == 2
    assert meta["contact_messages_count"] == 4

    # Verify multiline preservation
    multiline_msg = df[df["is_user"]].iloc[0]["text"]
    assert "I have a quick question regarding the loss function formulation." in multiline_msg

    print("✔ WhatsApp Parser Android verified successfully.")


def test_whatsapp_parser_ios_zip():
    print("\n--- TEST: WhatsApp Parser (iOS .zip export with _chat.txt) ---")
    raw_ios = (
        "[15/09/23, 14:30:10] Camila: Hey, what time are you leaving the lab? ❤️\n"
        "[15/09/23, 14:32:00] You: Leaving around 7pm as soon as the thesis model finishes compiling 💻\n"
        "[15/09/23, 14:33:15] Camila: Great let me know so we can have dinner together love you 😍🍕\n"
    )

    # In-memory zip creation
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "w") as zf:
        zf.writestr("_chat.txt", raw_ios.encode("utf-8"))

    parser = WhatsAppParser(user_name="You", contact_name="Camila")
    df, meta = parser.parse(zip_buffer.getvalue())

    assert len(df) == 3
    assert meta["contact_name"] == "Camila"
    assert meta["user_messages_count"] == 1
    assert meta["contact_messages_count"] == 2

    print("✔ WhatsApp Parser iOS .zip verified successfully.")


def test_contact_profiler_metrics():
    print("\n--- TEST: Contact Profiler (Response Median, % Initiation, 0-23h, Top Words/Emojis) ---")
    raw_chat = (
        "10/01/24, 08:00 - Carlos: Good morning colleague\n"
        "10/01/24, 08:10 - You: Hello Carlos how are you\n"
        "10/01/24, 08:20 - Carlos: Sharing the new training dataset with you 🔥🔥\n"
        "10/01/24, 08:25 - Carlos: Please review the model metrics report 📊\n"
        # Over 6 hours gap -> New conversation session
        "10/01/24, 16:00 - You: Evaluated the metrics, they look excellent 🔥\n"
        "10/01/24, 16:05 - Carlos: Fantastic, let's submit the thesis progress report today 🚀\n"
    )

    parser = WhatsAppParser(user_name="You", contact_name="Carlos")
    df, meta = parser.parse(raw_chat.encode("utf-8"))

    profiler = ContactProfiler(session_inactivity_hours=6.0)
    profile = profiler.build_full_profile(df, contact_name="Carlos")

    # Strict root column verification for real_contacts compatibility
    expected_root_columns = {
        "contact_name",
        "relationship_type",
        "total_messages_analyzed",
        "real_median_reply_minutes",
        "user_initiates_pct",
        "active_hours_distribution",
        "real_lexical_profile",
        "extracted_psych_summary",
        "last_interaction_at"
    }
    assert set(profile.keys()) == expected_root_columns, f"Root columns mismatch: {set(profile.keys())}"

    lex = profile["real_lexical_profile"]
    print(f"  * Carlos median reply latency: {profile['real_median_reply_minutes']} min")
    print(f"  * User initiation percentage: {profile['user_initiates_pct']}%")
    print(f"  * Total conversation sessions: {lex['total_conversation_sessions']}")
    print(f"  * User initiated sessions: {lex['user_initiated_sessions']}")

    # Session 1 started by Carlos (08:00), Session 2 started by You (16:00) -> 1 of 2 = 50%
    assert profile["user_initiates_pct"] == 50.0
    assert lex["total_conversation_sessions"] == 2
    assert lex["user_initiated_sessions"] == 1

    # Carlos reply median to You:
    # 1. You at 08:10 -> Carlos replies at 08:20 (10 minutes)
    # 2. You at 16:00 -> Carlos replies at 16:05 (5 minutes)
    # Median of [10, 5] = 7.5 minutes
    assert profile["real_median_reply_minutes"] == 7.5

    # Hourly distribution 0 to 23 hrs
    hours = profile["active_hours_distribution"]
    assert len(hours) == 24
    assert hours["8"] == 3   # Carlos sent at 08:00, 08:20, 08:25
    assert hours["16"] == 1  # Carlos sent at 16:05

    # Top emojis (must contain 🔥, 📊, 🚀)
    top_emojis = [item["emoji"] for item in lex["top_emojis"]]
    print(f"  * Top emojis: {top_emojis}")
    assert "🔥" in top_emojis
    assert "📊" in top_emojis

    # Top words
    top_words = [item["word"] for item in lex["top_words"]]
    print(f"  * Top words: {top_words[:5]}")
    assert any(w in top_words for w in ["metrics", "dataset", "report", "thesis", "training", "métrica", "reporte"])

    # Frequent idioms
    assert "frequent_idioms" in lex
    print(f"  * Frequent idioms: {lex['frequent_idioms'][:3]}")

    print("✔ Contact Profiler mathematically verified.")


def test_embedding_engine():
    print("\n--- TEST: Embedding Engine (Segmentation + 384d MiniLM-L12-v2 Vectorization) ---")
    raw_chat = (
        "01/02/24, 09:00 - You: Good morning Professor, sharing thesis milestones.\n"
        "01/02/24, 09:15 - Thesis Director: Thank you, reviewing methodology chapter and pgvector results.\n"
        "01/02/24, 09:20 - You: Standing by for your observations.\n"
        # 4-hour gap -> New episode
        "01/02/24, 14:00 - Thesis Director: The Monte Carlo mathematical analysis is very solid.\n"
        "01/02/24, 14:05 - You: Thank you Professor, simulations are now scripted in Python.\n"
    )

    parser = WhatsAppParser(user_name="You", contact_name="Thesis Director")
    df, meta = parser.parse(raw_chat.encode("utf-8"))

    engine = RealEmbeddingEngine()
    episodes = engine.process_and_vectorize_chat(df, contact_name="Thesis Director", user_name="You")

    assert len(episodes) == 2, f"Expected 2 episodes, got {len(episodes)}"

    for ep in episodes:
        assert ep.embedding is not None
        assert len(ep.embedding) == VECTOR_DIMENSION, f"Dimension {len(ep.embedding)} != {VECTOR_DIMENSION}"

    print(f"  * Episodes generated: {len(episodes)}")
    print(f"  * Verified vector dimension: {len(episodes[0].embedding)} d")
    print(f"  * Episode 1 summary: {episodes[0].conversation_summary}")
    print(f"  * Episode 1 tag: {episodes[0].conflict_or_support_tag}")

    # Test batch_insert_episodes with replace_existing=True
    insert_res = engine.batch_insert_episodes(episodes, contact_id="test-contact-123", replace_existing=True)
    assert insert_res["inserted_count"] == 2
    print(f"  * Batch insertion with replace_existing=True: {insert_res['status']}")

    print("✔ Embedding Engine 384d verified successfully.")


def test_calendar_and_github():
    print("\n--- TEST: Calendar .ics and GitHub Activity Analysis ---")
    
    # 1. Create real test .ics calendar
    cal = icalendar.Calendar()
    cal.add("prodid", "-//Mirror Future Production Test//")
    cal.add("version", "2.0")

    ev1 = icalendar.Event()
    ev1.add("summary", "Thesis Review Meeting with Advisor")
    ev1.add("description", "Chapter 3 progress review and experimental validation")
    ev1.add("dtstart", datetime(2024, 3, 15, 9, 0, tzinfo=timezone.utc))
    ev1.add("dtend", datetime(2024, 3, 15, 11, 0, tzinfo=timezone.utc)) # 2 hours
    cal.add_component(ev1)

    ev2 = icalendar.Event()
    ev2.add("summary", "Engineering Team Daily Standup")
    ev2.add("description", "Sprint synchronization and code review")
    ev2.add("dtstart", datetime(2024, 3, 15, 14, 0, tzinfo=timezone.utc))
    ev2.add("dtend", datetime(2024, 3, 15, 15, 0, tzinfo=timezone.utc)) # 1 hour
    cal.add_component(ev2)

    ics_bytes = cal.to_ical()
    events = RealCalendarParser.parse_ics(ics_bytes)
    cal_metrics = RealCalendarParser.calculate_busy_metrics(events)

    assert len(events) == 2
    assert cal_metrics["total_busy_hours"] == 3.0
    assert cal_metrics["thesis_hours_total"] == 2.0
    assert cal_metrics["work_hours_total"] == 1.0

    print(f"  * Total calendar busy hours: {cal_metrics['total_busy_hours']} hrs")
    print(f"  * Thesis hours in calendar: {cal_metrics['thesis_hours_total']} hrs")

    # 1.1 Monte Carlo daily projection starting today
    from app.models.schemas import DailyScheduleInput
    daily_schedule = RealCalendarParser.parse_ics_to_daily_hours(ics_bytes, num_days=180)
    assert len(daily_schedule) == 180
    assert isinstance(daily_schedule[0], DailyScheduleInput)
    assert daily_schedule[0].day_index == 0
    print(f"  * Monte Carlo daily schedule projected: {len(daily_schedule)} days from today.")

    # 2. Structured GitHub events simulation
    github_events_sample = [
        {
            "id": "1",
            "type": "PushEvent",
            "repo": {"name": "user/mirror-future-thesis"},
            "created_at": "2024-03-15T23:30:00Z", # Nocturnal (11:30 PM)
            "payload": {
                "commits": [
                    {"sha": "a1b2c3d", "message": "feat(thesis): add pgvector 384d semantic search for chat episodes"}
                ]
            }
        },
        {
            "id": "2",
            "type": "PushEvent",
            "repo": {"name": "user/dev-infra"},
            "created_at": "2024-03-15T16:00:00Z",
            "payload": {
                "commits": [
                    {"sha": "d4e5f6g", "message": "refactor: optimize database connection pooling"}
                ]
            }
        }
    ]

    analyzer = RealGitHubAnalyzer()
    gh_metrics = analyzer.analyze_events(github_events_sample)

    assert gh_metrics["total_commits"] == 2
    assert gh_metrics["thesis_commits_count"] == 1
    assert gh_metrics["nocturnal_commits_count"] == 1
    assert gh_metrics["nocturnal_commits_pct"] == 50.0

    print(f"  * Total GitHub commits: {gh_metrics['total_commits']}")
    print(f"  * Thesis commits: {gh_metrics['thesis_commits_count']}")
    print(f"  * Nocturnal percentage: {gh_metrics['nocturnal_commits_pct']}%")

    # 3. Correlation between calendar allocation and development pace
    correlation = RealProductivityCorrelator.correlate(cal_metrics, gh_metrics)
    print(f"  * Correlation status: {correlation['status']}")
    print(f"  * Thesis Pace Score: {correlation['thesis_pace_score']}")
    print(f"  * Burnout Risk Score: {correlation['burnout_risk_score']}")
    assert "thesis_pace_score" in correlation

    # 4. User profile telemetry builder
    user_telemetry = RealProductivityCorrelator.build_user_profile_telemetry(
        cal_metrics,
        gh_metrics,
        full_name="Principal Researcher",
        whatsapp_alias="You",
        occupation_and_goals="AI PhD Candidate & Dissertation Research",
        github_username="researcher"
    )
    assert user_telemetry["real_calendar_busy_hours_week"] > 0
    assert user_telemetry["real_study_thesis_hours_day"] > 0
    print(f"  * Telemetry generated for user profile: {user_telemetry}")

    print("✔ Calendar and GitHub Pipeline verified successfully.")


if __name__ == "__main__":
    test_whatsapp_parser_android()
    test_whatsapp_parser_ios_zip()
    test_contact_profiler_metrics()
    test_embedding_engine()
    test_calendar_and_github()
    print("\n========================================================")
    print("🚀 ALL MIRROR FUTURE INGESTION PIPELINE TESTS PASSED")
    print("========================================================")
