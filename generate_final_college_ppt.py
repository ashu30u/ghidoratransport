import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def build_synopsis_aligned_presentation():
    prs = Presentation()
    # 16:9 Widescreen Layout (13.333" x 7.5")
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # Professional Academic Color Palette
    NAVY = RGBColor(15, 23, 42)          # Deep Slate Navy (#0F172A)
    PRIMARY = RGBColor(30, 58, 138)      # Royal Navy Blue (#1E3A8A)
    ACCENT_BLUE = RGBColor(37, 99, 235)  # Vibrant Blue (#2563EB)
    ACCENT_GOLD = RGBColor(217, 119, 6)  # Warm Amber Gold (#D97706)
    BG_LIGHT = RGBColor(248, 250, 252)   # Slate 50 (#F8FAFC)
    CARD_BG = RGBColor(255, 255, 255)    # White
    CARD_BORDER = RGBColor(226, 232, 240)# Slate 200
    TEXT_DARK = RGBColor(15, 23, 42)     # Slate 900
    TEXT_MUTED = RGBColor(100, 116, 139) # Slate 500
    TEXT_LIGHT = RGBColor(203, 213, 225) # Slate 300
    WHITE = RGBColor(255, 255, 255)
    GREEN = RGBColor(16, 185, 129)       # Emerald Green
    PURPLE = RGBColor(126, 34, 206)      # Violet

    def set_background(slide, color=BG_LIGHT):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, section_tag="GHIDORA TRANSPORT | MINOR PROJECT PRESENTATION"):
        # Top Gold Accent Line
        accent = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
        accent.fill.solid()
        accent.fill.fore_color.rgb = ACCENT_GOLD
        accent.line.fill.background()

        # Dark Banner
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0.12), Inches(13.333), Inches(1.12))
        banner.fill.solid()
        banner.fill.fore_color.rgb = NAVY
        banner.line.fill.background()

        # Section Tag
        tag_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.2), Inches(9.0), Inches(0.3))
        tag_tf = tag_box.text_frame
        tag_tf.word_wrap = True
        p_tag = tag_tf.paragraphs[0]
        p_tag.text = section_tag.upper()
        p_tag.font.size = Pt(10)
        p_tag.font.bold = True
        p_tag.font.color.rgb = ACCENT_GOLD

        # Slide Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.48), Inches(9.5), Inches(0.65))
        title_tf = title_box.text_frame
        title_tf.word_wrap = True
        p_title = title_tf.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(21)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE

        # Right Academic Tag
        uni_box = slide.shapes.add_textbox(Inches(10.0), Inches(0.32), Inches(2.6), Inches(0.65))
        uni_tf = uni_box.text_frame
        p_uni = uni_tf.paragraphs[0]
        p_uni.text = "SSPU BHILAI\nMCA DEPARTMENT"
        p_uni.alignment = PP_ALIGN.RIGHT
        p_uni.font.size = Pt(10.5)
        p_uni.font.bold = True
        p_uni.font.color.rgb = RGBColor(148, 163, 184)

        # Bottom Academic Footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.15), Inches(11.733), Inches(0.3))
        ftf = footer_box.text_frame
        p_f = ftf.paragraphs[0]
        p_f.text = "Ghidora Transport | Online Booking Transport Platform | Amit Kumar Sahu (2526002003) & Raag Patel (2526002048) | Guide: Ms. Divya Jaiswal"
        p_f.font.size = Pt(8.5)
        p_f.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER, border_width=1.5):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(border_width)
        return card

    # =========================================================================
    # SLIDE 1: COVER / TITLE SLIDE (From Synopsis Cover Page)
    # =========================================================================
    slide1 = prs.slides.add_slide(blank_layout)
    set_background(slide1, NAVY)

    # Accent bar
    top_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.15))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = ACCENT_GOLD
    top_bar.line.fill.background()

    # Main Title Area
    tbox1 = slide1.shapes.add_textbox(Inches(0.8), Inches(0.85), Inches(11.733), Inches(2.5))
    ttf1 = tbox1.text_frame
    ttf1.word_wrap = True

    p0 = ttf1.paragraphs[0]
    p0.text = "SHRI SHANKARACHARYA PROFESSIONAL UNIVERSITY, BHILAI"
    p0.font.size = Pt(13.5)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_GOLD

    p1 = ttf1.add_paragraph()
    p1.text = "MINOR PROJECT PRESENTATION"
    p1.font.size = Pt(15)
    p1.font.bold = True
    p1.font.color.rgb = RGBColor(191, 219, 254)
    p1.space_before = Pt(4)

    p2 = ttf1.add_paragraph()
    p2.text = "GHIDORA TRANSPORT"
    p2.font.size = Pt(44)
    p2.font.bold = True
    p2.font.color.rgb = WHITE
    p2.space_before = Pt(6)

    p3 = ttf1.add_paragraph()
    p3.text = "Project Title: Online Booking Transport Platform"
    p3.font.size = Pt(18)
    p3.font.color.rgb = RGBColor(226, 232, 240)
    p3.space_before = Pt(4)

    # 3 Info Cards on Title Slide: Students, Guide, University
    card_w = Inches(3.64)
    card_h = Inches(3.0)
    
    # Card 1: Submitted By (Both Students from Synopsis)
    add_card(slide1, Inches(0.8), Inches(3.7), card_w, card_h, bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    sbox = slide1.shapes.add_textbox(Inches(1.0), Inches(3.85), Inches(3.24), Inches(2.7))
    stf = sbox.text_frame
    stf.word_wrap = True

    ps0 = stf.paragraphs[0]
    ps0.text = "SUBMITTED BY:"
    ps0.font.size = Pt(11)
    ps0.font.bold = True
    ps0.font.color.rgb = ACCENT_GOLD

    ps1 = stf.add_paragraph()
    ps1.text = "AMIT KUMAR SAHU"
    ps1.font.size = Pt(16)
    ps1.font.bold = True
    ps1.font.color.rgb = WHITE
    ps1.space_before = Pt(6)

    ps1_r = stf.add_paragraph()
    ps1_r.text = "Roll Number: 2526002003"
    ps1_r.font.size = Pt(11.5)
    ps1_r.font.color.rgb = TEXT_LIGHT

    ps2 = stf.add_paragraph()
    ps2.text = "RAAG PATEL"
    ps2.font.size = Pt(16)
    ps2.font.bold = True
    ps2.font.color.rgb = WHITE
    ps2.space_before = Pt(8)

    ps2_r = stf.add_paragraph()
    ps2_r.text = "Roll Number: 2526002048"
    ps2_r.font.size = Pt(11.5)
    ps2_r.font.color.rgb = TEXT_LIGHT

    # Card 2: Guided By
    add_card(slide1, Inches(4.84), Inches(3.7), card_w, card_h, bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    gbox = slide1.shapes.add_textbox(Inches(5.04), Inches(3.85), Inches(3.24), Inches(2.7))
    gtf = gbox.text_frame
    gtf.word_wrap = True

    pg0 = gtf.paragraphs[0]
    pg0.text = "UNDER THE GUIDANCE OF:"
    pg0.font.size = Pt(11)
    pg0.font.bold = True
    pg0.font.color.rgb = ACCENT_GOLD

    pg1 = gtf.add_paragraph()
    pg1.text = "MS. DIVYA JAISWAL"
    pg1.font.size = Pt(17)
    pg1.font.bold = True
    pg1.font.color.rgb = WHITE
    pg1.space_before = Pt(6)

    pg2 = gtf.add_paragraph()
    pg2.text = "Assistant Professor / Faculty\nDepartment of Computer Applications\nShri Shankaracharya Professional University (SSPU)"
    pg2.font.size = Pt(12)
    pg2.font.color.rgb = TEXT_LIGHT
    pg2.space_before = Pt(8)

    # Card 3: Department & University
    add_card(slide1, Inches(8.88), Inches(3.7), card_w, card_h, bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    ubox = slide1.shapes.add_textbox(Inches(9.08), Inches(3.85), Inches(3.24), Inches(2.7))
    utf = ubox.text_frame
    utf.word_wrap = True

    pu0 = utf.paragraphs[0]
    pu0.text = "INSTITUTION:"
    pu0.font.size = Pt(11)
    pu0.font.bold = True
    pu0.font.color.rgb = ACCENT_GOLD

    pu1 = utf.add_paragraph()
    pu1.text = "Shri Shankaracharya Professional University"
    pu1.font.size = Pt(15.5)
    pu1.font.bold = True
    pu1.font.color.rgb = WHITE
    pu1.space_before = Pt(6)

    pu2 = utf.add_paragraph()
    pu2.text = "Bhilai (C.G.), India\nDepartment of Computer Applications\nAcademic Session: 2025 - 2026"
    pu2.font.size = Pt(12)
    pu2.font.color.rgb = TEXT_LIGHT
    pu2.space_before = Pt(8)

    slide1.notes_slide.notes_text_frame.text = (
        "Good morning respected guide Ms. Divya Jaiswal ma'am, faculty members, and external examiners. "
        "We, Amit Kumar Sahu (Roll No: 2526002003) and Raag Patel (Roll No: 2526002048), from the Department of Computer Applications, "
        "Shri Shankaracharya Professional University, Bhilai, present our Minor Project titled 'Online Booking Transport Platform' - Ghidora Transport."
    )

    # =========================================================================
    # SLIDE 2: PRESENTATION AGENDA / OUTLINE (Exact Requested Order)
    # =========================================================================
    slide2 = prs.slides.add_slide(blank_layout)
    set_background(slide2)
    add_header(slide2, "Presentation Outline & Structure")

    agenda_cards = [
        ("01. INTRODUCTION", [
            "Project Title & Name",
            "Project Overview & Purpose",
            "Problem Solving Statement",
            "Aims & Core Objectives"
        ], PRIMARY),
        ("02. H/W & S/W REQUIREMENTS", [
            "Hardware Component Table",
            "Software & Tech Stack Table",
            "Python, Django & SQLite",
            "Render Cloud Deployment"
        ], ACCENT_BLUE),
        ("03. SYSTEM DESIGN", [
            "Form Design (UI/UX Architecture)",
            "Database Design (Relational Schema)",
            "Entity-Relationship (ER) Diagram",
            "DFD Level 0 & Level 1 Diagrams"
        ], NAVY),
        ("04. PROJECT METHODOLOGY", [
            "Agile Development Methodology",
            "5-Phase Execution Lifecycle",
            "Testing & Quality Assurance",
            "Future Scope & Conclusion"
        ], ACCENT_GOLD)
    ]

    col_positions = [Inches(0.8), Inches(3.8), Inches(6.8), Inches(9.8)]
    for i, (col_title, items, col) in enumerate(agenda_cards):
        cx = col_positions[i]
        add_card(slide2, cx, Inches(1.6), Inches(2.7), Inches(5.1))
        
        # Color bar on top
        top_c = slide2.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(1.6), Inches(2.7), Inches(0.12))
        top_c.fill.solid()
        top_c.fill.fore_color.rgb = col
        top_c.line.fill.background()

        abox = slide2.shapes.add_textbox(cx + Inches(0.15), Inches(1.85), Inches(2.4), Inches(4.6))
        atf = abox.text_frame
        atf.word_wrap = True

        ap0 = atf.paragraphs[0]
        ap0.text = col_title
        ap0.font.size = Pt(13)
        ap0.font.bold = True
        ap0.font.color.rgb = col

        for item in items:
            api = atf.add_paragraph()
            api.text = f"• {item}"
            api.font.size = Pt(11.5)
            api.font.color.rgb = TEXT_DARK
            api.space_before = Pt(12)

    slide2.notes_slide.notes_text_frame.text = (
        "Here is the outline of our presentation, structured exactly as required: "
        "Section 1 covers Introduction, Purpose, Problem Solving Statement, and Objectives. "
        "Section 2 covers the Hardware and Software Requirements as per our synopsis. "
        "Section 3 covers Form Design, Database Design, ER-Diagram, and DFD Diagrams. "
        "Section 4 details our Project Methodology, Phased Lifecycle, Testing, Future Scope, and Conclusion."
    )

    # =========================================================================
    # SECTION 1: INTRODUCTION
    # SLIDE 3: INTRODUCTION & PURPOSE (Directly from Synopsis Sections 2 & 5)
    # =========================================================================
    slide3 = prs.slides.add_slide(blank_layout)
    set_background(slide3)
    add_header(slide3, "Introduction & Project Purpose", "SECTION 1: INTRODUCTION")

    # Left Card: Project Introduction (From Synopsis Section 2)
    add_card(slide3, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
    bar3_1 = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.7), Inches(0.12))
    bar3_1.fill.solid()
    bar3_1.fill.fore_color.rgb = PRIMARY
    bar3_1.line.fill.background()

    box3_1 = slide3.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.2), Inches(4.7))
    tf3_1 = box3_1.text_frame
    tf3_1.word_wrap = True

    p3_0 = tf3_1.paragraphs[0]
    p3_0.text = "PROJECT INTRODUCTION"
    p3_0.font.size = Pt(14)
    p3_0.font.bold = True
    p3_0.font.color.rgb = PRIMARY

    intro_bullets = [
        ("Web-Based Booking Platform", "Ghidora Transport is a web-based platform developed to make local transport booking simple, fast, and accessible for everyone."),
        ("Customer Vehicle Selection", "Provides an online way for customers to book a transport vehicle according to their specific requirements."),
        ("Easy Online Input", "Users can enter their name, contact details, pickup location, drop location, booking date, and vehicle type through a clean web form."),
        ("Automated Fare Calculation", "Provides instant fare calculation based on booking parameters, saving all booking information securely into a database."),
        ("Cross-Device Responsiveness", "Designed to be responsive so that users can access the booking services smoothly from desktop computers as well as mobile phones.")
    ]

    for title, desc in intro_bullets:
        pt = tf3_1.add_paragraph()
        pt.text = f"✔ {title}:"
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = ACCENT_BLUE
        pt.space_before = Pt(6)

        pd = tf3_1.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_DARK
        pd.space_before = Pt(1)

    # Right Card: Project Purpose (From Synopsis Section 5)
    add_card(slide3, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1))
    bar3_2 = slide3.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(0.12))
    bar3_2.fill.solid()
    bar3_2.fill.fore_color.rgb = ACCENT_GOLD
    bar3_2.line.fill.background()

    box3_2 = slide3.shapes.add_textbox(Inches(7.05), Inches(1.85), Inches(5.2), Inches(4.7))
    tf3_2 = box3_2.text_frame
    tf3_2.word_wrap = True

    pp0 = tf3_2.paragraphs[0]
    pp0.text = "CORE PROJECT PURPOSE"
    pp0.font.size = Pt(14)
    pp0.font.bold = True
    pp0.font.color.rgb = ACCENT_GOLD

    purpose_bullets = [
        ("Simplifying Local Bookings", "The main purpose of Ghidora Transport is to make local transport booking easier and hassle-free for customers."),
        ("Overcoming Phone Call Bottlenecks", "Many local transport services depend on phone calls and manual communication, requiring customers to repeatedly ask about rates and vehicles."),
        ("Single Unified Digital Portal", "Ghidora Transport provides all basic services through a single website where customers enter requirements and submit requests online."),
        ("Digital Record Management", "Helps in storing booking details digitally, making booking information easy to manage, audit, and retrieve at any time."),
        ("Affordable & Transparent", "Eliminates confusion and hidden charges by providing transparent fare estimation before booking confirmation.")
    ]

    for title, desc in purpose_bullets:
        ppt = tf3_2.add_paragraph()
        ppt.text = f"🎯 {title}:"
        ppt.font.size = Pt(11)
        ppt.font.bold = True
        ppt.font.color.rgb = PRIMARY
        ppt.space_before = Pt(6)

        ppd = tf3_2.add_paragraph()
        ppd.text = desc
        ppd.font.size = Pt(10)
        ppd.font.color.rgb = TEXT_DARK
        ppd.space_before = Pt(1)

    slide3.notes_slide.notes_text_frame.text = (
        "As stated in our synopsis, Ghidora Transport is an online transport booking platform built with Python and Django. "
        "Its primary purpose is to eliminate traditional manual phone-call bookings by offering an automated web application. "
        "Users can easily enter pickup and drop details, choose a vehicle, get instant fare calculation, and submit bookings from both computers and mobile phones."
    )

    # =========================================================================
    # SLIDE 4: PROBLEM SOLVING STATEMENT (From Synopsis Section 6)
    # =========================================================================
    slide4 = prs.slides.add_slide(blank_layout)
    set_background(slide4)
    add_header(slide4, "Problem Solving Statement", "SECTION 1: INTRODUCTION")

    # 2 Big Comparative Cards: The Problem vs The Ghidora Solution
    # Left: The Traditional Problem
    add_card(slide4, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
    p_bar1 = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.7), Inches(0.12))
    p_bar1.fill.solid()
    p_bar1.fill.fore_color.rgb = RGBColor(239, 68, 68) # Red
    p_bar1.line.fill.background()

    p_box1 = slide4.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.2), Inches(4.7))
    p_tf1 = p_box1.text_frame
    p_tf1.word_wrap = True

    pp1_0 = p_tf1.paragraphs[0]
    pp1_0.text = "THE TRADITIONAL PROBLEM"
    pp1_0.font.size = Pt(14)
    pp1_0.font.bold = True
    pp1_0.font.color.rgb = RGBColor(239, 68, 68)

    trad_points = [
        ("Manual Phone Dependency", "Customers usually have to call the transport provider or physically visit the stand to book a vehicle."),
        ("Repetitive Inquiries", "Customers must separately explain requirements, ask about vehicle availability, and repeatedly negotiate the fare."),
        ("Time-Consuming Process", "This traditional manual approach takes significant time, leading to delayed transport dispatch."),
        ("Improper Recordkeeping", "Booking information may not always be recorded properly, leading to lost entries and scheduling disputes.")
    ]

    for title, desc in trad_points:
        pt = p_tf1.add_paragraph()
        pt.text = f"❌ {title}:"
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = RGBColor(220, 38, 38)
        pt.space_before = Pt(8)

        pd = p_tf1.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_DARK
        pd.space_before = Pt(1)

    # Right: How Ghidora Transport Solves It
    add_card(slide4, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1))
    p_bar2 = slide4.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(0.12))
    p_bar2.fill.solid()
    p_bar2.fill.fore_color.rgb = GREEN
    p_bar2.line.fill.background()

    p_box2 = slide4.shapes.add_textbox(Inches(7.05), Inches(1.85), Inches(5.2), Inches(4.7))
    p_tf2 = p_box2.text_frame
    p_tf2.word_wrap = True

    pp2_0 = p_tf2.paragraphs[0]
    pp2_0.text = "THE GHIDORA TRANSPORT SOLUTION"
    pp2_0.font.size = Pt(14)
    pp2_0.font.bold = True
    pp2_0.font.color.rgb = GREEN

    sol_points = [
        ("Online Booking Solution", "Users visit the website and enter their travel details directly into an interactive booking form."),
        ("Instant Vehicle & Date Choice", "Allows users to select pickup & drop locations, choose required vehicle type, select date, and enter contact details."),
        ("Clear Fare Calculation", "Automatically calculates fare information upfront before the user submits the booking online."),
        ("Centralized SQLite Database", "All booking information is saved digitally in SQLite, making data instantly accessible, organized, and auditable.")
    ]

    for title, desc in sol_points:
        pt = p_tf2.add_paragraph()
        pt.text = f"✔ {title}:"
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = GREEN
        pt.space_before = Pt(8)

        pd = p_tf2.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_DARK
        pd.space_before = Pt(1)

    slide4.notes_slide.notes_text_frame.text = (
        "Our Problem Solving Statement directly tackles the traditional booking bottleneck. "
        "In traditional systems, customers have to call or visit physical offices, ask about fares repeatedly, and records are maintained on paper slips. "
        "Ghidora Transport provides an end-to-end digital solution: customers select vehicles online, calculate fares instantly, and all records are saved securely in our database."
    )

    # =========================================================================
    # SLIDE 5: OBJECTIVES OF THE PROJECT (All 11 Points from Synopsis Section 3)
    # =========================================================================
    slide5 = prs.slides.add_slide(blank_layout)
    set_background(slide5)
    add_header(slide5, "Objectives of the Project", "SECTION 1: INTRODUCTION")

    # 11 objectives laid out in two neat columns
    obj_left = [
        ("Online Booking Facility", "To provide an online transport booking facility accessible 24/7."),
        ("Simple & Easy Booking", "To make the booking process simple, intuitive, and user-friendly."),
        ("Suitable Vehicle Selection", "To allow users to select a suitable transport vehicle per their cargo needs."),
        ("Location Details Capture", "To collect precise pickup and drop location details smoothly."),
        ("Automated Fare Calculation", "To provide accurate fare calculation for the booking upfront."),
        ("Digital Database Storage", "To save all booking information securely in a structured database.")
    ]

    obj_right = [
        ("Reduce Manual Booking", "To reduce the need for manual, error-prone phone call bookings."),
        ("Save Time for Customers", "To save valuable time for customers and transporters alike."),
        ("User-Friendly Website", "To provide a clean, simple, and intuitive website interface."),
        ("Cross-Device Responsiveness", "To make the website responsive for both mobile and computer users."),
        ("Digital Transport Ecosystem", "To provide a modern, organized digital platform for local transport services.")
    ]

    # Left Column Card
    add_card(slide5, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
    obox_l = slide5.shapes.add_textbox(Inches(1.0), Inches(1.75), Inches(5.3), Inches(4.8))
    otf_l = obox_l.text_frame
    otf_l.word_wrap = True
    op0_l = otf_l.paragraphs[0]
    op0_l.text = "CORE FUNCTIONAL OBJECTIVES"
    op0_l.font.size = Pt(12)
    op0_l.font.bold = True
    op0_l.font.color.rgb = PRIMARY

    for title, desc in obj_left:
        p = otf_l.add_paragraph()
        p.text = f"🎯 {title}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = ACCENT_BLUE
        p.space_before = Pt(6)

        pd = otf_l.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_DARK
        pd.space_before = Pt(1)

    # Right Column Card
    add_card(slide5, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1))
    obox_r = slide5.shapes.add_textbox(Inches(7.0), Inches(1.75), Inches(5.3), Inches(4.8))
    otf_r = obox_r.text_frame
    otf_r.word_wrap = True
    op0_r = otf_r.paragraphs[0]
    op0_r.text = "OPERATIONAL & USER OBJECTIVES"
    op0_r.font.size = Pt(12)
    op0_r.font.bold = True
    op0_r.font.color.rgb = ACCENT_GOLD

    for title, desc in obj_right:
        p = otf_r.add_paragraph()
        p.text = f"🎯 {title}"
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = ACCENT_GOLD
        p.space_before = Pt(6)

        pd = otf_r.add_paragraph()
        pd.text = desc
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_DARK
        pd.space_before = Pt(1)

    slide5.notes_slide.notes_text_frame.text = (
        "Here are the core objectives of our project as documented in our synopsis. "
        "Our primary goals include: providing an online booking facility, making booking simple and easy, "
        "allowing customers to select transport vehicles, computing fares automatically, storing records in the database, "
        "and ensuring full mobile responsiveness to save time for both customers and transporters."
    )

    # =========================================================================
    # SECTION 2: H/W & S/W REQUIREMENTS (Exact Tables from Synopsis Section 4)
    # SLIDE 6: HARDWARE & SOFTWARE REQUIREMENTS
    # =========================================================================
    slide6 = prs.slides.add_slide(blank_layout)
    set_background(slide6)
    add_header(slide6, "Hardware & Software Requirements", "SECTION 2: H/W & S/W REQUIREMENTS")

    # Left: Hardware Requirements Table (From Synopsis)
    add_card(slide6, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
    h_bar = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.7), Inches(0.12))
    h_bar.fill.solid()
    h_bar.fill.fore_color.rgb = PRIMARY
    h_bar.line.fill.background()

    hbox = slide6.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.2), Inches(4.7))
    htf = hbox.text_frame
    htf.word_wrap = True

    hp0 = htf.paragraphs[0]
    hp0.text = "HARDWARE REQUIREMENTS (SYNOPSIS TABLE)"
    hp0.font.size = Pt(13)
    hp0.font.bold = True
    hp0.font.color.rgb = PRIMARY

    hw_table_data = [
        ("Processor", "Intel Core i3 or equivalent (Min 2.0 GHz)"),
        ("RAM", "8 GB"),
        ("Storage", "20 GB free space (SSD recommended)"),
        ("Operating System", "Windows 10 / Windows 11"),
        ("Display / Resolution", "Standard 1366 x 768 or 1920 x 1080 Full HD"),
        ("Internet Connectivity", "Broadband / 4G cellular data connection")
    ]

    for comp, req in hw_table_data:
        pt = htf.add_paragraph()
        pt.text = f"💻 {comp}:"
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = ACCENT_BLUE
        pt.space_before = Pt(8)

        pd = htf.add_paragraph()
        pd.text = f"    Requirement: {req}"
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_DARK
        pd.space_before = Pt(1)

    # Right: Software Requirements Table (From Synopsis)
    add_card(slide6, Inches(6.8), Inches(1.6), Inches(5.7), Inches(5.1))
    s_bar = slide6.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), Inches(1.6), Inches(5.7), Inches(0.12))
    s_bar.fill.solid()
    s_bar.fill.fore_color.rgb = ACCENT_GOLD
    s_bar.line.fill.background()

    sbox = slide6.shapes.add_textbox(Inches(7.05), Inches(1.85), Inches(5.2), Inches(4.7))
    stf = sbox.text_frame
    stf.word_wrap = True

    sp0 = stf.paragraphs[0]
    sp0.text = "SOFTWARE REQUIREMENTS (SYNOPSIS TABLE)"
    sp0.font.size = Pt(13)
    sp0.font.bold = True
    sp0.font.color.rgb = ACCENT_GOLD

    sw_table_data = [
        ("Python", "Backend programming"),
        ("Django", "Web development framework"),
        ("HTML5", "Creating webpage structure"),
        ("CSS3", "Website design and styling"),
        ("JavaScript", "Adding interactive features"),
        ("SQLite", "Storing booking data"),
        ("Visual Studio Code", "Writing and managing code"),
        ("Google Chrome", "Website testing"),
        ("Git / GitHub", "Code storage and version control"),
        ("Render", "Online cloud deployment")
    ]

    for tech, purpose in sw_table_data:
        p = stf.add_paragraph()
        p.text = f"• {tech}: {purpose}"
        p.font.size = Pt(9.5)
        p.font.color.rgb = TEXT_DARK
        p.space_before = Pt(4)

    slide6.notes_slide.notes_text_frame.text = (
        "In Section 2, we present the exact Hardware and Software specifications from our approved synopsis. "
        "On the hardware side: an Intel Core i3 or equivalent processor, 8 GB of RAM, 20 GB free storage, and Windows 10/11. "
        "On the software side: Python for backend, Django as web framework, HTML5/CSS3/JS for frontend, SQLite for database storage, "
        "VS Code for development, Chrome for testing, Git/GitHub for version control, and Render for live cloud deployment."
    )

    # =========================================================================
    # SECTION 3: FORM DESIGN / DATABASE DESIGN / ER-DIAGRAM / DFD DIAGRAM
    # SLIDE 7: FORM DESIGN (UI / UX Architecture)
    # =========================================================================
    slide7 = prs.slides.add_slide(blank_layout)
    set_background(slide7)
    add_header(slide7, "Form Design & User Interface Architecture", "SECTION 3: SYSTEM DESIGN")

    # 4 Form Cards
    forms = [
        ("1. Online Transport Booking Form", [
            ("Customer Name", "Full name input field for booking identification"),
            ("Contact Details", "10-digit mobile number & optional email"),
            ("Pickup & Drop Locations", "Origin & destination address inputs with route matching"),
            ("Booking Date & Time", "HTML5 calendar & time picker for scheduling"),
            ("Vehicle Type Selection", "Dropdown/Cards: Bolero, Pickup, Tata Magic, 407 Truck"),
            ("Fare Display & Submit", "Auto-calculated fare display and instant confirmation button")
        ], PRIMARY),

        ("2. Pickupwala Cargo Dispatch Form", [
            ("Cargo Description", "Goods category: Furniture, Electronics, Agricultural produce"),
            ("Weight Selection", "Payload options: Below 500kg, 1 Ton, 1.5 Ton, 2+ Ton"),
            ("Delivery Urgency", "Standard dispatch vs Priority same-day dispatch"),
            ("Receiver Contact", "Recipient name & delivery contact phone"),
            ("Submit Action", "Instant dispatch notification to nearest available driver")
        ], ACCENT_BLUE),

        ("3. Quotation Request Form", [
            ("Client / Event Type", "Wedding logistics, Corporate shifting, Bulk freight"),
            ("Vehicle Fleet Count", "Multi-vehicle selection count (e.g. 2 Boleros, 1 Truck)"),
            ("Estimated Distance", "Round-trip kilometer input with outstation allowance"),
            ("Budget & Remarks", "Custom notes, specific labor/loading requirements"),
            ("Generate Action", "Produces branded, verifiable PDF quotation immediately")
        ], NAVY),

        ("4. Expense & Toll Log Form (Admin/Driver)", [
            ("Vehicle Selector", "Dropdown linking to registered fleet vehicles"),
            ("Expense Category", "Diesel / Fuel, Maintenance, Toll Plaza, Parking"),
            ("Amount & Date", "Rupee amount with date incurred"),
            ("Receipt Image Upload", "Photo upload of physical bill/toll slip for audit"),
            ("Audit Submit", "Updates vehicle profit & loss accounts instantly")
        ], ACCENT_GOLD)
    ]

    grid_pos = [
        (Inches(0.8), Inches(1.6)),
        (Inches(6.8), Inches(1.6)),
        (Inches(0.8), Inches(4.3)),
        (Inches(6.8), Inches(4.3)),
    ]

    for idx, (ftitle, ffields, fcol) in enumerate(forms):
        gx, gy = grid_pos[idx]
        add_card(slide7, gx, gy, Inches(5.7), Inches(2.4))

        # Top banner for card
        fbar = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, gx, gy, Inches(5.7), Inches(0.35))
        fbar.fill.solid()
        fbar.fill.fore_color.rgb = fcol
        fbar.line.fill.background()
        fbar_tf = fbar.text_frame
        fbar_p = fbar_tf.paragraphs[0]
        fbar_p.text = ftitle.upper()
        fbar_p.font.size = Pt(11)
        fbar_p.font.bold = True
        fbar_p.font.color.rgb = WHITE

        fbox = slide7.shapes.add_textbox(gx + Inches(0.2), gy + Inches(0.4), Inches(5.3), Inches(1.9))
        ftf = fbox.text_frame
        ftf.word_wrap = True

        for i_fld, (fld_name, fld_desc) in enumerate(ffields):
            pfld = ftf.paragraphs[0] if i_fld == 0 else ftf.add_paragraph()
            pfld.text = f"• {fld_name}: {fld_desc}"
            pfld.font.size = Pt(9.5)
            pfld.font.color.rgb = TEXT_DARK
            if i_fld > 0:
                pfld.space_before = Pt(2)

    slide7.notes_slide.notes_text_frame.text = (
        "In Section 3: System Design, we begin with Form Design. "
        "As highlighted in our synopsis, users interact with the system via clean online forms: "
        "The primary Booking Form collects customer name, phone, pickup, drop, booking date, and vehicle type; "
        "The Pickupwala form handles cargo dispatch; "
        "The Quotation form builds instant PDF estimates; "
        "and the Expense form allows logging diesel and toll bills with photo proof. "
        "All forms are built with Django Form validation and CSRF token security."
    )

    # =========================================================================
    # SLIDE 8: DATABASE DESIGN (SQLite Schema & Tables)
    # =========================================================================
    slide8 = prs.slides.add_slide(blank_layout)
    set_background(slide8)
    add_header(slide8, "Database Design & SQLite Tables Schema", "SECTION 3: SYSTEM DESIGN")

    db_tables = [
        ("tbl_Booking (Main Bookings)", [
            "booking_id (VARCHAR[20], PK)",
            "customer_name (VARCHAR[100])",
            "phone (VARCHAR[15])",
            "pickup_location (TEXT)",
            "drop_location (TEXT)",
            "booking_date (DATETIME)",
            "vehicle_type (VARCHAR[30])",
            "distance_km (DECIMAL)",
            "fare_amount (DECIMAL)",
            "status (Pending/Confirmed/Done)"
        ], PRIMARY),

        ("tbl_Vehicle (Transport Fleet)", [
            "vehicle_id (INT, PK AUTO_INC)",
            "vehicle_name (Bolero, Pickup, Magic)",
            "vehicle_number (VARCHAR[20], UNIQUE)",
            "tonnage_capacity (FLOAT)",
            "per_km_rate (DECIMAL)",
            "is_available (BOOLEAN)",
            "driver_name (VARCHAR[100])",
            "driver_phone (VARCHAR[15])"
        ], ACCENT_BLUE),

        ("tbl_Expense (Accounts & Tolls)", [
            "expense_id (INT, PK AUTO_INC)",
            "vehicle_id (FK -> tbl_Vehicle)",
            "category (Fuel/Toll/Maintenance)",
            "amount (DECIMAL)",
            "receipt_photo (VARCHAR[255])",
            "date_incurred (DATE)",
            "approved_by (VARCHAR[50])"
        ], NAVY),

        ("tbl_Quotation (Event Quotes)", [
            "quotation_id (VARCHAR[20], PK)",
            "client_name (VARCHAR[100])",
            "phone (VARCHAR[15])",
            "cargo_details (TEXT)",
            "quoted_fare (DECIMAL)",
            "created_date (DATETIME)",
            "status (Draft/Approved)"
        ], ACCENT_GOLD)
    ]

    for idx, (tname, fields, col) in enumerate(db_tables):
        cx = col_positions[idx]
        add_card(slide8, cx, Inches(1.6), Inches(2.7), Inches(5.1))
        
        # Header banner
        t_header = slide8.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, Inches(1.6), Inches(2.7), Inches(0.45))
        t_header.fill.solid()
        t_header.fill.fore_color.rgb = col
        t_header.line.fill.background()
        th_tf = t_header.text_frame
        th_p = th_tf.paragraphs[0]
        th_p.text = tname
        th_p.font.size = Pt(10)
        th_p.font.bold = True
        th_p.font.color.rgb = WHITE

        tbox = slide8.shapes.add_textbox(cx + Inches(0.1), Inches(2.1), Inches(2.5), Inches(4.5))
        ttf = tbox.text_frame
        ttf.word_wrap = True

        p_attr = ttf.paragraphs[0]
        p_attr.text = "ATTRIBUTES & DATA TYPES:"
        p_attr.font.size = Pt(8.5)
        p_attr.font.bold = True
        p_attr.font.color.rgb = col

        for fld in fields:
            pf = ttf.add_paragraph()
            pf.text = f"• {fld}"
            pf.font.size = Pt(9)
            pf.font.color.rgb = TEXT_DARK
            pf.space_before = Pt(2)

    slide8.notes_slide.notes_text_frame.text = (
        "Here is our SQLite database schema. As stated in our synopsis, SQLite is used to store all booking and customer information. "
        "The tbl_Booking table holds the customer credentials, pickup and drop addresses, booking date, vehicle type, and calculated fare. "
        "The tbl_Vehicle table tracks vehicle fleet details and availability. "
        "The tbl_Expense table records auditable fuel and toll expenses, and the tbl_Quotation table handles bulk inquiries. "
        "Foreign key relationships enforce referential data integrity."
    )

    # =========================================================================
    # SLIDE 9: ENTITY-RELATIONSHIP (ER) DIAGRAM
    # =========================================================================
    slide9 = prs.slides.add_slide(blank_layout)
    set_background(slide9)
    add_header(slide9, "Entity-Relationship (ER) Diagram", "SECTION 3: SYSTEM DESIGN")

    add_card(slide9, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.3))

    entities = [
        ("CUSTOMER", Inches(1.2), Inches(2.0), Inches(2.2), Inches(1.5), PRIMARY,
         ["customer_id (PK)", "name", "phone", "email"]),
        
        ("BOOKING", Inches(5.5), Inches(2.0), Inches(2.4), Inches(1.8), ACCENT_BLUE,
         ["booking_id (PK)", "pickup / drop", "booking_date", "vehicle_type", "fare, status"]),
        
        ("VEHICLE", Inches(9.8), Inches(2.0), Inches(2.3), Inches(1.6), GREEN,
         ["vehicle_id (PK)", "vehicle_name", "reg_number", "tonnage_cap", "is_available"]),
        
        ("QUOTATION", Inches(1.2), Inches(4.7), Inches(2.2), Inches(1.5), PURPLE,
         ["quotation_id (PK)", "client_name", "phone", "quoted_fare"]),
        
        ("DRIVER", Inches(5.5), Inches(4.7), Inches(2.4), Inches(1.5), NAVY,
         ["driver_id (PK)", "name, phone", "license_no", "assigned_vehicle"]),
        
        ("EXPENSE", Inches(9.8), Inches(4.7), Inches(2.3), Inches(1.5), ACCENT_GOLD,
         ["expense_id (PK)", "vehicle_id (FK)", "category, amount", "receipt_photo"])
    ]

    for ename, ex, ey, ew, eh, ecol, eattrs in entities:
        eh_shape = slide9.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, ex, ey, ew, Inches(0.35))
        eh_shape.fill.solid()
        eh_shape.fill.fore_color.rgb = ecol
        eh_shape.line.fill.background()
        ehtf = eh_shape.text_frame
        ehp = ehtf.paragraphs[0]
        ehp.text = f"ENTITY: {ename}"
        ehp.font.size = Pt(10)
        ehp.font.bold = True
        ehp.font.color.rgb = WHITE
        ehp.alignment = PP_ALIGN.CENTER

        eb_shape = slide9.shapes.add_shape(MSO_SHAPE.RECTANGLE, ex, ey + Inches(0.35), ew, eh - Inches(0.35))
        eb_shape.fill.solid()
        eb_shape.fill.fore_color.rgb = RGBColor(241, 245, 249)
        eb_shape.line.color.rgb = ecol
        eb_shape.line.width = Pt(1)
        ebtf = eb_shape.text_frame
        ebtf.word_wrap = True

        for i_a, attr in enumerate(eattrs):
            pa = ebtf.paragraphs[0] if i_a == 0 else ebtf.add_paragraph()
            pa.text = f"• {attr}"
            pa.font.size = Pt(9)
            pa.font.color.rgb = TEXT_DARK
            if "PK" in attr:
                pa.font.bold = True
                pa.font.color.rgb = ecol

    rel_badges = [
        ("PLACES [1:N]", Inches(3.6), Inches(2.4), Inches(1.7), Inches(0.4), PRIMARY),
        ("ASSIGNED [N:1]", Inches(8.1), Inches(2.4), Inches(1.5), Inches(0.4), GREEN),
        ("REQUESTS [1:N]", Inches(1.4), Inches(3.8), Inches(1.8), Inches(0.35), PURPLE),
        ("OPERATES [1:1]", Inches(5.8), Inches(4.0), Inches(1.8), Inches(0.35), NAVY),
        ("INCURS [1:N]", Inches(9.9), Inches(3.9), Inches(1.8), Inches(0.35), ACCENT_GOLD)
    ]

    for rtext, rx, ry, rw, rh, rcol in rel_badges:
        rshape = slide9.shapes.add_shape(MSO_SHAPE.OVAL, rx, ry, rw, rh)
        rshape.fill.solid()
        rshape.fill.fore_color.rgb = rcol
        rshape.line.fill.background()
        rtf = rshape.text_frame
        rp = rtf.paragraphs[0]
        rp.text = rtext
        rp.font.size = Pt(8.5)
        rp.font.bold = True
        rp.font.color.rgb = WHITE
        rp.alignment = PP_ALIGN.CENTER

    slide9.notes_slide.notes_text_frame.text = (
        "Slide 9 displays our Entity-Relationship Diagram. "
        "A CUSTOMER places one or more BOOKINGS (1 to N relationship). "
        "Each BOOKING is assigned to a specific transport VEHICLE (N to 1). "
        "Each VEHICLE is operated by a DRIVER (1 to 1). "
        "Each VEHICLE incurs operational EXPENSES such as fuel and tolls (1 to N). "
        "Customers can also generate multiple commercial QUOTATIONS (1 to N). "
        "Primary Keys and Foreign Keys maintain complete relational consistency."
    )

    # =========================================================================
    # SLIDE 10: DATA FLOW DIAGRAM: LEVEL 0 (CONTEXT DIAGRAM)
    # =========================================================================
    slide10 = prs.slides.add_slide(blank_layout)
    set_background(slide10)
    add_header(slide10, "Data Flow Diagram: Level 0 (Context Diagram)", "SECTION 3: SYSTEM DESIGN")

    add_card(slide10, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.3))

    # Central System Bubble
    center_circle = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(5.0), Inches(2.9), Inches(3.333), Inches(2.2))
    center_circle.fill.solid()
    center_circle.fill.fore_color.rgb = PRIMARY
    center_circle.line.color.rgb = ACCENT_GOLD
    center_circle.line.width = Pt(2.5)
    c_tf = center_circle.text_frame
    c_tf.word_wrap = True

    cp0 = c_tf.paragraphs[0]
    cp0.text = "PROCESS 0.0"
    cp0.font.size = Pt(12)
    cp0.font.bold = True
    cp0.font.color.rgb = ACCENT_GOLD
    cp0.alignment = PP_ALIGN.CENTER

    cp1 = c_tf.add_paragraph()
    cp1.text = "GHIDORA TRANSPORT\nONLINE PLATFORM"
    cp1.font.size = Pt(15)
    cp1.font.bold = True
    cp1.font.color.rgb = WHITE
    cp1.alignment = PP_ALIGN.CENTER
    cp1.space_before = Pt(4)

    cp2 = c_tf.add_paragraph()
    cp2.text = "(Central Django Application)"
    cp2.font.size = Pt(10)
    cp2.font.color.rgb = RGBColor(191, 219, 254)
    cp2.alignment = PP_ALIGN.CENTER
    cp2.space_before = Pt(4)

    # External Entity 1: CUSTOMER (Left)
    cust_box = slide10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.1), Inches(2.8), Inches(2.4), Inches(2.4))
    cust_box.fill.solid()
    cust_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
    cust_box.line.color.rgb = ACCENT_BLUE
    cust_box.line.width = Pt(2)
    cust_tf = cust_box.text_frame
    cust_tf.word_wrap = True

    cst0 = cust_tf.paragraphs[0]
    cst0.text = "EXTERNAL ENTITY"
    cst0.font.size = Pt(9)
    cst0.font.bold = True
    cst0.font.color.rgb = ACCENT_GOLD
    cst0.alignment = PP_ALIGN.CENTER

    cst1 = cust_tf.add_paragraph()
    cst1.text = "CUSTOMER /\nUSER"
    cst1.font.size = Pt(14)
    cst1.font.bold = True
    cst1.font.color.rgb = WHITE
    cst1.alignment = PP_ALIGN.CENTER
    cst1.space_before = Pt(4)

    cst2 = cust_tf.add_paragraph()
    cst2.text = "• Name & Contact\n• Pickup & Drop\n• Booking Date\n• Vehicle Choice"
    cst2.font.size = Pt(9.5)
    cst2.font.color.rgb = TEXT_LIGHT
    cst2.space_before = Pt(6)

    # External Entity 2: DRIVER (Top Right)
    drv_box = slide10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(9.8), Inches(1.8), Inches(2.4), Inches(2.0))
    drv_box.fill.solid()
    drv_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
    drv_box.line.color.rgb = GREEN
    drv_box.line.width = Pt(2)
    drv_tf = drv_box.text_frame
    drv_tf.word_wrap = True

    dr0 = drv_tf.paragraphs[0]
    dr0.text = "EXTERNAL ENTITY"
    dr0.font.size = Pt(9)
    dr0.font.bold = True
    dr0.font.color.rgb = GREEN
    dr0.alignment = PP_ALIGN.CENTER

    dr1 = drv_tf.add_paragraph()
    dr1.text = "DRIVER"
    dr1.font.size = Pt(13)
    dr1.font.bold = True
    dr1.font.color.rgb = WHITE
    dr1.alignment = PP_ALIGN.CENTER
    dr1.space_before = Pt(3)

    dr2 = drv_tf.add_paragraph()
    dr2.text = "• Availability Status\n• Trip Acceptance\n• Toll & Fuel Slips"
    dr2.font.size = Pt(9.5)
    dr2.font.color.rgb = TEXT_LIGHT
    dr2.space_before = Pt(4)

    # External Entity 3: ADMIN (Bottom Right)
    adm_box = slide10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(9.8), Inches(4.4), Inches(2.4), Inches(2.0))
    adm_box.fill.solid()
    adm_box.fill.fore_color.rgb = RGBColor(30, 41, 59)
    adm_box.line.color.rgb = ACCENT_GOLD
    adm_box.line.width = Pt(2)
    adm_tf = adm_box.text_frame
    adm_tf.word_wrap = True

    ad0 = adm_tf.paragraphs[0]
    ad0.text = "EXTERNAL ENTITY"
    ad0.font.size = Pt(9)
    ad0.font.bold = True
    ad0.font.color.rgb = ACCENT_GOLD
    ad0.alignment = PP_ALIGN.CENTER

    ad1 = adm_tf.add_paragraph()
    ad1.text = "ADMIN / OWNER"
    ad1.font.size = Pt(13)
    ad1.font.bold = True
    ad1.font.color.rgb = WHITE
    ad1.alignment = PP_ALIGN.CENTER
    ad1.space_before = Pt(3)

    ad2 = adm_tf.add_paragraph()
    ad2.text = "• Vehicle Roster\n• Rate Configuration\n• Booking & Audit Logs"
    ad2.font.size = Pt(9.5)
    ad2.font.color.rgb = TEXT_LIGHT
    ad2.space_before = Pt(4)

    flows = [
        ("→ Booking Form Details →", Inches(3.55), Inches(3.2), Inches(1.4), Inches(0.4), ACCENT_BLUE),
        ("← Fare Display, Booking ID ←", Inches(3.55), Inches(4.3), Inches(1.4), Inches(0.4), PRIMARY),
        ("← Trip Assignment Sheet ←", Inches(8.35), Inches(2.2), Inches(1.4), Inches(0.4), GREEN),
        ("→ Status Update, Toll Receipt →", Inches(8.35), Inches(2.9), Inches(1.4), Inches(0.4), GREEN),
        ("← Booking Reports & Logs ←", Inches(8.35), Inches(4.7), Inches(1.4), Inches(0.4), ACCENT_GOLD),
        ("→ Manage Rates & Fleet →", Inches(8.35), Inches(5.4), Inches(1.4), Inches(0.4), ACCENT_GOLD)
    ]

    for flabel, fx, fy, fw, fh, fcol in flows:
        f_shape = slide10.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, fx, fy, fw, fh)
        f_shape.fill.solid()
        f_shape.fill.fore_color.rgb = RGBColor(241, 245, 249)
        f_shape.line.color.rgb = fcol
        f_shape.line.width = Pt(1)
        ftf = f_shape.text_frame
        fp = ftf.paragraphs[0]
        fp.text = flabel
        fp.font.size = Pt(7.5)
        fp.font.bold = True
        fp.font.color.rgb = fcol
        fp.alignment = PP_ALIGN.CENTER

    slide10.notes_slide.notes_text_frame.text = (
        "Slide 10 presents the Level 0 Data Flow Diagram (Context Diagram). "
        "The central bubble represents Process 0.0 Ghidora Transport System. "
        "Customers provide booking details and receive calculated fares and booking IDs. "
        "Drivers receive trip assignments and send status updates. "
        "Admins manage vehicle rates and view overall booking and financial reports."
    )

    # =========================================================================
    # SLIDE 11: DATA FLOW DIAGRAM: LEVEL 1 (FUNCTIONAL DFD)
    # =========================================================================
    slide11 = prs.slides.add_slide(blank_layout)
    set_background(slide11)
    add_header(slide11, "Data Flow Diagram: Level 1 (Functional DFD)", "SECTION 3: SYSTEM DESIGN")

    add_card(slide11, Inches(0.8), Inches(1.5), Inches(11.733), Inches(5.3))

    dfd_processes = [
        ("1.0 FORM INPUT VALIDATION", Inches(1.2), Inches(1.8), Inches(2.6), Inches(1.4), PRIMARY,
         "Receives name, contact, pickup, drop & date. Validates form inputs & checks CSRF token."),
        
        ("2.0 FARE CALCULATION ENGINE", Inches(5.3), Inches(1.8), Inches(2.7), Inches(1.4), ACCENT_BLUE,
         "Evaluates distance between pickup & drop, applies vehicle rate chart, computes total fare."),
        
        ("3.0 BOOKING CONFIRMATION", Inches(9.5), Inches(1.8), Inches(2.6), Inches(1.4), GREEN,
         "Generates unique booking reference ID, registers booking, and dispatches trip details."),
        
        ("4.0 EXPENSE & TOLL AUDITING", Inches(1.2), Inches(4.5), Inches(2.6), Inches(1.4), ACCENT_GOLD,
         "Records driver fuel expenses and toll plaza receipt uploads for administrative auditing."),
        
        ("5.0 QUOTATION BUILDER", Inches(5.3), Inches(4.5), Inches(2.7), Inches(1.4), PURPLE,
         "Generates printable / downloadable commercial PDF quotations for event or bulk clients.")
    ]

    for pname, px, py, pw, ph, pcol, pdesc in dfd_processes:
        pshape = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, px, py, pw, ph)
        pshape.fill.solid()
        pshape.fill.fore_color.rgb = pcol
        pshape.line.fill.background()
        ptf = pshape.text_frame
        ptf.word_wrap = True

        p0 = ptf.paragraphs[0]
        p0.text = pname
        p0.font.size = Pt(11)
        p0.font.bold = True
        p0.font.color.rgb = WHITE

        p1 = ptf.add_paragraph()
        p1.text = pdesc
        p1.font.size = Pt(9)
        p1.font.color.rgb = RGBColor(241, 245, 249)
        p1.space_before = Pt(4)

    data_stores = [
        ("D1: USER STORE", Inches(9.5), Inches(3.6), Inches(2.6), Inches(0.65), NAVY),
        ("D2: BOOKINGS STORE", Inches(9.5), Inches(4.4), Inches(2.6), Inches(0.65), PRIMARY),
        ("D3: VEHICLE FLEET STORE", Inches(9.5), Inches(5.2), Inches(2.6), Inches(0.65), GREEN),
        ("D4: EXPENSE STORE", Inches(9.5), Inches(6.0), Inches(2.6), Inches(0.65), ACCENT_GOLD)
    ]

    for dname, dx, dy, dw, dh, dcol in data_stores:
        dshape = slide11.shapes.add_shape(MSO_SHAPE.RECTANGLE, dx, dy, dw, dh)
        dshape.fill.solid()
        dshape.fill.fore_color.rgb = RGBColor(248, 250, 252)
        dshape.line.color.rgb = dcol
        dshape.line.width = Pt(2)
        dtf = dshape.text_frame
        dtf.word_wrap = True
        dp = dtf.paragraphs[0]
        dp.text = f"🗄 {dname}"
        dp.font.size = Pt(10)
        dp.font.bold = True
        dp.font.color.rgb = dcol
        dp.alignment = PP_ALIGN.CENTER

    f_expl = slide11.shapes.add_textbox(Inches(1.2), Inches(6.0), Inches(7.5), Inches(0.7))
    f_etf = f_expl.text_frame
    f_ep = f_etf.paragraphs[0]
    f_ep.text = "Data Flow: Processes (1.0 - 5.0) write and retrieve structured data from SQLite Data Stores (D1 - D4) via Django ORM."
    f_ep.font.size = Pt(9.5)
    f_ep.font.italic = True
    f_ep.font.color.rgb = TEXT_MUTED

    slide11.notes_slide.notes_text_frame.text = (
        "On Slide 11, the Level 1 DFD decomposes the system into five sub-processes: "
        "Process 1.0 validates user booking input; Process 2.0 calculates the fare; "
        "Process 3.0 confirms booking and writes to D2 Booking Store; "
        "Process 4.0 audits expenses and toll receipts to D4 Expense Store; "
        "and Process 5.0 generates PDF quotations. "
        "All data stores map directly to SQLite relational tables."
    )

    # =========================================================================
    # SECTION 4: METHODOLOGY OF YOUR PROJECT
    # SLIDE 12: AGILE DEVELOPMENT METHODOLOGY
    # =========================================================================
    slide12 = prs.slides.add_slide(blank_layout)
    set_background(slide12)
    add_header(slide12, "Project Methodology: Agile Iterative SDLC Model", "SECTION 4: METHODOLOGY")

    add_card(slide12, Inches(0.8), Inches(1.6), Inches(5.7), Inches(5.1))
    ag_bar = slide12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.6), Inches(5.7), Inches(0.12))
    ag_bar.fill.solid()
    ag_bar.fill.fore_color.rgb = PRIMARY
    ag_bar.line.fill.background()

    ag_box = slide12.shapes.add_textbox(Inches(1.05), Inches(1.85), Inches(5.2), Inches(4.7))
    ag_tf = ag_box.text_frame
    ag_tf.word_wrap = True

    agp0 = ag_tf.paragraphs[0]
    agp0.text = "WHY AGILE ITERATIVE MODEL?"
    agp0.font.size = Pt(14)
    agp0.font.bold = True
    agp0.font.color.rgb = PRIMARY

    agile_reasons = [
        ("Modular App Architecture", "Allowed independent development and testing of standalone Django apps (booking, payments, expenses, quotations)."),
        ("Incremental Feature Delivery", "Built the core booking form first, then added fare calculation, driver allocation, and toll auditing iteratively."),
        ("Rapid Feedback Integration", "Early testing with local users helped refine the booking form and ensure high mobile responsiveness."),
        ("Continuous Code Testing", "Every sprint incorporated unit testing on models and cross-browser UI checks, catching bugs early.")
    ]

    for title, desc in agile_reasons:
        pag_t = ag_tf.add_paragraph()
        pag_t.text = f"✔ {title}:"
        pag_t.font.size = Pt(11)
        pag_t.font.bold = True
        pag_t.font.color.rgb = ACCENT_BLUE
        pag_t.space_before = Pt(8)

        pag_d = ag_tf.add_paragraph()
        pag_d.text = desc
        pag_d.font.size = Pt(10)
        pag_d.font.color.rgb = TEXT_DARK
        pag_d.space_before = Pt(1)

    sprints = [
        ("SPRINT 1: SETUP & DATABASE MODELING", "Python/Django initialization, SQLite database modeling for Bookings and Vehicles.", PRIMARY),
        ("SPRINT 2: BOOKING FORM & FARE ENGINE", "Online booking form design, pickup/drop location capture, automated fare computation.", ACCENT_BLUE),
        ("SPRINT 3: EXPENSE LOGS & ADMIN PANEL", "Toll receipt upload mechanism, driver expense auditing, and admin management panel.", NAVY),
        ("SPRINT 4: TESTING, POLISH & RENDER DEPLOY", "Mobile responsiveness testing, cross-browser validation, and cloud deployment on Render.", ACCENT_GOLD)
    ]

    for idx, (stitle, sdesc, scol) in enumerate(sprints):
        sy = Inches(1.6 + idx * 1.28)
        add_card(slide12, Inches(6.8), sy, Inches(5.7), Inches(1.15))
        
        s_strip = slide12.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(6.8), sy, Inches(0.15), Inches(1.15))
        s_strip.fill.solid()
        s_strip.fill.fore_color.rgb = scol
        s_strip.line.fill.background()

        sbox = slide12.shapes.add_textbox(Inches(7.05), sy + Inches(0.1), Inches(5.3), Inches(0.95))
        stf = sbox.text_frame
        stf.word_wrap = True

        sp0 = stf.paragraphs[0]
        sp0.text = stitle
        sp0.font.size = Pt(11.5)
        sp0.font.bold = True
        sp0.font.color.rgb = scol

        sp1 = stf.add_paragraph()
        sp1.text = sdesc
        sp1.font.size = Pt(9.5)
        sp1.font.color.rgb = TEXT_DARK
        sp1.space_before = Pt(2)

    slide12.notes_slide.notes_text_frame.text = (
        "In Section 4: Methodology, we adopted the Agile Iterative SDLC model. "
        "Agile allowed our 2-member team to work in iterative sprints: "
        "Sprint 1 set up Django and SQLite database models; "
        "Sprint 2 built the booking form and fare calculation engine; "
        "Sprint 3 implemented driver management and expense auditing; "
        "and Sprint 4 handled testing, UI refinement, and Render cloud deployment."
    )

    # =========================================================================
    # SLIDE 13: METHODOLOGY - PHASED EXECUTION LIFECYCLE
    # =========================================================================
    slide13 = prs.slides.add_slide(blank_layout)
    set_background(slide13)
    add_header(slide13, "Project Methodology: Phased Execution Lifecycle", "SECTION 4: METHODOLOGY")

    phases = [
        ("PHASE 1: REQUIREMENT ANALYSIS & SYNOPSIS", 
         "Analyzed manual booking challenges in local transport. Prepared Project Synopsis, defined hardware/software requirements, and established core objectives.",
         PRIMARY),
        ("PHASE 2: ARCHITECTURAL & DATABASE DESIGN", 
         "Designed Django MVT structure, normalized relational SQLite database tables (tbl_Booking, tbl_Vehicle, tbl_Expense), and drew ER and DFD diagrams.",
         ACCENT_BLUE),
        ("PHASE 3: IMPLEMENTATION & FRONTEND DESIGN", 
         "Developed backend using Python & Django. Created responsive frontend templates with HTML5, CSS3, and JavaScript with instant fare calculation.",
         NAVY),
        ("PHASE 4: TESTING & VALIDATION", 
         "Executed Unit Testing on Django models, verified form validation and CSRF security, tested mobile responsiveness on Chrome, Edge, and smartphones.",
         ACCENT_GOLD),
        ("PHASE 5: DEPLOYMENT ON RENDER", 
         "Configured Procfile, requirements.txt, and deployed project live on Render cloud hosting with Git/GitHub version control.",
         GREEN)
    ]

    for i, (ptitle, pcontent, pcol) in enumerate(phases):
        py = Inches(1.6 + i * 1.05)
        add_card(slide13, Inches(0.8), py, Inches(11.733), Inches(0.95))
        
        pbadge = slide13.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), py + Inches(0.12), Inches(3.2), Inches(0.7))
        pbadge.fill.solid()
        pbadge.fill.fore_color.rgb = pcol
        pbadge.line.fill.background()
        pbtf = pbadge.text_frame
        pbp = pbtf.paragraphs[0]
        pbp.text = ptitle
        pbp.font.size = Pt(10)
        pbp.font.bold = True
        pbp.font.color.rgb = WHITE
        pbp.alignment = PP_ALIGN.CENTER

        pbox = slide13.shapes.add_textbox(Inches(4.35), py + Inches(0.08), Inches(8.0), Inches(0.8))
        ptf = pbox.text_frame
        ptf.word_wrap = True
        pp = ptf.paragraphs[0]
        pp.text = pcontent
        pp.font.size = Pt(10.5)
        pp.font.color.rgb = TEXT_DARK

    slide13.notes_slide.notes_text_frame.text = (
        "Slide 13 outlines our 5-phase software development lifecycle: "
        "Phase 1: Synopsis preparation and requirement gathering; "
        "Phase 2: Database normalization and ER/DFD architectural design; "
        "Phase 3: Python and Django coding with responsive HTML/CSS/JS frontend; "
        "Phase 4: Unit testing, form validation, and mobile testing; "
        "and Phase 5: Production cloud deployment on Render."
    )

    # =========================================================================
    # SLIDE 14: TESTING & QUALITY ASSURANCE METHODOLOGY
    # =========================================================================
    slide14 = prs.slides.add_slide(blank_layout)
    set_background(slide14)
    add_header(slide14, "Testing, Validation & Quality Assurance", "SECTION 4: METHODOLOGY")

    testing_types = [
        ("Unit & Model Testing", 
         "Tested Django models (Booking, Vehicle, Expense) for field data types, primary keys, null constraints, and auto-timestamps.", 
         PRIMARY),
        ("Form Validation & Input Checks", 
         "Verified required fields (customer name, 10-digit phone, valid locations, dates) and client-side JavaScript prevention of empty submissions.", 
         ACCENT_BLUE),
        ("Fare Calculation Verification", 
         "Tested fare computation algorithm across various distances and vehicle types to ensure mathematically consistent rates.", 
         NAVY),
        ("Security & CSRF Protection", 
         "Ensured all form submissions include Django CSRF cryptographic tokens to prevent Cross-Site Request Forgery attacks.", 
         ACCENT_GOLD),
        ("Cross-Device Responsive Testing", 
         "Validated layout stability across Google Chrome, Firefox, Microsoft Edge, and Android mobile screens (360px to 1920px viewports).", 
         PURPLE),
        ("User Acceptance Testing (UAT)", 
         "Tested complete user journey: entering booking info, seeing calculated fare, submitting form, and verifying database record in SQLite.", 
         GREEN)
    ]

    for i, (ttitle, tdesc, tcol) in enumerate(testing_types):
        row = i // 2
        col_idx = i % 2
        px = Inches(0.8 if col_idx == 0 else 6.8)
        py = Inches(1.6 + row * 1.75)

        add_card(slide14, px, py, Inches(5.7), Inches(1.6))
        
        tbar = slide14.shapes.add_shape(MSO_SHAPE.RECTANGLE, px, py, Inches(5.7), Inches(0.08))
        tbar.fill.solid()
        tbar.fill.fore_color.rgb = tcol
        tbar.line.fill.background()

        tbox = slide14.shapes.add_textbox(px + Inches(0.2), py + Inches(0.12), Inches(5.3), Inches(1.35))
        ttf = tbox.text_frame
        ttf.word_wrap = True

        tp0 = ttf.paragraphs[0]
        tp0.text = f"🧪 {ttitle}"
        tp0.font.size = Pt(13)
        tp0.font.bold = True
        tp0.font.color.rgb = tcol

        tp1 = ttf.add_paragraph()
        tp1.text = tdesc
        tp1.font.size = Pt(10.5)
        tp1.font.color.rgb = TEXT_DARK
        tp1.space_before = Pt(3)

    slide14.notes_slide.notes_text_frame.text = (
        "Testing was an integral part of our project methodology. "
        "We performed Unit Testing on Django models; "
        "verified Form Validation to block empty or invalid phone numbers; "
        "checked Fare Calculation accuracy; "
        "validated CSRF security; "
        "and conducted extensive cross-device mobile testing."
    )

    # =========================================================================
    # SLIDE 15: FUTURE SCOPE (All 8 Items from Synopsis Section 7)
    # =========================================================================
    slide15 = prs.slides.add_slide(blank_layout)
    set_background(slide15)
    add_header(slide15, "Future Scope of the Project", "SECTION 4: METHODOLOGY")

    # 8 Future Scope items directly from Synopsis Section 7
    future_items_synopsis = [
        ("Automatic Distance Calculation", "Google Maps or another map service can be connected to automatically calculate the distance between pickup and drop locations.", PRIMARY),
        ("Online Payment Integration", "Online payment options such as UPI, debit/credit cards, and net banking can be added for instant settlements.", ACCENT_BLUE),
        ("WhatsApp Notification", "WhatsApp can be connected via Cloud API to send automated booking confirmations and driver details to customers.", NAVY),
        ("Live GPS Tracking", "GPS hardware tracking can be integrated so that customers can see the real-time live location of their transport vehicle.", ACCENT_GOLD),
        ("Customer Login System", "A dedicated customer authentication and profile system so users can check their booking history and invoices.", GREEN),
        ("Booking Status Tracking", "Users can track the real-time status of their trip: Pending, Confirmed, In-Transit, or Completed.", PURPLE),
        ("Native Mobile Application", "A cross-platform mobile application (Android/iOS) can be developed so customers can book directly from smartphones.", PRIMARY),
        ("AI Assistant / Chatbot", "An AI assistant can be embedded to answer basic customer questions and guide users through the booking process.", ACCENT_BLUE)
    ]

    for idx, (ftitle, fdesc, fcol) in enumerate(future_items_synopsis):
        row = idx // 4
        col = idx % 4
        cx = Inches(0.8 + col * 2.95)
        cy = Inches(1.6 + row * 2.55)

        add_card(slide15, cx, cy, Inches(2.8), Inches(2.4))
        
        # Header bar
        f_top = slide15.shapes.add_shape(MSO_SHAPE.RECTANGLE, cx, cy, Inches(2.8), Inches(0.1))
        f_top.fill.solid()
        f_top.fill.fore_color.rgb = fcol
        f_top.line.fill.background()

        fbox = slide15.shapes.add_textbox(cx + Inches(0.12), cy + Inches(0.15), Inches(2.55), Inches(2.15))
        ftf = fbox.text_frame
        ftf.word_wrap = True

        fp0 = ftf.paragraphs[0]
        fp0.text = f"🚀 {ftitle}"
        fp0.font.size = Pt(11)
        fp0.font.bold = True
        fp0.font.color.rgb = fcol

        fp1 = ftf.add_paragraph()
        fp1.text = fdesc
        fp1.font.size = Pt(9.5)
        fp1.font.color.rgb = TEXT_DARK
        fp1.space_before = Pt(6)

    slide15.notes_slide.notes_text_frame.text = (
        "Slide 15 highlights the Future Scope directly from our synopsis. "
        "Future enhancements include: Automatic Google Maps distance calculation; "
        "Online UPI payments; automated WhatsApp notifications; "
        "Live GPS tracking on map; Customer login and booking history; "
        "Live booking status updates (Pending, Confirmed, In-Transit); "
        "Dedicated Android/iOS mobile apps; and an AI Chatbot assistant for 24/7 customer queries."
    )

    # =========================================================================
    # SLIDE 16: CONCLUSION (From Synopsis Section 8)
    # =========================================================================
    slide16 = prs.slides.add_slide(blank_layout)
    set_background(slide16)
    add_header(slide16, "Conclusion & Project Summary", "SECTION 4: METHODOLOGY")

    add_card(slide16, Inches(1.0), Inches(1.6), Inches(11.333), Inches(5.1))
    cbox = slide16.shapes.add_textbox(Inches(1.4), Inches(1.85), Inches(10.5), Inches(4.6))
    ctf = cbox.text_frame
    ctf.word_wrap = True

    cp0 = ctf.paragraphs[0]
    cp0.text = "Project Summary & Conclusion (From Synopsis)"
    cp0.font.size = Pt(19)
    cp0.font.bold = True
    cp0.font.color.rgb = PRIMARY

    concl_points = [
        ("Web-Based Platform Accomplishment", 
         "Ghidora Transport successfully establishes a web-based platform that makes local transport booking simple, convenient, and accessible for everyone."),
        
        ("Key User Capabilities", 
         "Users can select a transport vehicle according to requirements, enter pickup and drop locations, get automated fare calculations, and submit booking requests online."),
        
        ("Robust Full-Stack Implementation", 
         "The project is fully developed using Python and Django for the backend, HTML5, CSS3, and JavaScript for the frontend, and SQLite to securely store all booking information."),
        
        ("Reduces Manual Effort & Future Ready", 
         "It effectively reduces manual booking dependency and provides an easy digital solution. Future improvements such as GPS tracking, online payment, WhatsApp alerts, customer login, and an AI assistant can be seamlessly integrated.")
    ]

    for title, desc in concl_points:
        pct = ctf.add_paragraph()
        pct.text = f"✔ {title}:"
        pct.font.size = Pt(13)
        pct.font.bold = True
        pct.font.color.rgb = ACCENT_BLUE
        pct.space_before = Pt(8)

        pcd = ctf.add_paragraph()
        pcd.text = desc
        pcd.font.size = Pt(11)
        pcd.font.color.rgb = TEXT_DARK
        pcd.space_before = Pt(2)

    slide16.notes_slide.notes_text_frame.text = (
        "In conclusion, as summarized in our synopsis, Ghidora Transport provides an easy, reliable, and convenient digital solution for local transport booking. "
        "It successfully reduces manual phone booking dependency, automates fare calculation, stores records securely in SQLite, and provides a solid foundation for future enhancements."
    )

    # =========================================================================
    # SLIDE 17: THANK YOU & Q&A
    # =========================================================================
    slide17 = prs.slides.add_slide(blank_layout)
    set_background(slide17, NAVY)

    # Top gold accent bar
    top_bar17 = slide17.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.15))
    top_bar17.fill.solid()
    top_bar17.fill.fore_color.rgb = ACCENT_GOLD
    top_bar17.line.fill.background()

    # Center Thank you text
    ty_box = slide17.shapes.add_textbox(Inches(1.0), Inches(0.9), Inches(11.333), Inches(2.0))
    ty_tf = ty_box.text_frame
    ty_tf.word_wrap = True

    typ0 = ty_tf.paragraphs[0]
    typ0.text = "THANK YOU!"
    typ0.font.size = Pt(46)
    typ0.font.bold = True
    typ0.font.color.rgb = WHITE
    typ0.alignment = PP_ALIGN.CENTER

    typ1 = ty_tf.add_paragraph()
    typ1.text = "Any Questions or Suggestions?"
    typ1.font.size = Pt(22)
    typ1.font.bold = True
    typ1.font.color.rgb = ACCENT_GOLD
    typ1.alignment = PP_ALIGN.CENTER
    typ1.space_before = Pt(6)

    # Presenter & Guide Card
    add_card(slide17, Inches(2.0), Inches(3.2), Inches(9.333), Inches(3.5), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    ci_box = slide17.shapes.add_textbox(Inches(2.3), Inches(3.4), Inches(8.733), Inches(3.1))
    ci_tf = ci_box.text_frame
    ci_tf.word_wrap = True

    cip0 = ci_tf.paragraphs[0]
    cip0.text = "PROJECT PRESENTED BY:"
    cip0.font.size = Pt(11)
    cip0.font.bold = True
    cip0.font.color.rgb = ACCENT_GOLD
    cip0.alignment = PP_ALIGN.CENTER

    cip1 = ci_tf.add_paragraph()
    cip1.text = "AMIT KUMAR SAHU (Roll: 2526002003)  |  RAAG PATEL (Roll: 2526002048)"
    cip1.font.size = Pt(16.5)
    cip1.font.bold = True
    cip1.font.color.rgb = WHITE
    cip1.alignment = PP_ALIGN.CENTER
    cip1.space_before = Pt(4)

    cip_g = ci_tf.add_paragraph()
    cip_g.text = "Under the Guidance of: MS. DIVYA JAISWAL"
    cip_g.font.size = Pt(13)
    cip_g.font.bold = True
    cip_g.font.color.rgb = RGBColor(191, 219, 254)
    cip_g.alignment = PP_ALIGN.CENTER
    cip_g.space_before = Pt(8)

    cip2 = ci_tf.add_paragraph()
    cip2.text = "Department of Computer Applications\nShri Shankaracharya Professional University (SSPU), Bhilai (C.G.), India"
    cip2.font.size = Pt(12)
    cip2.font.color.rgb = RGBColor(203, 213, 225)
    cip2.alignment = PP_ALIGN.CENTER
    cip2.space_before = Pt(4)

    slide17.notes_slide.notes_text_frame.text = (
        "We express our sincere gratitude to our respected guide Ms. Divya Jaiswal ma'am, faculty members, and examiners for their guidance and support. "
        "We are now open to any questions or suggestions. Thank you!"
    )

    output_path = "Ghidora_Transport_College_Project_Presentation.pptx"
    prs.save(output_path)
    print(f"Synopsis-aligned presentation successfully created: '{output_path}' with {len(prs.slides)} slides!")

if __name__ == "__main__":
    build_synopsis_aligned_presentation()
