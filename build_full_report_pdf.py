import os
import sys
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PDF_FILENAME = "CareerEquity_AI_Project_Report.pdf"

class NumberedCanvas(canvas.Canvas):
    """
    Two-pass canvas to dynamically compute total pages and draw consistent
    college-standard border, header, and footer on all pages.
    """
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        w, h = A4
        
        # 1. Outer Standard Border (2pt Black Border with 24pt margin)
        self.setStrokeColor(colors.black)
        self.setLineWidth(1.8)
        self.rect(26, 26, w - 52, h - 52)
        
        # 2. Header and Footer (Only on page 2 onwards)
        if self._pageNumber > 1:
            # Running Header
            self.setFont("Helvetica-Oblique", 8)
            self.setFillColor(colors.HexColor("#475569"))
            self.drawRightString(w - 36, h - 22, "CareerEquity AI • Enterprise Workforce Intelligence System")
            
            # Running Footer / Page Number
            self.setFont("Helvetica", 8.5)
            self.setFillColor(colors.HexColor("#1e293b"))
            self.drawRightString(w - 36, 15, f"Page {self._pageNumber} of {page_count}")
            self.drawString(36, 15, "PK Das Liberal College of Arts & Science • University of Calicut")
            
        self.restoreState()

def create_report_pdf():
    doc = SimpleDocTemplate(
        PDF_FILENAME,
        pagesize=A4,
        leftMargin=38,
        rightMargin=38,
        topMargin=42,
        bottomMargin=42
    )

    styles = getSampleStyleSheet()
    
    # Custom Academic Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=18,
        leading=24,
        alignment=1, # Center
        textColor=colors.HexColor('#0f172a'),
        spaceAfter=12
    )

    subtitle_style = ParagraphStyle(
        'DocSubTitle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        leading=16,
        alignment=1,
        textColor=colors.HexColor('#334155'),
        spaceAfter=10
    )

    h1_style = ParagraphStyle(
        'SectionH1',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        alignment=0, # Left
        textColor=colors.HexColor('#0f172a'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'SectionH2',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=11.5,
        leading=15,
        alignment=0,
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )

    h3_style = ParagraphStyle(
        'SectionH3',
        parent=styles['Heading3'],
        fontName='Helvetica-Bold',
        fontSize=10,
        leading=13,
        alignment=0,
        textColor=colors.HexColor('#334155'),
        spaceBefore=8,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'BodyAcademic',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=14.5,
        alignment=4, # Justify
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'BulletAcademic',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13.5,
        leftIndent=15,
        textColor=colors.HexColor('#1e293b'),
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'CodeSnippet',
        parent=styles['Code'],
        fontName='Courier',
        fontSize=7.5,
        leading=10,
        textColor=colors.HexColor('#0f172a'),
        backColor=colors.HexColor('#f8fafc'),
        borderColor=colors.HexColor('#e2e8f0'),
        borderWidth=0.8,
        borderPadding=6,
        spaceBefore=6,
        spaceAfter=8
    )

    caption_style = ParagraphStyle(
        'FigCaption',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=9,
        leading=12,
        alignment=1, # Center
        textColor=colors.HexColor('#1e293b'),
        spaceBefore=5,
        spaceAfter=10
    )

    story = []

    # =========================================================
    # 1. TITLE PAGE
    # =========================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("CAREEREQUITY AI: ENTERPRISE 4-LEVEL ROLE-BASED WORKFORCE INTELLIGENCE &amp; FAIRNESS SYSTEM", title_style))
    story.append(Spacer(1, 10))
    story.append(Paragraph("Project Report", ParagraphStyle('Sub1', fontName='Helvetica-Bold', fontSize=12, alignment=1, textColor=colors.HexColor('#334155'))))
    story.append(Paragraph("Submitted in partial fulfilment of the requirement for the award of the degree of", subtitle_style))
    story.append(Spacer(1, 4))
    story.append(Paragraph("<b>BACHELOR OF COMPUTER APPLICATIONS</b>", ParagraphStyle('BCA', fontName='Helvetica-Bold', fontSize=13, alignment=1, textColor=colors.HexColor('#0f172a'))))
    story.append(Paragraph("(University of Calicut)", ParagraphStyle('Uni', fontName='Helvetica', fontSize=11, alignment=1, textColor=colors.HexColor('#475569'))))
    story.append(Spacer(1, 15))

    story.append(Paragraph("<b>Submitted by</b>", subtitle_style))
    candidate_data = [
        [Paragraph("<b>CANDIDATE 1:</b> ABHINAND", body_style), Paragraph("<b>REGISTER NO:</b> 2023-BCA-001", body_style)],
        [Paragraph("<b>CANDIDATE 2:</b> PROJECT TEAM MEMBER", body_style), Paragraph("<b>REGISTER NO:</b> 2023-BCA-002", body_style)],
        [Paragraph("<b>CANDIDATE 3:</b> PROJECT TEAM MEMBER", body_style), Paragraph("<b>REGISTER NO:</b> 2023-BCA-003", body_style)],
    ]
    cand_table = Table(candidate_data, colWidths=[200, 200])
    cand_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(cand_table)
    story.append(Spacer(1, 20))

    # Official Logos
    calicut_logo = "report_assets/page_1_img_2.jpeg"
    college_banner = "report_assets/page_1_img_1.jpeg"
    if os.path.exists(calicut_logo):
        story.append(Image(calicut_logo, width=80, height=80))
        story.append(Spacer(1, 10))
    if os.path.exists(college_banner):
        story.append(Image(college_banner, width=320, height=58))
        story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2026-2027 Academic Year</b>", ParagraphStyle('Year', fontName='Helvetica-Bold', fontSize=11, alignment=1, textColor=colors.HexColor('#1e293b'))))
    story.append(PageBreak())

    # =========================================================
    # 2. BONAFIDE CERTIFICATE
    # =========================================================
    if os.path.exists(calicut_logo):
        story.append(Image(calicut_logo, width=65, height=65))
        story.append(Spacer(1, 4))
    story.append(Paragraph("<b>UNIVERSITY OF CALICUT</b>", ParagraphStyle('UC', fontName='Helvetica-Bold', fontSize=13, alignment=1)))
    story.append(Paragraph("BACHELOR OF COMPUTER APPLICATIONS", ParagraphStyle('BCA2', fontName='Helvetica', fontSize=11, alignment=1)))
    story.append(Spacer(1, 8))
    if os.path.exists(college_banner):
        story.append(Image(college_banner, width=300, height=54))
        story.append(Spacer(1, 14))

    cert_text = (
        "This is to certify that the project report entitled <b>“CAREEREQUITY AI: ENTERPRISE 4-LEVEL ROLE-BASED "
        "WORKFORCE INTELLIGENCE &amp; AI-DRIVEN FAIRNESS MANAGEMENT SYSTEM”</b> is a bonafide record done by "
        "<b>Abhinand &amp; Team</b> during the academic year <b>2026-2027</b> towards the partial fulfilment of the "
        "requirements for the award of <b>BACHELOR OF COMPUTER APPLICATIONS</b> of the University of Calicut."
    )
    story.append(Paragraph(cert_text, ParagraphStyle('CertBody', fontName='Helvetica', fontSize=10, leading=16, alignment=4)))
    story.append(Spacer(1, 40))

    sign_data = [
        [Paragraph("....................................................<br/><b>Project Guide</b><br/>Assistant Professor", body_style),
         Paragraph("....................................................<br/><b>Head of Department</b><br/>Musthafa Kamal Pasha A", body_style)],
        [Paragraph("<br/><br/>....................................................<br/><b>Principal</b><br/>Dr. K.G Ajith Kumar", body_style),
         Paragraph("<br/><br/>....................................................<br/><b>EXTERNAL EXAMINER</b>", body_style)]
    ]
    sign_table = Table(sign_data, colWidths=[240, 240])
    sign_table.setStyle(TableStyle([
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 12),
    ]))
    story.append(sign_table)
    story.append(PageBreak())

    # =========================================================
    # 3. INTERNSHIP / PROJECT CERTIFICATE
    # =========================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<u><b>PROJECT / INSTITUTIONAL COMPLETION CERTIFICATE</b></u>", ParagraphStyle('CertHead', fontName='Helvetica-Bold', fontSize=13, alignment=1)))
    story.append(Spacer(1, 30))
    internship_text = (
        "This is to certify that the project entitled <b>“CareerEquity AI: Enterprise 4-Level Role-Based Workforce "
        "Intelligence &amp; AI-Driven Fairness Management System”</b> has been successfully developed, integrated, "
        "tested, and validated on the enterprise technology framework at PK Das Liberal College of Arts &amp; Science "
        "for the academic curriculum of Bachelor of Computer Applications under University of Calicut.<br/><br/>"
        "The project encompasses a full-stack Python 3.12 and Django 4.2 architecture, Scikit-learn machine learning "
        "predictive pipelines for workload burnout detection and salary equity auditing, synchronized Indian Standard "
        "Time (Asia/Kolkata) biometric shift logging, and advanced role-based access control protecting enterprise operations."
    )
    story.append(Paragraph(internship_text, ParagraphStyle('CertBody2', fontName='Helvetica', fontSize=10.5, leading=17, alignment=4)))
    story.append(Spacer(1, 60))

    story.append(Paragraph("<b>Authorized Signatory / Project Coordinator</b>", ParagraphStyle('SignRight', fontName='Helvetica-Bold', fontSize=10, alignment=2)))
    story.append(Paragraph("PK Das Liberal College of Arts &amp; Science, Palakkad", ParagraphStyle('SignRight2', fontName='Helvetica', fontSize=9, alignment=2)))
    story.append(PageBreak())

    # =========================================================
    # 4. DECLARATION
    # =========================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<u><b>DECLARATION</b></u>", ParagraphStyle('DecHead', fontName='Helvetica-Bold', fontSize=14, alignment=1)))
    story.append(Spacer(1, 25))
    dec_text = (
        "We hereby declare that the project work entitled <b>“CAREEREQUITY AI: ENTERPRISE 4-LEVEL ROLE-BASED WORKFORCE "
        "INTELLIGENCE &amp; FAIRNESS MANAGEMENT SYSTEM”</b> developed at PK Das Liberal College of Arts and Science, "
        "Lakkidi, Palakkad, Kerala and submitted to the University of Calicut, in partial fulfilment of the requirements "
        "for the award of the degree of <b>Bachelor of Computer Applications</b>, is a record of original project work "
        "done by us during the academic year 2026-2027, under the supervision and guidance of our project guide, "
        "Assistant Professor, Department of Computer Science, PK Das Liberal College of Arts and Science, Palakkad.<br/><br/>"
        "We further declare that this report has not previously formed the basis for the award of any degree, diploma, "
        "associateship, or other similar title to the best of our knowledge and belief."
    )
    story.append(Paragraph(dec_text, ParagraphStyle('DecBody', fontName='Helvetica', fontSize=10, leading=16, alignment=4)))
    story.append(Spacer(1, 50))

    dec_meta = [
        [Paragraph("<b>Place:</b> Lakkidi, Palakkad<br/><b>Date:</b> November 26, 2026", body_style),
         Paragraph("<b>Signature of the Candidates:</b><br/><br/>1. ....................................................<br/>2. ....................................................<br/>3. ....................................................", body_style)]
    ]
    dec_table = Table(dec_meta, colWidths=[220, 260])
    story.append(dec_table)
    story.append(PageBreak())

    # =========================================================
    # 5. ACKNOWLEDGEMENT
    # =========================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<u><b>ACKNOWLEDGEMENT</b></u>", ParagraphStyle('AckHead', fontName='Helvetica-Bold', fontSize=14, alignment=1)))
    story.append(Spacer(1, 20))
    ack_text = (
        "We are very grateful to the Almighty who has blessed us with strength, health, and wisdom to complete this "
        "project successfully.<br/><br/>"
        "We have been fortunate enough to secure cooperation, guidance, and assistance from esteemed mentors throughout "
        "this journey. We express our deep indebtedness to our Principal, <b>Dr. K.G Ajith Kumar</b>, who granted us "
        "the requisite facilities and encouragement for the completion of this venture.<br/><br/>"
        "We would like to express our profound gratitude to <b>Mr. Musthafa Kamal Pasha A</b>, Head of the Department "
        "of Computer Science, for his invaluable support, constructive criticism, and guidance throughout the course.<br/><br/>"
        "We express our heartfelt appreciation to our Project Guide, Assistant Professor, Department of Computer Science, "
        "PK Das Liberal College of Arts and Science, for constant inspiration, technical guidance, and valuable insights.<br/><br/>"
        "We also extend our sincere thanks to all other faculty members and technical staff of the Department of Computer "
        "Science for their unwavering support.<br/><br/>"
        "Last but certainly not least, we express our warmest gratitude to our parents, family members, and beloved friends "
        "for their moral encouragement and faith in our endeavours."
    )
    story.append(Paragraph(ack_text, ParagraphStyle('AckBody', fontName='Helvetica', fontSize=9.5, leading=15, alignment=4)))
    story.append(PageBreak())

    # =========================================================
    # 6. ABSTRACT
    # =========================================================
    story.append(Spacer(1, 20))
    story.append(Paragraph("<u><b>ABSTRACT</b></u>", ParagraphStyle('AbsHead', fontName='Helvetica-Bold', fontSize=14, alignment=1)))
    story.append(Spacer(1, 20))
    abs_text = (
        "In modern knowledge-driven enterprises, organizations struggle with two deeply intertwined challenges: "
        "unconscious bias in compensation decisions and employee attrition triggered by unmonitored workload burnout. "
        "Traditional Human Resource Management Systems (HRMS) act as passive transactional databases, recording past "
        "data without providing predictive insights or organizational safeguards. "
        "<br/><br/>"
        "<b>CareerEquity AI</b> is an enterprise-grade, four-level role-based workforce intelligence and algorithmic fairness "
        "platform architected to solve these systemic challenges. Developed using <b>Python 3.12, Django 4.2, and Scikit-learn</b>, "
        "the system implements a hierarchical Role-Based Access Control (RBAC) model spanning four tiers: "
        "<b>HR Executive/Admin, Department Manager, Team Manager, and Employee (featuring 9 comprehensive operational modules)</b>. "
        "<br/><br/>"
        "The core innovation lies in its explainable AI subsystem featuring three deterministic machine learning engines: "
        "(1) <i>AI Workload Burnout Risk Monitor</i>, which analyzes assigned task complexity weights, pending delivery commitments, "
        "and deadlines to calculate a composite workload index alerting managers before burnout occurs; "
        "(2) <i>AI Salary Equity Predictor</i>, utilizing multi-factor Ridge Regression trained on objective skill metrics, experience "
        "vectors, and performance ratings to flag gender or demographic compensation disparities exceeding a 10% tolerance; and "
        "(3) <i>Career Progression &amp; Skill-Gap Advisor</i>, which computes geometric cosine distance across role requirements "
        "to deliver actionable promotion roadmaps. "
        "<br/><br/>"
        "The platform incorporates a synchronized biometric attendance terminal operating strictly in <b>Indian Standard Time "
        "(Asia/Kolkata, UTC+05:30)</b> with automatic duration logging, anti-double-submission tokens, CSRF protection, and "
        "team-level task distribution across 8 functional departments and 16 specialized teams. CareerEquity AI proves that modern "
        "workplaces can achieve maximum operational velocity while upholding transparent, objective equity for every worker."
    )
    story.append(Paragraph(abs_text, ParagraphStyle('AbsBody', fontName='Helvetica', fontSize=9.5, leading=15, alignment=4)))
    story.append(PageBreak())

    # =========================================================
    # 7. INDEX (TABLE OF CONTENTS)
    # =========================================================
    story.append(Spacer(1, 15))
    story.append(Paragraph("<b>INDEX</b>", ParagraphStyle('IdxHead', fontName='Helvetica-Bold', fontSize=14, alignment=1)))
    story.append(Spacer(1, 12))

    index_data = [
        [Paragraph("<b>Sl.NO</b>", body_style), Paragraph("<b>TOPIC</b>", body_style), Paragraph("<b>PAGE NO</b>", body_style)],
        ["1", Paragraph("<b>INTRODUCTION</b>", body_style), "1"],
        ["2", Paragraph("<b>SYSTEM CONFIGURATION</b><br/>"
                       "&nbsp;&nbsp;2.1 HARDWARE CONFIGURATION<br/>"
                       "&nbsp;&nbsp;2.2 SOFTWARE CONFIGURATION<br/>"
                       "&nbsp;&nbsp;2.3 USER REQUIREMENTS<br/>"
                       "&nbsp;&nbsp;&nbsp;&nbsp;2.3.1 FRONT-END SOFTWARE<br/>"
                       "&nbsp;&nbsp;&nbsp;&nbsp;2.3.2 BACK-END SOFTWARE", body_style), "3"],
        ["3", Paragraph("<b>SYSTEM DEVELOPMENT ANALYSIS</b><br/>"
                       "&nbsp;&nbsp;3.1 OBJECTIVE OF THE SYSTEM<br/>"
                       "&nbsp;&nbsp;3.2 EXISTING SYSTEM &amp; LIMITATIONS<br/>"
                       "&nbsp;&nbsp;3.3 PROPOSED SYSTEM &amp; ADVANTAGES", body_style), "5"],
        ["4", Paragraph("<b>SYSTEM DESIGN</b><br/>"
                       "&nbsp;&nbsp;4.1 INPUT DESIGN<br/>"
                       "&nbsp;&nbsp;4.2 OUTPUT DESIGN<br/>"
                       "&nbsp;&nbsp;4.3 DATASET &amp; DATABASE SCHEMA DESIGN<br/>"
                       "&nbsp;&nbsp;4.4 MODULE DESCRIPTION (4 ROLES &amp; 9 MODULES)", body_style), "8"],
        ["5", Paragraph("<b>SYSTEM IMPLEMENTATION AND TESTING</b><br/>"
                       "&nbsp;&nbsp;5.1 SYSTEM IMPLEMENTATION<br/>"
                       "&nbsp;&nbsp;5.2 SYSTEM TESTING &amp; TEST SUITE<br/>"
                       "&nbsp;&nbsp;&nbsp;&nbsp;5.2.1 TYPES OF TESTING (UNIT, INTEGRATION, CSRF)", body_style), "14"],
        ["6", Paragraph("<b>CONCLUSION &amp; FUTURE SCOPE</b>", body_style), "18"],
        ["7", Paragraph("<b>BIBLIOGRAPHY &amp; REFERENCES</b>", body_style), "20"],
        ["8", Paragraph("<b>SYSTEM DIAGRAMS</b><br/>"
                       "&nbsp;&nbsp;8.1 SYSTEM ARCHITECTURE DIAGRAM<br/>"
                       "&nbsp;&nbsp;8.2 USE CASE DIAGRAM<br/>"
                       "&nbsp;&nbsp;8.3 DATA FLOW DIAGRAMS (LEVEL 0, 1, 2, 3)<br/>"
                       "&nbsp;&nbsp;8.4 ENTITY RELATIONSHIP (ER) DIAGRAM<br/>"
                       "&nbsp;&nbsp;8.5 CLASS DIAGRAM<br/>"
                       "&nbsp;&nbsp;8.6 SEQUENCE DIAGRAM (IST SHIFT PUNCH)<br/>"
                       "&nbsp;&nbsp;8.7 ACTIVITY WORKFLOW DIAGRAM<br/>"
                       "&nbsp;&nbsp;8.8 MODEL EVALUATION &amp; BENCHMARK DIAGRAM", body_style), "21"],
        ["9", Paragraph("<b>SAMPLE SCREENSHOTS</b>", body_style), "31"],
        ["10", Paragraph("<b>SOURCE CODE REPOSITORY</b>", body_style), "34"],
    ]

    idx_table = Table(index_data, colWidths=[45, 390, 65])
    idx_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1.2, colors.HexColor('#1e293b')),
        ('INNERGRID', (0,0), (-1,-1), 0.6, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('PADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(idx_table)
    story.append(PageBreak())

    # =========================================================
    # CHAPTER 1: INTRODUCTION
    # =========================================================
    story.append(Paragraph("<b>1. INTRODUCTION</b>", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

    intro_p1 = (
        "Human Resource Management is undergoing an unprecedented transformation. For decades, corporate personnel "
        "administration was characterized by manual record-keeping, isolated desktop spreadsheets, and centralized paper "
        "filing cabinets. While early computerization produced electronic databases, the vast majority of existing "
        "enterprise software remains fundamentally transactional—recording what happened in the past rather than providing "
        "actionable intelligence on what is happening in the present or predicting what will happen in the future."
    )
    story.append(Paragraph(intro_p1, body_style))

    intro_p2 = (
        "Two profound challenges plague contemporary corporate environments: <b>algorithmic and human pay disparities</b>, "
        "and <b>unmonitored employee burnout</b>. Corporate compensation decisions are frequently made behind closed doors, "
        "subject to cognitive bias, historical inequities, and inconsistent managerial subjectivity. Meanwhile, fast-paced "
        "deliverable deadlines cause work to be piled disproportionately upon dependable employees without real-time "
        "visibility into their committed hours and cognitive load, leading to high attrition, reduced morale, and severe burnout."
    )
    story.append(Paragraph(intro_p2, body_style))

    intro_p3 = (
        "<b>CareerEquity AI</b> is engineered to provide an objective, transparent, and mathematically grounded alternative. "
        "It is an intelligent, multi-tier enterprise management suite that unifies four organizational echelons: "
        "Human Resources Executives, Department Heads, Frontline Team Managers, and Employees. By coupling transactional "
        "workplace workflows (such as biometric punch-in/out, leave approvals, and task distribution) with deterministic "
        "Machine Learning engines, CareerEquity AI detects compensation inequities before they become legal liabilities, "
        "and alerts managers to impending burnout before it impacts employee health."
    )
    story.append(Paragraph(intro_p3, body_style))

    story.append(Paragraph("<b>Purpose &amp; Scope of the Project:</b>", h2_style))
    story.append(Paragraph("• <b>Unified 4-Level Management:</b> Eliminate operational silos between HR strategy, departmental budgeting, team-level sprint assignment, and employee self-service.", bullet_style))
    story.append(Paragraph("• <b>Machine Learning Pay Equity:</b> Train regression models on objective performance factors to eliminate arbitrary pay gaps across demographic and tenure boundaries.", bullet_style))
    story.append(Paragraph("• <b>Proactive Burnout Prevention:</b> Continuous evaluation of assigned task complexity weights, pending delivery commitments, and deadlines.", bullet_style))
    story.append(Paragraph("• <b>Precision IST Biometric Tracking:</b> Fully localized attendance punching locked to Indian Standard Time (Asia/Kolkata, UTC+05:30) with automated shift duration calculation.", bullet_style))
    story.append(Paragraph("• <b>Employee Empowerment (9 Modules):</b> Provide every staff member an autonomous portal featuring Profile, Tasks, Shift Attendance, Leaves, Performance, Salary &amp; Payslips, Skills, Workload, and Career Growth.", bullet_style))
    story.append(PageBreak())

    # =========================================================
    # CHAPTER 2: SYSTEM CONFIGURATION
    # =========================================================
    story.append(Paragraph("<b>2. SYSTEM CONFIGURATION</b>", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

    story.append(Paragraph("<b>2.1 HARDWARE CONFIGURATION</b>", h2_style))
    story.append(Paragraph(
        "CareerEquity AI is engineered as an efficient, lightweight, and scalable web platform. The development and deployment "
        "specifications ensure seamless execution on modern institutional or cloud workstations:", body_style
    ))
    hw_data = [
        [Paragraph("<b>Component</b>", body_style), Paragraph("<b>Minimum Requirement</b>", body_style), Paragraph("<b>Recommended Specification</b>", body_style)],
        ["Processor (CPU)", "Intel Core i3 / AMD Ryzen 3 (2.0 GHz)", "Intel Core i5 / AMD Ryzen 5 or Apple M-series"],
        ["System Memory (RAM)", "4 GB DDR4", "8 GB / 16 GB DDR4/DDR5"],
        ["Hard Disk / Storage", "20 GB available SSD storage", "50 GB NVMe Solid State Drive"],
        ["Display Monitor", "1366 x 768 resolution display", "1920 x 1080 Full HD IPS Display"],
        ["Network Interface", "Standard 10/100 Mbps Ethernet / Wi-Fi", "Gigabit Ethernet / High-Speed Broadband"]
    ]
    hw_table = Table(hw_data, colWidths=[120, 180, 200])
    hw_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#334155')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(hw_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2.2 SOFTWARE CONFIGURATION</b>", h2_style))
    sw_data = [
        [Paragraph("<b>Layer</b>", body_style), Paragraph("<b>Environment &amp; Technology Stack</b>", body_style)],
        ["Operating System", "Microsoft Windows 10/11 (64-bit), Ubuntu Linux 22.04 LTS, or macOS"],
        ["Core Language", "Python 3.12 (High-performance scripting, type hinting, and robust standard library)"],
        ["Web Framework", "Django 4.2 LTS (Model-View-Template architecture, ORM, CSRF, Session Auth)"],
        ["Machine Learning Suite", "Scikit-Learn 1.4+, NumPy 1.26+, Pandas 2.2+, SciPy"],
        ["Relational Database", "SQLite3 (Embedded zero-configuration engine with ACID transaction compliance)"],
        ["Time Zone System", "Asia/Kolkata (Indian Standard Time, UTC+05:30 with Django USE_TZ = True)"],
        ["Web Browser", "Google Chrome 120+, Mozilla Firefox 120+, Microsoft Edge, Safari"]
    ]
    sw_table = Table(sw_data, colWidths=[150, 350])
    sw_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#334155')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(sw_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>2.3 USER REQUIREMENTS</b>", h2_style))
    story.append(Paragraph("<b>2.3.1 FRONT-END SOFTWARE</b>", h3_style))
    story.append(Paragraph(
        "The client tier requires zero third-party browser plugins or proprietary runtime environments. It employs semantic "
        "HTML5 markup, custom CSS3 responsive grid layouts with modern card aesthetics, and asynchronous JavaScript for live "
        "client-side validation and dynamic clock synchronization. Cross-Site Request Forgery (CSRF) tokens are embedded into "
        "every form payload alongside client-side double-submission locks to guarantee absolute transactional safety.", body_style
    ))
    story.append(Paragraph("<b>2.3.2 BACK-END SOFTWARE</b>", h3_style))
    story.append(Paragraph(
        "The server tier is powered by Django 4.2's asynchronous WSGI/ASGI application server. It integrates Django's Object-Relational "
        "Mapping (ORM) layer, enforcing strict database relationships, foreign key cascades, and atomic transactions. Authentication "
        "utilizes salted SHA-256 password hashing. In parallel, scikit-learn models execute within dedicated Python analytic modules, "
        "computing instant predictions on live database querysets without blocking HTTP request threads.", body_style
    ))
    story.append(PageBreak())

    # =========================================================
    # CHAPTER 3: SYSTEM DEVELOPMENT ANALYSIS
    # =========================================================
    story.append(Paragraph("<b>3. SYSTEM DEVELOPMENT ANALYSIS</b>", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

    story.append(Paragraph("<b>3.1 OBJECTIVE OF THE SYSTEM</b>", h2_style))
    story.append(Paragraph(
        "The overarching objective of CareerEquity AI is to engineer an ethical, transparent, and high-performance workforce "
        "management platform that replaces opaque managerial discretion with objective artificial intelligence. Key objectives include:", body_style
    ))
    story.append(Paragraph("1. <b>Algorithmic Compensation Auditing:</b> Establish benchmark compensation levels based strictly on tenure, demonstrated competencies, and past review ratings to eradicate gender and background pay disparities.", bullet_style))
    story.append(Paragraph("2. <b>Dynamic Workload Equilibrium:</b> Continuously balance task allocations across team members, factoring in complexity ratings and sprint deadlines to avert burnout.", bullet_style))
    story.append(Paragraph("3. <b>Synchronized Indian Standard Time Operations:</b> Ensure shift records, attendance punches, and audit trails accurately reflect IST wall-clock time without timezone disorientation.", bullet_style))
    story.append(Paragraph("4. <b>Actionable Career Mobility:</b> Provide transparent skill-gap visualization showing employees exactly what competencies are needed to achieve promotions.", bullet_style))

    story.append(Paragraph("<b>3.2 EXISTING SYSTEM</b>", h2_style))
    story.append(Paragraph(
        "In current organizational environments, enterprise workforce management is fragmented across disjointed tools: manual "
        "spreadsheets (e.g. Microsoft Excel), standalone biometric punch clocks, third-party ticket trackers, and disconnected "
        "payroll software. Managers allocate work based on memory or proximity, frequently overloading dependable staff members "
        "while underutilizing others. Performance reviews occur annually through subjective questionnaires vulnerable to recency bias.", body_style
    ))

    story.append(Paragraph("<b>LIMITATIONS OF THE EXISTING SYSTEM:</b>", h3_style))
    story.append(Paragraph("• <b>Lack of Predictive Insights:</b> Traditional HRMS merely log records retrospectively; they possess zero ability to forecast burnout or quantify overload risk.", bullet_style))
    story.append(Paragraph("• <b>Compensation Opacity:</b> Salary discrepancies between peers in identical roles persist undetected because no statistical parity model audits internal equity.", bullet_style))
    story.append(Paragraph("• <b>Operational Siloing:</b> Department heads cannot see granular team tasks, while team managers lack insight into departmental budgets and workforce risk metrics.", bullet_style))
    story.append(Paragraph("• <b>Vulnerability to Timezone Skew:</b> Cloud software configured to UTC frequently causes shift punch records and duration calculations to misalign with Indian local hours.", bullet_style))

    story.append(Paragraph("<b>3.3 PROPOSED SYSTEM</b>", h2_style))
    story.append(Paragraph(
        "The proposed <b>CareerEquity AI</b> platform establishes an integrated four-level hierarchy where operational workflows and "
        "machine learning models operate in tight synergy. When a manager assigns a task, the AI engine immediately calculates the "
        "recipient's cumulative cognitive workload score. If the assignment pushes the employee into the danger zone (>75%), an "
        "instant visual warning alerts the manager to redistribute the workload. Simultaneously, the platform audits salary equity "
        "and tracks shift attendance in precise Indian Standard Time.", body_style
    ))

    story.append(Paragraph("<b>ADVANTAGES OF THE PROPOSED SYSTEM:</b>", h3_style))
    story.append(Paragraph("• <b>Explainable Machine Learning:</b> Uses deterministic linear regression and mathematically transparent heuristics rather than uninterpretable black-box models.", bullet_style))
    story.append(Paragraph("• <b>Automated Workload Balancing:</b> Reduces voluntary employee turnover by proactively safeguarding staff well-being.", bullet_style))
    story.append(Paragraph("• <b>Zero Timezone Ambiguity:</b> Fully synchronized to Asia/Kolkata (IST), ensuring shift hours and punch logs are exact.", bullet_style))
    story.append(Paragraph("• <b>Comprehensive Employee Self-Service:</b> 9 dedicated employee modules put leaves, attendance, salary, tasks, and career planning in one unified portal.", bullet_style))
    story.append(PageBreak())

    # =========================================================
    # CHAPTER 4: SYSTEM DESIGN
    # =========================================================
    story.append(Paragraph("<b>4. SYSTEM DESIGN</b>", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

    story.append(Paragraph("<b>4.1 INPUT DESIGN</b>", h2_style))
    story.append(Paragraph(
        "Input design in CareerEquity AI focuses on data validation, user efficiency, and defensive security. Every user interaction "
        "passes through sanitization filters before persistence:", body_style
    ))
    story.append(Paragraph("• <b>Authentication Input:</b> Captures username/email, password, and designated role with automatic redirect routing.", bullet_style))
    story.append(Paragraph("• <b>Task Assignment Input:</b> Captures task title, description, team dropdown, complexity weight (Low=1.0, Medium=1.5, High=2.0, Critical=3.0), estimated hours, and ISO deadline.", bullet_style))
    story.append(Paragraph("• <b>Live Biometric Punch Input:</b> One-click form submission capturing instantaneous client timestamp, validated against server-side IST wall-clock time.", bullet_style))
    story.append(Paragraph("• <b>Leave Request Input:</b> Structured selection of leave type (Casual, Sick, Earned), start date, end date, and justification text.", bullet_style))

    story.append(Paragraph("<b>4.2 OUTPUT DESIGN</b>", h2_style))
    story.append(Paragraph(
        "Outputs are rendered through responsive visual dashboards tailored to each of the four organizational roles:", body_style
    ))
    story.append(Paragraph("• <b>HR Executive Dashboard:</b> Displays enterprise headcount (72 active employees across 8 departments and 16 teams), active burnout alerts, salary disparity flags, and department distribution tables.", bullet_style))
    story.append(Paragraph("• <b>Department Manager View:</b> Presents departmental budget utilization, cross-team task velocity, and attendance percentages.", bullet_style))
    story.append(Paragraph("• <b>Team Manager Workspace:</b> Features real-time team workload meters, task assignment forms, pending leave request approval queues, and member shift history.", bullet_style))
    story.append(Paragraph("• <b>Employee Workspace:</b> Renders the 9 comprehensive self-service cards, real-time IST biometric clock, task Kanban progress bars, and payslip breakdowns.", bullet_style))

    story.append(Paragraph("<b>4.3 DATASET &amp; DATABASE SCHEMA DESIGN</b>", h2_style))
    story.append(Paragraph(
        "The relational database schema is structured to ensure Third Normal Form (3NF) compliance and strict referential integrity. "
        "Primary models include:", body_style
    ))
    db_schema_data = [
        [Paragraph("<b>Model Name</b>", body_style), Paragraph("<b>Key Attributes &amp; Data Types</b>", body_style), Paragraph("<b>Relationships</b>", body_style)],
        ["AccountProfile", "user (OneToOne), role (Enum), employee_id (Char), department (Char), is_active (Bool)", "Links to Django auth.User"],
        ["Department", "name (Char), code (Char), budget (Decimal), manager (FK)", "Parent of Teams & Employees"],
        ["Team", "name (Char), department (FK), team_manager (FK)", "Child of Department"],
        ["EmployeeProfile", "employee_id (Char), position (FK), team (FK), current_salary (Decimal), experience_years (Decimal)", "Child of Department & Team"],
        ["Task", "title (Char), complexity (Enum: Low/Med/High/Critical), estimated_hours (Decimal)", "Parent of TaskAssignment"],
        ["TaskAssignment", "task (FK), employee (FK), status (Enum), assigned_date (Date), progress_percent (Int)", "Links Employee to Task"],
        ["AttendanceRecord", "employee (FK), date (Date), check_in (Time IST), check_out (Time IST), working_hours (Decimal)", "Daily shift log per Employee"],
        ["LeaveRequest", "employee (FK), leave_type (Enum), days_count (Int), status (Enum: Pending/Approved/Rejected)", "Workflow state per Employee"]
    ]
    db_table = Table(db_schema_data, colWidths=[110, 240, 150])
    db_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#334155')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(db_table)
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>4.4 MODULE DESCRIPTION (4 ROLES &amp; 9 EMPLOYEE MODULES)</b>", h2_style))
    story.append(Paragraph("<b>Level 1: HR Executive / Admin Portal:</b> Manages company-wide workforce intelligence, departmental budget governance, salary equity regression audits, and systemic burnout flags.", bullet_style))
    story.append(Paragraph("<b>Level 2: Department Manager Portal:</b> Oversees multi-team operational velocity, departmental attendance rates, and budget allocations.", bullet_style))
    story.append(Paragraph("<b>Level 3: Team Manager Portal:</b> Directly assigns deliverables to specialized teams, reviews daily shift attendance logs, and approves or rejects leave requests.", bullet_style))
    story.append(Paragraph("<b>Level 4: The 9 Comprehensive Employee Modules:</b>", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;1. <i>Dashboard:</i> Daily overview of work, live IST shift clock, active deliverables, and operational KPIs.", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;2. <i>Profile:</i> Personal credentials, team hierarchy, job title, and verified skill matrix.", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;3. <i>Tasks:</i> Assigned tasks with complexity weights, progress tracking, and deadline indicators.", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;4. <i>Task Updates:</i> Interactive progress update interface with completion confirmation.", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;5. <i>Attendance:</i> Live biometric terminal locked to Indian Standard Time with automatic shift duration.", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;6. <i>Leaves:</i> Leave balance tracking (12 Casual, 7 Sick, 15 Earned) and request history.", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;7. <i>Performance:</i> Quarterly managerial ratings, reviewer feedback, and leadership evaluations.", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;8. <i>Salary &amp; Payslip:</i> Transparent compensation summary, statutory deductions, and downloadable PDF payslips.", bullet_style))
    story.append(Paragraph("&nbsp;&nbsp;9. <i>Career Growth:</i> AI skill-gap analyzer matching current competencies to target promotion positions.", bullet_style))
    story.append(PageBreak())

    # =========================================================
    # CHAPTER 5: SYSTEM IMPLEMENTATION AND TESTING
    # =========================================================
    story.append(Paragraph("<b>5. SYSTEM IMPLEMENTATION AND TESTING</b>", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

    story.append(Paragraph("<b>5.1 SYSTEM IMPLEMENTATION</b>", h2_style))
    story.append(Paragraph(
        "CareerEquity AI was implemented following the modern <b>Django Model-View-Template (MVT)</b> paradigm, ensuring clean "
        "separation between presentation, application logic, and database entities. Key implementation pillars include:", body_style
    ))
    story.append(Paragraph("• <b>Machine Learning Integration:</b> Built within <code>Alpha/ml_engine/</code>, the AI components operate as pure Python classes using Scikit-learn and NumPy. The regression engine fits an empirical salary curve on historical enterprise profiles, comparing actual compensation against predicted parity to flag discrepancies exceeding 10%.", bullet_style))
    story.append(Paragraph("• <b>Timezone Localization:</b> Implemented by setting <code>TIME_ZONE = 'Asia/Kolkata'</code> and <code>USE_TZ = True</code> in <code>settings.py</code>. All server calculations evaluate via <code>timezone.localtime()</code>, while the client attendance terminal features a live JavaScript clock ticking in Indian Standard Time.", bullet_style))
    story.append(Paragraph("• <b>Defensive CSRF &amp; Double-Click Shield:</b> Forms incorporate Django's cryptographic <code>csrf_token</code>. Furthermore, client-side submit buttons automatically disable and display <code>Signing In... ⏳</code> upon first click, completely preventing duplicate HTTP POST requests.", bullet_style))

    story.append(Paragraph("<b>5.2 SYSTEM TESTING</b>", h2_style))
    story.append(Paragraph(
        "A rigorous multi-stage testing methodology was conducted to ensure system stability, security, and algorithmic accuracy. "
        "The test suite encompassed five formal tiers:", body_style
    ))
    story.append(Paragraph("<b>5.2.1 TYPES OF TESTING</b>", h3_style))
    story.append(Paragraph("1. <b>Unit Testing:</b> Verified individual model methods, duration calculations in <code>api_check_out</code>, and mathematical scoring functions in <code>WorkloadAnalyzer</code>.", bullet_style))
    story.append(Paragraph("2. <b>Integration Testing:</b> Validated end-to-end data flow between HTTP form POSTs, database transactions, session authentication cookies, and view template renders.", bullet_style))
    story.append(Paragraph("3. <b>Security &amp; CSRF Verification Testing:</b> Tested rapid double-submissions, expired cookies, and cross-site requests to confirm the custom CSRF failure handler safely redirects to the dashboard without crashing.", bullet_style))
    story.append(Paragraph("4. <b>Timezone Accuracy Testing:</b> Validated that punch-in at 09:15 AM and punch-out at 11:10 AM correctly logged 1.93 hours in IST rather than clamping to zero hours.", bullet_style))
    story.append(Paragraph("5. <b>User Acceptance Testing (UAT):</b> Demonstrated role-switching between HR Admin, Department Manager, Team Manager, and Employee to ensure zero unauthorized privilege escalation.", bullet_style))

    story.append(Spacer(1, 6))
    story.append(Paragraph("<b>Test Cases Execution Summary Table:</b>", h3_style))
    test_cases_data = [
        [Paragraph("<b>Test Case ID</b>", body_style), Paragraph("<b>Test Description</b>", body_style), Paragraph("<b>Expected Result</b>", body_style), Paragraph("<b>Status</b>", body_style)],
        ["TC-01", "User Login with valid credentials", "Redirects to appropriate role dashboard", "PASSED"],
        ["TC-02", "Rapid double-click on Sign In button", "Submit button disables; duplicate POST blocked", "PASSED"],
        ["TC-03", "Punch-in on Attendance Terminal", "Records current IST time; sets status to Present", "PASSED"],
        ["TC-04", "Punch-out on Attendance Terminal", "Calculates elapsed IST shift hours accurately", "PASSED"],
        ["TC-05", "Task assignment exceeding capacity", "AI triggers burnout risk badge (>75%)", "PASSED"],
        ["TC-06", "Salary audit with 15% pay gap", "Flags employee under Disparity Review", "PASSED"],
        ["TC-07", "Leave request submission & approval", "Deducts casual leave; notifies employee", "PASSED"]
    ]
    tc_table = Table(test_cases_data, colWidths=[65, 170, 205, 60])
    tc_table.setStyle(TableStyle([
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor('#334155')),
        ('INNERGRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f1f5f9')),
        ('TEXTCOLOR', (3,1), (3,-1), colors.HexColor('#15803d')),
        ('FONTNAME', (3,1), (3,-1), 'Helvetica-Bold'),
        ('PADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(tc_table)
    story.append(PageBreak())

    # =========================================================
    # CHAPTER 6: CONCLUSION & FUTURE SCOPE
    # =========================================================
    story.append(Paragraph("<b>6. CONCLUSION</b>", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

    conc_p1 = (
        "<b>CareerEquity AI</b> successfully demonstrates that modern human resource administration can transcend "
        "passive transactional record-keeping to become an active, fair, and predictive operational command center. "
        "By synthesizing a robust four-level Role-Based Access Control architecture with explainable machine learning "
        "algorithms, the system provides practical, deployable solutions to two of the most damaging workplace problems: "
        "unconscious compensation disparity and unmonitored employee burnout."
    )
    story.append(Paragraph(conc_p1, body_style))

    conc_p2 = (
        "The project rigorously fulfills every functional and academic objective established for the Bachelor of Computer "
        "Applications curriculum. The platform features 72 realistic employee records distributed across 8 functional "
        "departments and 16 specialized teams. The implementation of precision Indian Standard Time (Asia/Kolkata) guarantees "
        "flawless shift logging, while the 9 comprehensive employee modules deliver total transparency in tasks, leaves, "
        "evaluations, payslips, and career growth."
    )
    story.append(Paragraph(conc_p2, body_style))

    story.append(Paragraph("<b>FUTURE ENHANCEMENTS:</b>", h2_style))
    story.append(Paragraph("• <b>Multi-Tenant SaaS Architecture:</b> Extend the database schemas to support isolated corporate tenants under a single cloud deployment.", bullet_style))
    story.append(Paragraph("• <b>Automated Payroll Bank API Integration:</b> Connect salary disbursement modules directly with institutional banking gateways (e.g. RazorpayX, NEFT/RTGS).", bullet_style))
    story.append(Paragraph("• <b>Natural Language Processing (NLP) for Feedback:</b> Incorporate sentiment analysis on peer reviews to detect toxic team dynamics and unrecognized contributions.", bullet_style))
    story.append(Paragraph("• <b>Mobile Native Applications:</b> Build native Android and iOS mobile applications utilizing geofenced GPS biometric punches for remote and field staff.", bullet_style))
    story.append(PageBreak())

    # =========================================================
    # CHAPTER 7: BIBLIOGRAPHY & REFERENCES
    # =========================================================
    story.append(Paragraph("<b>7. BIBLIOGRAPHY</b>", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

    bib_items = [
        "1. <b>Pedregosa, F., et al.</b> (2011). <i>Scikit-learn: Machine Learning in Python</i>. Journal of Machine Learning Research, 12, 2825-2830.",
        "2. <b>Django Software Foundation.</b> (2024). <i>Django Documentation (Version 4.2 LTS)</i>. Retrieved from https://docs.djangoproject.com/en/4.2/",
        "3. <b>Python Software Foundation.</b> (2024). <i>Python Language Reference (Version 3.12)</i>. Retrieved from https://www.python.org/",
        "4. <b>Chodorow, K.</b> (2013). <i>Database Systems Design, Implementation, and Management</i>. Cengage Learning, 11th Edition.",
        "5. <b>Maslach, C., &amp; Leiter, M. P.</b> (2016). <i>Understanding the burnout experience: recent research and its implications for psychiatry</i>. World Psychiatry, 15(2), 103-111.",
        "6. <b>Barocas, S., Hardt, M., &amp; Narayanan, A.</b> (2019). <i>Fairness and Machine Learning: Limitations and Opportunities</i>. MIT Press.",
        "7. <b>Sommerville, I.</b> (2016). <i>Software Engineering</i>. Pearson Education, 10th Global Edition.",
        "8. <b>Pressman, R. S.</b> (2014). <i>Software Engineering: A Practitioner's Approach</i>. McGraw-Hill Education, 8th Edition.",
        "9. <b>University of Calicut.</b> (2023). <i>Regulations and Syllabus for Bachelor of Computer Applications (BCA) Programme</i>. University of Calicut Press.",
        "10. <b>Mozilla Developer Network (MDN).</b> (2024). <i>Web Security: Cross-Site Request Forgery (CSRF) Prevention</i>. Retrieved from https://developer.mozilla.org/"
    ]
    for b in bib_items:
        story.append(Paragraph(b, body_style))
        story.append(Spacer(1, 4))
    story.append(PageBreak())

    # =========================================================
    # CHAPTER 8: SYSTEM DIAGRAMS
    # =========================================================
    story.append(Paragraph("<b>8. SYSTEM DIAGRAMS</b>", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=10))

    diag_intro = (
        "This chapter presents the formal architectural, procedural, and object-oriented diagrams describing the structure, "
        "data flows, interactions, and evaluation metrics of CareerEquity AI. Every diagram follows standard software engineering "
        "specifications and is accompanied by an analytical description."
    )
    story.append(Paragraph(diag_intro, body_style))
    story.append(Spacer(1, 8))

    # 8.1 System Architecture
    story.append(Paragraph("<b>8.1 SYSTEM ARCHITECTURE DIAGRAM</b>", h2_style))
    story.append(Paragraph(
        "The system architecture follows a clean 4-tier model comprising the Client Presentation Tier, the Django Application "
        "Server Tier, the Machine Learning Analytics Engine, and the SQLite3 Relational Persistence Tier.", body_style
    ))
    arch_img = "report_assets/diagrams/fig_8_1_architecture.png"
    if os.path.exists(arch_img):
        story.append(Image(arch_img, width=470, height=310))
        story.append(Paragraph("<b>Fig 8.1: System Architecture Diagram</b>", caption_style))
    story.append(PageBreak())

    # 8.2 Use Case Diagram
    story.append(Paragraph("<b>8.2 USE CASE DIAGRAM</b>", h2_style))
    story.append(Paragraph(
        "The use case diagram illustrates the functional boundaries of the system and the interactions between the four primary "
        "actors (HR Admin, Department Manager, Team Manager, and Employee) and system functions.", body_style
    ))
    uc_img = "report_assets/diagrams/fig_8_2_use_case.png"
    if os.path.exists(uc_img):
        story.append(Image(uc_img, width=460, height=330))
        story.append(Paragraph("<b>Fig 8.2: Use Case Diagram</b>", caption_style))
    story.append(PageBreak())

    # 8.3 Data Flow Diagrams
    story.append(Paragraph("<b>8.3 DATA FLOW DIAGRAMS (DFD)</b>", h2_style))
    story.append(Paragraph("<b>8.3.1 DFD LEVEL 0 (CONTEXT DIAGRAM)</b>", h3_style))
    story.append(Paragraph(
        "The Level 0 context diagram models CareerEquity AI as a singular unified process interacting with external enterprise "
        "actors, highlighting core inbound credentials/tasks and outbound analytics/payslips.", body_style
    ))
    dfd0_img = "report_assets/diagrams/fig_8_3_dfd_0.png"
    if os.path.exists(dfd0_img):
        story.append(Image(dfd0_img, width=450, height=300))
        story.append(Paragraph("<b>Fig 8.3: DFD Level 0 (Context Diagram)</b>", caption_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>8.3.2 DFD LEVEL 1</b>", h3_style))
    story.append(Paragraph(
        "Level 1 decomposes the context process into 6 primary operational modules and shows interactions with the 5 core "
        "data stores (Users, Teams, Tasks, Attendance, and Salaries).", body_style
    ))
    dfd1_img = "report_assets/diagrams/fig_8_4_dfd_1.png"
    if os.path.exists(dfd1_img):
        story.append(Image(dfd1_img, width=460, height=320))
        story.append(Paragraph("<b>Fig 8.4: DFD Level 1 (Modular Subsystems)</b>", caption_style))
    story.append(PageBreak())

    # 8.3.3 & 8.3.4 DFD 2 & DFD 3
    story.append(Paragraph("<b>8.3.3 DFD LEVEL 2</b>", h3_style))
    story.append(Paragraph(
        "Level 2 expands Process 3.0 (Task Management) and Process 5.0 (AI Burnout Evaluation), tracing task complexity weights "
        "and weekly hour aggregations.", body_style
    ))
    dfd2_img = "report_assets/diagrams/fig_8_5_dfd_2.png"
    if os.path.exists(dfd2_img):
        story.append(Image(dfd2_img, width=440, height=260))
        story.append(Paragraph("<b>Fig 8.5: DFD Level 2 (Task Assignment &amp; Workload Burnout)</b>", caption_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>8.3.4 DFD LEVEL 3</b>", h3_style))
    story.append(Paragraph(
        "Level 3 details Process 6.0 (AI Salary Equity Modeling), illustrating feature vector assembly, regression inference, "
        "disparity margin checking, and HR alert dispatching.", body_style
    ))
    dfd3_img = "report_assets/diagrams/fig_8_5b_dfd_3.png"
    if os.path.exists(dfd3_img):
        story.append(Image(dfd3_img, width=440, height=260))
        story.append(Paragraph("<b>Fig 8.5(b): DFD Level 3 (AI Salary Regression &amp; Disparity Engine)</b>", caption_style))
    story.append(PageBreak())

    # 8.4 ER Diagram
    story.append(Paragraph("<b>8.4 ENTITY RELATIONSHIP (ER) DIAGRAM</b>", h2_style))
    story.append(Paragraph(
        "The Entity-Relationship diagram maps out relational cardinality (1:1, 1:N, M:N) across user profiles, organizational "
        "units, task assignments, and shift attendance records.", body_style
    ))
    er_img = "report_assets/diagrams/fig_8_6_er_diagram.png"
    if os.path.exists(er_img):
        story.append(Image(er_img, width=470, height=320))
        story.append(Paragraph("<b>Fig 8.6: Entity Relationship (ER) Diagram</b>", caption_style))
    story.append(PageBreak())

    # 8.5 Class Diagram
    story.append(Paragraph("<b>8.5 CLASS DIAGRAM</b>", h2_style))
    story.append(Paragraph(
        "The UML Class diagram specifies Django models and Machine Learning service classes, showcasing encapsulation of "
        "attributes, member data types, and method signatures.", body_style
    ))
    class_img = "report_assets/diagrams/fig_8_7_class_diagram.png"
    if os.path.exists(class_img):
        story.append(Image(class_img, width=460, height=330))
        story.append(Paragraph("<b>Fig 8.7: UML Class Diagram</b>", caption_style))
    story.append(PageBreak())

    # 8.6 Sequence Diagram
    story.append(Paragraph("<b>8.6 SEQUENCE DIAGRAM</b>", h2_style))
    story.append(Paragraph(
        "The Sequence diagram chronicles time-ordered message passing during a live biometric shift punch-out in Indian Standard Time (IST), "
        "highlighting automatic elapsed hour computation.", body_style
    ))
    seq_img = "report_assets/diagrams/fig_8_8_sequence_diagram.png"
    if os.path.exists(seq_img):
        story.append(Image(seq_img, width=460, height=310))
        story.append(Paragraph("<b>Fig 8.8: Sequence Diagram (IST Biometric Punch)</b>", caption_style))
    story.append(PageBreak())

    # 8.7 Activity Diagram
    story.append(Paragraph("<b>8.7 ACTIVITY DIAGRAM</b>", h2_style))
    story.append(Paragraph(
        "The Activity workflow diagram diagrams the procedural lifecycle of a task assignment, illustrating decision branches "
        "when employee workload score exceeds the safe 75% threshold.", body_style
    ))
    act_img = "report_assets/diagrams/fig_8_9_activity_diagram.png"
    if os.path.exists(act_img):
        story.append(Image(act_img, width=390, height=410))
        story.append(Paragraph("<b>Fig 8.9: Activity Workflow Diagram</b>", caption_style))
    story.append(PageBreak())

    # 8.8 Model Evaluation Diagram
    story.append(Paragraph("<b>8.8 MODEL EVALUATION DIAGRAM</b>", h2_style))
    story.append(Paragraph(
        "The Model Evaluation diagram presents the empirical parity scatter plot (Actual vs. Predicted Salary) alongside "
        "comparative validation benchmarks (R² Score and MAE) across evaluated regression algorithms.", body_style
    ))
    eval_img = "report_assets/diagrams/fig_8_10_evaluation.png"
    if os.path.exists(eval_img):
        story.append(Image(eval_img, width=470, height=225))
        story.append(Paragraph("<b>Fig 8.10: AI Model Evaluation &amp; Algorithmic Benchmark Diagram</b>", caption_style))
    story.append(PageBreak())

    # =========================================================
    # CHAPTER 9: SAMPLE SCREENSHOTS
    # =========================================================
    story.append(Paragraph("<b>9. SAMPLE SCREENSHOTS</b>", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

    story.append(Paragraph("<b>Sample 1: HR Workforce Intelligence Dashboard</b>", h2_style))
    story.append(Paragraph(
        "The executive command center provides real-time organizational KPIs: 72 active personnel, 8 structured departments, "
        "live workload burnout alerts, and salary equity audit findings.", body_style
    ))
    s1 = "report_assets/screenshots/screenshot_hr_dashboard.jpg"
    if os.path.exists(s1):
        story.append(Image(s1, width=460, height=230))
        story.append(Paragraph("<b>Screenshot 1: Executive HR Workforce Intelligence Portal</b>", caption_style))
    story.append(Spacer(1, 10))

    story.append(Paragraph("<b>Sample 2: Team Task Assignment &amp; Workload Distribution</b>", h2_style))
    story.append(Paragraph(
        "Allows managers to distribute deliverables directly to specialized teams with calibrated complexity ratings and hours, "
        "preventing individual bottlenecking.", body_style
    ))
    s2 = "report_assets/screenshots/screenshot_task_assignment.jpg"
    if os.path.exists(s2):
        story.append(Image(s2, width=460, height=230))
        story.append(Paragraph("<b>Screenshot 2: Team-Level Task Distribution Interface</b>", caption_style))
    story.append(PageBreak())

    story.append(Paragraph("<b>Sample 3: Employee Workspace &amp; Live Attendance Terminal (IST)</b>", h2_style))
    story.append(Paragraph(
        "Demonstrates the employee self-service hub featuring 9 operational modules and the live biometric shift clock operating "
        "in Indian Standard Time (Asia/Kolkata) with logged shift durations.", body_style
    ))
    s3 = "report_assets/screenshots/screenshot_employee_workspace.jpg"
    if os.path.exists(s3):
        story.append(Image(s3, width=460, height=230))
        story.append(Paragraph("<b>Screenshot 3: Employee Workspace with Live IST Attendance Punch</b>", caption_style))
    story.append(PageBreak())

    # =========================================================
    # CHAPTER 10: SOURCE CODE
    # =========================================================
    story.append(Paragraph("<b>10. SOURCE CODE</b>", h1_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#0284c7'), spaceAfter=12))

    story.append(Paragraph(
        "This chapter includes authoritative, production-tested source code excerpts demonstrating the core algorithms, "
        "models, controllers, and security defenses implemented in CareerEquity AI.", body_style
    ))

    story.append(Paragraph("<b>10.1 CORE ATTENDANCE &amp; CSRF DEFENSIVE CONTROLLER (Alpha/views.py)</b>", h2_style))
    code_views = (
        "@login_required\n"
        "def api_check_out(request):\n"
        "    if request.method == 'POST':\n"
        "        employee = EmployeeProfile.objects.filter(user=request.user).first()\n"
        "        today = timezone.localdate()\n"
        "        rec = AttendanceRecord.objects.filter(employee=employee, date=today).first()\n"
        "        if rec and rec.check_in:\n"
        "            now_local = timezone.localtime()\n"
        "            rec.check_out = now_local.time()\n"
        "            # Calculate exact elapsed shift hours in Indian Standard Time\n"
        "            checkin_dt = datetime.combine(today, rec.check_in)\n"
        "            checkout_dt = datetime.combine(today, rec.check_out)\n"
        "            duration = (checkout_dt - checkin_dt).total_seconds() / 3600.0\n"
        "            rec.working_hours = Decimal(f\"{max(0.0, duration):.2f}\")\n"
        "            rec.save()\n"
        "            messages.success(request, f'Checked out at {now_local.strftime(\"%I:%M %p\")} IST ({rec.working_hours} hrs)!')\n"
        "    return redirect(request.META.get('HTTP_REFERER', 'employee_attendance'))\n\n"
        "def custom_csrf_failure_view(request, reason=''):\n"
        "    # Gracefully prevents 403 Forbidden on rapid double-clicks or token rotation\n"
        "    if getattr(request, 'user', None) and request.user.is_authenticated:\n"
        "        return redirect('dashboard')\n"
        "    session = getattr(request, 'session', None)\n"
        "    if session and '_auth_user_id' in session:\n"
        "        return redirect('dashboard')\n"
        "    return redirect('login_page')"
    )
    story.append(Paragraph(code_views.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))

    story.append(Paragraph("<b>10.2 AI WORKLOAD BURNOUT ANALYZER (Alpha/ml_engine/workload_model.py)</b>", h2_style))
    code_ml = (
        "class WorkloadAnalyzer:\n"
        "    WEIGHTS = {'Low': 1.0, 'Medium': 1.5, 'High': 2.0, 'Critical': 3.0}\n"
        "    @classmethod\n"
        "    def analyze_employee(cls, employee):\n"
        "        active_assignments = employee.assignments.filter(status__in=['Pending', 'In Progress'])\n"
        "        total_weighted_hours = sum(\n"
        "            float(a.task.estimated_hours) * cls.WEIGHTS.get(a.task.complexity, 1.5)\n"
        "            for a in active_assignments\n"
        "        )\n"
        "        overdue_count = sum(1 for a in active_assignments if a.task.deadline < timezone.localdate())\n"
        "        # Composite Workload Score (0 to 100)\n"
        "        workload_score = min(100.0, (total_weighted_hours / 40.0) * 70.0 + (overdue_count * 15.0))\n"
        "        is_burnout_risk = workload_score >= 75.0\n"
        "        return {\n"
        "            'workload_score': round(workload_score, 1),\n"
        "            'is_burnout_risk': is_burnout_risk,\n"
        "            'workload_level': 'Overloaded' if is_burnout_risk else 'Balanced'\n"
        "        }"
    )
    story.append(Paragraph(code_ml.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))

    story.append(Paragraph("<b>10.3 TIMEZONE SETTINGS CONFIGURATION (CAREEREQUITY/settings.py)</b>", h2_style))
    code_settings = (
        "# Internationalization & Indian Standard Time\n"
        "LANGUAGE_CODE = 'en-us'\n"
        "TIME_ZONE = 'Asia/Kolkata'  # Locked to Indian Standard Time (UTC+05:30)\n"
        "USE_I18N = True\n"
        "USE_TZ = True\n\n"
        "# CSRF & Security Failure Handler\n"
        "CSRF_TRUSTED_ORIGINS = ['http://127.0.0.1:8000', 'http://localhost:8000']\n"
        "CSRF_FAILURE_VIEW = 'Alpha.views.custom_csrf_failure_view'"
    )
    story.append(Paragraph(code_settings.replace("\n", "<br/>").replace(" ", "&nbsp;"), code_style))

    # Build Document with NumberedCanvas
    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"Report PDF built successfully: {PDF_FILENAME}")

if __name__ == '__main__':
    create_report_pdf()

