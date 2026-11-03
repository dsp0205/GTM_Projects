import json, random

random.seed(7)
REP, BUYER = "1001", "2002"
OBJ = {
    "price": ["Your price is about double what we pay today.",
              "Finance says the annual commit is too high for us."],
    "security": ["Our security team needs SOC 2 Type II before we sign.",
                 "Where is call data stored, and can we choose the region?"],
    "integration": ["We live in Salesforce. Does it write back without a custom build?",
                    "Our last vendor promised a Salesforce sync and it took four months."],
    "competitor": ["We are also looking at Gong, and they have the bigger name.",
                   "Another vendor showed us a cheaper bundle with the same features."],
    "timing": ["We are mid-reorg, so this has to wait until next fiscal year.",
               "Not now. Come back in January when the new VP starts."],
}
WEAK = ["I understand. Let me send you a deck.", "No problem. I will follow up next week."]
GOOD = ["Two customers had that concern. I can share what they did."]

def make_call(i):
    turns = [(REP, "Thanks for making time. Let me show you the platform."),
             (BUYER, "Sure. We have forty reps and a messy call process."),
             (REP, "What gets in the way of a decision on your side?")]
    for theme in random.sample(list(OBJ), k=random.choice([1, 2, 2, 3])):
        turns += [(BUYER, random.choice(OBJ[theme])),
                  (REP, random.choice(WEAK if random.random() < .7 else GOOD))]
    turns.append((BUYER, "Thanks. We will think about it."))
    tr = [{"speakerId": who, "topic": "Objections",
           "sentences": [{"start": 6000 * n, "end": 6000 * n + 4000, "text": text}]}
          for n, (who, text) in enumerate(turns, 1)]
    return {"callId": f"call-{i:03d}", "parties": {REP: "Internal", BUYER: "External"},
            "transcript": tr}

if __name__ == "__main__":
    calls = [make_call(i) for i in range(100)]
    with open("lost_calls.json", "w", encoding="utf-8") as f:
        json.dump(calls, f, indent=2)
    print("Generated 100 synthetic lost calls in lost_calls.json")
