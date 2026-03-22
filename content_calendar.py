"""
Content Calendar - Tracks posted topics to avoid repeats and ensure balanced content mix.
Stores data in a local JSON file (content_history.json).
"""

import json
import os
from datetime import datetime, timedelta

HISTORY_FILE = os.path.join(os.path.dirname(__file__), "content_history.json")

TOPIC_OPTIONS = [
    "Software Engineering Internships",
    "Free AI/Tech Courses",
    "Resume Building Tips",
    "Interview Preparation",
    "Career Growth Mindset",
    "Hackathons & Competitions",
    "Freelancing & Side Projects",
    "LinkedIn Profile Optimization",
]


def load_history() -> list:
    """Load posting history from JSON file."""
    if not os.path.exists(HISTORY_FILE):
        return []
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []


def save_history(history: list):
    """Save posting history to JSON file."""
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)


def log_post(topic: str, post_preview: str):
    """Log a completed post to the history."""
    history = load_history()
    history.append({
        "date": datetime.now().isoformat(),
        "topic": topic,
        "preview": post_preview[:100],
    })
    # Keep only the last 90 days of history
    cutoff = (datetime.now() - timedelta(days=90)).isoformat()
    history = [h for h in history if h["date"] >= cutoff]
    save_history(history)


def get_recent_topics(days: int = 7) -> list:
    """Get topics posted in the last N days."""
    history = load_history()
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    recent = [h for h in history if h["date"] >= cutoff]
    return recent


def get_topic_summary() -> str:
    """
    Returns a human-readable summary of recent posting activity 
    that can be fed to the Head Agent.
    """
    recent = get_recent_topics(days=7)
    if not recent:
        return (
            "CONTENT CALENDAR: No posts recorded in the last 7 days. "
            f"Available topics: {', '.join(TOPIC_OPTIONS)}. "
            "Pick any topic freely."
        )

    topic_counts = {}
    for entry in recent:
        t = entry["topic"]
        topic_counts[t] = topic_counts.get(t, 0) + 1

    lines = ["CONTENT CALENDAR - Last 7 days:"]
    for entry in recent:
        date_str = entry["date"][:10]
        lines.append(f"  - {date_str}: {entry['topic']}")

    # Identify topics NOT posted recently
    posted_topics = set(topic_counts.keys())
    fresh_topics = [t for t in TOPIC_OPTIONS if t not in posted_topics]

    lines.append(f"\nTopics already covered this week: {', '.join(posted_topics)}")
    if fresh_topics:
        lines.append(f"RECOMMENDED fresh topics (not posted recently): {', '.join(fresh_topics)}")
    else:
        lines.append("All topics have been covered this week. Pick the one with the least posts.")

    return "\n".join(lines)
