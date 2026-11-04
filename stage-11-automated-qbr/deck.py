from pptx import Presentation
from pptx.chart.data import CategoryChartData
from pptx.dml.color import RGBColor
from pptx.enum.chart import XL_CHART_TYPE
from pptx.util import Inches, Pt

BRAND = {"navy": RGBColor(0x1F, 0x2A, 0x44), "teal": RGBColor(0x0E, 0x7C, 0x86),
         "grey": RGBColor(0x6B, 0x72, 0x80), "font": "Calibri"}

def text(slide, x, y, w, h, s, size=18, bold=False, color="navy"):
    tf = slide.shapes.add_textbox(Inches(x), Inches(y), Inches(w), Inches(h)).text_frame
    tf.word_wrap = True
    for i, line in enumerate(s.split("\n")):
        p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
        p.text = line
        p.font.size, p.font.bold, p.font.name = Pt(size), bold, BRAND["font"]
        p.font.color.rgb = BRAND[color]
    return tf

def new_slide(prs, title, footer, draft):
    s = prs.slides.add_slide(prs.slide_layouts[6])
    text(s, 0.6, 0.4, 12.1, 1.2, title, size=28, bold=True)
    text(s, 0.6, 6.95, 10, 0.4, footer, size=11, color="grey")
    if draft:
        text(s, 10.5, 6.95, 2.4, 0.4, "DRAFT: CSM review pending", size=11, bold=True, color="teal")
    return s

def build(account_name, quarter_label, weekly, facts, summary, assumptions, out_path, draft=True):
    prs = Presentation()
    prs.slide_width, prs.slide_height = Inches(13.333), Inches(7.5)
    foot = f"{account_name} | {quarter_label} business review | Source: product usage data"

    s = prs.slides.add_slide(prs.slide_layouts[6])
    text(s, 0.8, 2.4, 11.5, 1.2, f"{account_name}: {quarter_label} business review", size=40, bold=True)
    text(s, 0.8, 3.8, 11.5, 0.6, "Value delivered and plan for next quarter", size=20, color="teal")

    s = new_slide(prs, summary.headline, foot, draft)
    text(s, 0.8, 2.0, 11.5, 4, "\n".join(summary.bullets), size=22)

    ch = facts["tasks_change"].value
    s = new_slide(prs, f"Tasks completed {'grew' if ch >= 0 else 'fell'} {abs(ch):.0%} quarter on quarter",
                  foot, draft)
    cd = CategoryChartData(number_format="#,##0")
    cd.categories = list(weekly["week_start"])
    cd.add_series("Tasks completed per week", list(weekly["tasks_completed"]))
    chart = s.shapes.add_chart(XL_CHART_TYPE.LINE, Inches(0.8), Inches(1.9), Inches(11.7),
                               Inches(4.8), cd).chart
    chart.has_legend = False
    chart.value_axis.has_major_gridlines = False
    chart.series[0].format.line.color.rgb = BRAND["teal"]
    chart.series[0].format.line.width = Pt(3)
    chart.series[0].smooth = False

    s = new_slide(prs, f"{facts['hours_saved'].show()} saved: {facts['value'].show()} of labor value "
                       f"against {facts['cost'].show()} of license", foot, draft)
    keys = ("tasks", "hours_saved", "value", "cost", "roi", "payback")
    rows = [("Measure", "This quarter")] + [(facts[k].label, facts[k].show()) for k in keys]
    t = s.shapes.add_table(len(rows), 2, Inches(0.8), Inches(1.9), Inches(11.7),
                           Inches(0.5 * len(rows))).table
    for i, row in enumerate(rows):
        for j, v in enumerate(row):
            t.cell(i, j).text = v
            t.cell(i, j).text_frame.paragraphs[0].font.size = Pt(18)

    s = new_slide(prs, "How we calculated this, so you can challenge it", foot, draft)
    text(s, 0.8, 1.9, 11.5, 4.5, "\n".join(f"- {a}" for a in assumptions), size=18)

    s = new_slide(prs, "Next quarter: two decisions for you", foot, draft)
    text(s, 0.8, 1.9, 11.5, 4, "[CSM: write the two recommendations and the ask]", size=22, color="grey")
    s.notes_slide.notes_text_frame.text = "Fill in from the last call. Delete this note before sending."

    prs.save(out_path)
