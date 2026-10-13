# GHIDORA TRANSPORT — DATABASE ER DIAGRAM DOCUMENTATION
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
