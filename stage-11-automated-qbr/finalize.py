import sys
from pathlib import Path
from pptx import Presentation

if len(sys.argv) < 2:
    print("Usage: python finalize.py <path-to-draft.pptx>")
    sys.exit(1)

src = Path(sys.argv[1])
prs = Presentation(src)
open_items = []

for n, slide in enumerate(prs.slides, 1):
    for shape in list(slide.shapes):
        if not shape.has_text_frame:
            continue
        t = shape.text_frame.text
        if "[CSM:" in t:
            open_items.append(f"slide {n}: placeholder still present")
        if t.startswith("DRAFT:"):
            shape._element.getparent().remove(shape._element)
    if slide.has_notes_slide:
        slide.notes_slide.notes_text_frame.text = ""

review_file = src.parent / "review.md"
if review_file.exists() and "- [ ]" in review_file.read_text(encoding="utf-8"):
    open_items.append("review.md has unchecked boxes")

if open_items:
    raise SystemExit("Not final:\n" + "\n".join(open_items))

final = src.with_name(src.name.replace("-DRAFT", ""))
prs.save(final)
print("wrote", final)
