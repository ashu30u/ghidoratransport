"""
Ghidora Transport ER Diagram Generator
Generates:
1. ghidora_transport_er_diagram.svg (Vector SVG)
2. ghidora_transport_er_diagram.png (High Resolution 3200x2000 PNG via Chrome/Edge headless)
3. ghidora_transport_er_diagram_source.dot (Graphviz DOT source)
4. ghidora_transport_er_diagram_source.mmd (Mermaid ER diagram source)
5. ghidora_transport_er_diagram_explanation.md (Academic Viva Explanation)
"""

import os
import sys
import subprocess
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "project_documentation" / "er_diagram"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

SVG_PATH = OUTPUT_DIR / "ghidora_transport_er_diagram.svg"
PNG_PATH = OUTPUT_DIR / "ghidora_transport_er_diagram.png"
DOT_PATH = OUTPUT_DIR / "ghidora_transport_er_diagram_source.dot"
MMD_PATH = OUTPUT_DIR / "ghidora_transport_er_diagram_source.mmd"
EXPLANATION_PATH = OUTPUT_DIR / "ghidora_transport_er_diagram_explanation.md"


def build_svg():
    # Canvas dimensions
    width = 2500
    height = 1560

    svg_lines = []
    svg_lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">')
    
    # Defs: Filters, Gradients, Styles
    svg_lines.append("""
  <defs>
    <!-- Soft Drop Shadow -->
    <filter id="shadow" x="-8%" y="-8%" width="120%" height="120%">
      <feDropShadow dx="0" dy="4" stdDeviation="5" flood-color="#0f172a" flood-opacity="0.12"/>
    </filter>
    <filter id="glow" x="-10%" y="-10%" width="125%" height="125%">
      <feDropShadow dx="0" dy="2" stdDeviation="3" flood-color="#1e3a8a" flood-opacity="0.25"/>
    </filter>

    <!-- Entity Gradient: Deep Royal Blue to Rich Cobalt -->
    <linearGradient id="entityGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#2563EB" />
      <stop offset="100%" stop-color="#1E3A8A" />
    </linearGradient>

    <!-- Central Booking Entity Gradient: Special Vibrant Sapphire -->
    <linearGradient id="bookingGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#3B82F6" />
      <stop offset="100%" stop-color="#1D4ED8" />
    </linearGradient>

    <!-- Relationship Gradient: Rich Crimson to Ruby Red -->
    <linearGradient id="relGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#EF4444" />
      <stop offset="100%" stop-color="#B91C1C" />
    </linearGradient>

    <!-- Attribute Gradient: Fresh Meadow Green -->
    <linearGradient id="attrGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#ECFDF5" />
      <stop offset="100%" stop-color="#A7F3D0" />
    </linearGradient>

    <!-- Composite Attribute Gradient: Soft Sky Blue -->
    <linearGradient id="compGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#F0F9FF" />
      <stop offset="100%" stop-color="#BAE6FD" />
    </linearGradient>

    <!-- Primary Key Highlight Gradient -->
    <linearGradient id="pkGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#FEF3C7" />
      <stop offset="100%" stop-color="#FDE68A" />
    </linearGradient>

    <style>
      .title-main { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 32px; font-weight: 800; fill: #0F172A; letter-spacing: 2.5px; }
      .title-sub1 { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 19px; font-style: italic; font-weight: 600; fill: #334155; }
      .title-sub2 { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 16px; font-style: italic; font-weight: 700; fill: #2563EB; letter-spacing: 1px; }
      
      .entity-text { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 16px; font-weight: 700; fill: #FFFFFF; text-anchor: middle; dominant-baseline: central; letter-spacing: 0.5px; }
      .entity-subtext { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 11px; font-weight: 500; fill: #BFDBFE; text-anchor: middle; dominant-baseline: central; }
      
      .rel-text { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 14px; font-weight: 700; font-style: italic; fill: #FFFFFF; text-anchor: middle; dominant-baseline: central; }
      
      .attr-text { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: 600; fill: #064E3B; text-anchor: middle; dominant-baseline: central; }
      .attr-pk-text { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: 800; fill: #064E3B; text-anchor: middle; dominant-baseline: central; text-decoration: underline; }
      .comp-text { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 12px; font-weight: 700; fill: #0369A1; text-anchor: middle; dominant-baseline: central; }
      
      .card-text { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 14.5px; font-weight: 800; font-style: italic; fill: #DC2626; text-anchor: middle; dominant-baseline: central; }
      
      .legend-title { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 15px; font-weight: 800; fill: #0F172A; letter-spacing: 1px; }
      .legend-text { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 12.5px; font-weight: 600; fill: #334155; }
      .meta-text { font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; font-size: 11px; font-weight: 500; fill: #64748B; }
    </style>
  </defs>
""")

    # Background
    svg_lines.append(f'  <!-- Canvas Background -->')
    svg_lines.append(f'  <rect width="{width}" height="{height}" fill="#FFFFFF" />')
    svg_lines.append(f'  <!-- Subtle Grid Pattern / Frame -->')
    svg_lines.append(f'  <rect x="15" y="15" width="{width-30}" height="{height-30}" rx="12" fill="none" stroke="#E2E8F0" stroke-width="2" />')

    # Header
    svg_lines.append("""
  <!-- ==================== HEADER SECTION ==================== -->
  <g id="header" transform="translate(1250, 25)">
    <rect x="-420" y="5" width="840" height="90" rx="10" fill="#F8FAFC" stroke="#E2E8F0" stroke-width="1.5" />
    <text x="0" y="32" class="title-main" text-anchor="middle">GHIDORA TRANSPORT</text>
    <text x="0" y="58" class="title-sub1" text-anchor="middle">Online Booking Transport Platform</text>
    <text x="0" y="80" class="title-sub2" text-anchor="middle">DATABASE ER DIAGRAM (CHEN&#39;S NOTATION)</text>
    <line x1="-360" y1="95" x2="360" y2="95" stroke="#2563EB" stroke-width="3" stroke-linecap="round" />
  </g>
""")

    # Data structures for elements
    entities = {}
    relationships = {}
    attributes = {}
    links = []

    def add_entity(e_id, name, cx, cy, w, h, subtext="", is_central=False):
        entities[e_id] = {
            "name": name, "cx": cx, "cy": cy, "w": w, "h": h,
            "subtext": subtext, "is_central": is_central
        }

    def add_rel(r_id, name, cx, cy, w=110, h=56):
        relationships[r_id] = {
            "name": name, "cx": cx, "cy": cy, "w": w, "h": h
        }

    def add_attr(a_id, name, parent_id, cx, cy, rx=48, ry=18, is_pk=False, is_comp=False, is_multi=False):
        attributes[a_id] = {
            "name": name, "parent": parent_id, "cx": cx, "cy": cy,
            "rx": rx, "ry": ry, "is_pk": is_pk, "is_comp": is_comp, "is_multi": is_multi
        }

    def add_link(from_id, to_id, card1=None, card1_pos=None, card2=None, card2_pos=None):
        links.append({
            "from": from_id, "to": to_id,
            "card1": card1, "card1_pos": card1_pos,
            "card2": card2, "card2_pos": card2_pos
        })

    # -------------------------------------------------------------
    # 1. ENTITIES
    # -------------------------------------------------------------
    # User / Customer (Center Top)
    add_entity("user", "Customer / User", 1250, 220, 200, 56, subtext="auth_user")

    # Central Hub: Booking (Center)
    add_entity("booking", "Booking", 1250, 600, 220, 66, subtext="booking_booking", is_central=True)

    # BookingAttachment (Upper-Left)
    add_entity("attachment", "BookingAttachment", 480, 460, 220, 56, subtext="booking_bookingattachment")

    # PaymentRequest (Middle-Left)
    add_entity("payment", "PaymentRequest", 480, 820, 210, 58, subtext="payments_paymentrequest")

    # Receipt (Lower-Left)
    add_entity("receipt", "Receipt", 480, 1170, 190, 56, subtext="payments_receipt")

    # Driver (Middle-Right)
    add_entity("driver", "Driver", 1980, 600, 190, 58, subtext="drivers_driver")

    # Vehicle (Lower-Right)
    add_entity("vehicle", "Vehicle", 1980, 940, 190, 56, subtext="drivers_vehicle")

    # Review (Upper-Right)
    add_entity("review", "Review", 1980, 250, 190, 56, subtext="booking_review")

    # PredefinedRouteFare (Bottom Center-Left)
    add_entity("route_fare", "PredefinedRouteFare", 920, 1050, 230, 58, subtext="booking_predefinedroutefare")

    # PredefinedRouteDistance (Bottom Center-Right)
    add_entity("route_dist", "PredefinedRouteDistance", 1510, 1050, 240, 58, subtext="booking_predefinedroutedistance")

    # -------------------------------------------------------------
    # 2. RELATIONSHIPS (Red Diamonds)
    # -------------------------------------------------------------
    # Customer - books - Booking
    add_rel("rel_books", "books", 1250, 410, w=110, h=56)
    add_link("user", "rel_books", card1="1", card1_pos=(1268, 280))
    add_link("rel_books", "booking", card2="0..*", card2_pos=(1272, 545))

    # Booking - includes - BookingAttachment
    add_rel("rel_includes", "includes", 780, 470, w=110, h=56)
    add_link("booking", "rel_includes", card1="1", card1_pos=(1085, 565))
    add_link("rel_includes", "attachment", card2="0..*", card2_pos=(625, 435))

    # Booking - generates - PaymentRequest
    add_rel("rel_generates", "generates", 780, 770, w=116, h=56)
    add_link("booking", "rel_generates", card1="1", card1_pos=(1085, 645))
    add_link("rel_generates", "payment", card2="0..*", card2_pos=(620, 800))

    # PaymentRequest - issues - Receipt
    add_rel("rel_issues", "issues", 480, 1000, w=106, h=54)
    add_link("payment", "rel_issues", card1="1", card1_pos=(498, 875))
    add_link("rel_issues", "receipt", card2="0..1", card2_pos=(502, 1120))

    # Booking - assigns - Driver
    add_rel("rel_assigns", "assigns", 1660, 600, w=110, h=56)
    add_link("booking", "rel_assigns", card1="0..*", card1_pos=(1395, 580))
    add_link("rel_assigns", "driver", card2="0..1", card2_pos=(1855, 580))

    # Driver - operates - Vehicle (One-to-One)
    add_rel("rel_operates", "operates", 1980, 780, w=114, h=56)
    add_link("driver", "rel_operates", card1="1", card1_pos=(1998, 655))
    add_link("rel_operates", "vehicle", card2="1", card2_pos=(1998, 895))

    # User - submits - Review
    add_rel("rel_submits", "submits", 1640, 230, w=110, h=54)
    add_link("user", "rel_submits", card1="1", card1_pos=(1380, 215))
    add_link("rel_submits", "review", card2="0..*", card2_pos=(1850, 235))

    # Booking - receives - Review
    add_rel("rel_receives", "receives", 1640, 390, w=110, h=54)
    add_link("booking", "rel_receives", card1="0..1", card1_pos=(1335, 555))
    add_link("rel_receives", "review", card2="0..*", card2_pos=(1885, 305))

    # Booking - applies - PredefinedRouteFare
    add_rel("rel_applies", "applies", 1060, 860, w=110, h=56)
    add_link("booking", "rel_applies", card1="0..*", card1_pos=(1180, 665))
    add_link("rel_applies", "route_fare", card2="0..1", card2_pos=(975, 995))

    # Booking - measures - PredefinedRouteDistance
    add_rel("rel_measures", "measures", 1390, 860, w=116, h=56)
    add_link("booking", "rel_measures", card1="0..*", card1_pos=(1325, 665))
    add_link("rel_measures", "route_dist", card2="0..1", card2_pos=(1475, 995))

    # -------------------------------------------------------------
    # 3. ATTRIBUTES
    # -------------------------------------------------------------
    # USER Attributes
    add_attr("u_id", "id", "user", 1250, 135, rx=42, ry=18, is_pk=True)
    add_attr("u_uname", "username", "user", 1120, 155, rx=48, ry=18)
    add_attr("u_name", "Name", "user", 995, 205, rx=42, ry=18, is_comp=True)
    add_attr("u_fname", "first_name", "u_name", 875, 175, rx=48, ry=18)
    add_attr("u_lname", "last_name", "u_name", 875, 235, rx=48, ry=18)
    add_attr("u_email", "email", "user", 1400, 155, rx=44, ry=18)
    add_attr("u_phone", "phone", "user", 1435, 215, rx=44, ry=18, is_multi=True)
    add_attr("u_joined", "date_joined", "user", 1390, 275, rx=50, ry=18)
    add_attr("u_staff", "is_staff", "user", 1120, 280, rx=44, ry=18)

    # BOOKING Attributes - Carefully positioned around Booking
    # Top-left of Booking:
    add_attr("b_id", "id", "booking", 1150, 515, rx=40, ry=18, is_pk=True)
    add_attr("b_bid", "booking_id", "booking", 1045, 515, rx=52, ry=18)
    add_attr("b_status", "status", "booking", 1100, 465, rx=40, ry=18)

    # Top-right of Booking:
    add_attr("b_pstatus", "payment_status", "booking", 1365, 515, rx=60, ry=18)
    add_attr("b_ttype", "trip_type", "booking", 1465, 515, rx=45, ry=18)
    
    # Left of Booking: Route (Composite)
    add_attr("b_route", "Route", "booking", 1010, 575, rx=42, ry=18, is_comp=True)
    add_attr("b_pickup", "pickup", "b_route", 885, 550, rx=45, ry=18)
    add_attr("b_dest", "destination", "b_route", 885, 605, rx=52, ry=18)

    # Left of Booking: Coordinates (Composite)
    add_attr("b_coords", "Coordinates", "booking", 1010, 650, rx=54, ry=18, is_comp=True)
    add_attr("b_platlng", "pickup_coords", "b_coords", 880, 655, rx=56, ry=18)
    add_attr("b_dlatlng", "dest_coords", "b_coords", 880, 710, rx=56, ry=18)

    # Directly Below Booking:
    add_attr("b_jdate", "journey_date", "booking", 1200, 710, rx=52, ry=18)
    add_attr("b_dist", "distance (KM)", "booking", 1300, 710, rx=50, ry=18)
    add_attr("b_vtype", "vehicle_type", "booking", 1250, 765, rx=52, ry=18)

    # Upper-Right of Booking: Cargo Details (Composite) - placed above the assigns line
    add_attr("b_cargocomp", "Cargo Details", "booking", 1470, 440, rx=54, ry=18, is_comp=True)
    add_attr("b_ctype", "cargo_type", "b_cargocomp", 1595, 415, rx=48, ry=18)
    add_attr("b_cweight", "weight_value", "b_cargocomp", 1595, 470, rx=52, ry=18)

    # Lower-Right of Booking: Fare Details (Composite) - placed well below the assigns line
    add_attr("b_farecomp", "Fare Details", "booking", 1470, 720, rx=52, ry=18, is_comp=True)
    add_attr("b_fare", "fare", "b_farecomp", 1585, 675, rx=38, ry=18)
    add_attr("b_ftype", "fare_type", "b_farecomp", 1595, 725, rx=46, ry=18)
    add_attr("b_toll", "toll_charges", "b_farecomp", 1600, 775, rx=54, ry=18)

    # BOOKING ATTACHMENT Attributes
    add_attr("att_id", "id", "attachment", 330, 410, rx=40, ry=18, is_pk=True)
    add_attr("att_type", "attachment_type", "attachment", 450, 380, rx=65, ry=18)
    add_attr("att_file", "file", "attachment", 590, 380, rx=40, ry=18)
    add_attr("att_date", "uploaded_at", "attachment", 320, 470, rx=52, ry=18)

    # PAYMENT REQUEST Attributes
    add_attr("pay_id", "id", "payment", 310, 760, rx=38, ry=18, is_pk=True)
    add_attr("pay_pid", "payment_id", "payment", 415, 735, rx=50, ry=18)
    add_attr("pay_status", "status", "payment", 530, 735, rx=40, ry=18)
    add_attr("pay_amt", "amount", "payment", 300, 820, rx=40, ry=18)
    add_attr("pay_tot", "total_fare", "payment", 310, 880, rx=45, ry=18)
    add_attr("pay_type", "payment_type", "payment", 420, 920, rx=55, ry=18)
    add_attr("pay_meth", "preferred_method", "payment", 565, 920, rx=68, ry=18)

    # RECEIPT Attributes
    add_attr("rc_id", "id", "receipt", 320, 1120, rx=38, ry=18, is_pk=True)
    add_attr("rc_rid", "receipt_id", "receipt", 310, 1180, rx=50, ry=18)
    add_attr("rc_file", "pdf_file", "receipt", 320, 1240, rx=42, ry=18)
    add_attr("rc_date", "generated_at", "receipt", 440, 1255, rx=54, ry=18)
    add_attr("rc_email", "sent_to_email", "receipt", 570, 1255, rx=56, ry=18)
    add_attr("rc_sent", "is_sent", "receipt", 640, 1180, rx=40, ry=18)

    # DRIVER Attributes
    add_attr("dr_id", "id", "driver", 1865, 495, rx=38, ry=18, is_pk=True)
    add_attr("dr_name", "name", "driver", 1975, 495, rx=40, ry=18)
    add_attr("dr_mobile", "mobile", "driver", 2085, 515, rx=44, ry=18, is_multi=True)
    add_attr("dr_lic", "license_number", "driver", 2145, 575, rx=60, ry=18)
    add_attr("dr_exp", "experience_years", "driver", 2140, 640, rx=64, ry=18)
    add_attr("dr_stat", "status", "driver", 2080, 700, rx=40, ry=18)
    add_attr("dr_def", "is_default", "driver", 1970, 700, rx=44, ry=18)

    # VEHICLE Attributes
    add_attr("vh_id", "id", "vehicle", 1830, 885, rx=38, ry=18, is_pk=True)
    add_attr("vh_num", "vehicle_number", "vehicle", 1795, 955, rx=60, ry=18)
    add_attr("vh_type", "vehicle_type", "vehicle", 1865, 1025, rx=52, ry=18)
    add_attr("vh_cap", "capacity", "vehicle", 1985, 1025, rx=44, ry=18)
    add_attr("vh_rc", "rc_number", "vehicle", 2095, 985, rx=48, ry=18)

    # REVIEW Attributes
    add_attr("rv_id", "id", "review", 1870, 150, rx=38, ry=18, is_pk=True)
    add_attr("rv_rate", "rating (⭐)", "review", 1980, 140, rx=45, ry=18)
    add_attr("rv_comm", "comment / review", "review", 2110, 160, rx=64, ry=18)
    add_attr("rv_serv", "service_used", "review", 2150, 225, rx=54, ry=18)
    add_attr("rv_appr", "is_approved", "review", 2140, 290, rx=50, ry=18)
    add_attr("rv_date", "created_at", "review", 2040, 335, rx=48, ry=18)

    # PREDEFINED ROUTE FARE Attributes
    add_attr("rf_id", "id", "route_fare", 755, 1005, rx=38, ry=18, is_pk=True)
    add_attr("rf_from", "from_location", "route_fare", 735, 1065, rx=54, ry=18)
    add_attr("rf_to", "to_location", "route_fare", 755, 1130, rx=50, ry=18)
    add_attr("rf_rates", "Fare Rates", "route_fare", 885, 1160, rx=48, ry=18, is_comp=True)
    add_attr("rf_fix", "fixed_fare (1-Way)", "rf_rates", 805, 1225, rx=58, ry=18)
    add_attr("rf_dtrip", "double_trip_fare (2-Way)", "rf_rates", 995, 1225, rx=68, ry=18)
    add_attr("rf_dist", "distance_km", "route_fare", 1060, 1160, rx=50, ry=18)
    add_attr("rf_both", "same_direction_both", "route_fare", 1115, 1100, rx=68, ry=18)
    add_attr("rf_act", "is_active", "route_fare", 1095, 1030, rx=44, ry=18)

    # PREDEFINED ROUTE DISTANCE Attributes
    add_attr("rd_id", "id", "route_dist", 1335, 1010, rx=38, ry=18, is_pk=True)
    add_attr("rd_from", "from_location", "route_dist", 1320, 1075, rx=54, ry=18)
    add_attr("rd_to", "to_location", "route_dist", 1355, 1140, rx=50, ry=18)
    add_attr("rd_dist", "distance_km", "route_dist", 1475, 1175, rx=50, ry=18)
    add_attr("rd_both", "same_direction_both", "route_dist", 1620, 1150, rx=68, ry=18)
    add_attr("rd_act", "is_active", "route_dist", 1670, 1080, rx=44, ry=18)

    # -------------------------------------------------------------
    # 4. DRAW CONNECTING LINES
    # -------------------------------------------------------------
    svg_lines.append("  <!-- ==================== CONNECTING LINES ==================== -->")
    svg_lines.append('  <g id="connectors" stroke="#2563EB" stroke-width="2.2" stroke-linecap="round">')

    # Attribute lines
    for a_id, a in attributes.items():
        parent_id = a["parent"]
        if parent_id in entities:
            px, py = entities[parent_id]["cx"], entities[parent_id]["cy"]
        elif parent_id in attributes:
            px, py = attributes[parent_id]["cx"], attributes[parent_id]["cy"]
        else:
            continue
        svg_lines.append(f'    <line x1="{px}" y1="{py}" x2="{a["cx"]}" y2="{a["cy"]}" />')

    # Relationship lines
    for l in links:
        f_id = l["from"]
        t_id = l["to"]
        
        # Determine source coords
        if f_id in entities:
            fx, fy = entities[f_id]["cx"], entities[f_id]["cy"]
        else:
            fx, fy = relationships[f_id]["cx"], relationships[f_id]["cy"]
            
        # Determine target coords
        if t_id in entities:
            tx, ty = entities[t_id]["cx"], entities[t_id]["cy"]
        else:
            tx, ty = relationships[t_id]["cx"], relationships[t_id]["cy"]

        svg_lines.append(f'    <line x1="{fx}" y1="{fy}" x2="{tx}" y2="{ty}" stroke="#1E40AF" stroke-width="2.6" />')

    svg_lines.append("  </g>")

    # Cardinality Labels
    svg_lines.append("  <!-- ==================== CARDINALITY LABELS ==================== -->")
    svg_lines.append('  <g id="cardinalities">')
    for l in links:
        if l["card1"] and l["card1_pos"]:
            cx, cy = l["card1_pos"]
            svg_lines.append(f'    <text x="{cx}" y="{cy}" class="card-text">{l["card1"]}</text>')
        if l["card2"] and l["card2_pos"]:
            cx, cy = l["card2_pos"]
            svg_lines.append(f'    <text x="{cx}" y="{cy}" class="card-text">{l["card2"]}</text>')
    svg_lines.append("  </g>")

    # -------------------------------------------------------------
    # 5. DRAW ATTRIBUTES (Green Ovals & Blue Composite Ovals)
    # -------------------------------------------------------------
    svg_lines.append("  <!-- ==================== ATTRIBUTES ==================== -->")
    svg_lines.append('  <g id="attributes">')
    for a_id, a in attributes.items():
        cx, cy, rx, ry = a["cx"], a["cy"], a["rx"], a["ry"]
        name = a["name"]

        if a["is_comp"]:
            # Composite Attribute (Blue)
            svg_lines.append(f'    <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#compGrad)" stroke="#0284C7" stroke-width="2" filter="url(#shadow)" />')
            svg_lines.append(f'    <text x="{cx}" y="{cy}" class="comp-text">{name}</text>')
        elif a["is_multi"]:
            # Multi-valued Attribute (Double Green Oval)
            svg_lines.append(f'    <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#attrGrad)" stroke="#15803D" stroke-width="2" filter="url(#shadow)" />')
            svg_lines.append(f'    <ellipse cx="{cx}" cy="{cy}" rx="{rx-4}" ry="{ry-3}" fill="none" stroke="#15803D" stroke-width="1.4" />')
            svg_lines.append(f'    <text x="{cx}" y="{cy}" class="attr-text">{name}</text>')
        elif a["is_pk"]:
            # Primary Key (Yellow/Gold tint fill or standard green with underline)
            svg_lines.append(f'    <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#pkGrad)" stroke="#15803D" stroke-width="2.2" filter="url(#shadow)" />')
            svg_lines.append(f'    <text x="{cx}" y="{cy}" class="attr-pk-text">{name}</text>')
        else:
            # Standard Attribute (Green Oval)
            svg_lines.append(f'    <ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="url(#attrGrad)" stroke="#15803D" stroke-width="1.8" filter="url(#shadow)" />')
            svg_lines.append(f'    <text x="{cx}" y="{cy}" class="attr-text">{name}</text>')
    svg_lines.append("  </g>")

    # -------------------------------------------------------------
    # 6. DRAW RELATIONSHIPS (Red Diamonds)
    # -------------------------------------------------------------
    svg_lines.append("  <!-- ==================== RELATIONSHIPS ==================== -->")
    svg_lines.append('  <g id="relationships">')
    for r_id, r in relationships.items():
        cx, cy, w, h = r["cx"], r["cy"], r["w"], r["h"]
        hw, hh = w / 2, h / 2
        pts = f"{cx},{cy-hh} {cx+hw},{cy} {cx},{cy+hh} {cx-hw},{cy}"
        svg_lines.append(f'    <polygon points="{pts}" fill="url(#relGrad)" stroke="#991B1B" stroke-width="2.2" filter="url(#shadow)" />')
        svg_lines.append(f'    <text x="{cx}" y="{cy}" class="rel-text">{r["name"]}</text>')
    svg_lines.append("  </g>")

    # -------------------------------------------------------------
    # 7. DRAW ENTITIES (Blue Rectangles)
    # -------------------------------------------------------------
    svg_lines.append("  <!-- ==================== ENTITIES ==================== -->")
    svg_lines.append('  <g id="entities">')
    for e_id, e in entities.items():
        cx, cy, w, h = e["cx"], e["cy"], e["w"], e["h"]
        x = cx - w / 2
        y = cy - h / 2
        grad = "url(#bookingGrad)" if e["is_central"] else "url(#entityGrad)"
        border_col = "#1E3A8A"
        stroke_w = "3" if e["is_central"] else "2.4"
        
        svg_lines.append(f'    <rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{grad}" stroke="{border_col}" stroke-width="{stroke_w}" filter="url(#shadow)" />')
        
        if e["subtext"]:
            svg_lines.append(f'    <text x="{cx}" y="{cy-8}" class="entity-text">{e["name"]}</text>')
            svg_lines.append(f'    <text x="{cx}" y="{cy+12}" class="entity-subtext">[{e["subtext"]}]</text>')
        else:
            svg_lines.append(f'    <text x="{cx}" y="{cy}" class="entity-text">{e["name"]}</text>')
    svg_lines.append("  </g>")

    # -------------------------------------------------------------
    # 8. LEGEND BOX (Bottom-Right)
    # -------------------------------------------------------------
    svg_lines.append("""
  <!-- ==================== NOTATION LEGEND ==================== -->
  <g id="legend" transform="translate(1820, 1140)">
    <!-- Legend Card Container -->
    <rect x="0" y="0" width="630" height="360" rx="12" fill="#F8FAFC" stroke="#CBD5E1" stroke-width="2" filter="url(#shadow)" />
    
    <text x="315" y="32" class="legend-title" text-anchor="middle">ER NOTATION &amp; SCHEMA REFERENCE</text>
    <line x1="25" y1="46" x2="605" y2="46" stroke="#E2E8F0" stroke-width="1.5" />
    
    <!-- Item 1: Entity -->
    <rect x="30" y="65" width="85" height="30" rx="4" fill="url(#entityGrad)" stroke="#1E3A8A" stroke-width="1.8" />
    <text x="72.5" y="80" class="entity-text" font-size="11px">Entity</text>
    <text x="135" y="82" class="legend-text">Entity Set (Django DB Table / Model)</text>
    
    <!-- Item 2: Attribute -->
    <ellipse cx="72.5" cy="122" rx="42" ry="15" fill="url(#attrGrad)" stroke="#15803D" stroke-width="1.6" />
    <text x="72.5" y="122" class="attr-text" font-size="11px">Attribute</text>
    <text x="135" y="124" class="legend-text">Standard Attribute (Model Field / Column)</text>
    
    <!-- Item 3: Primary Key Attribute -->
    <ellipse cx="72.5" cy="164" rx="42" ry="15" fill="url(#pkGrad)" stroke="#15803D" stroke-width="1.8" />
    <text x="72.5" y="164" class="attr-pk-text" font-size="11px"><u>PK Field</u></text>
    <text x="135" y="166" class="legend-text">Primary Key (PK, Underlined e.g. id, booking_id)</text>
    
    <!-- Item 4: Composite Attribute -->
    <ellipse cx="72.5" cy="206" rx="42" ry="15" fill="url(#compGrad)" stroke="#0284C7" stroke-width="1.6" />
    <text x="72.5" y="206" class="comp-text" font-size="11px">Composite</text>
    <text x="135" y="208" class="legend-text">Composite Attribute (Grouped Fields e.g. Route, Name)</text>
    
    <!-- Item 5: Multi-valued Attribute -->
    <ellipse cx="72.5" cy="248" rx="42" ry="15" fill="url(#attrGrad)" stroke="#15803D" stroke-width="1.6" />
    <ellipse cx="72.5" cy="248" rx="38" ry="12" fill="none" stroke="#15803D" stroke-width="1.2" />
    <text x="72.5" y="248" class="attr-text" font-size="10.5px">Multi-val</text>
    <text x="135" y="250" class="legend-text">Multi-valued / Alternative Contact Attribute</text>
    
    <!-- Item 6: Relationship Diamond -->
    <polygon points="72.5,274 105,290 72.5,306 40,290" fill="url(#relGrad)" stroke="#991B1B" stroke-width="1.8" />
    <text x="72.5" y="290" class="rel-text" font-size="10px">Rel</text>
    <text x="135" y="292" class="legend-text">Relationship Diamond (Foreign Key Association)</text>

    <!-- Item 7: Cardinality -->
    <text x="72.5" y="334" class="card-text" font-size="15px">1 .. *</text>
    <text x="135" y="334" class="legend-text">Cardinality: 1 (One), 0..1 (Optional), 0..* / 1..* (Many)</text>
  </g>
""")

    svg_lines.append("</svg>")
    return "\n".join(svg_lines)


def render_png_with_browser():
    """Render high-res PNG using Edge or Chrome headless browser."""
    browsers = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    ]
    
    browser_bin = None
    for b in browsers:
        if os.path.exists(b):
            browser_bin = b
            break

    if not browser_bin:
        print("[WARN] No headless Chrome or Edge found to render PNG directly.")
        return False

    # Create a small HTML wrapper to render SVG at high resolution
    html_wrapper = OUTPUT_DIR / "_temp_render.html"
    html_content = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <style>
    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
    body {{ background: #FFFFFF; display: flex; justify-content: center; align-items: center; width: 2500px; height: 1560px; }}
    img {{ width: 2500px; height: 1560px; display: block; }}
  </style>
</head>
<body>
  <img src="ghidora_transport_er_diagram.svg" />
</body>
</html>
"""
    html_wrapper.write_text(html_content, encoding="utf-8")

    temp_profile = BASE_DIR / "scratch" / "_browser_profile"
    temp_profile.mkdir(parents=True, exist_ok=True)

    cmd = [
        browser_bin,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        f"--user-data-dir={temp_profile}",
        "--window-size=2500,1560",
        f"--screenshot={PNG_PATH}",
        f"file:///{html_wrapper.as_posix()}"
    ]

    print(f"Rendering high-resolution PNG using {Path(browser_bin).name}...")
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=20)
        if html_wrapper.exists():
            html_wrapper.unlink()
        if PNG_PATH.exists() and PNG_PATH.stat().st_size > 0:
            print(f"[OK] PNG successfully generated: {PNG_PATH} ({PNG_PATH.stat().st_size // 1024} KB)")
            return True
        else:
            print(f"[WARN] Screenshot failed. Stderr: {res.stderr}")
            return False
    except Exception as e:
        print(f"[ERROR] Failed to run browser screenshot: {e}")
        return False


def build_dot_source():
    """Generates clean Graphviz DOT format representation."""
    dot_content = """/*
 * GHIDORA TRANSPORT - Online Booking Transport Platform
 * Database ER Diagram (Graphviz DOT Source)
 * College Minor Project Database Architecture
 */

graph GhidoraTransportER {
    layout=neato;
    overlap=false;
    splines=true;
    bgcolor="#FFFFFF";

    // Global Font Settings
    node [fontname="Segoe UI, Helvetica, Arial", fontsize=12];
    edge [fontname="Segoe UI, Helvetica, Arial", fontsize=11, color="#1D4ED8", penwidth=2.0];

    // ==========================================
    // ENTITY SETS (Blue Rectangles)
    // ==========================================
    node [shape=box, style="filled,rounded", fillcolor="#1E3A8A", fontcolor="#FFFFFF", fontname="Segoe UI Bold", fontsize=14, margin="0.25,0.15", penwidth=2.5, color="#0F172A"];
    User [label="Customer (User)\\n[auth_user]"];
    Booking [label="Booking\\n[booking_booking]"];
    BookingAttachment [label="BookingAttachment\\n[booking_bookingattachment]"];
    PaymentRequest [label="PaymentRequest\\n[payments_paymentrequest]"];
    Receipt [label="Receipt\\n[payments_receipt]"];
    Driver [label="Driver\\n[drivers_driver]"];
    Vehicle [label="Vehicle\\n[drivers_vehicle]"];
    Review [label="Review\\n[booking_review]"];
    PredefinedRouteFare [label="PredefinedRouteFare\\n[booking_predefinedroutefare]"];
    PredefinedRouteDistance [label="PredefinedRouteDistance\\n[booking_predefinedroutedistance]"];

    // ==========================================
    // RELATIONSHIPS (Red Diamonds)
    // ==========================================
    node [shape=diamond, style=filled, fillcolor="#DC2626", fontcolor="#FFFFFF", fontname="Segoe UI Bold Italic", fontsize=12, margin="0.15,0.1", penwidth=2.0, color="#991B1B"];
    rel_books [label="books"];
    rel_includes [label="includes"];
    rel_generates [label="generates"];
    rel_issues [label="issues"];
    rel_assigns [label="assigns"];
    rel_operates [label="operates"];
    rel_submits [label="submits"];
    rel_receives [label="receives"];
    rel_applies [label="applies"];
    rel_measures [label="measures"];

    // ==========================================
    // ATTRIBUTES (Green Ovals)
    // ==========================================
    node [shape=ellipse, style=filled, fillcolor="#DCFCE7", fontcolor="#064E3B", fontname="Segoe UI Semibold", fontsize=11, margin="0.1,0.05", penwidth=1.8, color="#15803D"];
    
    // User Attributes
    node [fillcolor="#FEF3C7", fontname="Segoe UI Bold"];
    u_id [label=<<u>id</u>>];
    node [fillcolor="#DCFCE7", fontname="Segoe UI Semibold"];
    u_username [label="username"];
    u_email [label="email"];
    u_phone [label="phone", peripheries=2];
    u_fname [label="first_name"];
    u_lname [label="last_name"];
    u_date_joined [label="date_joined"];

    // Booking Attributes
    node [fillcolor="#FEF3C7", fontname="Segoe UI Bold"];
    b_id [label=<<u>id</u>>];
    node [fillcolor="#DCFCE7", fontname="Segoe UI Semibold"];
    b_booking_id [label="booking_id"];
    b_pickup [label="pickup"];
    b_dest [label="destination"];
    b_pickup_coords [label="pickup_lat/lng"];
    b_dest_coords [label="dest_lat/lng"];
    b_distance [label="distance"];
    b_fare [label="fare"];
    b_fare_type [label="fare_type"];
    b_toll [label="toll_charges"];
    b_status [label="status"];
    b_payment_status [label="payment_status"];
    b_journey_date [label="journey_date"];
    b_vehicle_type [label="vehicle_type"];
    b_cargo_type [label="cargo_type"];

    // Driver Attributes
    node [fillcolor="#FEF3C7", fontname="Segoe UI Bold"];
    dr_id [label=<<u>id</u>>];
    node [fillcolor="#DCFCE7", fontname="Segoe UI Semibold"];
    dr_name [label="name"];
    dr_mobile [label="mobile", peripheries=2];
    dr_license [label="license_number"];
    dr_exp [label="experience_years"];
    dr_status [label="status"];

    // Vehicle Attributes
    node [fillcolor="#FEF3C7", fontname="Segoe UI Bold"];
    vh_id [label=<<u>id</u>>];
    node [fillcolor="#DCFCE7", fontname="Segoe UI Semibold"];
    vh_num [label="vehicle_number"];
    vh_type [label="vehicle_type"];
    vh_capacity [label="capacity"];
    vh_rc [label="rc_number"];

    // PaymentRequest Attributes
    node [fillcolor="#FEF3C7", fontname="Segoe UI Bold"];
    pay_id [label=<<u>id</u>>];
    node [fillcolor="#DCFCE7", fontname="Segoe UI Semibold"];
    pay_payment_id [label="payment_id"];
    pay_amount [label="amount"];
    pay_total_fare [label="total_fare"];
    pay_status [label="status"];
    pay_method [label="preferred_method"];

    // Receipt Attributes
    node [fillcolor="#FEF3C7", fontname="Segoe UI Bold"];
    rc_id [label=<<u>id</u>>];
    node [fillcolor="#DCFCE7", fontname="Segoe UI Semibold"];
    rc_receipt_id [label="receipt_id"];
    rc_pdf [label="pdf_file"];
    rc_sent [label="sent_to_email"];

    // Review Attributes
    node [fillcolor="#FEF3C7", fontname="Segoe UI Bold"];
    rv_id [label=<<u>id</u>>];
    node [fillcolor="#DCFCE7", fontname="Segoe UI Semibold"];
    rv_rating [label="rating (⭐)"];
    rv_comment [label="comment"];
    rv_service [label="service_used"];

    // Predefined Route Fares
    node [fillcolor="#FEF3C7", fontname="Segoe UI Bold"];
    rf_id [label=<<u>id</u>>];
    node [fillcolor="#DCFCE7", fontname="Segoe UI Semibold"];
    rf_from [label="from_location"];
    rf_to [label="to_location"];
    rf_fixed [label="fixed_fare"];
    rf_double [label="double_trip_fare"];

    // Predefined Route Distances
    node [fillcolor="#FEF3C7", fontname="Segoe UI Bold"];
    rd_id [label=<<u>id</u>>];
    node [fillcolor="#DCFCE7", fontname="Segoe UI Semibold"];
    rd_from [label="from_location"];
    rd_to [label="to_location"];
    rd_km [label="distance_km"];

    // ==========================================
    // EDGES & CARDINALITIES
    // ==========================================
    // Entity -> Attribute connections
    User -- {u_id u_username u_email u_phone u_fname u_lname u_date_joined};
    Booking -- {b_id b_booking_id b_pickup b_dest b_pickup_coords b_dest_coords b_distance b_fare b_fare_type b_toll b_status b_payment_status b_journey_date b_vehicle_type b_cargo_type};
    Driver -- {dr_id dr_name dr_mobile dr_license dr_exp dr_status};
    Vehicle -- {vh_id vh_num vh_type vh_capacity vh_rc};
    PaymentRequest -- {pay_id pay_payment_id pay_amount pay_total_fare pay_status pay_method};
    Receipt -- {rc_id rc_receipt_id rc_pdf rc_sent};
    Review -- {rv_id rv_rating rv_comment rv_service};
    PredefinedRouteFare -- {rf_id rf_from rf_to rf_fixed rf_double};
    PredefinedRouteDistance -- {rd_id rd_from rd_to rd_km};

    // Relationship connections with cardinalities
    User -- rel_books [label="1", fontcolor="#DC2626"];
    rel_books -- Booking [label="0..*", fontcolor="#DC2626"];

    Booking -- rel_includes [label="1", fontcolor="#DC2626"];
    rel_includes -- BookingAttachment [label="0..*", fontcolor="#DC2626"];

    Booking -- rel_generates [label="1", fontcolor="#DC2626"];
    rel_generates -- PaymentRequest [label="0..*", fontcolor="#DC2626"];

    PaymentRequest -- rel_issues [label="1", fontcolor="#DC2626"];
    rel_issues -- Receipt [label="0..1", fontcolor="#DC2626"];

    Booking -- rel_assigns [label="0..*", fontcolor="#DC2626"];
    rel_assigns -- Driver [label="0..1", fontcolor="#DC2626"];

    Driver -- rel_operates [label="1", fontcolor="#DC2626"];
    rel_operates -- Vehicle [label="1", fontcolor="#DC2626"];

    User -- rel_submits [label="1", fontcolor="#DC2626"];
    rel_submits -- Review [label="0..*", fontcolor="#DC2626"];

    Booking -- rel_receives [label="0..1", fontcolor="#DC2626"];
    rel_receives -- Review [label="0..*", fontcolor="#DC2626"];

    Booking -- rel_applies [label="0..*", fontcolor="#DC2626"];
    rel_applies -- PredefinedRouteFare [label="0..1", fontcolor="#DC2626"];

    Booking -- rel_measures [label="0..*", fontcolor="#DC2626"];
    rel_measures -- PredefinedRouteDistance [label="0..1", fontcolor="#DC2626"];
}
"""
    DOT_PATH.write_text(dot_content, encoding="utf-8")
    print(f"[OK] Graphviz DOT source generated: {DOT_PATH}")


def build_mermaid_source():
    """Generates Mermaid ER diagram source."""
    mmd_content = """erDiagram
    %% =======================================================
    %% GHIDORA TRANSPORT - Online Booking Transport Platform
    %% Entity-Relationship Model (Mermaid Notation)
    %% =======================================================

    USER ||--o{ BOOKING : "places / books (1 to 0..*)"
    USER ||--o{ REVIEW : "submits (1 to 0..*)"
    BOOKING ||--o{ BOOKING_ATTACHMENT : "includes (1 to 0..*)"
    BOOKING ||--o{ PAYMENT_REQUEST : "generates (1 to 0..*)"
    PAYMENT_REQUEST ||--o| RECEIPT : "issues (1 to 0..1)"
    BOOKING }o--o| DRIVER : "assigns (0..* to 0..1)"
    DRIVER ||--|| VEHICLE : "operates / owns (1 to 1)"
    BOOKING |o--o{ REVIEW : "receives feedback (0..1 to 0..*)"
    BOOKING }o--o| PREDEFINED_ROUTE_FARE : "applies fixed route fare"
    BOOKING }o--o| PREDEFINED_ROUTE_DISTANCE : "measures fixed distance"

    USER {
        bigint id PK "Primary Key"
        varchar username "User Login Name"
        varchar email "Email Address"
        varchar first_name "First Name"
        varchar last_name "Last Name"
        boolean is_staff "Admin/Staff Status"
        datetime date_joined "Account Registration Timestamp"
    }

    BOOKING {
        bigint id PK "Primary Key"
        varchar booking_id UK "Unique Reference e.g. GT4592"
        bigint user_id FK "Registered Customer (Nullable)"
        bigint assigned_driver_id FK "Assigned Driver (Nullable)"
        varchar name "Customer Name"
        varchar phone "Customer Phone Number"
        varchar email "Customer Email (Nullable)"
        varchar pickup "Pickup Address / Location"
        varchar destination "Destination Address / Location"
        float pickup_lat "Pickup Latitude GPS"
        float pickup_lng "Pickup Longitude GPS"
        float destination_lat "Destination Latitude GPS"
        float destination_lng "Destination Longitude GPS"
        varchar duration_text "Google Route Travel Duration"
        float distance "Route Distance in KM"
        varchar distance_source "Google Maps Route / Manual"
        float fare "Base Journey Fare in INR"
        varchar fare_type "Predefined Route / Distance Based"
        float toll_charges "Toll Plaza Charges"
        float parking_charges "Parking Fees"
        varchar vehicle_type "Mahindra Pickup, Bolero, etc."
        varchar trip_type "One Way / Round Trip"
        varchar cargo_type "Type of Goods Transported"
        decimal weight_value "Cargo Weight"
        varchar weight_unit "kg / ton"
        varchar status "Pending, Confirmed, Completed, Cancelled"
        varchar payment_status "Pending, Paid, Partial, Failed"
        datetime booking_date "Booking Creation Timestamp"
        date journey_date "Scheduled Date of Travel"
    }

    DRIVER {
        bigint id PK "Primary Key"
        varchar name "Driver Full Name"
        varchar mobile UK "10-Digit Mobile Number"
        varchar license_number UK "Commercial Driving License Number"
        varchar address "Driver Residence Address"
        int experience_years "Driving Experience in Years"
        varchar status "available / busy"
        boolean is_default "Auto-Assign Default Driver Flag"
        datetime created_at "Registration Timestamp"
    }

    VEHICLE {
        bigint id PK "Primary Key"
        bigint driver_id FK,UK "One-To-One Assigned Driver"
        varchar vehicle_number UK "Vehicle Registration Number (e.g. CG05 AB 1234)"
        varchar vehicle_type "Vehicle Model / Category"
        varchar capacity "Load Carrying Capacity (e.g. 1 Ton)"
        varchar rc_number "Registration Certificate Number"
    }

    PAYMENT_REQUEST {
        bigint id PK "Primary Key"
        varchar payment_id UK "Unique Payment Tracking Code e.g. PAY-A1B2C3"
        bigint booking_id FK "Foreign Key to Booking"
        bigint created_by_id FK "Admin User Who Created Request"
        varchar payment_type "full / advance / remaining"
        decimal amount "Payment Requested Amount in INR"
        decimal total_fare "Total Booking Trip Fare in INR"
        decimal amount_already_paid "Previously Received Payment"
        varchar status "pending / submitted / verified / rejected"
        datetime due_date "Payment Expiry / Due Timestamp"
        varchar preferred_method "qr / upi / bank"
        varchar gateway "manual / razorpay / phonepe"
        datetime created_at "Creation Timestamp"
    }

    RECEIPT {
        bigint id PK "Primary Key"
        varchar receipt_id UK "Unique Receipt Number e.g. RCPT-X9Y8"
        bigint payment_request_id FK,UK "One-To-One Payment Request Link"
        varchar pdf_file "Generated PDF Receipt File Path"
        datetime generated_at "Receipt Generation Timestamp"
        varchar sent_to_email "Recipient Customer Email"
        boolean is_sent "Email Dispatch Status"
    }

    BOOKING_ATTACHMENT {
        bigint id PK "Primary Key"
        bigint booking_id FK "Foreign Key to Booking"
        varchar attachment_type "voice / photo / video"
        varchar file "Uploaded Media File Path"
        datetime uploaded_at "Upload Timestamp"
    }

    REVIEW {
        bigint id PK "Primary Key"
        bigint booking_id FK "Foreign Key to Booking (Nullable)"
        bigint user_id FK "Foreign Key to User (Nullable)"
        varchar guest_name "Guest Reviewer Name"
        int rating "Star Rating 1 to 5"
        text comment "Customer Review Feedback"
        varchar service_used "Transport Service Utilized"
        boolean is_approved "Admin Moderation Approval Flag"
        boolean is_verified "Verified Customer Badge"
        datetime created_at "Submission Timestamp"
    }

    PREDEFINED_ROUTE_FARE {
        bigint id PK "Primary Key"
        varchar from_location "Origin City / Village"
        varchar to_location "Destination City / Village"
        decimal fixed_fare "Single Trip One-Way Fixed Rate in INR"
        decimal double_trip_fare "Round Trip Fixed Rate in INR"
        decimal distance_km "Pre-Calculated Route Distance in KM"
        boolean same_direction_both "Bi-directional Route Active Flag (Both Ways)"
        boolean is_active "Route Active / Inactive Status"
    }

    PREDEFINED_ROUTE_DISTANCE {
        bigint id PK "Primary Key"
        varchar from_location "Origin City / Village"
        varchar to_location "Destination City / Village"
        decimal distance_km "Official Fixed Distance in KM"
        boolean same_direction_both "Bi-directional Distance Active Flag"
        boolean is_active "Record Active / Inactive Status"
    }
"""
    MMD_PATH.write_text(mmd_content, encoding="utf-8")
    print(f"[OK] Mermaid ER source generated: {MMD_PATH}")


def build_explanation_markdown():
    """Generates the viva & presentation explanation document."""
    doc = """# GHIDORA TRANSPORT — DATABASE ER DIAGRAM DOCUMENTATION
**Project Name:** Ghidora Transport — Online Booking Transport Platform  
**Technology Stack:** Python, Django 6.0, SQLite / PostgreSQL, HTML5, CSS3, JavaScript  
**Course / Level:** College Minor Project / Technical Presentation & Viva Voce  
**Date:** October 2026  

---

## 1. Executive Summary & Design Overview

This database Entity-Relationship (ER) diagram strictly models the actual, verified production database schema of the **Ghidora Transport** platform. It has been engineered in **Extended Chen's Notation** to match academic standards for college project presentations and viva examinations:

- **Entity Sets (Blue Rectangles):** Represent verified database tables mapped directly from Django models (`Booking`, `Driver`, `Vehicle`, `PaymentRequest`, `Receipt`, `BookingAttachment`, `Review`, `PredefinedRouteFare`, `PredefinedRouteDistance`, and Django's built-in `User`).
- **Attributes (Green Ovals):** Represent verified model fields and table columns.
  - **Primary Keys (PK):** Highlighted with bold underlined text (`<u>id</u>`, `<u>booking_id</u>`, etc.).
  - **Composite Attributes (Blue Ovals):** Group logical sub-fields (e.g., `Route` &rarr; `pickup`, `destination`; `Coordinates` &rarr; `pickup_coords`, `dest_coords`; `Fare Details` &rarr; `fare`, `fare_type`, `toll_charges`).
  - **Multi-Valued / Alternative Attributes (Double Border Ovals):** Attributes that can hold multiple contact representations (e.g., `phone`, `mobile`).
- **Relationships (Red Diamonds):** Represent relational constraints, foreign keys (`ForeignKey`), and one-to-one fields (`OneToOneField`) enforcing referential integrity.
- **Cardinalities (Red Italic Text):** Document minimum and maximum mapping constraints (`1`, `0..1`, `0..*`, `1..*`).

---

## 2. Entity Descriptions & Field Specifications

### 2.1 Entity: `Customer / User` (Table: `auth_user`)
- **Django Origin:** `django.contrib.auth.models.User` (Referenced via `settings.AUTH_USER_MODEL`).
- **Description:** Represents authenticated customers, registered clients, and administrative dispatchers.
- **Attributes:**
  - `id` (**PK**, BigAutoField) — Unique system identifier.
  - `username` (CharField) — Login handle.
  - `email` (EmailField) — Official email address for confirmation receipts.
  - `Name` (**Composite Attribute**):
    - `first_name` (CharField) — Given name.
    - `last_name` (CharField) — Surname.
  - `phone` (**Multi-valued Attribute**, CharField) — Linked mobile contact from `social.Profile`.
  - `is_staff` (BooleanField) — Admin / Dispatcher privilege flag.
  - `date_joined` (DateTimeField) — Timestamp of account creation.

### 2.2 Entity: `Booking` (Table: `booking_booking`)
- **Django Origin:** `booking.models.Booking`
- **Description:** The central transaction hub of the entire platform. Every transport job, route calculation, vehicle selection, and dispatch event connects to this entity.
- **Attributes:**
  - `id` (**PK**, BigAutoField) — Internal primary key.
  - `booking_id` (CharField, Unique) — Customer tracking code (e.g., `GT4592`).
  - `user_id` (**FK**, Nullable) — Reference to registered `User` (null for guest checkout).
  - `assigned_driver_id` (**FK**, Nullable) — Reference to assigned `Driver`.
  - `name`, `phone`, `email` — Contact details of customer placing the order.
  - `Route` (**Composite Attribute**):
    - `pickup` (CharField) — Starting address / city.
    - `destination` (CharField) — Destination address / city.
  - `Coordinates` (**Composite Attribute**):
    - `pickup_lat`, `pickup_lng` (FloatFields) — GPS origin coordinates from Google Maps / Open-Meteo.
    - `destination_lat`, `destination_lng` (FloatFields) — GPS destination coordinates.
  - `distance` (FloatField) — Road distance in Kilometers.
  - `distance_source` (CharField) — Source (`Google Generated`, `Google Maps Route`, `Manual Entered`).
  - `Fare Details` (**Composite Attribute**):
    - `fare` (FloatField) — Base transportation cost in ₹.
    - `fare_type` (CharField) — Calculation method (`Predefined Route Fare`, `Distance Based Fare`).
    - `toll_charges` (FloatField) — Toll plaza charges.
    - `parking_charges` (FloatField) — Parking or permit expenses.
  - `Cargo Details` (**Composite Attribute**):
    - `cargo_type` (CharField) — Cargo category (Agricultural, Industrial, Furniture, etc.).
    - `weight_value` (DecimalField) & `weight_unit` (`kg` / `ton`).
  - `vehicle_type` (CharField) — Chosen vehicle (Mahindra Pickup, Bolero, Tata Ace, etc.).
  - `trip_type` (CharField) — `One Way` or `Round Trip`.
  - `status` (CharField) — `Pending`, `Confirmed`, `Completed`, `Cancelled`.
  - `payment_status` (CharField) — `Pending`, `Paid`, `Partial`, `Failed`.
  - `journey_date` (DateField) — Scheduled date for transportation.
  - `booking_date` (DateTimeField) — Creation timestamp.

### 2.3 Entity: `Driver` (Table: `drivers_driver`)
- **Django Origin:** `drivers.models.Driver`
- **Description:** Commercial drivers registered to transport consignments.
- **Attributes:**
  - `id` (**PK**, BigAutoField) — Primary key.
  - `name` (CharField) — Driver's full legal name.
  - `mobile` (CharField, Unique) — 10-digit registered mobile number.
  - `license_number` (CharField, Unique) — Official RTO commercial driving license.
  - `experience_years` (PositiveIntegerField) — Driving experience in years.
  - `status` (CharField) — Current status (`available` / `busy`).
  - `is_default` (BooleanField) — System auto-assign default driver flag.
  - `address` (CharField) — Residential address.

### 2.4 Entity: `Vehicle` (Table: `drivers_vehicle`)
- **Django Origin:** `drivers.models.Vehicle`
- **Description:** Commercial transport vehicles operating in the Ghidora fleet.
- **Attributes:**
  - `id` (**PK**, BigAutoField) — Primary key.
  - `driver_id` (**FK, OneToOne**, Unique) — The driver assigned to this vehicle.
  - `vehicle_number` (CharField, Unique) — RTO registration number (e.g., `CG05 AB 1234`).
  - `vehicle_type` (CharField) — Model (e.g., `Mahindra Pickup`, `Mini Truck`).
  - `capacity` (CharField) — Payload capacity (e.g., `1 Ton`).
  - `rc_number` (CharField) — Registration certificate number.

### 2.5 Entity: `PaymentRequest` (Table: `payments_paymentrequest`)
- **Django Origin:** `payments.models.PaymentRequest`
- **Description:** Financial transactions requested for a booking (Advance, Full, Remaining).
- **Attributes:**
  - `id` (**PK**, BigAutoField) — Primary key.
  - `payment_id` (CharField, Unique) — Tracking code (e.g., `PAY-7E3B1C`).
  - `booking_id` (**FK**) — Associated `Booking`.
  - `payment_type` (CharField) — `full`, `advance`, `remaining`, `custom`.
  - `amount` (DecimalField) — Requested amount in ₹.
  - `total_fare` (DecimalField) — Full trip fare.
  - `amount_already_paid` (DecimalField) — Prior received credits.
  - `status` (CharField) — `pending`, `submitted`, `verified`, `rejected`, `completed`.
  - `due_date` (DateTimeField) — Expiration deadline for payment.
  - `preferred_method` (CharField) — `qr`, `upi`, `bank`.
  - `gateway` (CharField) — `manual`, `razorpay`, `phonepe`.

### 2.6 Entity: `Receipt` (Table: `payments_receipt`)
- **Django Origin:** `payments.models.Receipt`
- **Description:** Verifiable payment receipt generated after approval and dispatched to customer.
- **Attributes:**
  - `id` (**PK**, BigAutoField) — Primary key.
  - `receipt_id` (CharField, Unique) — Receipt identifier (e.g., `RCPT-8A2F`).
  - `payment_request_id` (**FK, OneToOne**, Unique) — Linked `PaymentRequest`.
  - `pdf_file` (FileField) — Generated PDF receipt document.
  - `generated_at` (DateTimeField) — Timestamp of receipt creation.
  - `sent_to_email` (CharField) — Email address where receipt was sent.
  - `is_sent` (BooleanField) — Dispatch status flag.

### 2.7 Entity: `BookingAttachment` (Table: `booking_bookingattachment`)
- **Django Origin:** `booking.models.BookingAttachment`
- **Description:** Multimedia attachments submitted by customer for route instructions or cargo identification.
- **Attributes:**
  - `id` (**PK**, BigAutoField) — Primary key.
  - `booking_id` (**FK**) — Associated `Booking`.
  - `attachment_type` (CharField) — `voice` (audio voice memo), `photo` (cargo/location image), `video`.
  - `file` (FileField) — Stored media file.
  - `uploaded_at` (DateTimeField) — Timestamp of upload.

### 2.8 Entity: `Review` (Table: `booking_review`)
- **Django Origin:** `booking.models.Review`
- **Description:** Customer feedback and rating system for completed transport trips.
- **Attributes:**
  - `id` (**PK**, BigAutoField) — Primary key.
  - `booking_id` (**FK**, Nullable) — The trip being reviewed.
  - `user_id` (**FK**, Nullable) — The registered user writing the review.
  - `rating` (IntegerField) — 1 to 5 stars.
  - `comment` / `review` (TextField) — Testimonial text.
  - `service_used` (CharField) — Transport service utilized.
  - `is_approved` (BooleanField) — Admin moderation approval flag.
  - `is_verified` (BooleanField) — Verified customer badge flag.
  - `created_at` (DateTimeField) — Timestamp of submission.

### 2.9 Entity: `PredefinedRouteFare` (Table: `booking_predefinedroutefare`)
- **Django Origin:** `booking.models.PredefinedRouteFare`
- **Description:** Master route catalog containing established, pre-negotiated commercial fares between major cities and industrial hubs in Chhattisgarh.
- **Attributes:**
  - `id` (**PK**, BigAutoField) — Primary key.
  - `from_location` (CharField) — Origin city (e.g., `Dhamtari`).
  - `to_location` (CharField) — Destination city (e.g., `Raipur`).
  - `Fare Rates` (**Composite Attribute**):
    - `fixed_fare` (DecimalField) — Single trip (One-Way) fare in ₹.
    - `double_trip_fare` (DecimalField) — Round trip fare in ₹.
  - `distance_km` (DecimalField) — Pre-verified road distance in KM.
  - `same_direction_both` (BooleanField) — Bi-directional flag (applies also for reverse route).
  - `is_active` (BooleanField) — Active toggle for real-time booking calculations.

### 2.10 Entity: `PredefinedRouteDistance` (Table: `booking_predefinedroutedistance`)
- **Django Origin:** `booking.models.PredefinedRouteDistance`
- **Description:** Master lookup table storing verified road distances between remote villages and city markets where GPS routing might otherwise fluctuate.
- **Attributes:**
  - `id` (**PK**, BigAutoField) — Primary key.
  - `from_location` (CharField) — Pickup location name (e.g., `Kodebod`).
  - `to_location` (CharField) — Drop location name (e.g., `Raipur`).
  - `distance_km` (DecimalField) — Fixed verified distance in KM.
  - `same_direction_both` (BooleanField) — Reversible distance flag.
  - `is_active` (BooleanField) — Active status flag.

---

## 3. Relationships and Cardinality Matrix

| Relationship | Entities Involved | Type | Cardinality | Explanation |
|---|---|---|---|---|
| **`books`** | `Customer` &rarr; `Booking` | One-to-Many | `1` to `0..*` | A registered customer can make 0 or multiple bookings over time; each booking is initiated by at most 1 registered customer (or guest). |
| **`assigns`** | `Booking` &rarr; `Driver` | Many-to-One (Optional) | `0..*` to `0..1` | A driver can be assigned to multiple bookings over their career; a booking has at most 1 assigned driver (or none if still pending). |
| **`operates`** | `Driver` &rarr; `Vehicle` | One-to-One | `1` to `1` | Enforced via Django `OneToOneField`. Each driver operates exactly one dedicated fleet vehicle; each vehicle has one primary driver. |
| **`generates`** | `Booking` &rarr; `PaymentRequest` | One-to-Many | `1` to `0..*` | A booking can generate zero, one, or multiple payment requests (e.g. an initial Advance Payment request followed by a Remaining Balance request). |
| **`issues`** | `PaymentRequest` &rarr; `Receipt` | One-to-One (Optional) | `1` to `0..1` | Enforced via Django `OneToOneField`. An approved payment request issues exactly 0 or 1 official downloadable receipt. |
| **`includes`** | `Booking` &rarr; `BookingAttachment` | One-to-Many | `1` to `0..*` | A booking can have 0 or multiple attachments (voice notes, cargo photos, delivery receipts). |
| **`submits`** | `Customer` &rarr; `Review` | One-to-Many | `1` to `0..*` | A customer can write multiple reviews across their service history. |
| **`receives`** | `Booking` &rarr; `Review` | One-to-Many (Optional) | `0..1` to `0..*` | A booking optionally receives review feedback upon completion. |
| **`applies`** | `Booking` &rarr; `PredefinedRouteFare` | Reference Association | `0..*` to `0..1` | When calculating trip pricing, a booking checks if an active predefined route exists between pickup and destination. |
| **`measures`** | `Booking` &rarr; `PredefinedRouteDistance` | Reference Association | `0..*` to `0..1` | When computing road mileage, a booking checks if an established route distance exists in the master distance catalog. |

---

## 4. Key Questions & Answers for College Viva

### Q1: Why is `assigned_driver` on the `Booking` model rather than a Many-to-Many junction table?
> **Answer:** In single-truck logistics, a specific transport job is assigned to exactly **one driver** at any given moment. Therefore, storing `assigned_driver` as a `ForeignKey(Driver, null=True, blank=True, on_delete=models.SET_NULL)` on the `Booking` model accurately models a **0..1 cardinality**, preventing scheduling ambiguities while preserving the booking history even if a driver record is modified.

### Q2: How does the system handle Guest Bookings vs. Registered Customer Bookings?
> **Answer:** The `user` field on `Booking` is configured as `ForeignKey(User, null=True, blank=True)`. If an unregistered customer places an order, their contact information (`name`, `phone`, `email`) is captured directly on the `Booking` record with `user = NULL`. If a logged-in user places the booking, `user` links directly to their account, allowing it to populate their customer dashboard under `/my-bookings/`.

### Q3: Why is `PaymentRequest` a separate entity instead of just a status field on `Booking`?
> **Answer:** In commercial transport, freight payments are rarely a single instantaneous transaction. Ghidora Transport supports **split payments** (e.g., 30% advance on booking approval, 70% remaining balance upon goods delivery), manual QR/UPI verification, and payment gateway integration. Having a dedicated `PaymentRequest` entity with a `One-to-Many` relation to `Booking` allows multiple payment stages, audit histories, and digital receipts for a single transport consignment.

### Q4: How is route pricing calculated in the database?
> **Answer:** Ghidora Transport employs a dual pricing strategy:
> 1. **Predefined Route Fare:** If the route matches a catalog record in `PredefinedRouteFare` (e.g., Dhamtari &harr; Raipur), the system enforces the fixed rate (`fixed_fare` for One-Way, `double_trip_fare` for Round-Trip).
> 2. **Distance-Based Fare:** If no predefined route is found, the system calculates distance via GPS coordinates (`pickup_lat`, `pickup_lng` to destination coordinates via Haversine / Open-Meteo API) or looks up `PredefinedRouteDistance`, and multiplies the distance by the per-kilometer tariff assigned to the chosen `vehicle_type`.
> Any toll charges (`toll_charges`) and parking fees (`parking_charges`) are added to arrive at the `total_fare`.

---

## 5. File Deliverables Summary

All diagram artifacts are available in `project_documentation/er_diagram/`:
1. `ghidora_transport_er_diagram.png` — High-resolution (2500x1560) presentation image for PowerPoint and project reports.
2. `ghidora_transport_er_diagram.svg` — Scalable vector graphic diagram that scales infinitely without losing sharpness.
3. `ghidora_transport_er_diagram_source.dot` — Editable Graphviz DOT source script.
4. `ghidora_transport_er_diagram_source.mmd` — Editable Mermaid source script.
5. `ghidora_transport_er_diagram_explanation.md` — This comprehensive academic viva and presentation reference.
"""
    EXPLANATION_PATH.write_text(doc, encoding="utf-8")
    print(f"[OK] Explanation Markdown generated: {EXPLANATION_PATH}")


def main():
    print("==================================================")
    print("BUILDING GHIDORA TRANSPORT DATABASE ER DIAGRAM")
    print("==================================================")
    
    # 1. Build Vector SVG
    svg_data = build_svg()
    SVG_PATH.write_text(svg_data, encoding="utf-8")
    print(f"[OK] Vector SVG successfully created: {SVG_PATH}")

    # 2. Render High-Resolution PNG
    render_png_with_browser()

    # 3. Build Graphviz DOT Source & direct source file
    build_dot_source()
    source_exact_path = OUTPUT_DIR / "ghidora_transport_er_diagram_source"
    source_exact_path.write_text(DOT_PATH.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"[OK] Source file without extension generated: {source_exact_path}")

    # 4. Build Mermaid Source
    build_mermaid_source()

    # 5. Build Explanation Document
    build_explanation_markdown()

    print("==================================================")
    print("ALL ER DIAGRAM DELIVERABLES READY!")
    print("==================================================")


if __name__ == "__main__":
    main()
