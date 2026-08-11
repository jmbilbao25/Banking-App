#!/usr/bin/env python3
"""Build CloudConsolidation_ProposalPaper.docx from the Markdown source.

Pandoc is not available in this environment, so this does the conversion
directly with python-docx. That is a feature rather than a workaround: it lets
the output carry a real title page, a Word field-based table of contents that
repaginates itself, genuine Word tables that can be re-styled by the reader, and
a landscape section for the wide topology figure.

Supported Markdown subset -- deliberately only what the paper actually uses:

    # .. ####     headings
    | a | b |     tables, including alignment rows
    - / 1.        bullet and numbered lists
    ```code```    fenced code blocks
    ---           horizontal rule (rendered as spacing, not a line)
    **bold**, *italic*, `code`, [text](url)

Usage:  python3 build_docx.py
"""
from __future__ import annotations

import os
import re
import sys

from docx import Document
from docx.enum.section import WD_ORIENT, WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "CloudConsolidation_ProposalPaper.md")
OUT = os.path.join(HERE, "CloudConsolidation_ProposalPaper.docx")
FIGURE = os.path.normpath(os.path.join(
    HERE, "..", "architecture", "excalidraw", "preview", "05-network-topology.png"))

BODY_FONT = "Aptos"          # matches the user's Word default
MONO_FONT = "Consolas"
INK = RGBColor(0x1E, 0x29, 0x3B)
ACCENT = RGBColor(0x1D, 0x4E, 0xD8)
MUTED = RGBColor(0x64, 0x74, 0x8B)
HEADER_SHADE = "DBEAFE"
CODE_SHADE = "F1F5F9"


# --------------------------------------------------------------------------
# low-level helpers
# --------------------------------------------------------------------------
def shade(cell_or_para, hexcolor: str) -> None:
    """Apply a solid background fill to a table cell or a paragraph."""
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear")
    el.set(qn("w:color"), "auto")
    el.set(qn("w:fill"), hexcolor)
    target = (cell_or_para._tc.get_or_add_tcPr()
              if hasattr(cell_or_para, "_tc")
              else cell_or_para._p.get_or_add_pPr())
    target.append(el)


def field(paragraph, instr: str) -> None:
    """Insert a Word field code, e.g. PAGE or TOC.

    Fields are computed by Word, not by us, so the table of contents and the
    page numbers stay correct after the reader edits the document.
    """
    run = paragraph.add_run()
    begin = OxmlElement("w:fldChar")
    begin.set(qn("w:fldCharType"), "begin")
    instr_el = OxmlElement("w:instrText")
    instr_el.set(qn("xml:space"), "preserve")
    instr_el.text = instr
    sep = OxmlElement("w:fldChar")
    sep.set(qn("w:fldCharType"), "separate")
    end = OxmlElement("w:fldChar")
    end.set(qn("w:fldCharType"), "end")
    for el in (begin, instr_el, sep, end):
        run._r.append(el)


def hyperlink(paragraph, url: str, text: str) -> None:
    part = paragraph.part
    r_id = part.relate_to(
        url,
        "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink",
        is_external=True)
    link = OxmlElement("w:hyperlink")
    link.set(qn("r:id"), r_id)
    run = OxmlElement("w:r")
    props = OxmlElement("w:rPr")
    colour = OxmlElement("w:color")
    colour.set(qn("w:val"), "1D4ED8")
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    props.append(colour)
    props.append(underline)
    run.append(props)
    text_el = OxmlElement("w:t")
    text_el.text = text
    run.append(text_el)
    link.append(run)
    paragraph._p.append(link)


# --------------------------------------------------------------------------
# inline formatting
# --------------------------------------------------------------------------
# Ordered so that ** is consumed before *, and links before everything else.
INLINE = re.compile(
    r"(\[[^\]]+\]\([^)]+\))"      # links
    r"|(\*\*[^*]+\*\*)"           # bold
    r"|(`[^`]+`)"                 # code
    r"|(\*[^*]+\*)"               # italic
)


def write_inline(paragraph, text: str, *, size=None, colour=None,
                 bold_all=False, italic_all=False) -> None:
    """Render one line of Markdown inline formatting into a paragraph."""
    for part in INLINE.split(text):
        if not part:
            continue
        link = re.fullmatch(r"\[([^\]]+)\]\(([^)]+)\)", part)
        if link:
            hyperlink(paragraph, link.group(2), link.group(1))
            continue
        bold, italic, mono = bold_all, italic_all, False
        if part.startswith("**") and part.endswith("**") and len(part) > 4:
            part, bold = part[2:-2], True
        elif part.startswith("`") and part.endswith("`") and len(part) > 2:
            part, mono = part[1:-1], True
        elif part.startswith("*") and part.endswith("*") and len(part) > 2:
            part, italic = part[1:-1], True
        run = paragraph.add_run(part)
        run.bold = bold
        run.italic = italic
        run.font.name = MONO_FONT if mono else BODY_FONT
        run.font.size = Pt(9.5) if mono else (size or Pt(10.5))
        if mono:
            run.font.color.rgb = RGBColor(0xB4, 0x53, 0x09)
        elif colour is not None:
            run.font.color.rgb = colour


# --------------------------------------------------------------------------
# document setup
# --------------------------------------------------------------------------
def configure(doc: Document) -> None:
    normal = doc.styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = INK
    normal.paragraph_format.space_after = Pt(7)
    normal.paragraph_format.line_spacing = 1.15

    for name, size, colour, before, after in (
        ("Heading 1", 19, ACCENT, 22, 9),
        ("Heading 2", 14.5, ACCENT, 16, 7),
        ("Heading 3", 12, INK, 13, 5),
        ("Heading 4", 10.5, INK, 11, 4),
    ):
        st = doc.styles[name]
        st.font.name = BODY_FONT
        st.font.size = Pt(size)
        st.font.color.rgb = colour
        st.font.bold = True
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True

    section = doc.sections[0]
    section.page_width, section.page_height = Inches(8.27), Inches(11.69)  # A4
    for attr in ("top_margin", "bottom_margin"):
        setattr(section, attr, Inches(0.9))
    for attr in ("left_margin", "right_margin"):
        setattr(section, attr, Inches(0.95))

    footer = section.footer.paragraphs[0]
    footer.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run = footer.add_run("Cloud Consolidation Proposal    |    ")
    run.font.size = Pt(8)
    run.font.color.rgb = MUTED
    run.font.name = BODY_FONT
    field(footer, "PAGE")
    for r in footer.runs:
        r.font.size = Pt(8)
        r.font.color.rgb = MUTED
        r.font.name = BODY_FONT


def title_page(doc: Document) -> None:
    for _ in range(3):
        doc.add_paragraph()

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("CLOUD CONSOLIDATION PROPOSAL")
    r.font.size = Pt(11)
    r.font.bold = True
    r.font.color.rgb = MUTED
    r.font.name = BODY_FONT

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(14)
    r = p.add_run("Consolidating a Two-Application Payment\nPrototype onto a Single Azure Platform")
    r.font.size = Pt(25)
    r.font.bold = True
    r.font.color.rgb = ACCENT
    r.font.name = BODY_FONT

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(10)
    r = p.add_run("A Proposal Paper on Cloud Consolidation, Database Engine\n"
                  "Selection, and Network Segregation")
    r.font.size = Pt(12.5)
    r.font.italic = True
    r.font.color.rgb = INK
    r.font.name = BODY_FONT

    for _ in range(2):
        doc.add_paragraph()

    meta = doc.add_table(rows=0, cols=2)
    meta.alignment = WD_TABLE_ALIGNMENT.CENTER
    for key, value in (
        ("Subject system", "jmbilbao25/Banking-App"),
        ("", "banking application + e-commerce application"),
        ("Document type", "Proposal paper"),
        ("Version", "1.0"),
        ("Status", "For review"),
    ):
        row = meta.add_row().cells
        kp = row[0].paragraphs[0]
        kp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        kr = kp.add_run(key)
        kr.font.bold = True
        kr.font.size = Pt(10)
        kr.font.color.rgb = MUTED
        kr.font.name = BODY_FONT
        vr = row[1].paragraphs[0].add_run(value)
        vr.font.size = Pt(10)
        vr.font.color.rgb = INK
        vr.font.name = BODY_FONT
    for row in meta.rows:
        row.cells[0].width = Inches(1.6)
        row.cells[1].width = Inches(3.4)

    doc.add_paragraph()
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(
        "This paper answers two questions: whether the banking and e-commerce\n"
        "applications share a database, and which database engine the\n"
        "consolidated platform should use.")
    r.font.size = Pt(9.5)
    r.font.italic = True
    r.font.color.rgb = MUTED
    r.font.name = BODY_FONT

    doc.add_page_break()

    doc.add_heading("Contents", level=1)
    p = doc.add_paragraph()
    field(p, r'TOC \o "1-3" \h \z \u')
    p = doc.add_paragraph()
    r = p.add_run("If the contents list appears empty, right-click it and choose "
                  "\u201cUpdate Field\u201d \u2014 Word builds it on demand.")
    r.font.size = Pt(9)
    r.font.italic = True
    r.font.color.rgb = MUTED
    r.font.name = BODY_FONT
    doc.add_page_break()


def add_figure(doc: Document) -> None:
    """The topology figure, in its own landscape section so it is legible."""
    if not os.path.exists(FIGURE):
        sys.stderr.write(f"WARNING: figure not found at {FIGURE}\n")
        return

    landscape = doc.add_section(WD_SECTION.NEW_PAGE)
    landscape.orientation = WD_ORIENT.LANDSCAPE
    landscape.page_width, landscape.page_height = Inches(11.69), Inches(8.27)
    for attr in ("top_margin", "bottom_margin", "left_margin", "right_margin"):
        setattr(landscape, attr, Inches(0.5))

    doc.add_heading("Figure 1 \u2014 Target Network Topology", level=1)
    p = doc.add_paragraph()
    write_inline(p, "Hub and spoke, one region. The numbers 1 to 6 trace a single "
                    "customer payment from phone to database. Full-resolution and "
                    "editable versions are listed in Section 8.2.",
                 size=Pt(9.5), colour=MUTED, italic_all=True)

    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.space_before = Pt(4)
    p.add_run().add_picture(FIGURE, width=Inches(10.6))

    portrait = doc.add_section(WD_SECTION.NEW_PAGE)
    portrait.orientation = WD_ORIENT.PORTRAIT
    portrait.page_width, portrait.page_height = Inches(8.27), Inches(11.69)
    for attr in ("top_margin", "bottom_margin"):
        setattr(portrait, attr, Inches(0.9))
    for attr in ("left_margin", "right_margin"):
        setattr(portrait, attr, Inches(0.95))


# --------------------------------------------------------------------------
# block parsing
# --------------------------------------------------------------------------
def split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def is_divider(line: str) -> bool:
    return bool(re.fullmatch(r"\|[\s:|-]+\|", line.strip()))


def add_table(doc: Document, rows: list[list[str]]) -> None:
    width = max(len(r) for r in rows)
    table = doc.add_table(rows=0, cols=width)
    table.style = "Table Grid"
    table.alignment = WD_TABLE_ALIGNMENT.CENTER

    for i, cells in enumerate(rows):
        cells = cells + [""] * (width - len(cells))
        row = table.add_row()
        for cell, text in zip(row.cells, cells):
            cell.paragraphs[0].text = ""
            para = cell.paragraphs[0]
            para.paragraph_format.space_after = Pt(2)
            para.paragraph_format.space_before = Pt(2)
            # a centred single-character cell is a score column; keep it centred
            if i > 0 and len(text) <= 3 and text.strip().isdigit():
                para.alignment = WD_ALIGN_PARAGRAPH.CENTER
            write_inline(para, text, size=Pt(9), bold_all=(i == 0))
            if i == 0:
                shade(cell, HEADER_SHADE)

    para = doc.add_paragraph()
    para.paragraph_format.space_after = Pt(9)


def add_code(doc: Document, lines: list[str]) -> None:
    for line in lines:
        p = doc.add_paragraph()
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.left_indent = Inches(0.22)
        p.paragraph_format.line_spacing = 1.0
        shade(p, CODE_SHADE)
        r = p.add_run(line if line.strip() else " ")
        r.font.name = MONO_FONT
        r.font.size = Pt(8.5)
        r.font.color.rgb = INK
    doc.add_paragraph().paragraph_format.space_after = Pt(6)


def build() -> None:
    with open(SRC, encoding="utf-8") as fh:
        lines = fh.read().split("\n")

    doc = Document()
    configure(doc)
    title_page(doc)

    i = 0
    figure_done = False
    # the paper's own H1/H2 title block is replaced by the title page
    skipping_frontmatter = True

    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        # Everything above the executive summary is title-block material that the
        # generated title page already carries, so drop it rather than repeat it.
        if skipping_frontmatter:
            if re.match(r"^#{1,3}\s+Executive Summary\s*$", stripped):
                skipping_frontmatter = False
            else:
                i += 1
                continue

        # ---- fenced code
        if stripped.startswith("```"):
            i += 1
            block: list[str] = []
            while i < len(lines) and not lines[i].strip().startswith("```"):
                block.append(lines[i])
                i += 1
            i += 1
            add_code(doc, block)
            continue

        # ---- table
        if stripped.startswith("|") and stripped.endswith("|"):
            rows: list[list[str]] = []
            while i < len(lines):
                cur = lines[i].strip()
                if not (cur.startswith("|") and cur.endswith("|")):
                    break
                if not is_divider(cur):
                    rows.append(split_row(cur))
                i += 1
            if rows:
                add_table(doc, rows)
            continue

        # ---- headings
        heading = re.match(r"^(#{1,4})\s+(.*)$", stripped)
        if heading:
            level = len(heading.group(1))
            text = heading.group(2).strip()

            # The source uses H1 for the paper title, which the title page now
            # carries, so every remaining level shifts up one. Numbered sections
            # then land on Heading 1 and drive the table of contents correctly.
            level = max(1, level - 1)

            # place the figure immediately before Section 9
            if not figure_done and text.startswith("9."):
                add_figure(doc)
                figure_done = True

            para = doc.add_heading("", level=level)
            write_inline(para, text,
                         size=Pt({1: 19, 2: 14.5, 3: 12, 4: 10.5}[level]),
                         colour=ACCENT if level <= 2 else INK,
                         bold_all=True)
            i += 1
            continue

        # ---- horizontal rule -> spacing only
        if re.fullmatch(r"-{3,}", stripped):
            doc.add_paragraph().paragraph_format.space_after = Pt(4)
            i += 1
            continue

        # ---- blockquote
        if stripped.startswith(">"):
            block = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                block.append(lines[i].strip().lstrip(">").strip())
                i += 1
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.3)
            p.paragraph_format.space_before = Pt(5)
            p.paragraph_format.space_after = Pt(7)
            write_inline(p, " ".join(x for x in block if x),
                         colour=MUTED, italic_all=True)
            continue

        # ---- lists
        bullet = re.match(r"^([-*])\s+(.*)$", stripped)
        number = re.match(r"^(\d+)\.\s+(.*)$", stripped)
        if bullet or number:
            style = "List Number" if number else "List Bullet"
            text = (number or bullet).group(2)
            p = doc.add_paragraph(style=style)
            p.paragraph_format.space_after = Pt(3)
            write_inline(p, text)
            i += 1
            continue

        # ---- blank
        if not stripped:
            i += 1
            continue

        # ---- paragraph (join soft-wrapped lines)
        block = []
        while i < len(lines):
            cur = lines[i].strip()
            if (not cur or cur.startswith(("#", "|", "```", ">"))
                    or re.fullmatch(r"-{3,}", cur)
                    or re.match(r"^([-*])\s+", cur)
                    or re.match(r"^\d+\.\s+", cur)):
                break
            block.append(cur)
            i += 1
        if block:
            p = doc.add_paragraph()
            write_inline(p, " ".join(block))

    if not figure_done:
        add_figure(doc)

    doc.save(OUT)
    size_kb = os.path.getsize(OUT) / 1024
    print(f"{OUT}  ({size_kb:.0f} KB)")


if __name__ == "__main__":
    build()
