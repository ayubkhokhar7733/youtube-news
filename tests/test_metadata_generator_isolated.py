import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import metadata_generator

dummy_script = {
    "title": "The Discovery of Penicillin: The World-Changing Lab Mistake",
    "scenes": [
        {"narration": "In 1928, Alexander Fleming returned from vacation to find mold destroying bacteria on his petri dish."},
        {"narration": "This accidental discovery was refined by Howard Florey and Ernst Chain at Oxford."},
        {"narration": "Penicillin transformed medicine forever, saving hundreds of millions of lives."},
    ],
}

print("--- Testing Mock Generation ---")
mock_meta = metadata_generator.generate_metadata(dummy_script, topic="The Discovery of Penicillin: The World-Changing Lab Mistake", mock=True)
print(f"Mock Title: \"{mock_meta['title']}\" (Length: {len(mock_meta['title'])})")
assert not mock_meta['title'].lower().startswith("the the"), f"Duplicate article found: {mock_meta['title']}"
assert not mock_meta['title'].endswith("..."), f"Ellipsis found: {mock_meta['title']}"
assert len(mock_meta['title']) <= 70, f"Length > 70: {mock_meta['title']}"

print("\n--- Testing Live Groq Generation ---")
live_meta = metadata_generator.generate_metadata(dummy_script, topic="The Discovery of Penicillin: The World-Changing Lab Mistake", mock=False)
print(f"Live Title: \"{live_meta['title']}\" (Length: {len(live_meta['title'])})")
print(f"Pattern Used: {live_meta.get('pattern_used')}")
print(f"Tags Count: {len(live_meta.get('tags', []))}")
assert not live_meta['title'].lower().startswith("the the"), f"Duplicate article found: {live_meta['title']}"
assert not live_meta['title'].endswith("..."), f"Ellipsis found: {live_meta['title']}"
assert len(live_meta['title']) <= 70, f"Length > 70: {live_meta['title']}"

print("\n=== ALL ISOLATED METADATA TESTS PASSED ===")
