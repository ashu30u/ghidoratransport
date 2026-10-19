# GHIDORA TRANSPORT — DATABASE ER DIAGRAM & RELATIONAL SCHEMA DOCUMENTATION
**Project Name:** Ghidora Transport — Online Logistics & Consignment Booking Platform  
**Course & Purpose:** Master of Computer Applications (MCA) Minor Project Presentation & Viva Voce  
**Technology Stack:** Python 3.12, Django 6.0, SQLite / PostgreSQL, HTML5, CSS3, JavaScript  
**Diagram Edition:** Academic Black & White / Grayscale (Chen's Notation & Relational Schema)  
**Date of Verification:** October 2026  

---

## 1. Executive Summary & Design Overview

This database Entity-Relationship (ER) diagram strictly models the actual, verified production database schema of the **Ghidora Transport** project. Designed specifically for academic presentations, project reports, and external viva examinations, it adheres to the following principles:

1. **Zero Hallucination / 100% Code-Verified:** Every entity, attribute, relationship, key, and constraint is derived directly from the active Django codebase (`booking/models.py`, `drivers/models.py`, `payments/models.py`, and `django.contrib.auth.models.User`).
2. **Academic Black & White (B&W) High-Contrast Palette:** Built for professional university presentation slides, high-resolution classroom projector display, and black-and-white thesis report printing.
3. **Comprehensive Key Categorization:** Explicitly differentiates between:
   - **Primary Keys (PK):** Auto-incrementing 64-bit integer surrogate keys (`BigAutoField`), underlined and labeled `[PK]`.
   - **Foreign Keys (FK):** Referential integrity pointers, dashed ovals labeled `[FK]` with parent table pointers.
   - **Unique / Alternate Keys (UK / AK):** Natural candidate keys with unique constraints (`UNIQUE=True`), labeled `[UK]`.
   - **Composite Attributes (COMP):** Logical groupings of related atomic sub-fields (e.g., `Route`, `GPS Coordinates`, `Fare Details`, `Cargo Details`).
   - **Multi-Valued Attributes:** Attributes that support multiple contact representations (represented by double ovals).
4. **Third Normal Form (3NF) Compliance:** Eliminates insertion, deletion, and update anomalies through decoupled relations (e.g., Drivers decoupled from Vehicles; Bookings decoupled from Invoices and Receipts).
5. **100% Native Editable PowerPoint (.pptx):** The delivered PowerPoint presentation contains native, individual shapes (rectangles, diamonds, ovals, connectors, and tables) that can be directly clicked, edited, recolored, resized, and modified by the student in Microsoft PowerPoint.

---

## 2. Comprehensive Keys Classification Matrix (सारे प्रकार की Keys का विवरण)

In database management systems (DBMS), keys enforce entity identity and referential integrity. The Ghidora Transport schema utilizes five distinct key types:

| Key Classification | Theoretical DBMS Definition | Columns in Ghidora Transport | Database Constraint | Academic & Viva Justification |
| :--- | :--- | :--- | :--- | :--- |
| **Primary Key (PK)**<br>`[प्राथमिक कुंजी]` | An attribute or minimal set of attributes that uniquely and unambiguously identifies each record in a relation. Cannot be NULL. | • `auth_user.id`<br>• `booking_booking.id`<br>• `drivers_driver.id`<br>• `drivers_vehicle.id`<br>• `payments_paymentrequest.id`<br>• `payments_receipt.id`<br>• `booking_bookingattachment.id`<br>• `booking_review.id`<br>• `booking_predefinedroutefare.id`<br>• `booking_predefinedroutedistance.id` | `PRIMARY KEY`<br>(64-bit `BigAutoField`)<br>`NOT NULL` + `UNIQUE` | Guarantees $O(1)$ B-Tree clustered indexing, compact Foreign Key references in child tables, and total isolation from business tracking code modifications. |
| **Candidate Key (CK)**<br>`[उम्मीदवार कुंजी]` | A minimal superkey with no redundant attributes; an attribute capable of serving as the primary key. | • `id` vs `booking_id` in `Booking`<br>• `id` vs `mobile` in `Driver`<br>• `id` vs `license_number` in `Driver`<br>• `id` vs `vehicle_number` in `Vehicle`<br>• `id` vs `payment_id` in `PaymentRequest`<br>• `id` vs `receipt_id` in `Receipt` | Mathematical candidate sets: Each satisfies uniqueness and minimality. | Demonstrates that the schema has multiple candidate keys. The integer surrogate was selected as the PK, and the others were designated as Alternate/Unique Keys. |
| **Alternate / Unique Key (UK)**<br>`[वैकल्पिक / अद्वितीय कुंजी]` | Candidate keys that are not selected as the primary key. Enforced in SQL via `UNIQUE` constraints. | • `Booking.booking_id` (e.g. `GT4592`)<br>• `Driver.mobile` (10-digit number)<br>• `Driver.license_number` (RTO License)<br>• `Vehicle.vehicle_number` (e.g. `CG05 AB 1234`)<br>• `PaymentRequest.payment_id` (`PAY-XXXXXX`)<br>• `Receipt.receipt_id` (`RCPT-XXXXXX`)<br>• `User.username` (Login Handle) | `UNIQUE=True`<br>`db_index=True` | Provides human-readable tracking identifiers for customers and administrative dispatchers while maintaining surrogate keys for database engine efficiency. |
| **Foreign Key (FK)**<br>`[विदेशी कुंजी]` | An attribute in a child table that references the Primary Key of a parent table, establishing referential integrity. | • `Booking.user_id` &rarr; `User(id)`<br>• `Booking.assigned_driver_id` &rarr; `Driver(id)`<br>• `PaymentRequest.booking_id` &rarr; `Booking(id)`<br>• `PaymentRequest.created_by_id` &rarr; `User(id)`<br>• `BookingAttachment.booking_id` &rarr; `Booking(id)`<br>• `Review.booking_id` &rarr; `Booking(id)`<br>• `Review.user_id` &rarr; `User(id)` | `FOREIGN KEY REFERENCES`<br>Governed by `ON DELETE CASCADE` or `ON DELETE SET_NULL` | Prevents orphan records. Guarantees that invoices, attachments, and assignments cannot point to non-existent parent bookings or accounts. |
| **One-to-One Unique FK**<br>`[एक-से-एक विदेशी कुंजी]` | A Foreign Key with a strict `UNIQUE` constraint, restricting cardinality to at most one child per parent. | • `Vehicle.driver_id` &rarr; `Driver(id)`<br>• `Receipt.payment_request_id` &rarr; `PaymentRequest(id)` | `OneToOneField`<br>(`FOREIGN KEY` + `UNIQUE`) | Enforces physical real-world business logic: Exactly one commercial vehicle per driver; exactly one official tax receipt per payment request. |
| **Composite Attribute (COMP)**<br>`[संयुक्त विशेषता]` | An attribute composed of multiple atomic sub-attributes grouped logically. | • `Route`: `pickup` + `destination`<br>• `Coordinates`: `lat` + `lng` (origin & dest)<br>• `Fare Details`: `fare` + `toll` + `parking`<br>• `Cargo Details`: `cargo_type` + `weight_value` + `weight_unit` | Stored as separate atomic columns in 1NF, grouped logically in ER modeling. | Reflects real-world domain concepts without violating First Normal Form (1NF). |

---

## 3. Entity Descriptions & Field Specifications (10 Verified Tables)

### 3.1 Entity: `Customer (User)` (Table: `auth_user`)
- **Django Model:** `django.contrib.auth.models.User`
- **Description:** Represents authenticated customers, client organizations, and administrative dispatchers.
- **Attributes:**
  - `id` (**PK**, `BigAutoField`) — Surrogate Primary Key.
  - `username` (**UK**, `CharField(150)`) — Unique user login identifier.
  - `email` (`EmailField`) — Registered email for electronic booking receipts.
  - `Name` (**COMP**): `first_name` + `last_name`.
  - `phone` (**Multi-valued**, `CharField(15)`) — Customer telephone from linked profile.
  - `is_staff` (`BooleanField`) — Staff/Dispatcher authorization flag.
  - `date_joined` (`DateTimeField`) — Account registration timestamp.

### 3.2 Entity: `Booking` (Table: `booking_booking`)
- **Django Model:** `booking.models.Booking`
- **Description:** The central transaction hub of the Ghidora Transport platform. Orchestrates trip scheduling, vehicle dispatch, GPS metrics, and pricing.
- **Attributes:**
  - `id` (**PK**, `BigAutoField`) — Surrogate Primary Key.
  - `booking_id` (**UK**, `CharField(20)`) — Unique customer-facing reference (e.g., `GT4592`).
  - `user_id` (**FK**, `ForeignKey(User)`, Nullable, `SET_NULL`) — Authenticated user link (supports unauthenticated Guest Bookings).
  - `assigned_driver_id` (**FK**, `ForeignKey(Driver)`, Nullable, `SET_NULL`) — Commercial driver assigned by dispatcher.
  - `name`, `phone`, `email` (`CharField`) — Customer contact coordinates.
  - `Route` (**COMP**): `pickup` + `destination`.
  - `Coordinates` (**COMP**): `pickup_lat`, `pickup_lng`, `destination_lat`, `destination_lng` (`FloatField`).
  - `duration_text` (`CharField(50)`) — Google Directions road travel time (e.g., "1 hour 45 mins").
  - `distance` (`FloatField`) — Road distance in Kilometers.
  - `distance_source` (`CharField(50)`) — Calculation origin (`Google Generated`, `Manual Entered`, `Predefined Route`).
  - `Fare Details` (**COMP**): `fare` (Base ₹) + `toll_charges` (Tolls ₹) + `parking_charges` (Parking ₹).
  - `fare_type` (`CharField(50)`) — Calculation model (`Predefined Route Fare` vs `Distance Based Fare`).
  - `vehicle_type` (`CharField(50)`) — Commercial vehicle category (`Mahindra Pickup`, `Bolero Pickup`).
  - `trip_type` (`CharField(30)`) — Travel mode (`One Way` vs `Round Trip`).
  - `Cargo Details` (**COMP**): `cargo_type` (`CharField`) + `weight_value` (`DecimalField`) + `weight_unit` (`kg` / `ton`).
  - `status` (`CharField(30)`) — Lifecycle state (`Pending`, `Confirmed`, `Completed`, `Cancelled`).
  - `payment_status` (`CharField(30)`) — Settlement state (`Pending`, `Paid`, `Partial`, `Failed`).
  - `journey_date` (`DateField`) — Scheduled transportation date.
  - `booking_date` (`DateTimeField`) — Booking placement timestamp.

### 3.3 Entity: `Driver` (Table: `drivers_driver`)
- **Django Model:** `drivers.models.Driver`
- **Description:** Registered commercial transport drivers operating in the logistics fleet.
- **Attributes:**
  - `id` (**PK**, `BigAutoField`) — Surrogate Primary Key.
  - `name` (`CharField(100)`) — Full legal driver name.
  - `mobile` (**UK**, `CharField(15)`) — Unique 10-digit primary mobile contact.
  - `license_number` (**UK**, `CharField(50)`) — Unique commercial RTO driving license.
  - `experience_years` (`PositiveIntegerField`) — Commercial driving experience in years.
  - `status` (`CharField(20)`) — Operational status (`available` / `busy`).
  - `is_default` (`BooleanField`) — Automated dispatch default driver flag.
  - `address` (`CharField(255)`) — Verified residential address.
  - `created_at` (`DateTimeField`) — Onboarding timestamp.

### 3.4 Entity: `Vehicle` (Table: `drivers_vehicle`)
- **Django Model:** `drivers.models.Vehicle`
- **Description:** Commercial transport vehicles in the logistics fleet.
- **Attributes:**
  - `id` (**PK**, `BigAutoField`) — Surrogate Primary Key.
  - `driver_id` (**FK, 1:1, UK**, `OneToOneField(Driver)`) — Dedicated assigned driver.
  - `vehicle_number` (**UK**, `CharField(20)`) — Official RTO registration plate (e.g., `CG05 AB 1234`).
  - `vehicle_type` (`CharField(50)`) — Vehicle category (`Mahindra Pickup`, `Bolero`, `Mini Truck`).
  - `capacity` (`CharField(50)`) — Rated cargo carrying payload (e.g., `1.2 Ton`, `1.7 Ton`).
  - `rc_number` (`CharField(50)`) — Registration Certificate (RC) number.

### 3.5 Entity: `PaymentRequest` (Table: `payments_paymentrequest`)
- **Django Model:** `payments.models.PaymentRequest`
- **Description:** Financial billing invoices generated for customer payment milestones.
- **Attributes:**
  - `id` (**PK**, `BigAutoField`) — Surrogate Primary Key.
  - `payment_id` (**UK**, `CharField(50)`) — Unique payment tracking code (e.g., `PAY-7E3B1C`).
  - `booking_id` (**FK**, `ForeignKey(Booking)`, `CASCADE`) — Invoiced booking.
  - `created_by_id` (**FK**, `ForeignKey(User)`, Nullable, `SET_NULL`) — Dispatcher who initiated the invoice.
  - `payment_type` (`CharField(20)`) — Settlement milestone (`advance`, `full`, `remaining`).
  - `amount` (`DecimalField(10,2)`) — Requested amount in INR (₹).
  - `total_fare` (`DecimalField(10,2)`) — Total agreed journey fare in INR.
  - `amount_already_paid` (`DecimalField(10,2)`) — Previously settled funds.
  - `status` (`CharField(20)`) — Invoice status (`pending`, `submitted`, `verified`, `rejected`).
  - `due_date` (`DateTimeField`) — Payment validity cutoff timestamp.
  - `preferred_method` (`CharField(30)`) — Payment mode (`qr`, `upi`, `bank`).
  - `gateway` (`CharField(30)`) — Payment gateway (`manual`, `razorpay`, `phonepe`).
  - `created_at` (`DateTimeField`) — Invoice generation timestamp.

### 3.6 Entity: `Receipt` (Table: `payments_receipt`)
- **Django Model:** `payments.models.Receipt`
- **Description:** Legally binding financial receipts generated upon payment verification.
- **Attributes:**
  - `id` (**PK**, `BigAutoField`) — Surrogate Primary Key.
  - `receipt_id` (**UK**, `CharField(50)`) — Unique receipt number (e.g., `RCPT-4A2D8E`).
  - `payment_request_id` (**FK, 1:1, UK**, `OneToOneField(PaymentRequest)`, `CASCADE`) — Linked verified invoice.
  - `pdf_file` (`FileField`) — Stored ReportLab-generated PDF tax invoice path.
  - `generated_at` (`DateTimeField`) — Receipt creation timestamp.
  - `sent_to_email` (`CharField(254)`) — Recipient customer email address.
  - `is_sent` (`BooleanField`) — Automated email delivery status flag.

### 3.7 Entity: `BookingAttachment` (Table: `booking_bookingattachment`)
- **Django Model:** `booking.models.BookingAttachment`
- **Description:** Media files uploaded by customers to clarify consignment requirements.
- **Attributes:**
  - `id` (**PK**, `BigAutoField`) — Surrogate Primary Key.
  - `booking_id` (**FK**, `ForeignKey(Booking)`, `CASCADE`) — Parent booking reference.
  - `attachment_type` (`CharField(20)`) — Media classification (`voice`, `photo`, `video`).
  - `file` (`FileField`) — Stored consignment audio note, photograph, or video.
  - `uploaded_at` (`DateTimeField`) — Upload timestamp.

### 3.8 Entity: `Review` (Table: `booking_review`)
- **Django Model:** `booking.models.Review`
- **Description:** Customer feedback, star ratings, and testimonials.
- **Attributes:**
  - `id` (**PK**, `BigAutoField`) — Surrogate Primary Key.
  - `booking_id` (**FK**, `ForeignKey(Booking)`, Nullable, `SET_NULL`) — Linked booking.
  - `user_id` (**FK**, `ForeignKey(User)`, Nullable, `SET_NULL`) — Authenticated customer.
  - `guest_name` (`CharField(100)`) — Reviewer name for unauthenticated reviews.
  - `rating` (`IntegerField`) — Star rating on 1 to 5 scale.
  - `comment` (`TextField`) — Written customer feedback.
  - `service_used` (`CharField(100)`) — Logistics service utilized.
  - `is_approved` (`BooleanField`) — Administrative moderation approval flag.
  - `is_verified` (`BooleanField`) — Verified customer booking badge.
  - `created_at` (`DateTimeField`) — Submission timestamp.

### 3.9 Entity: `PredefinedRouteFare` (Table: `booking_predefinedroutefare`)
- **Django Model:** `booking.models.PredefinedRouteFare`
- **Description:** Fixed pricing matrix for popular transport routes.
- **Attributes:**
  - `id` (**PK**, `BigAutoField`) — Surrogate Primary Key.
  - `from_location` (`CharField(100)`) — Origin commercial hub.
  - `to_location` (`CharField(100)`) — Destination hub.
  - `fixed_fare` (`DecimalField(10,2)`) — One-way flat rate in INR.
  - `double_trip_fare` (`DecimalField(10,2)`) — Round-trip flat rate in INR.
  - `distance_km` (`DecimalField(8,2)`) — Standardized route road distance.
  - `same_direction_both` (`BooleanField`) — Bidirectional applicability (A &rarr; B and B &rarr; A).
  - `is_active` (`BooleanField`) — Pricing active status flag.

### 3.10 Entity: `PredefinedRouteDistance` (Table: `booking_predefinedroutedistance`)
- **Django Model:** `booking.models.PredefinedRouteDistance`
- **Description:** Standardized road distance table used when Google Maps API is unavailable or overridden.
- **Attributes:**
  - `id` (**PK**, `BigAutoField`) — Surrogate Primary Key.
  - `from_location`, `to_location` (`CharField(100)`) — Origin and destination pair.
  - `distance_km` (`DecimalField(8,2)`) — Official road distance in KM.
  - `same_direction_both` (`BooleanField`) — Bidirectional applicability.
  - `is_active` (`BooleanField`) — Active status flag.

---

## 4. Entity Relationships & Cardinality Analysis

| Relationship Name | Connecting Entities | Cardinality | Django Implementation | Integrity Action (`on_delete`) | Business & Technical Explanation |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **places / books** | `User` &rarr; `Booking` | **1 : N**<br>(`1` to `0..*`) | `ForeignKey(User, null=True)` | `ON DELETE SET_NULL` | A registered customer can place multiple bookings over time. If a user deletes their account, historical trip records are preserved with `user_id = NULL` for financial audits. |
| **includes** | `Booking` &rarr; `BookingAttachment` | **1 : N**<br>(`1` to `0..*`) | `ForeignKey(Booking)` | `ON DELETE CASCADE` | A booking may include multiple voice notes, photos, or videos of cargo. Deleting a booking cleanly purges all its dependent consignment media files. |
| **generates** | `Booking` &rarr; `PaymentRequest` | **1 : N**<br>(`1` to `0..*`) | `ForeignKey(Booking)` | `ON DELETE CASCADE` | A booking can have multiple payment requests for milestone billing (Advance deposit + Remaining balance). Deleting a booking removes associated payment invoices. |
| **issues** | `PaymentRequest` &rarr; `Receipt` | **1 : 1**<br>(`1` to `0..1`) | `OneToOneField(PaymentRequest)` | `ON DELETE CASCADE` | A verified payment request generates exactly one official tax invoice PDF receipt. Enforces strict single-invoice integrity. |
| **assigns** | `Booking` &rarr; `Driver` | **N : 1**<br>(`0..*` to `0..1`) | `ForeignKey(Driver, null=True)` | `ON DELETE SET_NULL` | A commercial driver can be assigned to multiple bookings over time. New bookings can exist unassigned initially (`NULL`). Deleting a driver preserves historical trip data. |
| **operates** | `Driver` &rarr; `Vehicle` | **1 : 1**<br>(`1` to `1`) | `OneToOneField(Driver)` | `ON DELETE CASCADE` | Dedicated commercial fleet binding: Exactly one commercial vehicle is assigned to exactly one driver. Prevents duplicate vehicle assignments. |
| **submits** | `User` &rarr; `Review` | **1 : N**<br>(`1` to `0..*`) | `ForeignKey(User, null=True)` | `ON DELETE SET_NULL` | Users can submit multiple reviews for different completed trips. Guest reviews are supported with `user_id = NULL`. |
| **receives** | `Booking` &rarr; `Review` | **1 : N**<br>(`0..1` to `0..*`) | `ForeignKey(Booking, null=True)` | `ON DELETE SET_NULL` | A trip booking can receive customer feedback. Decoupled to allow general platform testimonials. |
| **applies** | `Booking` &rarr; `PredefinedRouteFare` | **N : 1**<br>(`0..*` to `0..1`) | Logical Lookup Query | Query-time reference | If origin and destination match a pre-configured route pair, fixed fare rates override default distance calculations. |
| **measures** | `Booking` &rarr; `PredefinedRouteDistance`| **N : 1**<br>(`0..*` to `0..1`) | Logical Lookup Query | Query-time reference | Provides official pre-calculated road distances, serving as an offline fallback when Google Distance Matrix is unavailable. |

---

## 5. Third Normal Form (3NF) Normalization Proof

During your college viva, examiners often ask: **"Is your database normalized? Prove it satisfies 3NF."**

1. **First Normal Form (1NF):**
   - *Requirement:* All attributes must be atomic; no multi-valued attributes or repeating groups.
   - *Ghidora Implementation:* Every column in the database stores single, indivisible values. Composite concepts (like `Route` and `Coordinates`) are decomposed into atomic columns (`pickup`, `destination`, `pickup_lat`, `pickup_lng`). No arrays or comma-separated strings are used.
2. **Second Normal Form (2NF):**
   - *Requirement:* Must be in 1NF, and all non-key attributes must be fully functionally dependent on the primary key (no partial dependencies on composite keys).
   - *Ghidora Implementation:* Every table uses a single-attribute surrogate Primary Key (`id`). Since no composite primary keys exist, partial functional dependencies are mathematically impossible.
3. **Third Normal Form (3NF):**
   - *Requirement:* Must be in 2NF, and no transitive dependencies must exist (non-key attributes must not depend on other non-key attributes: $X \rightarrow Y$ where $Y$ is non-prime and $X$ is not a superkey).
   - *Ghidora Implementation:*
     - Driver details (`mobile`, `license_number`) are separated from Vehicle details (`rc_number`, `capacity`). Vehicle stores only `driver_id`.
     - Payment details (`amount`, `gateway`) are separated from Receipt details (`pdf_file`, `sent_to_email`). Receipt stores only `payment_request_id`.
     - Fixed route fares (`fixed_fare`, `double_trip_fare`) are extracted into `PredefinedRouteFare` rather than being redundantly repeated inside every `Booking` row.

---

## 6. Presentation Files & Editable PowerPoint Assets

All ER diagram assets are saved in `project_documentation/er_diagram/`:

1. `Ghidora_Transport_ER_Diagram_Presentation.pptx` — **Comprehensive 10-Slide Academic Presentation (100% Native Editable Shapes & Tables)**:
   - **Slide 1:** Interactive Academic ER Diagram (Chen's Notation) with 91 native PowerPoint shapes, connector lines, key badges, and legend card.
   - **Slide 2:** High-Resolution Print / Projector ER Diagram (5200x3250 B&W vector-rendered).
   - **Slide 3:** Relational Database Schema (Crow's Foot Table Architecture with editable cells).
   - **Slide 4:** Comprehensive Keys Classification Matrix (PK vs FK vs UK vs Candidate Keys).
   - **Slide 5:** Subsystem Deep-Dive 1: Customer Accounts & Trip Bookings.
   - **Slide 6:** Subsystem Deep-Dive 2: Fleet Dispatch & Driver Operations.
   - **Slide 7:** Subsystem Deep-Dive 3: Financial Invoicing, Gateways & Receipts.
   - **Slide 8:** Subsystem Deep-Dive 4: Pricing Engine, Distance Matrix & Reviews.
   - **Slide 9:** Master Cardinality, Referential Integrity (`CASCADE`/`SET_NULL`) & 3NF Proof.
   - **Slide 10:** Top 10 MCA Minor Project Viva Voce Questions & Model Technical Answers.
2. `Ghidora_Transport_ER_Diagram_Editable.pptx` — Focused editable presentation for direct copying into existing project slides.
3. `Ghidora_Transport_ER_Diagram_OnePage.pptx` — Single-slide academic master presentation.
4. `ghidora_transport_er_diagram_bw.png` / `ghidora_transport_er_diagram.png` — Ultra-high-definition (5209 x 3250) presentation images.
5. `ghidora_transport_er_diagram_bw.svg` / `ghidora_transport_er_diagram.svg` — Scalable vector graphics.
6. `ghidora_transport_er_diagram_source.dot` — Graphviz DOT source in Black & White.
7. `ghidora_transport_er_diagram_source.mmd` — Mermaid ER source with all key types.
