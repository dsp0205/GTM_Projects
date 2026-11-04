import json
import re
from pydantic import BaseModel
from metrics import Fact

MODEL = "claude-sonnet-5-5"
TOKEN = re.compile(r"\{(\w+)\}")
SYSTEM = (
    "You write the executive summary slide of a customer business review. "
    "You get a list of facts with ids. Refer to a number ONLY by writing its id in braces, "
    "for example {hours_saved}. Never write a digit or a spelled-out number yourself. "
    "Use only the facts given. If the facts do not support a claim, leave it out. "
    "Write one headline sentence and exactly 3 short bullets. Plain words, no hype."
)

class Summary(BaseModel):
    headline: str
    bullets: list[str]

def check(s: Summary, facts: dict[str, Fact]) -> None:
    for text in [s.headline, *s.bullets]:
        unknown = set(TOKEN.findall(text)) - set(facts)
        if unknown:
            raise ValueError(f"unknown fact ids: {unknown}")
        rest = TOKEN.sub("", text)
        if re.search(r"\d", rest):
            raise ValueError(f"model wrote its own digits: {text!r}")
        if "{" in rest or "}" in rest:
            raise ValueError(f"malformed placeholder: {text!r}")
    if len(s.bullets) != 3:
        raise ValueError("need exactly 3 bullets")

def render(s: Summary, facts: dict[str, Fact]) -> Summary:
    def fill(t: str) -> str:
        return TOKEN.sub(lambda m: facts[m.group(1)].show(), t)
    return Summary(headline=fill(s.headline), bullets=[fill(b) for b in s.bullets])

def fallback() -> Summary:
    return Summary(
        headline="{hours_saved} saved this quarter, a {roi} return on the license.",
        bullets=["{tasks} tasks completed, {tasks_change} versus last quarter.",
                 "{utilization} of licensed seats were active in an average week.",
                 "The investment pays back its onboarding fee in {payback}."])

def write_summary(facts: dict[str, Fact], client=None, tries: int = 2) -> Summary:
    if client is not None:
        table = json.dumps([{"id": f.id, "label": f.label, "value": round(float(f.value), 3)}
                            for f in facts.values()])
        for _ in range(tries):
            resp = client.messages.parse(
                model=MODEL, max_tokens=800, system=SYSTEM,
                messages=[{"role": "user", "content": f"Facts:\n{table}"}],
                output_format=Summary)
            try:
                check(resp.parsed_output, facts)
                return render(resp.parsed_output, facts)
            except ValueError as e:
                print("rejected model output:", e)
    return render(fallback(), facts)
