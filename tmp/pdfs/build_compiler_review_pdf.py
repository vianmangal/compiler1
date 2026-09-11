from pathlib import Path

from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer


OUTPUT = Path("output/pdf/LLVM_Pass_Transformation_Analyzer_Proposal.pdf")


def add_section(story, styles, title, text):
    story.append(Paragraph(title, styles["Heading"]))
    story.append(Paragraph(text, styles["Body"]))
    story.append(Spacer(1, 3 * mm))


def add_bullets(story, styles, items):
    for item in items:
        story.append(Paragraph(f"<bullet>&bull;</bullet>{item}", styles["Bullet"]))


def build():
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(
        str(OUTPUT),
        pagesize=A4,
        leftMargin=23 * mm,
        rightMargin=23 * mm,
        topMargin=22 * mm,
        bottomMargin=22 * mm,
        title="LLVM Pass Transformation Analyzer",
        author="Vian Mangal",
        subject="Compiler Design Lab",
    )

    base = getSampleStyleSheet()
    styles = {
        "CoverLabel": ParagraphStyle(
            "CoverLabel", parent=base["Normal"], fontName="Helvetica-Bold",
            fontSize=12, leading=16, alignment=TA_CENTER, textColor="black",
            spaceAfter=2 * mm,
        ),
        "CoverTopic": ParagraphStyle(
            "CoverTopic", parent=base["Title"], fontName="Helvetica-Bold",
            fontSize=23, leading=29, alignment=TA_CENTER, textColor="black",
            spaceAfter=24 * mm,
        ),
        "CoverInfo": ParagraphStyle(
            "CoverInfo", parent=base["Normal"], fontName="Helvetica",
            fontSize=14, leading=22, alignment=TA_CENTER, textColor="black",
            spaceAfter=5 * mm,
        ),
        "Heading": ParagraphStyle(
            "Heading", parent=base["Heading2"], fontName="Helvetica-Bold",
            fontSize=14, leading=18, textColor="black", spaceBefore=1 * mm,
            spaceAfter=2 * mm,
        ),
        "Body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10.5, leading=15, textColor="black", spaceAfter=1 * mm,
        ),
        "Bullet": ParagraphStyle(
            "Bullet", parent=base["BodyText"], fontName="Helvetica",
            fontSize=10.3, leading=14.5, leftIndent=6 * mm,
            firstLineIndent=-4 * mm, bulletIndent=0, textColor="black",
            spaceAfter=1.4 * mm,
        ),
        "Flow": ParagraphStyle(
            "Flow", parent=base["Normal"], fontName="Courier-Bold",
            fontSize=10.5, leading=16, alignment=TA_CENTER, textColor="black",
            borderColor="black", borderWidth=0.7, borderPadding=4 * mm,
            spaceAfter=4 * mm,
        ),
    }

    story = []

    # Page 1: minimal cover.
    story.append(Spacer(1, 42 * mm))
    story.append(Paragraph("TOPIC", styles["CoverLabel"]))
    story.append(Paragraph("LLVM Pass Transformation Analyzer", styles["CoverTopic"]))
    story.append(Paragraph("Name: Vian Mangal", styles["CoverInfo"]))
    story.append(Paragraph("Register Number: 24BAI0134", styles["CoverInfo"]))
    story.append(Paragraph("Subject: Compiler Design Lab", styles["CoverInfo"]))
    story.append(PageBreak())

    # Page 2: introduction and project definition.
    add_section(
        story, styles, "Abstract",
        "This project is a simple educational tool that shows how LLVM optimization passes change a C program. It collects LLVM IR snapshots, removes repeated output, and produces a short transformation report for students.",
    )
    add_section(
        story, styles, "1. Introduction",
        "Modern compilers perform many internal optimization steps before producing machine code. These steps are difficult to observe in normal compilation. <b>Motivation:</b> making the intermediate stages visible helps students learn and explain optimization. <b>Scope:</b> the first version supports small C files and a local Clang compiler. It does not execute input programs, modify LLVM, use AI, require a GPU, or need a server or database.",
    )
    add_section(
        story, styles, "2. Problem Statement",
        "LLVM can print the result of individual optimization passes, but the raw output is long and difficult to follow. A compact analyzer is needed to organize the output and show only the passes that meaningfully changed the program.",
    )
    story.append(Paragraph("3. Objectives", styles["Heading"]))
    add_bullets(story, styles, [
        "Accept one small C source file and run Clang safely.",
        "Extract the pass name, scope, order, and LLVM IR.",
        "Remove consecutive unchanged snapshots.",
        "Generate a readable timeline, manifest, and numbered IR files.",
        "Provide clear errors for invalid input or compilation failure.",
    ])
    story.append(Spacer(1, 2 * mm))
    add_section(
        story, styles, "4. Background Study",
        "Clang converts C source into LLVM Intermediate Representation. LLVM then runs an ordered pass pipeline. Passes may simplify instructions, remove dead code, improve loops, or clean control flow. LLVM can print IR after each pass, but the dump must be parsed and organized before it is useful for learning.",
    )
    story.append(PageBreak())

    # Page 3: system, method, concepts, and implementation.
    story.append(Paragraph("5. System Design", styles["Heading"]))
    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "C Source  -&gt;  Clang  -&gt;  IR Parser  -&gt;  Change Filter  -&gt;  Report",
        styles["Flow"],
    ))
    add_bullets(story, styles, [
        "Clang Runner: validates input and captures LLVM pass output.",
        "IR Parser: converts dump blocks into structured snapshots.",
        "Change Filter: removes consecutive unchanged snapshots per scope.",
        "Report Writer: produces JSON, Markdown, and .ll files.",
    ])
    story.append(Paragraph(
        "<b>Data flow and workflow:</b> the C path enters the runner, raw pass output moves to the parser, filtered snapshots move to the report writer, and the user opens the generated timeline.",
        styles["Body"],
    ))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("6. Methodology", styles["Heading"]))
    add_bullets(story, styles, [
        "Check the source file and locate Clang.",
        "Run Clang at optimization level O1 without using a shell.",
        "Parse each IR dump and compare snapshots within the same scope.",
        "Retain meaningful changes and write the final report.",
        "Verify each module using automated tests and a real Clang smoke test.",
    ])
    story.append(Spacer(1, 2 * mm))

    story.append(Paragraph("7. Compiler Design Concepts Used", styles["Heading"]))
    add_bullets(story, styles, [
        "Intermediate code: LLVM IR represents the program between source and machine code.",
        "Optimization passes: ordered stages analyze or transform the IR.",
        "Parsing: pass banners and IR blocks are converted into structured data.",
        "Function and module scope: unrelated snapshots are not compared.",
        "Dead-code elimination and simplification: common transformations visible in reports.",
    ])
    story.append(Spacer(1, 2 * mm))

    add_section(
        story, styles, "8. Implementation",
        "Major modules cover the data model, parser, change filter, compiler runner, command-line interface, and report writer. The algorithm parses ordered snapshots, compares them by scope, and retains only meaningful changes.",
    )
    add_section(
        story, styles, "Technology Stack",
        "Python 3.10 or newer and its standard library are used for the analyzer and tests. Clang and LLVM provide the compiler pipeline. The interface is command-line based, and output is stored as JSON, Markdown, and LLVM .ll files.",
    )
    story.append(PageBreak())

    # Page 4: validation, outcome, next work, and supporting material.
    story.append(Paragraph("9. Testing and Results", styles["Heading"]))
    add_bullets(story, styles, [
        "Parser tests check valid, repeated, and malformed pass dumps.",
        "Compiler tests check discovery, safe command creation, and failure messages.",
        "Expected result: ordered snapshots with unchanged entries removed.",
        "Current result: snapshot parsing, filtering, and the Clang boundary are complete; 21 automated tests pass.",
        "Pending result: command-line and final report integration will complete the initial version.",
    ])
    story.append(Spacer(1, 2 * mm))

    add_section(
        story, styles, "10. Conclusion",
        "The proposed analyzer makes a real LLVM optimization pipeline easier to understand. Its narrow C input scope and local design keep it technically useful, safe, and achievable for a student project.",
    )

    story.append(Paragraph("11. Future Enhancements", styles["Heading"]))
    add_bullets(story, styles, [
        "Show line-by-line differences between adjacent IR snapshots.",
        "Add simple descriptions for common optimization passes.",
        "Provide filters by function or pass name.",
        "Add a small local visual timeline after the command-line version is complete.",
    ])
    story.append(Spacer(1, 2 * mm))

    story.append(Paragraph("12. References", styles["Heading"]))
    add_bullets(story, styles, [
        "LLVM Project, LLVM Language Reference Manual.",
        "LLVM Project, Using the New Pass Manager.",
        "Clang Project, Clang Compiler User's Manual.",
        "Keith Cooper and Linda Torczon, Engineering a Compiler.",
    ])
    story.append(Spacer(1, 2 * mm))

    add_section(
        story, styles, "13. Appendix",
        "Prototype command: python -m analyzer analyze examples/loop.c. Expected output files are manifest.json, timeline.md, and numbered LLVM IR snapshots inside a report directory.",
    )

    document.build(story)
    print(OUTPUT.resolve())


if __name__ == "__main__":
    build()
