"""Build a batch of ATS-friendly variant resumes for Niv Schendel.

SoT: this script + the variant config dicts at the bottom.
Outputs land in batches/<YYYY-MM-DD>_v<N>/ as immutable snapshots.

Style rules (do not violate):
- No em-dash, no en-dash anywhere. Use regular hyphen with surrounding spaces.
- Body and bullets are LEFT-aligned, never justified.
- Job title at Inspiria is "Solutions Engineer" (no "Senior").
"""

from __future__ import annotations

import os
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle,
)
from reportlab.lib.colors import HexColor, black
from reportlab.lib.enums import TA_LEFT, TA_RIGHT


ACCENT = HexColor("#1F3A5F")
GREY_DARK = HexColor("#2E2E2E")
GREY_MID = HexColor("#6A6A6A")
GREY_LINE = HexColor("#B5B5B5")

CONTACT_LINE = (
    '<a href="mailto:niv@schendel.me" color="#2E2E2E">niv@schendel.me</a>'
    '  &nbsp;•&nbsp;  +972-52-555-5579'
    '  &nbsp;•&nbsp;  <a href="https://linkedin.com/in/niv-schendel" '
    'color="#2E2E2E">linkedin.com/in/niv-schendel</a>'
    '  &nbsp;•&nbsp;  <a href="https://github.com/schendel2606" '
    'color="#2E2E2E">github.com/schendel2606</a>'
    '  &nbsp;•&nbsp;  <a href="https://schendel.me" color="#2E2E2E">schendel.me</a>'
)


def render(config: dict, output_path: str) -> None:
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=0.55 * inch, rightMargin=0.55 * inch,
        topMargin=0.38 * inch, bottomMargin=0.38 * inch,
        title=f"Niv Schendel - {config['variant']}",
        author="Niv Schendel",
    )

    s_name = ParagraphStyle("Name", fontName="Helvetica-Bold", fontSize=22,
                            leading=24, textColor=black, spaceAfter=2)
    s_title = ParagraphStyle("Title", fontName="Helvetica", fontSize=10.5,
                             leading=13, textColor=ACCENT, spaceAfter=3)
    s_contact = ParagraphStyle("Contact", fontName="Helvetica", fontSize=9,
                               leading=12, textColor=GREY_DARK, spaceAfter=4)
    s_section = ParagraphStyle("Section", fontName="Helvetica-Bold", fontSize=10.5,
                               leading=13, textColor=ACCENT,
                               spaceBefore=5, spaceAfter=2)
    s_job_title = ParagraphStyle("JobTitle", fontName="Helvetica-Bold",
                                 fontSize=10.5, leading=13, textColor=black)
    s_job_dates = ParagraphStyle("JobDates", fontName="Helvetica", fontSize=9.5,
                                 leading=13, textColor=GREY_MID, alignment=TA_RIGHT)
    s_body = ParagraphStyle("Body", fontName="Helvetica", fontSize=9.5,
                            leading=12.5, textColor=GREY_DARK,
                            spaceAfter=2, alignment=TA_LEFT)
    s_bullet = ParagraphStyle("Bullet", fontName="Helvetica", fontSize=9.5,
                              leading=12.5, textColor=GREY_DARK,
                              leftIndent=12, bulletIndent=0,
                              spaceBefore=1, spaceAfter=0, alignment=TA_LEFT)
    s_skill = ParagraphStyle("Skill", fontName="Helvetica", fontSize=9.5,
                             leading=12.5, textColor=GREY_DARK, spaceAfter=1)

    flow: list = []

    flow.append(Paragraph("NIV SCHENDEL, 25", s_name))
    flow.append(Paragraph(config["headline"], s_title))
    flow.append(Paragraph(CONTACT_LINE, s_contact))
    flow.append(HRFlowable(width="100%", thickness=0.6, color=GREY_LINE,
                           spaceBefore=2, spaceAfter=4))

    def section(title: str) -> None:
        flow.append(Paragraph(title.upper(), s_section))
        flow.append(HRFlowable(width="100%", thickness=0.4, color=GREY_LINE,
                               spaceBefore=0, spaceAfter=3))

    def job_row(title: str, date: str) -> None:
        t = Table(
            [[Paragraph(title, s_job_title), Paragraph(date, s_job_dates)]],
            colWidths=[None, 1.5 * inch],
        )
        t.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))
        flow.append(t)

    def bullet(text: str) -> None:
        flow.append(Paragraph(text, s_bullet, bulletText="•"))

    section("Summary")
    flow.append(Paragraph(config["summary"], s_body))

    section("Experience")
    job_row("Solutions Engineer &nbsp;-&nbsp; Inspiria LTD", "Mar 2024 - Present")
    for b in config["senior_bullets"]:
        bullet(b)

    flow.append(Spacer(1, 3))
    job_row("SAP Business One Implementer &nbsp;-&nbsp; Inspiria LTD",
            "Mar 2023 - Mar 2024")
    for b in config["implementer_bullets"]:
        bullet(b)

    flow.append(Spacer(1, 3))
    job_row(
        "Industrial Operations Engineer &nbsp;-&nbsp; IDF Ground Forces, Engineering Branch",
        "Jun 2020 - Mar 2023",
    )
    bullet(
        "Applied industrial engineering methods to operational planning and process "
        "improvement; built Excel models and authored queries against military "
        "operational systems for analysis and reporting."
    )

    section("Education")
    job_row(
        "B.Sc. in Computer Science &nbsp;-&nbsp; Holon Institute of Technology (HIT)",
        "Nov 2024 - 2027",
    )
    bullet(
        "Evening program while working full-time. Completed coursework: Data Structures, "
        "Object-Oriented Programming, Advanced Programming Workshop."
    )
    flow.append(Spacer(1, 3))
    job_row(
        "Industrial Engineering Technician Certificate &nbsp;-&nbsp; Revivim College",
        "Sep 2018 - Jun 2020",
    )

    section("Skills")
    for label, text in config["skills"]:
        flow.append(Paragraph(
            f'<font name="Helvetica-Bold" color="#000000">{label}</font>'
            f' &nbsp;&nbsp; {text}',
            s_skill,
        ))

    doc.build(flow)


# --------------------------------------------------------------------------
# Variant: BACKEND
# --------------------------------------------------------------------------
BACKEND = {
    "variant": "Backend",
    "headline": "Backend Engineer  &nbsp;|&nbsp;  C# .NET 8  •  SQL Server  •  AI Agents &amp; Automation",
    "summary": (
        "Backend Engineer with 3 years building production C# / .NET APIs, "
        "configuration-driven engines, and SQL Server data layers across dozens of "
        "enterprise customers. Recently shipped a custom AI agent and Skill toolkit "
        "that runs inside sandboxed environments and auto-generates code for a closed "
        "legacy system, automating significant portions of recurring engineering work "
        "that previously required manual scripting. Combine layered .NET architecture "
        "with deep T-SQL, performance-tuning, and SAP DI API / Service Layer integration "
        "expertise; reduced new-customer deployment time from ~1 day to under 1 hour by "
        "abstracting core logic into reusable, multi-tenant components. Completing a "
        "B.Sc. in Computer Science at HIT (evening) while working full-time."
    ),
    "senior_bullets": [
        "<b>Built a custom AI agent and Skill toolkit that runs inside sandboxed "
        "environments and auto-generates code for a closed legacy system "
        "(B1UP / Boyum IT)</b>. Enforces data isolation while automating significant "
        "portions of recurring engineering work that previously required manual "
        "scripting. Materially compresses delivery cycles.",

        "<b>Architected configuration-driven backend engines for multi-tenant rollouts</b> "
        "using declarative parameter tables and dynamic T-SQL generation. "
        "<b>Reduced new-customer deployment from ~1 day to under 1 hour</b>. "
        "Engines power vendor-risk scoring (VendorScoringEngine), advanced inventory "
        "models, and complex financial modules (Budgeting, Aging, VAT Allocation).",

        "<b>Shipped production REST APIs</b> in C# / .NET 8 / ASP.NET Core with input "
        "validation, structured logging (NLog), and error handling. Integrated with "
        "external systems via <b>SAP DI API and Service Layer</b>. Authored Postman "
        "regression suites covering JSON / XML payloads across critical flows.",

        "<b>Designed analytical SQL Server data models</b> (fact tables, KPI logic, "
        "stored procedures, SQL views) feeding Power BI dashboards consumed by "
        "finance and operations teams in place of ad-hoc reporting workflows.",

        "<b>Resolved high-volume database bottlenecks</b> by analyzing execution plans "
        "and applying targeted indexing strategies. Cut report runtimes in production "
        "and unblocked client month-end closes.",

        "<b>Drove iterative product delivery with enterprise customers across 6+ "
        "on-site engagements</b>. Translated requirements into technical specs, ran "
        "releases through UAT to production, and maintained engineering quality via "
        "layered (Service / Repository) architecture, OOP / SOLID, and peer code reviews.",
    ],
    "implementer_bullets": [
        "<b>Authored T-SQL fixes, stored procedures, and SQL views across dozens of "
        "enterprise customer deployments</b>. Root-caused in production data, integrated "
        "via <b>SAP DI API and Service Layer</b>, ran UAT, and shipped to production.",

        "<b>Delivered scoped technical projects</b>: wrote engineering specifications, "
        "coordinated with developers, integrated via DI API / Service Layer, and "
        "documented releases for handover.",
    ],
    "skills": [
        ("Languages &amp; Frameworks",
         "C# (.NET 8), ASP.NET Core Web API, T-SQL, SQL, C / C++ (foundations)"),
        ("API &amp; Backend",
         "REST APIs, JSON / XML, Layered Architecture (Service / Repository), "
         "OOP &amp; SOLID, Configuration-Driven / Declarative Engines, Dynamic Query "
         "Generation, Production Hardening &amp; Observability"),
        ("AI &amp; Automation",
         "AI Agent Development, Skill / Tool-Use Pipelines, Sandboxed Execution, "
         "Automated Code Generation"),
        ("Data &amp; Databases",
         "Microsoft SQL Server (MSSQL), Stored Procedures, SQL Views, Relational Data "
         "Modeling, Analytical Data Models (Fact tables, KPI logic), Performance Tuning "
         "(Execution Plans, Indexing), ETL-style Data Loads"),
        ("Integration &amp; ERP Context",
         "SAP DI API, SAP Service Layer, SAP Business One, B1UP (Boyum IT), Power BI"),
        ("Tools &amp; Practices",
         "Git, Postman, NLog, Code Reviews"),
    ],
}


# --------------------------------------------------------------------------
# Variant: DATA / SQL / BI / ETL
# --------------------------------------------------------------------------
DATA = {
    "variant": "Data",
    "headline": "Data &amp; SQL Engineer  &nbsp;|&nbsp;  T-SQL  •  SQL Server  •  Analytical Data Models  •  ETL  •  Power BI",
    "summary": (
        "Data-focused Engineer with 3 years building production SQL Server data layers, "
        "stored procedures, fact tables, and KPI views feeding BI dashboards across dozens "
        "of enterprise customers. Combine deep T-SQL and performance-tuning expertise with "
        "C# (.NET 8) backend skills to ship reusable, multi-tenant data engines and "
        "ETL-style loads, reducing new-customer deployment time from ~1 day to under 1 hour. "
        "Recently extended throughput by building a sandboxed AI agent and Skill toolkit "
        "that auto-generates SQL artifacts and functions inside a closed legacy system. "
        "Completing a B.Sc. in Computer Science at HIT (evening) while working full-time."
    ),
    "senior_bullets": [
        "<b>Designed analytical SQL Server data models</b> (fact tables, KPI logic, "
        "stored procedures, SQL views) feeding Power BI dashboards consumed by "
        "finance and operations teams across <b>dozens of enterprise customers</b>.",

        "<b>Resolved high-volume database bottlenecks</b> by analyzing execution plans "
        "and applying targeted indexing strategies. Cut report runtimes in production "
        "and unblocked client month-end closes.",

        "<b>Architected configuration-driven data engines for multi-tenant rollouts</b> "
        "using declarative parameter tables and dynamic T-SQL generation. "
        "<b>Reduced new-customer deployment from ~1 day to under 1 hour</b>. Engines "
        "power vendor-risk scoring, inventory analytics, and complex financial modules "
        "(Budgeting, Aging, VAT Allocation).",

        "<b>Built ETL-style data loads</b> from transactional ERP tables into curated "
        "analytical layers, sourcing data via <b>SAP DI API / Service Layer</b> and "
        "T-SQL. Surfaced clean, reusable datasets for downstream BI consumption.",

        "<b>Built a custom AI agent and Skill toolkit that auto-generates SQL artifacts "
        "and functions for a closed legacy system</b> (B1UP / Boyum IT), executing "
        "within sandboxed environments. Automates significant portions of recurring "
        "data-engineering work that previously required manual scripting.",

        "<b>Shipped production REST APIs</b> in C# / .NET 8 / ASP.NET Core to expose "
        "curated data layers, with structured logging (NLog) and Postman regression "
        "suites. Drove delivery across <b>6+ on-site customer engagements</b>.",
    ],
    "implementer_bullets": [
        "<b>Authored T-SQL fixes, stored procedures, and SQL views across dozens of "
        "enterprise customer deployments</b>. Root-cause analysis in production data, "
        "integrated via <b>SAP DI API and Service Layer</b>, UAT, and rollout.",

        "<b>Delivered scoped data and integration projects</b>: wrote technical "
        "specifications, coordinated with developers, and documented releases.",
    ],
    "skills": [
        ("Data &amp; Databases",
         "Microsoft SQL Server (MSSQL), T-SQL, Stored Procedures, SQL Views, Relational "
         "Data Modeling, Analytical Data Models (Fact tables, KPI logic), Performance "
         "Tuning (Execution Plans, Indexing), ETL-style Data Loads"),
        ("BI &amp; Reporting",
         "Power BI, KPI Logic, Dashboard-feeding SQL Layers"),
        ("Languages &amp; Frameworks",
         "T-SQL, SQL, C# (.NET 8), ASP.NET Core, C / C++ (foundations)"),
        ("API &amp; Backend",
         "REST APIs, JSON / XML, Layered Architecture (Service / Repository), "
         "Configuration-Driven / Declarative Engines, Dynamic Query Generation"),
        ("AI &amp; Automation",
         "AI Agent Development, Sandboxed Execution, Automated SQL / Code Generation"),
        ("Integration &amp; ERP Context",
         "SAP DI API, SAP Service Layer, SAP Business One, B1UP (Boyum IT)"),
        ("Tools &amp; Practices",
         "Git, Postman, NLog, Code Reviews"),
    ],
}


# --------------------------------------------------------------------------
# Variant: SOLUTIONS / FORWARD-DEPLOYED ENGINEER
# --------------------------------------------------------------------------
SOLUTIONS = {
    "variant": "Solutions",
    "headline": "Solutions Engineer  &nbsp;|&nbsp;  C# .NET  •  SQL Server  •  AI Automation  •  Enterprise Delivery",
    "summary": (
        "Solutions Engineer with 3 years partnering with enterprise customers across "
        "dozens of accounts and 6+ on-site engagements, translating business "
        "requirements into production .NET APIs, SQL Server data models, and reusable "
        "backend engines. Cut new-customer deployment from ~1 day to under 1 hour by "
        "abstracting core logic into multi-tenant components. Recently shipped a "
        "sandboxed AI agent and Skill toolkit that auto-generates code for a closed "
        "legacy system, automating significant portions of recurring engineering work. "
        "Combine hands-on engineering depth (C# / .NET 8 / T-SQL / SAP DI API &amp; Service "
        "Layer) with discovery, delivery, and stakeholder communication. Completing a "
        "B.Sc. in Computer Science at HIT (evening) while working full-time."
    ),
    "senior_bullets": [
        "<b>Partnered with enterprise customers across 6+ on-site engagements and dozens "
        "of accounts</b>: led discovery sessions, translated business requirements into "
        "engineering specs, and shipped iterative releases through UAT to production.",

        "<b>Architected configuration-driven backend engines for multi-tenant rollouts</b> "
        "using declarative parameter tables and dynamic T-SQL generation. "
        "<b>Reduced new-customer deployment from ~1 day to under 1 hour</b>. Engines "
        "power vendor-risk scoring, inventory models, and financial modules (Budgeting, "
        "Aging, VAT Allocation).",

        "<b>Built a custom AI agent and Skill toolkit</b> that runs inside sandboxed "
        "environments and auto-generates code for a closed legacy system "
        "(B1UP / Boyum IT). Automates significant portions of recurring "
        "solution-engineering work.",

        "<b>Shipped production REST APIs</b> (C# / .NET 8 / ASP.NET Core) with input "
        "validation, structured logging (NLog), error handling, and Postman regression "
        "suites. Integrated via <b>SAP DI API and Service Layer</b> where ERP "
        "integration was required.",

        "<b>Designed analytical SQL Server data models</b> (fact tables, KPI logic, "
        "stored procedures, SQL views) feeding Power BI dashboards consumed by "
        "finance and operations teams.",

        "<b>Resolved high-volume database bottlenecks</b> in production environments "
        "by analyzing execution plans and applying targeted indexing strategies. "
        "Unblocked client month-end closes and shortened iteration cycles.",
    ],
    "implementer_bullets": [
        "<b>Owned production incidents and change requests across dozens of enterprise "
        "customer deployments</b>. Root-caused in T-SQL, wrote fixes (stored "
        "procedures, SQL views), integrated via <b>SAP DI API and Service Layer</b>, "
        "ran UAT, and shipped to production.",

        "<b>Delivered scoped technical projects</b>: wrote engineering specifications, "
        "coordinated with developers, and documented releases.",
    ],
    "skills": [
        ("API &amp; Backend",
         "C# (.NET 8), ASP.NET Core Web API, REST APIs, JSON / XML, Layered Architecture "
         "(Service / Repository), OOP &amp; SOLID, Configuration-Driven / Declarative Engines"),
        ("Customer Engineering",
         "Discovery &amp; Requirements Translation, Multi-Tenant Rollout, On-Site "
         "Delivery, UAT &amp; Production Handover, Stakeholder Communication"),
        ("AI &amp; Automation",
         "AI Agent Development, Skill / Tool-Use Pipelines, Sandboxed Execution, "
         "Automated Code Generation"),
        ("Data &amp; Databases",
         "Microsoft SQL Server, T-SQL, Stored Procedures, SQL Views, Performance Tuning "
         "(Execution Plans, Indexing), ETL-style Data Loads"),
        ("Integration &amp; ERP Context",
         "SAP DI API, SAP Service Layer, SAP Business One, B1UP (Boyum IT), Power BI"),
        ("Tools &amp; Practices",
         "Git, Postman, NLog, Code Reviews"),
    ],
}


VARIANTS = [BACKEND, DATA, SOLUTIONS]

# Update each session.
BATCH_DIR = str(Path(__file__).parent / "batches" / "2026-05-05")


def main() -> None:
    os.makedirs(BATCH_DIR, exist_ok=True)
    for cfg in VARIANTS:
        out = f"{BATCH_DIR}/Niv Schendel Resume - {cfg['variant']}.pdf"
        render(cfg, out)
        print("Built:", out)


if __name__ == "__main__":
    main()
