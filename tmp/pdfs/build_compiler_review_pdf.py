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

    # Page 2: project need and boundaries.
    add_section(
        story, styles, "1. Abstract",
        "This project is a simple educational tool that shows how LLVM optimization passes change a C program. It runs Clang, collects LLVM IR snapshots, removes repeated unchanged output, and produces a short transformation report. This helps students understand the compiler optimization pipeline step by step.",
    )
    add_section(
        story, styles, "2. Problem Statement",
        "LLVM can print the result of its optimization passes, but the raw output is long and difficult to follow. Students need a small tool that organizes this output and clearly shows which pass changed the program.",
    )
    add_section(
        story, styles, "3. Motivation",
        "Compiler optimization is often taught using only the original program and the final output. The analyzer exposes the intermediate stages, making the process easier to learn, explain, and demonstrate.",
    )
    story.append(Paragraph("4. Objectives", styles["Heading"]))
    add_bullets(story, styles, [
        "Accept one small C source file.",
        "Run Clang with LLVM pass output enabled.",
        "Extract the pass name, scope, order, and LLVM IR.",
        "Remove consecutive unchanged snapshots.",
        "Generate a manifest, timeline, and numbered IR files.",
        "Show clear error messages when input or compilation fails.",
    ])
    story.append(Spacer(1, 2 * mm))
    add_section(
        story, styles, "5. Scope",
        "The first version supports small C programs and a local Clang compiler. It creates reports offline. It does not execute the input program, modify LLVM passes, use AI, require a GPU, or use a web server or database.",
    )
    story.append(PageBreak())

    # Page 3: compiler concepts and approach.
    add_section(
        story, styles, "6. Background Study",
        "Clang converts C source code into LLVM Intermediate Representation, or LLVM IR. LLVM then runs a sequence of optimization passes. A pass may simplify instructions, remove dead code, improve loops, or clean control flow. LLVM can print IR after each pass, but this output must be organized before it is easy to study.",
    )
    story.append(Paragraph("7. Compiler Design Concepts Involved", styles["Heading"]))
    add_bullets(story, styles, [
        "Intermediate Representation: LLVM IR is the program form between source code and machine code.",
        "Optimization Pass: a compiler stage that analyzes or transforms the program.",
        "Pass Pipeline: the ordered sequence of compiler passes.",
        "Function and Module Scope: snapshots are compared only within the same scope.",
        "Dead Code Elimination and Simplification: common changes visible in the saved IR.",
    ])
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("8. Proposed Methodology", styles["Heading"]))
    add_bullets(story, styles, [
        "Check that the input is an existing C file and locate Clang.",
        "Run Clang safely as a subprocess at optimization level O1.",
        "Parse each IR dump into a structured snapshot.",
        "Compare snapshots and retain only meaningful changes.",
        "Write the transformation timeline and LLVM IR files.",
        "Test the parser, compiler boundary, report output, and command line.",
    ])
    story.append(PageBreak())

    # Page 4: design, stack, feasibility, and current prototype.
    story.append(Paragraph("9. System Architecture", styles["Heading"]))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "C Source  -&gt;  Clang  -&gt;  IR Parser  -&gt;  Change Filter  -&gt;  Report",
        styles["Flow"],
    ))
    story.append(Paragraph(
        "The complete system is one local Python pipeline. It does not need a database, login, backend service, or internet connection.",
        styles["Body"],
    ))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("10. Technology Stack", styles["Heading"]))
    add_bullets(story, styles, [
        "Python 3.10 or newer for the analyzer.",
        "Clang and LLVM for the real compiler pipeline.",
        "Command-line interface for simple use.",
        "JSON, Markdown, and .ll files for the report.",
        "Python unittest for automated testing.",
    ])
    story.append(Spacer(1, 2 * mm))

    add_section(
        story, styles, "11. Innovation and Feasibility",
        "The analyzer converts a large expert-oriented compiler dump into a small timeline containing only meaningful changes. The project is practical because it uses Python and Clang, needs no dataset or special hardware, and handles a clearly limited input scope.",
    )
    story.append(Paragraph("12. Initial Prototype", styles["Heading"]))
    add_bullets(story, styles, [
        "LLVM snapshot model and pass-dump parser completed.",
        "Unchanged-snapshot filtering completed.",
        "Safe Clang discovery and execution boundary completed.",
        "Twenty-one automated tests currently pass.",
        "Next step: connect the command line and final report writer.",
    ])

    document.build(story)
    print(OUTPUT.resolve())


if __name__ == "__main__":
    build()
