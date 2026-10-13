import os
import sys
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE

def create_presentation():
    prs = Presentation()
    # 16:9 widescreen layout
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_slide_layout = prs.slide_layouts[6] # Blank layout

    # Colors
    NAVY = RGBColor(15, 23, 42)        # Slate 900
    PRIMARY = RGBColor(30, 58, 138)    # Blue 900
    ACCENT_BLUE = RGBColor(37, 99, 235)# Blue 600
    ACCENT_GOLD = RGBColor(217, 119, 6)# Amber 600
    BG_LIGHT = RGBColor(248, 250, 252) # Slate 50
    CARD_BG = RGBColor(255, 255, 255)  # White
    CARD_BORDER = RGBColor(226, 232, 240) # Slate 200
    TEXT_DARK = RGBColor(15, 23, 42)   # Slate 900
    TEXT_MUTED = RGBColor(100, 116, 139) # Slate 500
    WHITE = RGBColor(255, 255, 255)

    def set_slide_background(slide, color=BG_LIGHT):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(7.5))
        bg.fill.solid()
        bg.fill.fore_color.rgb = color
        bg.line.fill.background() # No border
        return bg

    def add_header(slide, title_text, category="GHIDORA TRANSPORT - MCA PROJECT PRESENTATION"):
        # Top accent bar
        bar = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.12))
        bar.fill.solid()
        bar.fill.fore_color.rgb = ACCENT_GOLD
        bar.line.fill.background()

        # Header card banner
        banner = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0.12), Inches(13.333), Inches(1.1))
        banner.fill.solid()
        banner.fill.fore_color.rgb = NAVY
        banner.line.fill.background()

        # Category text
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.2), Inches(9.0), Inches(0.3))
        cat_tf = cat_box.text_frame
        cat_tf.word_wrap = True
        p_cat = cat_tf.paragraphs[0]
        p_cat.text = category.upper()
        p_cat.font.size = Pt(10)
        p_cat.font.bold = True
        p_cat.font.color.rgb = ACCENT_GOLD

        # Title text
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.48), Inches(9.0), Inches(0.65))
        title_tf = title_box.text_frame
        title_tf.word_wrap = True
        p_title = title_tf.paragraphs[0]
        p_title.text = title_text
        p_title.font.size = Pt(22)
        p_title.font.bold = True
        p_title.font.color.rgb = WHITE

        # Right header tag
        tag_box = slide.shapes.add_textbox(Inches(10.0), Inches(0.35), Inches(2.6), Inches(0.6))
        tag_tf = tag_box.text_frame
        p_tag = tag_tf.paragraphs[0]
        p_tag.text = "SSPU BHILAI\nMCA 3rd SEM"
        p_tag.alignment = PP_ALIGN.RIGHT
        p_tag.font.size = Pt(11)
        p_tag.font.bold = True
        p_tag.font.color.rgb = RGBColor(148, 163, 184)

        # Bottom footer
        footer_box = slide.shapes.add_textbox(Inches(0.8), Inches(7.15), Inches(11.733), Inches(0.3))
        ftf = footer_box.text_frame
        p_f = ftf.paragraphs[0]
        p_f.text = "Ghidora Transport | MCA Major Project | Shri Shankaracharya Professional University, Bhilai | Amit Kumar Sahu"
        p_f.font.size = Pt(9)
        p_f.font.color.rgb = TEXT_MUTED

    def add_card(slide, left, top, width, height, bg_color=CARD_BG, border_color=CARD_BORDER):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = bg_color
        card.line.color.rgb = border_color
        card.line.width = Pt(1.5)
        return card

    # ==========================================
    # SLIDE 1: TITLE SLIDE
    # ==========================================
    slide1 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide1, NAVY)

    # Decorative accent graphic
    top_bar = slide1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.15))
    top_bar.fill.solid()
    top_bar.fill.fore_color.rgb = ACCENT_GOLD
    top_bar.line.fill.background()

    # Large Main Title Box
    title_box = slide1.shapes.add_textbox(Inches(1.0), Inches(1.0), Inches(11.333), Inches(2.4))
    tf1 = title_box.text_frame
    tf1.word_wrap = True
    
    p0 = tf1.paragraphs[0]
    p0.text = "COLLEGE MAJOR PROJECT PRESENTATION"
    p0.font.size = Pt(14)
    p0.font.bold = True
    p0.font.color.rgb = ACCENT_GOLD

    p1 = tf1.add_paragraph()
    p1.text = "GHIDORA TRANSPORT"
    p1.font.size = Pt(44)
    p1.font.bold = True
    p1.font.color.rgb = WHITE
    p1.space_before = Pt(8)

    p2 = tf1.add_paragraph()
    p2.text = "Smart Web-Based Logistics, Fleet & On-Demand Transport Management System"
    p2.font.size = Pt(18)
    p2.font.color.rgb = RGBColor(191, 219, 254)
    p2.space_before = Pt(6)

    # Info Cards Container on Title Slide
    # Left Card: Student Info
    add_card(slide1, Inches(1.0), Inches(3.6), Inches(5.4), Inches(2.8), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    s_box = slide1.shapes.add_textbox(Inches(1.3), Inches(3.8), Inches(4.8), Inches(2.4))
    s_tf = s_box.text_frame
    s_tf.word_wrap = True

    p_s0 = s_tf.paragraphs[0]
    p_s0.text = "SUBMITTED BY:"
    p_s0.font.size = Pt(12)
    p_s0.font.bold = True
    p_s0.font.color.rgb = ACCENT_GOLD

    p_s1 = s_tf.add_paragraph()
    p_s1.text = "Amit Kumar Sahu"
    p_s1.font.size = Pt(22)
    p_s1.font.bold = True
    p_s1.font.color.rgb = WHITE
    p_s1.space_before = Pt(6)

    p_s2 = s_tf.add_paragraph()
    p_s2.text = "Program: Master of Computer Applications (MCA)\nSemester: 3rd Semester\nDepartment: Department of Computer Applications"
    p_s2.font.size = Pt(13)
    p_s2.font.color.rgb = RGBColor(203, 213, 225)
    p_s2.space_before = Pt(8)

    # Right Card: Institution Info
    add_card(slide1, Inches(6.9), Inches(3.6), Inches(5.4), Inches(2.8), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    i_box = slide1.shapes.add_textbox(Inches(7.2), Inches(3.8), Inches(4.8), Inches(2.4))
    i_tf = i_box.text_frame
    i_tf.word_wrap = True

    p_i0 = i_tf.paragraphs[0]
    p_i0.text = "SUBMITTED TO:"
    p_i0.font.size = Pt(12)
    p_i0.font.bold = True
    p_i0.font.color.rgb = ACCENT_GOLD

    p_i1 = i_tf.add_paragraph()
    p_i1.text = "Shri Shankaracharya Professional University"
    p_i1.font.size = Pt(19)
    p_i1.font.bold = True
    p_i1.font.color.rgb = WHITE
    p_i1.space_before = Pt(6)

    p_i2 = i_tf.add_paragraph()
    p_i2.text = "Bhilai, Chhattisgarh, India\nAcademic Session: 2025 - 2026\nUnder the Guidance of: Project Coordinator & Faculty"
    p_i2.font.size = Pt(13)
    p_i2.font.color.rgb = RGBColor(203, 213, 225)
    p_i2.space_before = Pt(8)

    # Slide 1 Notes
    slide1.notes_slide.notes_text_frame.text = (
        "Good morning / afternoon respected professors and external examiners. "
        "My name is Amit Kumar Sahu, a student of MCA 3rd Semester at Shri Shankaracharya Professional University, Bhilai. "
        "Today, I am pleased to present my major project titled 'Ghidora Transport - A Smart Web-Based Logistics & Fleet Management System'."
    )

    # ==========================================
    # SLIDE 2: PRESENTATION OUTLINE
    # ==========================================
    slide2 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide2)
    add_header(slide2, "Presentation Outline & Agenda")

    # 4 Agenda Columns/Cards
    agenda_items = [
        ("01. FOUNDATION", ["Project Overview & Abstract", "Problem Statement & Need", "Aims & Core Objectives", "Market Relevance"]),
        ("02. ARCHITECTURE", ["Technology Stack (Full)", "System Architecture (MVT)", "System Modules Breakdown", "Data Flow Diagram (DFD)"]),
        ("03. IMPLEMENTATION", ["Database Design & Models", "Key Functional Features", "Pickupwala & Booking", "Security & Validation"]),
        ("04. EVALUATION", ["Testing & Code Quality", "Advantages & Impact", "Future Enhancements", "Conclusion & References"])
    ]

    left_positions = [Inches(0.8), Inches(3.8), Inches(6.8), Inches(9.8)]
    for i, (col_title, items) in enumerate(agenda_items):
        add_card(slide2, left_positions[i], Inches(1.6), Inches(2.7), Inches(5.1))
        box = slide2.shapes.add_textbox(left_positions[i] + Inches(0.15), Inches(1.8), Inches(2.4), Inches(4.7))
        tf = box.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = col_title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = PRIMARY
        
        for item in items:
            p_item = tf.add_paragraph()
            p_item.text = f"• {item}"
            p_item.font.size = Pt(12)
            p_item.font.color.rgb = TEXT_DARK
            p_item.space_before = Pt(10)

    slide2.notes_slide.notes_text_frame.text = (
        "Here is the outline of today's presentation. I will cover the foundation of the project, "
        "the technical architecture and tech stack, the implementation details with database schema, "
        "and finally testing, benefits, future scope and conclusion."
    )

    # ==========================================
    # SLIDE 3: PROJECT OVERVIEW & ABSTRACT
    # ==========================================
    slide3 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide3)
    add_header(slide3, "Project Overview & Abstract")

    # Left Hero Box
    add_card(slide3, Inches(0.8), Inches(1.6), Inches(6.8), Inches(5.1))
    box = slide3.shapes.add_textbox(Inches(1.1), Inches(1.8), Inches(6.2), Inches(4.6))
    tf = box.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "What is Ghidora Transport?"
    p.font.size = Pt(18)
    p.font.bold = True
    p.font.color.rgb = PRIMARY

    abstract_points = [
        ("Digital Logistics Platform", "An enterprise web solution built with Python & Django to streamline commercial transportation and goods movement in regional and urban areas."),
        ("Direct Booking & Quotations", "Enables individuals and businesses to book commercial vehicles (Pickups, Boleros, Mini Trucks) with automated distance and route fare calculation."),
        ("Fleet & Driver Administration", "Equips transport business owners with centralized tracking of drivers, daily trips, fuel expenses, and toll disbursements."),
        ("Integrated Support Ecosystem", "Includes an intelligent Chatbot assistant, social review hub, and verifiable PDF quotation generator for complete end-to-end service.")
    ]

    for title, desc in abstract_points:
        p_sub = tf.add_paragraph()
        p_sub.text = f"✔ {title}:"
        p_sub.font.size = Pt(13)
        p_sub.font.bold = True
        p_sub.font.color.rgb = ACCENT_BLUE
        p_sub.space_before = Pt(10)

        p_desc = tf.add_paragraph()
        p_desc.text = desc
        p_desc.font.size = Pt(11.5)
        p_desc.font.color.rgb = TEXT_DARK
        p_desc.space_before = Pt(2)

    # Right Highlights Column (3 mini cards)
    right_cards = [
        ("TARGET SECTOR", "Local & Regional Freight, Commercial Vehicles, Marriage/Occasion Fleet Rentals", ACCENT_GOLD),
        ("PRIMARY USERS", "Cargo Customers, Small Businesses, Commercial Fleet Owners & Professional Drivers", PRIMARY),
        ("CORE VALUE", "Zero booking friction, transparent pricing, automated expense auditing & paperless management", ACCENT_BLUE)
    ]
    for idx, (title, desc, color) in enumerate(right_cards):
        top_pos = Inches(1.6 + idx * 1.8)
        card = add_card(slide3, Inches(8.0), top_pos, Inches(4.5), Inches(1.5))
        cbox = slide3.shapes.add_textbox(Inches(8.2), top_pos + Inches(0.15), Inches(4.1), Inches(1.2))
        ctf = cbox.text_frame
        ctf.word_wrap = True

        cp1 = ctf.paragraphs[0]
        cp1.text = title
        cp1.font.size = Pt(12)
        cp1.font.bold = True
        cp1.font.color.rgb = color

        cp2 = ctf.add_paragraph()
        cp2.text = desc
        cp2.font.size = Pt(11.5)
        cp2.font.color.rgb = TEXT_DARK
        cp2.space_before = Pt(4)

    slide3.notes_slide.notes_text_frame.text = (
        "Ghidora Transport was conceptualized to address the unorganized transport and logistics sector. "
        "In cities like Bhilai, Durg, and Raipur, finding reliable commercial transport for goods or events often requires "
        "manual phone calls and arbitrary price negotiations. Ghidora Transport solves this by digitizing the entire flow."
    )

    # ==========================================
    # SLIDE 4: PROBLEM STATEMENT & MOTIVATION
    # ==========================================
    slide4 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide4)
    add_header(slide4, "Problem Statement & Need Analysis")

    # 4 Problem Cards in 2x2 Grid
    problems = [
        ("1. Manual Booking & Fare Disputes", 
         "Traditional transport bookings rely heavily on unrecorded phone calls and handwritten notes. Without verified distance calculation, frequent disputes arise between customers and vehicle owners regarding rates, toll charges, and waiting times.",
         RGBColor(239, 68, 68)), # Red
        
        ("2. Lack of Centralized Fleet Tracking", 
         "Transporters lack real-time visibility into driver assignments, trip progress, and vehicle availability. This causes vehicle underutilization and missed pickup commitments.",
         RGBColor(234, 88, 12)), # Orange

        ("3. Inefficient Expense & Toll Auditing", 
         "Tracking daily operational expenses like diesel, maintenance, driver allowances, and toll plaza payments is done on paper slips which often get lost, leading to revenue leakage.",
         RGBColor(217, 119, 6)), # Amber

        ("4. Delayed Quotations for Bulk / Events", 
         "Commercial clients or families booking multiple vehicles for marriages and bulk shipments must wait hours or days for formal quotations, leading to lost business opportunities.",
         RGBColor(37, 99, 235)) # Blue
    ]

    grid_pos = [
        (Inches(0.8), Inches(1.6)),
        (Inches(6.8), Inches(1.6)),
        (Inches(0.8), Inches(4.3)),
        (Inches(6.8), Inches(4.3)),
    ]

    for idx, (title, text, col) in enumerate(problems):
        gx, gy = grid_pos[idx]
        add_card(slide4, gx, gy, Inches(5.7), Inches(2.4))
        pbox = slide4.shapes.add_textbox(gx + Inches(0.25), gy + Inches(0.2), Inches(5.2), Inches(2.0))
        ptf = pbox.text_frame
        ptf.word_wrap = True

        p1 = ptf.paragraphs[0]
        p1.text = title
        p1.font.size = Pt(14)
        p1.font.bold = True
        p1.font.color.rgb = col

        p2 = ptf.add_paragraph()
        p2.text = text
        p2.font.size = Pt(11.5)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(6)

    slide4.notes_slide.notes_text_frame.text = (
        "Here we identify four primary challenges in the current transport industry: "
        "unstructured booking, zero centralized driver tracking, financial leakage from unmonitored expenses, "
        "and slow manual quotation turnaround. Ghidora Transport was built to specifically solve each of these pain points."
    )

    # ==========================================
    # SLIDE 5: PROJECT OBJECTIVES
    # ==========================================
    slide5 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide5)
    add_header(slide5, "Project Objectives & Scope")

    objectives = [
        ("Automated On-Demand Booking", "Develop a seamless web interface for customers to select vehicles (Bolero, Pickup, Magic, Truck) with transparent pricing based on pickup, destination, and distance."),
        ("Intelligent Fare & Toll Computation", "Implement dynamic algorithms supporting both Predefined Route Fares and Distance-based fares with toll/parking screenshot verification."),
        ("Dedicated 'Pickupwala' Logistics Engine", "Create a specialized logistics workflow tailored for local goods dispatch, weight capacity choices (kg/ton), and priority scheduling."),
        ("Driver & Trip Dispatch Management", "Provide administrative controls to register drivers, verify driving licenses, monitor availability, and assign vehicles per trip."),
        ("Financial & Expense Auditing", "Provide systematic logging of fuel costs, vehicle repairs, and toll receipts to give fleet owners a clear profit-and-loss overview."),
        ("AI Chatbot & Social Trust Ecosystem", "Integrate an interactive customer support chatbot and a public review system to build trust and resolve queries 24/7 without human delay.")
    ]

    for i, (obj_title, obj_desc) in enumerate(objectives):
        row = i // 2
        col = i % 2
        pos_x = Inches(0.8 if col == 0 else 6.8)
        pos_y = Inches(1.6 + row * 1.75)

        add_card(slide5, pos_x, pos_y, Inches(5.7), Inches(1.6))
        ob_box = slide5.shapes.add_textbox(pos_x + Inches(0.2), pos_y + Inches(0.12), Inches(5.3), Inches(1.35))
        ob_tf = ob_box.text_frame
        ob_tf.word_wrap = True

        p1 = ob_tf.paragraphs[0]
        p1.text = f"🎯 {obj_title}"
        p1.font.size = Pt(13.5)
        p1.font.bold = True
        p1.font.color.rgb = PRIMARY

        p2 = ob_tf.add_paragraph()
        p2.text = obj_desc
        p2.font.size = Pt(11)
        p2.font.color.rgb = TEXT_DARK
        p2.space_before = Pt(3)

    slide5.notes_slide.notes_text_frame.text = (
        "Our project objectives are comprehensive and focused on end-to-end digitization. "
        "Key goals include automated vehicle booking, transparent fare calculation, specialized logistics via 'Pickupwala', "
        "fleet expense monitoring, and an interactive customer chatbot."
    )

    # ==========================================
    # SLIDE 6: TECHNOLOGY STACK
    # ==========================================
    slide6 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide6)
    add_header(slide6, "Technology Stack & Development Tools")

    tech_cards = [
        ("BACKEND TECHNOLOGIES", [
            ("Python 3.12+", "Primary programming language offering high performance and readability."),
            ("Django 5.x Framework", "Robust Web framework following MVT (Model-View-Template) pattern."),
            ("Django ORM", "Secure database abstraction protecting against SQL injection attacks."),
            ("Django Auth & Sessions", "Role-based access control, cryptographic password hashing.")
        ], PRIMARY),
        ("FRONTEND & UI DESIGN", [
            ("HTML5 & Modern CSS3", "Semantic markup with custom glassmorphism and clean typography."),
            ("JavaScript (ES6+)", "Dynamic UI interactivity, asynchronous fetching, and form validation."),
            ("Responsive Mobile UI", "Optimized viewports for desktop, tablets, and mobile smartphones."),
            ("Font Awesome & Icons", "Intuitive iconography for vehicles, status badges, and actions.")
        ], ACCENT_BLUE),
        ("DATABASE & STORAGE", [
            ("SQLite3 (Development)", "Zero-configuration relational database for agile local development."),
            ("PostgreSQL (Production)", "Enterprise ACID-compliant database ready for cloud deployment."),
            ("Pillow (PIL)", "Image handling and compression for toll slips & vehicle photos."),
            ("Media & Static Storage", "Organized file structure for uploads, scripts, and stylesheets.")
        ], NAVY),
        ("INTEGRATIONS & DEPLOYMENT", [
            ("AI / Rule-Based Chatbot", "Intelligent response system for instant transport inquiry handling."),
            ("PDF & QR Generator", "Dynamic quotation generation and scannable verification codes."),
            ("Render / Cloud Ready", "Configured Procfile, build scripts, and production environment."),
            ("Git & GitHub", "Version control system managing commits and feature branches.")
        ], ACCENT_GOLD)
    ]

    for idx, (title, items, color) in enumerate(tech_cards):
        cx = left_positions[idx]
        add_card(slide6, cx, Inches(1.6), Inches(2.7), Inches(5.1))
        tbox = slide6.shapes.add_textbox(cx + Inches(0.12), Inches(1.75), Inches(2.45), Inches(4.8))
        ttf = tbox.text_frame
        ttf.word_wrap = True

        tp = ttf.paragraphs[0]
        tp.text = title
        tp.font.size = Pt(12)
        tp.font.bold = True
        tp.font.color.rgb = color

        for name, desc in items:
            p_n = ttf.add_paragraph()
            p_n.text = f"• {name}"
            p_n.font.size = Pt(11.5)
            p_n.font.bold = True
            p_n.font.color.rgb = TEXT_DARK
            p_n.space_before = Pt(6)

            p_d = ttf.add_paragraph()
            p_d.text = desc
            p_d.font.size = Pt(9.5)
            p_d.font.color.rgb = TEXT_MUTED
            p_d.space_before = Pt(1)

    slide6.notes_slide.notes_text_frame.text = (
        "For our technology stack, we selected Python and Django for the backend due to Django's batteries-included approach, "
        "built-in ORM security, and rapid development capabilities. The frontend is built using clean HTML5, CSS3, and JavaScript "
        "ensuring responsive mobile compatibility for on-the-road drivers and customers alike."
    )

    # ==========================================
    # SLIDE 7: SYSTEM ARCHITECTURE (MVT PATTERN)
    # ==========================================
    slide7 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide7)
    add_header(slide7, "System Architecture - Django MVT Design")

    # 3 Horizontal Architecture Tiers
    tiers = [
        ("1. USER & CLIENT PRESENTATION TIER (VIEW / TEMPLATES)",
         "HTML5, CSS3 Glassmorphism UI, Responsive Mobile Views, Booking Modals, Status Badges\n"
         "Handles user input: route selection, vehicle choice, cargo details, toll screenshot uploads, and real-time review feedback.",
         PRIMARY),
        ("2. APPLICATION LOGIC & CONTROLLER TIER (DJANGO VIEWS & ROUTING)",
         "URL Dispatcher -> Django Class/Function Views -> Business Calculation Services\n"
         "• Distance & Fare Calculation Engine (Predefined vs Google Distance calculation)\n"
         "• Quotation Builder (Automated PDF & Pricing generation)\n"
         "• Pickupwala Dispatch Engine & Driver Assignment Logic\n"
         "• Chatbot Natural Language matching engine & Expense Auditor",
         ACCENT_BLUE),
        ("3. DATA & PERSISTENCE TIER (DJANGO ORM & DATABASE)",
         "Relational Database (SQLite3 / PostgreSQL) with relational integrity & Foreign Key constraints\n"
         "Tables: Users/Auth, Bookings, Drivers, Vehicles, Expenses, Toll Slips, Quotations, Social Reviews.\n"
         "Protected by Django ORM with automated migrations and parameterized query execution.",
         NAVY)
    ]

    for i, (title, content, col) in enumerate(tiers):
        ty = Inches(1.6 + i * 1.75)
        add_card(slide7, Inches(0.8), ty, Inches(11.733), Inches(1.6))
        
        # Left color indicator
        ind = slide7.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), ty, Inches(0.15), Inches(1.6))
        ind.fill.solid()
        ind.fill.fore_color.rgb = col
        ind.line.fill.background()

        abox = slide7.shapes.add_textbox(Inches(1.2), ty + Inches(0.12), Inches(11.1), Inches(1.35))
        atf = abox.text_frame
        atf.word_wrap = True

        ap1 = atf.paragraphs[0]
        ap1.text = title
        ap1.font.size = Pt(13)
        ap1.font.bold = True
        ap1.font.color.rgb = col

        ap2 = atf.add_paragraph()
        ap2.text = content
        ap2.font.size = Pt(10.5)
        ap2.font.color.rgb = TEXT_DARK
        ap2.space_before = Pt(4)

    slide7.notes_slide.notes_text_frame.text = (
        "Ghidora Transport follows Django's proven Model-View-Template (MVT) architecture. "
        "The Presentation Tier handles user interaction on both mobile and desktop. "
        "The Controller and Logic Tier coordinates fare calculation, quotation generation, and chatbot responses. "
        "The Persistence Tier guarantees transactional safety and data integrity."
    )

    # ==========================================
    # SLIDE 8: CORE MODULES - PART 1 (CUSTOMER FACING)
    # ==========================================
    slide8 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide8)
    add_header(slide8, "Key Modules: Customer & Booking Workflows")

    mod_customer = [
        ("Online Booking System", [
            "Real-time vehicle selection: Bolero, Mahindra Pickup, Cruiser, Magic, Mini Truck.",
            "Dynamic pickup & drop destination inputs with instant distance mapping.",
            "Choice of Predefined Route Fare or Per-Kilometer Distance Rate.",
            "Toll & parking charges upload mechanism with receipt verification.",
            "Generates unique alphanumeric Booking ID for easy tracking."
        ]),
        ("Pickupwala Logistics Engine", [
            "Specialized module tailored for micro-freight, shifting, and shop inventory.",
            "Configurable cargo weight limits (Kilograms and Tons).",
            "Pickup scheduling: Immediate vs. Planned dispatch options.",
            "Driver location and availability matching for rapid turnaround."
        ]),
        ("Quotation Generation System", [
            "Instant custom quotation creator for marriage, events, or corporate logistics.",
            "Auto-computes estimated vehicle requirements, distance, and base prices.",
            "Clean printable / downloadable quotation layout for client sign-off.",
            "Status pipeline: Draft -> Under Review -> Approved -> Booked."
        ]),
        ("AI Support Chatbot & Helpdesk", [
            "24/7 automated transport inquiry responder embedded on every screen.",
            "Answers questions about vehicle load capacities, rates per km, and policies.",
            "Zero wait-time customer assistance reducing telephone workload."
        ])
    ]

    for idx, (title, points) in enumerate(mod_customer):
        gx, gy = grid_pos[idx]
        add_card(slide8, gx, gy, Inches(5.7), Inches(2.4))
        mbox = slide8.shapes.add_textbox(gx + Inches(0.2), gy + Inches(0.15), Inches(5.3), Inches(2.1))
        mtf = mbox.text_frame
        mtf.word_wrap = True

        p1 = mtf.paragraphs[0]
        p1.text = f"📦 {title}"
        p1.font.size = Pt(13.5)
        p1.font.bold = True
        p1.font.color.rgb = PRIMARY

        for pt in points:
            p_pt = mtf.add_paragraph()
            p_pt.text = f"• {pt}"
            p_pt.font.size = Pt(10.5)
            p_pt.font.color.rgb = TEXT_DARK
            p_pt.space_before = Pt(3)

    slide8.notes_slide.notes_text_frame.text = (
        "Here are the four key customer-facing modules: the main vehicle Booking system, "
        "the 'Pickupwala' module dedicated to local freight and cargo, "
        "the Quotation builder for bulk and occasion bookings, and the integrated AI Chatbot for instant support."
    )

    # ==========================================
    # SLIDE 9: CORE MODULES - PART 2 (ADMIN & FLEET OPS)
    # ==========================================
    slide9 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide9)
    add_header(slide9, "Key Modules: Fleet & Operations Management")

    mod_admin = [
        ("Driver & Vehicle Fleet Management", [
            "Central repository of registered commercial drivers with contact & license records.",
            "Vehicle fleet tracking (registration number, payload capacity, fitness, insurance).",
            "Real-time driver assignment to newly placed customer bookings.",
            "Driver status monitoring: Available, On Trip, On Leave."
        ]),
        ("Expense & Accounting Management", [
            "Granular operational expense logging: Diesel/Petrol, Maintenance, Tolls, Police/Challan.",
            "Receipt attachment upload to prevent bogus expense claims.",
            "Vehicle-wise expense auditing to calculate net profitability per vehicle.",
            "Date-range filtering for monthly and quarterly financial summaries."
        ]),
        ("Payments & Billing Hub", [
            "Multi-channel payment recording: Advance payment, Cash on Delivery (COD), UPI/Online.",
            "Automated fare settlement accounting with toll & parking reconciliation.",
            "Digital receipts and invoices generated for customer documentation."
        ]),
        ("Social Community & Review Engine", [
            "Customer feedback system with star ratings and honest text reviews.",
            "Community updates feed sharing transport routes and seasonal deals.",
            "Helps establish credibility and reputation in the local transport market."
        ])
    ]

    for idx, (title, points) in enumerate(mod_admin):
        gx, gy = grid_pos[idx]
        add_card(slide9, gx, gy, Inches(5.7), Inches(2.4))
        mbox = slide9.shapes.add_textbox(gx + Inches(0.2), gy + Inches(0.15), Inches(5.3), Inches(2.1))
        mtf = mbox.text_frame
        mtf.word_wrap = True

        p1 = mtf.paragraphs[0]
        p1.text = f"⚙ {title}"
        p1.font.size = Pt(13.5)
        p1.font.bold = True
        p1.font.color.rgb = ACCENT_GOLD

        for pt in points:
            p_pt = mtf.add_paragraph()
            p_pt.text = f"• {pt}"
            p_pt.font.size = Pt(10.5)
            p_pt.font.color.rgb = TEXT_DARK
            p_pt.space_before = Pt(3)

    slide9.notes_slide.notes_text_frame.text = (
        "On the administrative and fleet side, Ghidora Transport gives business owners complete control: "
        "Driver and vehicle management, daily operational expense tracking with receipt upload, "
        "multi-channel payment accounting, and a verified customer review engine."
    )

    # ==========================================
    # SLIDE 10: DATABASE DESIGN & KEY MODELS
    # ==========================================
    slide10 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide10)
    add_header(slide10, "Database Schema & Entity Relationship")

    # 4 Model Cards
    models_data = [
        ("Booking Model", [
            "booking_id (Char, Unique PK/Code)",
            "name, phone, email (Customer Info)",
            "pickup, destination (Locations)",
            "pickup_lat/lng, dest_lat/lng (Coordinates)",
            "vehicle_type (Choices: Bolero, Pickup, etc.)",
            "distance (Float) & distance_source",
            "fare (Float) & fare_type",
            "toll_charges, parking_charges (Floats)",
            "toll_screenshot (ImageField)",
            "status (Pending / Confirmed / Completed)"
        ]),
        ("Driver & Fleet Model", [
            "driver_name, phone_number",
            "license_number, emergency_contact",
            "vehicle_assigned (ForeignKey)",
            "vehicle_number, vehicle_type",
            "payload_capacity, fitness_validity",
            "is_active, is_available (Booleans)",
            "current_location / base_hub"
        ]),
        ("Expense Model", [
            "vehicle (ForeignKey to Fleet)",
            "category (Fuel, Maintenance, Toll, Other)",
            "amount (Decimal / Float)",
            "date_incurred (DateField)",
            "bill_receipt_image (ImageField)",
            "approved_by (Admin User)",
            "notes / remarks (TextField)"
        ]),
        ("Quotation & Review Model", [
            "quotation_id, client_name, client_phone",
            "cargo_description, weight_category",
            "from_city, to_city, estimated_distance",
            "quoted_amount, valid_until_date",
            "review_user, rating (1 to 5 Stars)",
            "review_comment, timestamp"
        ])
    ]

    for idx, (m_title, fields) in enumerate(models_data):
        cx = left_positions[idx]
        add_card(slide10, cx, Inches(1.6), Inches(2.7), Inches(5.1))
        mbox = slide10.shapes.add_textbox(cx + Inches(0.12), Inches(1.75), Inches(2.45), Inches(4.8))
        mtf = mbox.text_frame
        mtf.word_wrap = True

        mp = mtf.paragraphs[0]
        mp.text = m_title
        mp.font.size = Pt(12.5)
        mp.font.bold = True
        mp.font.color.rgb = PRIMARY

        p_h = mtf.add_paragraph()
        p_h.text = "ATTRIBUTES / SCHEMA:"
        p_h.font.size = Pt(9)
        p_h.font.bold = True
        p_h.font.color.rgb = ACCENT_GOLD
        p_h.space_before = Pt(4)

        for fld in fields:
            pf = mtf.add_paragraph()
            pf.text = f"• {fld}"
            pf.font.size = Pt(9.5)
            pf.font.color.rgb = TEXT_DARK
            pf.space_before = Pt(2)

    slide10.notes_slide.notes_text_frame.text = (
        "Here is the database schema design. The Booking model links customers, destinations, vehicle choices, "
        "and toll charges. The Driver model manages driver availability and vehicle assignments. "
        "The Expense model ensures auditability with image receipts, and the Quotation model handles commercial inquiries."
    )

    # ==========================================
    # SLIDE 11: WORKFLOW & DATA FLOW
    # ==========================================
    slide11 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide11)
    add_header(slide11, "End-to-End System Workflow (Data Flow)")

    # 5 Sequential Flow Steps
    steps = [
        ("STEP 1: USER REQUEST", "Customer visits portal, chooses vehicle type (Pickup / Bolero / Truck), enters origin and destination addresses."),
        ("STEP 2: PRICE COMPUTATION", "System calculates route distance, applies per-km rate chart, checks predefined routes, and displays transparent fare."),
        ("STEP 3: CONFIRMATION & DISPATCH", "Booking is logged with unique ID. Fleet administrator reviews trip details and assigns an available registered driver."),
        ("STEP 4: TRIP EXECUTION & AUDITING", "Driver conducts trip. Any toll or parking charges incurred are uploaded with receipt photos directly to the system."),
        ("STEP 5: INVOICE & SETTLEMENT", "Final bill reconciled with tolls. Customer receives digital invoice and provides verified rating on social feed.")
    ]

    step_colors = [PRIMARY, ACCENT_BLUE, NAVY, ACCENT_GOLD, RGBColor(16, 185, 129)] # Green for finish
    for i, (stitle, sdesc) in enumerate(steps):
        sy = Inches(1.6 + i * 1.05)
        add_card(slide11, Inches(0.8), sy, Inches(11.733), Inches(0.95))
        
        # Step Number Badge
        badge = slide11.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, Inches(1.0), sy + Inches(0.15), Inches(2.2), Inches(0.65))
        badge.fill.solid()
        badge.fill.fore_color.rgb = step_colors[i]
        badge.line.fill.background()
        btf = badge.text_frame
        bp = btf.paragraphs[0]
        bp.text = stitle
        bp.font.size = Pt(11)
        bp.font.bold = True
        bp.font.color.rgb = WHITE
        bp.alignment = PP_ALIGN.CENTER

        # Step Text
        sbox = slide11.shapes.add_textbox(Inches(3.4), sy + Inches(0.12), Inches(8.8), Inches(0.7))
        stf = sbox.text_frame
        stf.word_wrap = True
        sp = stf.paragraphs[0]
        sp.text = sdesc
        sp.font.size = Pt(11)
        sp.font.color.rgb = TEXT_DARK

    slide11.notes_slide.notes_text_frame.text = (
        "The end-to-end workflow follows a 5-step lifecycle: from initial user vehicle selection, "
        "automated route calculation, administrative driver assignment, execution with toll slip uploading, "
        "to final invoice settlement and customer feedback."
    )

    # ==========================================
    # SLIDE 12: SECURITY & SOFTWARE ENGINEERING PRACTICES
    # ==========================================
    slide12 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide12)
    add_header(slide12, "Security Implementation & Code Quality")

    sec_cards = [
        ("SQL Injection Protection", "All database transactions use Django ORM parameterized queries, completely insulating the system against SQL injection attempts.", PRIMARY),
        ("Cross-Site Request Forgery (CSRF)", "Every HTML form submission is protected by cryptographic CSRF tokens, preventing unauthorized cross-domain actions.", ACCENT_BLUE),
        ("Secure Authentication & Passwords", "User & admin credentials are encrypted using PBKDF2 with SHA256 hashing. Passwords are never stored in plaintext.", NAVY),
        ("File Upload Sanitization", "Toll receipts and driver document uploads are strictly validated by MIME-type and stored in designated media directories.", ACCENT_GOLD),
        ("Modular Architecture", "Clean separation into independent Django apps (booking, drivers, expenses, quotations, chatbot, social) ensuring high maintainability.", PRIMARY),
        ("Responsive Cross-Device Design", "Custom CSS layout optimized for both low-bandwidth mobile devices and widescreen administrative desktops.", ACCENT_BLUE)
    ]

    for i, (stitle, sdesc, col) in enumerate(sec_cards):
        row = i // 2
        col_idx = i % 2
        px = Inches(0.8 if col_idx == 0 else 6.8)
        py = Inches(1.6 + row * 1.75)

        add_card(slide12, px, py, Inches(5.7), Inches(1.6))
        sbox = slide12.shapes.add_textbox(px + Inches(0.2), py + Inches(0.12), Inches(5.3), Inches(1.35))
        stf = sbox.text_frame
        stf.word_wrap = True

        sp1 = stf.paragraphs[0]
        sp1.text = f"🛡 {stitle}"
        sp1.font.size = Pt(13)
        sp1.font.bold = True
        sp1.font.color.rgb = col

        sp2 = stf.add_paragraph()
        sp2.text = sdesc
        sp2.font.size = Pt(10.5)
        sp2.font.color.rgb = TEXT_DARK
        sp2.space_before = Pt(3)

    slide12.notes_slide.notes_text_frame.text = (
        "Security and code quality were given prime importance during implementation. "
        "Django's built-in security features such as CSRF tokens, ORM SQL injection prevention, "
        "and PBKDF2 password encryption were fully leveraged alongside modular code architecture."
    )

    # ==========================================
    # SLIDE 13: ADVANTAGES & BUSINESS IMPACT
    # ==========================================
    slide13 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide13)
    add_header(slide13, "Key Advantages & Real-World Impact")

    benefits = [
        ("FOR CUSTOMERS & SHIPPERS", [
            "Transparent upfront fare estimation without awkward verbal bargaining.",
            "Easy vehicle choice matching exact cargo volume and weight.",
            "24/7 self-service booking anytime without relying on office business hours.",
            "Instant quotation generation for marriages, family occasions, or shifting."
        ], PRIMARY),
        ("FOR FLEET OPERATORS & TRANSPORTERS", [
            "Complete digitization of vehicle roster, active trips, and driver schedules.",
            "100% auditable fuel and maintenance expenses backed by photo receipts.",
            "Eliminates revenue leakage and unauthorized vehicle usage.",
            "Ready for multi-city business expansion with unified cloud data."
        ], ACCENT_BLUE),
        ("FOR COMMERCIAL DRIVERS", [
            "Direct digital trip dispatch with exact pickup and drop address details.",
            "Documented toll and parking expense reimbursement without conflict.",
            "Professional digital profile helping build long-term driving records."
        ], NAVY)
    ]

    for idx, (title, pts, col) in enumerate(benefits):
        cx = Inches(0.8 + idx * 4.0)
        add_card(slide13, cx, Inches(1.6), Inches(3.7), Inches(5.1))
        bbox = slide13.shapes.add_textbox(cx + Inches(0.15), Inches(1.8), Inches(3.4), Inches(4.7))
        btf = bbox.text_frame
        btf.word_wrap = True

        bp = btf.paragraphs[0]
        bp.text = title
        bp.font.size = Pt(13)
        bp.font.bold = True
        bp.font.color.rgb = col

        for pt in pts:
            p_pt = btf.add_paragraph()
            p_pt.text = f"✔ {pt}"
            p_pt.font.size = Pt(11)
            p_pt.font.color.rgb = TEXT_DARK
            p_pt.space_before = Pt(8)

    slide13.notes_slide.notes_text_frame.text = (
        "The project delivers tangible value to all three stakeholders: "
        "Customers enjoy transparent pricing and zero bargaining; fleet owners gain auditable financial control; "
        "and drivers receive clear digital dispatch information and fair reimbursement."
    )

    # ==========================================
    # SLIDE 14: TESTING & QUALITY ASSURANCE
    # ==========================================
    slide14 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide14)
    add_header(slide14, "Testing, Validation & Quality Assurance")

    tests = [
        ("Unit & Model Testing", "Validated Django models (Booking, Driver, Expense) for field constraints, default values, null handlers, and foreign key cascading."),
        ("Functional & Route Testing", "Tested fare calculation algorithms across various distances and vehicle types, verifying accurate computation of per-km rates."),
        ("Media Upload & Toll Verification", "Tested uploading high-resolution toll plaza receipts and images, ensuring proper file path resolution and MIME checking."),
        ("Admin CRUD Operations", "Validated complete Create, Read, Update, Delete workflows across the Django Admin panel for fleet and driver records."),
        ("Cross-Browser Compatibility", "Tested the application across Google Chrome, Mozilla Firefox, Microsoft Edge, and mobile Chrome on Android."),
        ("Mobile Responsiveness", "Verified responsive rendering and modal behavior across screen viewports from 375px (smartphones) to 1920px (desktops).")
    ]

    for i, (ttitle, tdesc) in enumerate(tests):
        row = i // 2
        col_idx = i % 2
        px = Inches(0.8 if col_idx == 0 else 6.8)
        py = Inches(1.6 + row * 1.75)

        add_card(slide14, px, py, Inches(5.7), Inches(1.6))
        tbox = slide14.shapes.add_textbox(px + Inches(0.2), py + Inches(0.12), Inches(5.3), Inches(1.35))
        ttf = tbox.text_frame
        ttf.word_wrap = True

        tp1 = ttf.paragraphs[0]
        tp1.text = f"🧪 {ttitle}"
        tp1.font.size = Pt(13)
        tp1.font.bold = True
        tp1.font.color.rgb = PRIMARY

        tp2 = ttf.add_paragraph()
        tp2.text = tdesc
        tp2.font.size = Pt(10.5)
        tp2.font.color.rgb = TEXT_DARK
        tp2.space_before = Pt(3)

    slide14.notes_slide.notes_text_frame.text = (
        "Rigorous quality assurance was carried out. "
        "We performed unit testing on Django models, verified edge cases in distance fare calculation, "
        "checked file upload integrity for toll receipts, and ensured full cross-browser mobile responsiveness."
    )

    # ==========================================
    # SLIDE 15: FUTURE SCOPE & ENHANCEMENTS
    # ==========================================
    slide15 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide15)
    add_header(slide15, "Future Scope & Potential Enhancements")

    future_items = [
        ("Live GPS Vehicle Tracking", "Integrating Google Maps JavaScript API & GPS hardware sensors to provide live on-map tracking of assigned vehicles for shippers.", PRIMARY),
        ("Native Mobile App (Android/iOS)", "Building cross-platform Flutter / React Native applications with push notifications for drivers and customers.", ACCENT_BLUE),
        ("Automated WhatsApp / SMS Alerts", "Integrating Twilio or WhatsApp Cloud API for automated booking confirmations, driver contact dispatch, and arrival alerts.", NAVY),
        ("AI Dynamic Pricing & Route Optimization", "Applying Machine Learning models to predict high-demand festival seasons, return-load matching, and optimal fuel-efficient routes.", ACCENT_GOLD)
    ]

    for idx, (ftitle, fdesc, col) in enumerate(future_items):
        cx = left_positions[idx]
        add_card(slide15, cx, Inches(1.6), Inches(2.7), Inches(5.1))
        fbox = slide15.shapes.add_textbox(cx + Inches(0.15), Inches(1.8), Inches(2.4), Inches(4.7))
        ftf = fbox.text_frame
        ftf.word_wrap = True

        fp = ftf.paragraphs[0]
        fp.text = ftitle
        fp.font.size = Pt(13.5)
        fp.font.bold = True
        fp.font.color.rgb = col

        p_det = ftf.add_paragraph()
        p_det.text = fdesc
        p_det.font.size = Pt(11)
        p_det.font.color.rgb = TEXT_DARK
        p_det.space_before = Pt(12)

    slide15.notes_slide.notes_text_frame.text = (
        "While the current system fulfills all core requirements, future iterations can introduce "
        "real-time GPS map tracking, native Flutter mobile apps, automated WhatsApp status updates, "
        "and machine learning for return-load optimization."
    )

    # ==========================================
    # SLIDE 16: CONCLUSION
    # ==========================================
    slide16 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide16)
    add_header(slide16, "Conclusion & Project Summary")

    # Large Main Card
    add_card(slide16, Inches(1.0), Inches(1.6), Inches(11.333), Inches(5.1))
    c_box = slide16.shapes.add_textbox(Inches(1.4), Inches(1.9), Inches(10.5), Inches(4.5))
    ctf = c_box.text_frame
    ctf.word_wrap = True

    cp0 = ctf.paragraphs[0]
    cp0.text = "Project Summary & Learning Outcomes"
    cp0.font.size = Pt(20)
    cp0.font.bold = True
    cp0.font.color.rgb = PRIMARY

    concl_points = [
        ("Successful Problem Resolution", "Ghidora Transport successfully bridges the communication and operational gap in the regional commercial logistics market, transforming manual dispatching into an automated web portal."),
        ("Practical Mastery of MVT Architecture", "This capstone project provided in-depth practical exposure to Python, the Django web framework, relational schema modeling, security tokenization, and responsive UI engineering."),
        ("Industry-Aligned Features", "From dynamic fare algorithms and toll verification to automated quotation PDFs and an AI customer support chatbot, the system demonstrates high practical utility."),
        ("Scalable & Deployment-Ready", "The application has been engineered with a clean modular structure, prepared for real-world hosting and database migration from development to enterprise production.")
    ]

    for title, desc in concl_points:
        p_t = ctf.add_paragraph()
        p_t.text = f"✔ {title}:"
        p_t.font.size = Pt(13.5)
        p_t.font.bold = True
        p_t.font.color.rgb = ACCENT_BLUE
        p_t.space_before = Pt(10)

        p_d = ctf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(11.5)
        p_d.font.color.rgb = TEXT_DARK
        p_d.space_before = Pt(2)

    slide16.notes_slide.notes_text_frame.text = (
        "In conclusion, Ghidora Transport successfully meets all objectives of our MCA 3rd Semester curriculum. "
        "It provides a robust, secure, and scalable solution to commercial logistics problems, while giving me hands-on "
        "experience in modern full-stack Python and Django web development."
    )

    # ==========================================
    # SLIDE 17: THANK YOU & Q&A
    # ==========================================
    slide17 = prs.slides.add_slide(blank_slide_layout)
    set_slide_background(slide17, NAVY)

    # Top accent bar
    top_bar17 = slide17.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0), Inches(0), Inches(13.333), Inches(0.15))
    top_bar17.fill.solid()
    top_bar17.fill.fore_color.rgb = ACCENT_GOLD
    top_bar17.line.fill.background()

    # Thank you box
    ty_box = slide17.shapes.add_textbox(Inches(1.0), Inches(1.2), Inches(11.333), Inches(2.0))
    ty_tf = ty_box.text_frame
    ty_tf.word_wrap = True

    typ1 = ty_tf.paragraphs[0]
    typ1.text = "THANK YOU!"
    typ1.font.size = Pt(46)
    typ1.font.bold = True
    typ1.font.color.rgb = WHITE
    typ1.alignment = PP_ALIGN.CENTER

    typ2 = ty_tf.add_paragraph()
    typ2.text = "Any Questions or Suggestions?"
    typ2.font.size = Pt(22)
    typ2.font.color.rgb = ACCENT_GOLD
    typ2.alignment = PP_ALIGN.CENTER
    typ2.space_before = Pt(8)

    # Info card in center
    add_card(slide17, Inches(2.5), Inches(3.5), Inches(8.333), Inches(3.0), bg_color=RGBColor(30, 41, 59), border_color=RGBColor(51, 65, 85))
    cinfo_box = slide17.shapes.add_textbox(Inches(2.8), Inches(3.7), Inches(7.7), Inches(2.6))
    citf = cinfo_box.text_frame
    citf.word_wrap = True

    cip1 = citf.paragraphs[0]
    cip1.text = "PROJECT PRESENTED BY:"
    cip1.font.size = Pt(12)
    cip1.font.bold = True
    cip1.font.color.rgb = ACCENT_GOLD
    cip1.alignment = PP_ALIGN.CENTER

    cip2 = citf.add_paragraph()
    cip2.text = "AMIT KUMAR SAHU"
    cip2.font.size = Pt(24)
    cip2.font.bold = True
    cip2.font.color.rgb = WHITE
    cip2.alignment = PP_ALIGN.CENTER
    cip2.space_before = Pt(4)

    cip3 = citf.add_paragraph()
    cip3.text = "Master of Computer Applications (MCA) – 3rd Semester\nDepartment of Computer Applications\nShri Shankaracharya Professional University (SSPU), Bhilai"
    cip3.font.size = Pt(13.5)
    cip3.font.color.rgb = RGBColor(203, 213, 225)
    cip3.alignment = PP_ALIGN.CENTER
    cip3.space_before = Pt(6)

    slide17.notes_slide.notes_text_frame.text = (
        "Thank you to my respected project guide, department faculty, and examiners for your valuable time and guidance. "
        "I am now open to any questions or feedback regarding the Ghidora Transport project."
    )

    output_filename = "Ghidora_Transport_College_Project_Presentation.pptx"
    prs.save(output_filename)
    print(f"Presentation saved successfully as '{output_filename}' with {len(prs.slides)} slides!")

if __name__ == "__main__":
    create_presentation()
