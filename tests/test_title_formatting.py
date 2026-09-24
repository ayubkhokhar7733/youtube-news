# Test script for title formatting and truncation logic
import re

def clean_topic_for_pattern(topic: str) -> str:
    """Cleans a topic string for embedding into pattern templates."""
    clean = topic.strip()
    # If topic has a colon with a long subtitle, use the main topic name if it's long enough
    if ":" in clean:
        parts = clean.split(":", 1)
        main_part = parts[0].strip()
        if len(main_part) >= 12:
            clean = main_part
    return clean

def strip_leading_article(text: str) -> str:
    """Strips leading 'the', 'a', 'an' (case-insensitive)."""
    return re.sub(r'^(the|a|an)\s+', '', text.strip(), flags=re.IGNORECASE)

def truncate_title(title: str, max_length: int = 70) -> str:
    """Intelligently shortens a title to max_length characters without mid-word splits."""
    title = " ".join(title.split()).strip()
    # Fix duplicate leading articles
    title = re.sub(r'^(the\s+)+the\b', 'The', title, flags=re.IGNORECASE)
    title = re.sub(r'^(a\s+)+a\b', 'A', title, flags=re.IGNORECASE)
    
    if len(title) <= max_length:
        return title
    
    # Try cutting at natural phrase breaks
    for delim in [": ", " - ", " – ", " — "]:
        if delim in title:
            prefix = title.split(delim)[0].strip()
            if 30 <= len(prefix) <= max_length:
                return prefix

    # Otherwise cut at word boundary (never slice mid-word)
    cut = title[:max_length].rsplit(" ", 1)[0].rstrip(" ,;:-—")
    return cut

def build_pattern_title(pattern: str, topic: str) -> str:
    base_topic = clean_topic_for_pattern(topic)
    topic_no_art = strip_leading_article(base_topic)
    
    titles_map = {
        "a": f"The {topic_no_art} Detail Nobody Talks About",
        "b": f"5 {topic_no_art} Facts That Sound Fake (But Aren't)",
        "c": f"Why Did {base_topic} Actually Happen?",
        "d": f"The Truth About {base_topic} Is Not What You Think",
        "e": f"The {topic_no_art} That Changed Everything",
    }
    raw_title = titles_map.get(pattern, titles_map["a"])
    return truncate_title(raw_title, max_length=70)

# Run tests
test_topics = [
    "The Discovery of Penicillin: The World-Changing Lab Mistake",
    "The Mary Celeste: The Ghost Ship Found Floating Perfectly Intact",
    "The Tunguska Event: The 1908 Siberian Explosion",
    "The Great Molasses Flood of 1919",
    "The Bronze Age Collapse: When Civilization Disappeared Overnight",
    "The Voynich Manuscript: The Book Nobody Can Read",
    "Antikythera Mechanism: Ancient Greek Computer",
    "Quantum Entanglement: Spooky Action at a Distance Explained in Simple Terms",
]

print("=== PATTERN TITLE TESTS ===")
for t in test_topics:
    print(f"\nORIGINAL TOPIC: {t}")
    for p in ["a", "b", "c", "d", "e"]:
        res = build_pattern_title(p, t)
        print(f"  [{p}] ({len(res)} chars): {res}")
        assert not res.lower().startswith("the the"), f"Duplicate 'The': {res}"
        assert not res.endswith("..."), f"Ellipsis truncation: {res}"
        assert len(res) <= 70, f"Exceeds 70 chars ({len(res)}): {res}"

print("\n=== ALL ISOLATED TESTS PASSED ===")
