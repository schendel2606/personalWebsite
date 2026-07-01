"""Build a batch of ATS-friendly variant resumes for Niv Schendel.

SoT: this script + the variant config dicts at the bottom.
Outputs land in batches/<YYYY-MM-DD>/{detailed,concise}/ as immutable snapshots.
Each variant is rendered at two lengths: detailed (2-page) and concise (1-page).

Style rules (do not violate):
- No em-dash, no en-dash anywhere. Use regular hyphen with surrounding spaces.
- Body and bullets are LEFT-aligned, never justified.
- Job title at Inspiria is "Solutions Engineer" (no "Senior").
"""

from __future__ import annotations

import os
import shutil
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


IDF_BULLETS_DETAILED = [
    "Applied industrial engineering methods to operational planning and process "
    "improvement within the Engineering Branch.",
    "Built Excel models and authored queries against military operational systems "
    "for analysis and reporting.",
]

IDF_BULLETS_CONCISE = [
    "Applied industrial engineering methods to operational planning and process "
    "improvement; built Excel models and authored queries against military "
    "operational systems for analysis and reporting.",
]

# Personal projects. Detailed length only.
PROJECTS = [
    ("FPL Revenue", "fpl.schendel.me",
     "<b>Designed and built a full-stack Fantasy Premier League analytics "
     "platform</b> that syncs teams, leagues, and gameweek history and applies "
     "configurable financial rules (entry fees, payouts) to compute league "
     "standings and earnings. ASP.NET Core 10, EF Core, SQL Server, "
     "React 19 / TypeScript; layered architecture, automated tests, GitHub "
     "Actions CI/CD."),
    ("TaskManager", "tasks.schendel.me",
     "<b>Designed and built a production work-management platform with "
     "lightweight CRM</b>, engineered for dual operation by people and AI agents "
     "under server-side guardrails. ASP.NET Core 10, EF Core, SQL Server, "
     "React 19 / TypeScript; layered architecture, multi-tenancy, GitHub Actions "
     "CI/CD."),
]

# Detailed-length-only bullets, shared across all variants.
REVERSE_ENGINEERING_BULLET = (
    "<b>Diagnosed and resolved production defects in SAP Business One and Boyum "
    "systems under time pressure</b>, reverse-engineering undocumented dashboard "
    "logic through network-traffic analysis and SQL debugging."
)

ONBOARDING_BULLET = (
    "<b>Onboarded new enterprise customers onto SAP Business One</b>: modeled and "
    "configured data structures, workflows, and reporting to each customer's "
    "processes, and debugged integration defects between SAP and third-party "
    "systems."
)


def render(config: dict, length: str, output_path: str) -> None:
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        leftMargin=0.55 * inch, rightMargin=0.55 * inch,
        topMargin=0.38 * inch, bottomMargin=0.38 * inch,
        title=f"Niv Schendel - {config['variant']}",
        author="Niv Schendel",
    )

    # Density is length-aware: detailed runs roomy across 2 pages; concise runs
    # tighter so the full section set still holds a single page.
    if length == "detailed":
        lead, sec_before, blt_before, blt_after, skl_after, job_gap = (
            14, 12, 4, 3, 4, 8)
    else:  # concise
        lead, sec_before, blt_before, blt_after, skl_after, job_gap = (
            12, 5, 2, 0.5, 1.5, 3)

    s_name = ParagraphStyle("Name", fontName="Helvetica-Bold", fontSize=22,
                            leading=24, textColor=black, spaceAfter=2)
    s_title = ParagraphStyle("Title", fontName="Helvetica", fontSize=10.5,
                             leading=13, textColor=ACCENT, spaceAfter=3)
    s_contact = ParagraphStyle("Contact", fontName="Helvetica", fontSize=9,
                               leading=12, textColor=GREY_DARK, spaceAfter=4)
    s_section = ParagraphStyle("Section", fontName="Helvetica-Bold", fontSize=10.5,
                               leading=13, textColor=ACCENT,
                               spaceBefore=sec_before, spaceAfter=3)
    s_job_title = ParagraphStyle("JobTitle", fontName="Helvetica-Bold",
                                 fontSize=10.5, leading=13, textColor=black)
    s_job_dates = ParagraphStyle("JobDates", fontName="Helvetica", fontSize=9.5,
                                 leading=13, textColor=GREY_MID, alignment=TA_RIGHT)
    s_body = ParagraphStyle("Body", fontName="Helvetica", fontSize=9.5,
                            leading=lead, textColor=GREY_DARK,
                            spaceAfter=2, alignment=TA_LEFT)
    s_bullet = ParagraphStyle("Bullet", fontName="Helvetica", fontSize=9.5,
                              leading=lead, textColor=GREY_DARK,
                              leftIndent=12, bulletIndent=0,
                              spaceBefore=blt_before, spaceAfter=blt_after,
                              alignment=TA_LEFT)
    s_skill = ParagraphStyle("Skill", fontName="Helvetica", fontSize=9.5,
                             leading=lead, textColor=GREY_DARK, spaceAfter=skl_after)

    flow: list = []

    flow.append(Paragraph("NIV SCHENDEL", s_name))
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

    # 1. SUMMARY
    section("Summary")
    flow.append(Paragraph(config[f"summary_{length}"], s_body))

    # 2. SKILLS
    section("Skills")
    for label, text in config["skills"]:
        flow.append(Paragraph(
            f'<font name="Helvetica-Bold" color="#000000">{label}</font>'
            f' &nbsp;&nbsp; {text}',
            s_skill,
        ))

    # 3. EXPERIENCE
    section("Experience")
    job_row("Solutions Engineer &nbsp;-&nbsp; Inspiria LTD", "Mar 2024 - Present")
    for b in config[f"senior_bullets_{length}"]:
        bullet(b)
    if length == "detailed":
        bullet(REVERSE_ENGINEERING_BULLET)

    flow.append(Spacer(1, job_gap))
    job_row("SAP Business One Implementer &nbsp;-&nbsp; Inspiria LTD",
            "Mar 2023 - Mar 2024")
    for b in config[f"implementer_bullets_{length}"]:
        bullet(b)
    if length == "detailed":
        bullet(ONBOARDING_BULLET)

    # 4. PROJECTS (detailed length only)
    if length == "detailed":
        section("Projects")
        for i, (proj_name, proj_url, proj_desc) in enumerate(PROJECTS):
            if i:
                flow.append(Spacer(1, job_gap))
            job_row(
                proj_name,
                f'<a href="https://{proj_url}" color="#2E2E2E">{proj_url}</a>',
            )
            bullet(proj_desc)

    # 5. EDUCATION  (placed after Experience and Projects: experience is the ticket,
    # not student status; no "student / evening / while working" phrasing)
    section("Education")
    job_row(
        "B.Sc. in Computer Science &nbsp;-&nbsp; Holon Institute of Technology (HIT)",
        "2024 - 2027",
    )
    if length == "detailed":
        bullet(
            "Core CS coursework: Data Structures and Algorithms, Object-Oriented "
            "Programming, and Advanced Programming Workshop (C / C++)."
        )
    flow.append(Spacer(1, job_gap))
    job_row(
        "Industrial Engineering Technician Certificate &nbsp;-&nbsp; Revivim College",
        "Sep 2018 - Jun 2020",
    )

    # 6. MILITARY SERVICE
    section("Military Service")
    job_row(
        "Industrial Operations Engineer &nbsp;-&nbsp; IDF Ground Forces, Engineering Branch",
        "Jun 2020 - Mar 2023",
    )
    idf_bullets = IDF_BULLETS_DETAILED if length == "detailed" else IDF_BULLETS_CONCISE
    for b in idf_bullets:
        bullet(b)

    # 7. LANGUAGES
    section("Languages")
    flow.append(Paragraph(
        '<font name="Helvetica-Bold" color="#000000">Hebrew</font>'
        ' &nbsp; Native &nbsp;&nbsp;&nbsp;&nbsp; '
        '<font name="Helvetica-Bold" color="#000000">English</font>'
        ' &nbsp; Professional',
        s_skill,
    ))

    doc.build(flow)


# --------------------------------------------------------------------------
# Variant: BACKEND
# --------------------------------------------------------------------------
BACKEND = {
    "variant": "Backend",
    "headline": "Backend Engineer  &nbsp;|&nbsp;  C# / .NET  •  SQL Server  •  AI-Native Delivery (Custom Agents, Skills, MCP)",
    "summary_detailed": (
        "Backend engineer with 3 years shipping production C# / .NET APIs, "
        "configuration-driven engines, and SQL Server data layers across dozens of "
        "enterprise customers. Works AI-native: builds custom agents, skills, plugins, "
        "and MCP tools to automate recurring engineering work, and has shipped a "
        "platform engineered for dual human and AI-agent operation under server-side "
        "guardrails - while keeping architecture, code review, and security ownership "
        "hands-on. In a small, project-driven organization, owns solutions end to end "
        "across a broad technical surface - backend, T-SQL and DBA work, "
        "on-premise-to-cloud integration, and internal IT - coordinating across teams "
        "in a matrixed structure and ramping fast on unfamiliar systems and languages. "
        "Reduced new-customer deployment from ~1 day to under 1 hour by abstracting "
        "core logic into reusable, multi-tenant components; combines layered .NET "
        "architecture with deep T-SQL, performance tuning, and SAP DI API / Service "
        "Layer integration."
    ),
    "summary_concise": (
        "Backend engineer with 3 years shipping production C# / .NET APIs, "
        "configuration-driven engines, and SQL Server data layers across dozens of "
        "enterprise customers. Works AI-native: builds custom agents, skills, and MCP "
        "tools to automate recurring engineering work, as a reviewed, "
        "security-conscious accelerator. In a small, project-driven organization, owns "
        "solutions end to end across a broad technical surface - backend, T-SQL / DBA, "
        "on-premise-to-cloud integration, and IT - ramping fast on unfamiliar systems "
        "and languages. Cut new-customer deployment from ~1 day to under 1 hour via "
        "reusable, multi-tenant components."
    ),
    "senior_bullets_detailed": [
        "<b>Built custom AI agents, skills, plugins, and MCP tools that run inside "
        "sandboxed environments and auto-generate code for a closed legacy system "
        "(B1UP / Boyum IT)</b>. Enforces data isolation while automating recurring "
        "engineering work that previously required manual scripting, materially "
        "compressing delivery cycles.",

        "<b>Architected configuration-driven backend engines for multi-tenant rollouts</b> "
        "using declarative parameter tables and dynamic T-SQL generation. "
        "<b>Reduced new-customer deployment from ~1 day to under 1 hour</b>. "
        "Engines power vendor-risk scoring (VendorScoringEngine), advanced inventory "
        "models, and complex financial modules (Budgeting, Aging, VAT Allocation).",

        "<b>Owned solutions end to end across a broad technical surface</b> in a small, "
        "project-driven organization - backend, T-SQL and DBA work, "
        "on-premise-to-cloud integration, and internal IT - delivering across 6+ "
        "on-site enterprise engagements. Coordinated in a matrixed structure and ramped "
        "quickly on unfamiliar systems, languages, and tools.",

        "<b>Shipped production REST APIs</b> in C# / .NET / ASP.NET Core with input "
        "validation, structured logging (NLog), and error handling. Integrated with "
        "external systems via <b>SAP DI API and Service Layer</b>. Authored Postman "
        "regression suites covering JSON / XML payloads across critical flows.",

        "<b>Designed analytical SQL Server data models</b> (fact tables, KPI logic, "
        "stored procedures, SQL views) feeding Power BI dashboards consumed by "
        "finance and operations teams in place of ad-hoc reporting workflows.",

        "<b>Resolved high-volume database bottlenecks</b> by analyzing execution plans "
        "and applying targeted indexing strategies. Cut report runtimes in production "
        "and unblocked client month-end closes.",
    ],
    "implementer_bullets_detailed": [
        "<b>Authored T-SQL fixes, stored procedures, and SQL views across dozens of "
        "enterprise customer deployments</b>. Root-caused in production data, integrated "
        "via <b>SAP DI API and Service Layer</b>, ran UAT, and shipped to production.",

        "<b>Delivered scoped technical projects</b>: wrote engineering specifications, "
        "coordinated with developers, integrated via DI API / Service Layer, and "
        "documented releases for handover.",
    ],
    "skills": [
        ("Languages &amp; Frameworks",
         "C# (.NET 8 / 10), ASP.NET Core Web API, T-SQL, SQL; Bash / PowerShell / Linux "
         "shell scripting; Python, JavaScript, React, HTML, C / C++ (foundations)"),
        ("API &amp; Backend",
         "REST APIs, JSON / XML, Layered Architecture (Service / Repository), "
         "OOP &amp; SOLID, Configuration-Driven / Declarative Engines, Dynamic Query "
         "Generation, Production Hardening &amp; Observability"),
        ("AI &amp; Automation",
         "AI Agent Development, Multi-Agent Orchestration, Human + AI-Agent Systems, "
         "Anthropic SDK, Skill / Tool-Use &amp; MCP Pipelines, Sandboxed Execution, "
         "Automated Code Generation"),
        ("AI-Assisted Development",
         "Agentic Coding Tools (Claude Code, Codex), Custom Skills, Plugins, MCP Tools "
         "&amp; Hooks, Rapid Adoption of New Tooling, Reviewed &amp; Security-Conscious "
         "AI Workflows"),
        ("Data &amp; Databases",
         "Microsoft SQL Server (MSSQL), Stored Procedures, SQL Views, Relational Data "
         "Modeling, Analytical Data Models (Fact tables, KPI logic), Performance Tuning "
         "(Execution Plans, Indexing), ETL-style Data Loads"),
        ("Cloud &amp; DevOps",
         "Microsoft Azure, Azure SQL Database, GitHub Actions (CI/CD), "
         "Git &amp; GitHub, Branching Workflows, Pull Requests"),
        ("Systems &amp; IT",
         "Linux / Unix, SQL Server Administration (DBA), On-Premise-to-Cloud "
         "Integration, System Administration, Network Traffic Analysis, Cross-System "
         "Troubleshooting"),
        ("Integration &amp; ERP Context",
         "SAP DI API, SAP Service Layer, SAP Business One, B1UP (Boyum IT), Power BI"),
        ("Tools &amp; Practices",
         "Visual Studio, VS Code, Postman, NLog, Code Reviews"),
    ],
}


# --------------------------------------------------------------------------
# Variant: DATA / SQL / BI / ETL
# --------------------------------------------------------------------------
DATA = {
    "variant": "Data",
    "headline": "Data &amp; SQL Engineer  &nbsp;|&nbsp;  T-SQL  •  SQL Server  •  Analytical Data Models  •  ETL  •  Power BI  •  AI-Native",
    "summary_detailed": (
        "Data-focused engineer with 3 years building production SQL Server data layers, "
        "stored procedures, fact tables, and KPI views feeding BI dashboards across dozens "
        "of enterprise customers. Combines deep T-SQL and performance-tuning expertise with "
        "C# (.NET 8 / 10) backend skills to ship reusable, multi-tenant data engines and "
        "ETL-style loads, cutting new-customer deployment from ~1 day to under 1 hour. "
        "Works AI-native: built custom agents, skills, and MCP tools that auto-generate SQL "
        "artifacts and functions inside a closed legacy system, as a reviewed, "
        "security-conscious accelerator - while keeping data modeling, code review, and "
        "security ownership hands-on. In a small, project-driven organization, works end "
        "to end across a broad surface - data modeling and DBA work, on-premise-to-cloud "
        "integration, backend, and internal IT - coordinating in a matrixed structure and "
        "ramping fast on unfamiliar systems and languages."
    ),
    "summary_concise": (
        "Data-focused engineer with 3 years building production SQL Server data layers, "
        "stored procedures, fact tables, and KPI views feeding BI dashboards across dozens "
        "of enterprise customers. Combines deep T-SQL and performance tuning with "
        "C# (.NET 8 / 10) backend skills, and works AI-native - built custom agents and MCP "
        "tools that auto-generate SQL artifacts for a closed legacy system, as a reviewed, "
        "security-conscious accelerator. In a small, project-driven organization, works "
        "end to end across data modeling, DBA, on-premise-to-cloud integration, and IT, "
        "ramping fast on unfamiliar systems."
    ),
    "senior_bullets_detailed": [
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

        "<b>Built custom AI agents, skills, and MCP tools that auto-generate SQL "
        "artifacts and functions for a closed legacy system</b> (B1UP / Boyum IT), "
        "executing within sandboxed environments. Automates recurring data-engineering "
        "work that previously required manual scripting.",

        "<b>Worked end to end across a broad technical surface</b> in a small, "
        "project-driven organization - data modeling and DBA, on-premise-to-cloud "
        "integration, backend REST APIs (C# / .NET), and internal IT - across 6+ "
        "on-site enterprise engagements, coordinating in a matrixed structure and "
        "ramping fast on unfamiliar systems.",
    ],
    "implementer_bullets_detailed": [
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
         "Tuning (Execution Plans, Indexing), SQL Server Administration (DBA), "
         "ETL-style Data Loads"),
        ("BI &amp; Reporting",
         "Power BI, KPI Logic, Dashboard-feeding SQL Layers"),
        ("Languages &amp; Frameworks",
         "T-SQL, SQL, C# (.NET 8 / 10), ASP.NET Core; Bash / PowerShell / Linux shell; "
         "Python, JavaScript, React, HTML, C / C++ (foundations)"),
        ("API &amp; Backend",
         "REST APIs, JSON / XML, Layered Architecture (Service / Repository), "
         "Configuration-Driven / Declarative Engines, Dynamic Query Generation"),
        ("AI &amp; Automation",
         "AI Agent Development, Multi-Agent Orchestration, Human + AI-Agent Systems, "
         "Anthropic SDK, Sandboxed Execution, Automated SQL / Code Generation"),
        ("AI-Assisted Development",
         "Agentic Coding Tools (Claude Code, Codex), Custom Skills, Plugins &amp; MCP "
         "Tools, Rapid Adoption of New Tooling, Reviewed &amp; Security-Conscious AI "
         "Workflows"),
        ("Cloud &amp; DevOps",
         "Microsoft Azure, Azure SQL Database, On-Premise-to-Cloud Integration, "
         "GitHub Actions (CI/CD), Git &amp; GitHub, Linux / Unix"),
        ("Integration &amp; ERP Context",
         "SAP DI API, SAP Service Layer, SAP Business One, B1UP (Boyum IT)"),
        ("Tools &amp; Practices",
         "Visual Studio, VS Code, Postman, NLog, Code Reviews"),
    ],
}


# --------------------------------------------------------------------------
# Variant: SOLUTIONS / FORWARD-DEPLOYED ENGINEER
# --------------------------------------------------------------------------
SOLUTIONS = {
    "variant": "Solutions",
    "headline": "Solutions Engineer  &nbsp;|&nbsp;  C# / .NET  •  SQL Server  •  AI-Native Automation  •  Enterprise Delivery",
    "summary_detailed": (
        "Solutions engineer with 3 years partnering with enterprise customers across "
        "dozens of accounts and 6+ on-site engagements, translating business "
        "requirements into production .NET APIs, SQL Server data models, and reusable "
        "backend engines. Cut new-customer deployment from ~1 day to under 1 hour by "
        "abstracting core logic into multi-tenant components. Works AI-native: builds "
        "custom agents, skills, plugins, and MCP tools to automate recurring "
        "engineering work, while keeping architecture, code review, and security "
        "ownership hands-on. In a small, project-driven organization, owns delivery end "
        "to end across a broad technical surface - backend, T-SQL and DBA, "
        "on-premise-to-cloud integration, and internal IT - coordinating in a matrixed "
        "structure and ramping fast on unfamiliar systems, with hands-on depth in "
        "C# / .NET, T-SQL, and SAP DI API / Service Layer."
    ),
    "summary_concise": (
        "Solutions engineer with 3 years partnering with enterprise customers across "
        "dozens of accounts and 6+ on-site engagements, translating requirements into "
        "production .NET APIs, SQL Server data models, and reusable backend engines. "
        "Cut new-customer deployment from ~1 day to under 1 hour, and works AI-native - "
        "builds custom agents, skills, and MCP tools to automate recurring work, as a "
        "reviewed, security-conscious accelerator. In a small, project-driven "
        "organization, owns delivery end to end across backend, T-SQL / DBA, "
        "on-premise-to-cloud integration, and IT, ramping fast on unfamiliar systems."
    ),
    "senior_bullets_detailed": [
        "<b>Partnered with enterprise customers across 6+ on-site engagements and dozens "
        "of accounts</b>: led discovery, translated business requirements into "
        "engineering specs, and shipped iterative releases through UAT to production. "
        "In a small, project-driven organization, owned delivery end to end across a "
        "broad surface - backend, T-SQL / DBA, on-premise-to-cloud integration, and IT "
        "- coordinating in a matrixed structure and ramping fast on unfamiliar systems.",

        "<b>Architected configuration-driven backend engines for multi-tenant rollouts</b> "
        "using declarative parameter tables and dynamic T-SQL generation. "
        "<b>Reduced new-customer deployment from ~1 day to under 1 hour</b>. Engines "
        "power vendor-risk scoring, inventory models, and financial modules (Budgeting, "
        "Aging, VAT Allocation).",

        "<b>Built custom AI agents, skills, plugins, and MCP tools</b> that run inside "
        "sandboxed environments and auto-generate code for a closed legacy system "
        "(B1UP / Boyum IT). Automates recurring solution-engineering work that "
        "previously required manual scripting.",

        "<b>Shipped production REST APIs</b> (C# / .NET / ASP.NET Core) with input "
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
    "implementer_bullets_detailed": [
        "<b>Owned production incidents and change requests across dozens of enterprise "
        "customer deployments</b>. Root-caused in T-SQL, wrote fixes (stored "
        "procedures, SQL views), integrated via <b>SAP DI API and Service Layer</b>, "
        "ran UAT, and shipped to production.",

        "<b>Delivered scoped technical projects</b>: wrote engineering specifications, "
        "coordinated with developers, and documented releases.",
    ],
    "skills": [
        ("API &amp; Backend",
         "C# (.NET 8 / 10), ASP.NET Core Web API, REST APIs, JSON / XML, Layered Architecture "
         "(Service / Repository), OOP &amp; SOLID, Configuration-Driven / Declarative Engines"),
        ("Customer Engineering",
         "Discovery &amp; Requirements Translation, Multi-Tenant Rollout, On-Site "
         "Delivery, Matrixed / Cross-Team Coordination, UAT &amp; Production Handover, "
         "Stakeholder Communication"),
        ("AI &amp; Automation",
         "AI Agent Development, Multi-Agent Orchestration, Human + AI-Agent Systems, "
         "Anthropic SDK, Skill / Tool-Use &amp; MCP Pipelines, Sandboxed Execution, "
         "Automated Code Generation"),
        ("AI-Assisted Development",
         "Agentic Coding Tools (Claude Code, Codex), Custom Skills, Plugins, MCP Tools "
         "&amp; Hooks, Rapid Adoption of New Tooling, Reviewed &amp; Security-Conscious "
         "AI Workflows"),
        ("Data &amp; Databases",
         "Microsoft SQL Server, T-SQL, Stored Procedures, SQL Views, SQL Server "
         "Administration (DBA), Performance Tuning (Execution Plans, Indexing), "
         "ETL-style Data Loads"),
        ("Cloud &amp; DevOps",
         "Microsoft Azure, Azure SQL Database, On-Premise-to-Cloud Integration, "
         "GitHub Actions (CI/CD), Git &amp; GitHub, Linux / Unix"),
        ("Languages &amp; Scripting",
         "C# (.NET 8 / 10), T-SQL, SQL, Bash / PowerShell / Linux shell; Python, "
         "JavaScript, React, HTML, C / C++ (foundations)"),
        ("Integration &amp; ERP Context",
         "SAP DI API, SAP Service Layer, SAP Business One, B1UP (Boyum IT), Power BI"),
        ("Tools &amp; Practices",
         "Visual Studio, VS Code, Postman, NLog, Code Reviews"),
    ],
}


# Concise bullet sets: curated subsets of the detailed lists, one page.
BACKEND["senior_bullets_concise"] = [
    BACKEND["senior_bullets_detailed"][0],   # AI agent + Skill toolkit
    BACKEND["senior_bullets_detailed"][1],   # config-driven engines + deployment metric
    BACKEND["senior_bullets_detailed"][2],   # end-to-end broad surface + adaptability
]
BACKEND["implementer_bullets_concise"] = [BACKEND["implementer_bullets_detailed"][0]]

DATA["senior_bullets_concise"] = [
    DATA["senior_bullets_detailed"][0],      # analytical SQL Server data models
    DATA["senior_bullets_detailed"][2],      # config-driven data engines + metric
    DATA["senior_bullets_detailed"][4],      # AI agent for SQL generation
]
DATA["implementer_bullets_concise"] = [DATA["implementer_bullets_detailed"][0]]

SOLUTIONS["senior_bullets_concise"] = [
    SOLUTIONS["senior_bullets_detailed"][0], # partnered with customers / discovery
    SOLUTIONS["senior_bullets_detailed"][1], # config-driven engines + metric
    SOLUTIONS["senior_bullets_detailed"][2], # AI agent + Skill toolkit
]
SOLUTIONS["implementer_bullets_concise"] = [SOLUTIONS["implementer_bullets_detailed"][0]]


VARIANTS = [BACKEND, DATA, SOLUTIONS]

# Site mirror of the resumeOpt SoT. Keep the variant content in sync with
# resumeOpt/build_resume.py after each approved batch. Paths are repo-relative so
# this runs anywhere (local, CI). main() also exports the 1-page concise variants
# into the site's served location so the CV download links always point at the
# current files.
_HERE = Path(__file__).resolve().parent
BATCH_DIR = str(_HERE / "batches" / "2026-07-01")
# apps/site/public/resumes is what ResumeDownloads.astro links to (/resumes/<file>).
SERVED_DIR = _HERE.parents[1] / "apps" / "site" / "public" / "resumes"
LENGTHS = ["detailed", "concise"]
SERVED_LENGTH = "concise"  # the site serves the clean 1-page variant


def main() -> None:
    for length in LENGTHS:
        out_dir = f"{BATCH_DIR}/{length}"
        os.makedirs(out_dir, exist_ok=True)
        for cfg in VARIANTS:
            out = f"{out_dir}/Niv Schendel Resume - {cfg['variant']}.pdf"
            render(cfg, length, out)
            print("Built:", out)

    # Export the served length into the site's public/resumes (same filenames the
    # site links to). This is the "CV export points to the right files" step.
    os.makedirs(SERVED_DIR, exist_ok=True)
    for cfg in VARIANTS:
        name = f"Niv Schendel Resume - {cfg['variant']}.pdf"
        shutil.copyfile(f"{BATCH_DIR}/{SERVED_LENGTH}/{name}", SERVED_DIR / name)
        print("Exported to site:", SERVED_DIR / name)


if __name__ == "__main__":
    main()
