import re

ROLE = {"Internal": "REP", "External": "BUYER"}

def to_turns(call):
    turns = []
    for block in call["transcript"]:
        text = " ".join(s["text"] for s in block["sentences"])
        role = ROLE.get(call["parties"].get(block["speakerId"]), "OTHER")
        if turns and turns[-1]["role"] == role:
            turns[-1]["text"] += " " + text
        else:
            turns.append({"role": role, "text": text, "t": block["sentences"][0]["start"] // 1000})
    return turns

def redact(text):
    text = re.sub(r"[\w.+-]+@[\w-]+\.[\w.]+", "[EMAIL]", text)
    return re.sub(r"\+?\d[\d\s().-]{7,}\d", "[PHONE]", text)

def render(turns):
    return "\n".join(f"[{t['role']} @{t['t']}s] {t['text']}" for t in turns)

def chunk(turns, size=6, overlap=2):
    return [turns[i:i + size] for i in range(0, max(len(turns) - overlap, 1), size - overlap)]
