import json
import os
import sqlite3
import sys

MODEL = os.environ.get("ANTHROPIC_MODEL", "claude-sonnet-5-5")
PROMPT_VERSION = "v1"
CHANNELS = ["peer_word_of_mouth", "community", "podcast", "social_post", "search",
            "ai_assistant", "review_site", "event", "ad", "other", "unknown"]
SYSTEM = ("You code survey answers to 'How did you hear about us?'. Pick one channel. "
          "peer_word_of_mouth is a person (friend, coworker). community is a Slack, Discord "
          "or forum group. Use unknown when no source is stated. Copy any named person, "
          "podcast, group or site into named_source, else an empty string. Never guess.")
SCHEMA = {
    "type": "object",
    "properties": {"channel": {"type": "string", "enum": CHANNELS},
                   "named_source": {"type": "string"},
                   "confidence": {"type": "string", "enum": ["low", "medium", "high"]}},
    "required": ["channel", "named_source", "confidence"],
    "additionalProperties": False,
}
RULES = [("peer_word_of_mouth", ("friend", "colleague", "coworker", "word of mouth")),
         ("community", ("discord", "slack")), ("podcast", ("podcast",)),
         ("ai_assistant", ("chatgpt",)), ("review_site", ("g2", "review")),
         ("search", ("google", "search"))]

def code_with_claude(client, text):
    resp = client.messages.create(
        model=MODEL, max_tokens=300, system=SYSTEM,
        messages=[{"role": "user", "content": f"<answer>{text}</answer>"}],
        output_config={"format": {"type": "json_schema", "schema": SCHEMA}},
    )
    if resp.stop_reason != "end_turn":
        raise RuntimeError(f"unexpected stop_reason {resp.stop_reason}")
    return json.loads(next(b.text for b in resp.content if b.type == "text"))

def code_offline(text):
    low = text.lower()
    for channel, words in RULES:
        if any(w in low for w in words):
            return {"channel": channel, "named_source": "", "confidence": "low"}
    return {"channel": "unknown", "named_source": "", "confidence": "low"}

if __name__ == "__main__":
    offline = "--offline" in sys.argv
    client = None
    if not offline:
        from dotenv import load_dotenv, find_dotenv
        import anthropic
        load_dotenv(find_dotenv(usecwd=True))
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("No ANTHROPIC_API_KEY found. Falling back to --offline.")
            offline = True
        else:
            client = anthropic.Anthropic(api_key=api_key)

    version = f"offline-{PROMPT_VERSION}" if offline else f"claude-{PROMPT_VERSION}"
    db = sqlite3.connect("dark_social.db")
    if "--recode" in sys.argv:
        db.execute("DELETE FROM coded_answers")
    rows = db.execute("""SELECT s.signup_id, s.hdyhau_text FROM signups s
        LEFT JOIN coded_answers c USING (signup_id) WHERE c.signup_id IS NULL""").fetchall()
    for signup_id, text in rows:
        text = text or ""
        r = code_offline(text) if offline else code_with_claude(client, text)
        db.execute("INSERT INTO coded_answers VALUES (?,?,?,?,?)",
                   (signup_id, r["channel"], r["named_source"], r["confidence"], version))
        db.commit()
    print(f"coded {len(rows)} answers with {version}")
    db.close()
