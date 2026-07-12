# 🌐 Skybiz Communication Network

A full-featured Django-based ISP (Internet Service Provider) web application with admin management, real-time speed test, carousel image management, branch location maps, and more.

---

## 📋 Table of Contents

- [Project Overview](#project-overview)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Features](#features)
  - [1. Carousel Image Management](#1-carousel-image-management)
  - [2. Real-Time Speed Test](#2-real-time-speed-test)
  - [3. Branch Location Maps](#3-branch-location-maps)
  - [4. Direct Phone Support](#4-direct-phone-support)
  - [5. Footer Location Grid Maps](#5-footer-location-grid-maps)
  - [6. Admin Panel](#6-admin-panel)
  - [7. News Ticker](#7-news-ticker)
  - [8. Internet Packages](#8-internet-packages)
  - [9. Contact Form](#9-contact-form)
  - [10. Business Quote Request](#10-business-quote-request)
- [Installation & Setup](#installation--setup)
- [Environment Variables](#environment-variables)
- [Database Models](#database-models)
- [URL Routes](#url-routes)
- [Screenshots](#screenshots)

---

## 📌 Project Overview

**Skybiz Communication Network** is a professional ISP web platform built with Django. It allows customers to explore internet packages, test their real-time internet speed, view branch locations on Google Maps, and contact support directly. The admin panel provides full control over all dynamic content including carousel images, news ticker, branches, packages, footer maps, and user management.

---

## 🛠 Tech Stack

| Layer        | Technology                          |
|--------------|-------------------------------------|
| Backend      | Python 3.14, Django 5.x             |
| Frontend     | HTML5, Tailwind CSS (CDN), Vanilla JS |
| Database     | PostgreSQL (`skybiz_web`)           |
| Media Files  | Django Media (Pillow for images)    |
| Auth         | Django built-in authentication      |

---

## 📁 Project Structure

```
Skybiz-communication-network/
├── skybiz/                        # Django project root
│   ├── internet/                  # Main application
│   │   ├── models.py              # All database models
│   │   ├── views.py               # All views & API endpoints
│   │   ├── urls.py                # URL routing
│   │   ├── forms.py               # Django forms
│   │   ├── context_processors.py  # Global template context
│   │   └── migrations/            # Database migrations
│   ├── templates/                 # HTML templates
│   │   ├── base.html              # Base layout with navbar & footer
│   │   ├── home.html              # Home page (carousel + speed test)
│   │   ├── contact.html           # Contact page with branches & maps
│   │   ├── admin_panel.html       # Admin management dashboard
│   │   ├── packages.html          # Internet packages listing
│   │   ├── services.html          # Services page
│   │   ├── business.html          # Business solutions page
│   │   ├── about.html             # About us page
│   │   └── faq.html               # FAQ page
│   ├── static/                    # Static files (CSS, JS, images)
│   ├── media/                     # Uploaded media files
│   └── skybiz/                    # Django settings package
│       ├── settings.py
│       ├── urls.py
│       └── wsgi.py
├── requirements.txt
└── README.md
```

---

## ✨ Features

---

### 1. 🖼️ Carousel Image Management

**Admin can upload, manage, and delete homepage carousel/slider images directly from the Admin Panel.**

#### How it works:
- Admin navigates to **Admin Panel → Carousel Images**
- Can **upload** new images with a title and optional caption
- **Maximum 5 images** can be active at a time (enforced on both backend and form level)
- Can **delete** any existing carousel image
- Uploaded images are stored in `media/carousel/`

#### Frontend Behaviour:
- If carousel images are available → a **full-screen dynamic slider** is shown as the hero section
- If no images are uploaded → a **static fallback hero** with background image is shown
- Slider features:
  - ⏱️ **Auto-advances** every 5 seconds
  - ◀▶ **Prev/Next buttons** (appear on hover)
  - 🔵 **Dot indicators** (clickable, highlights active slide)
  - 👆 **Touch/Swipe support** for mobile devices
  - Smooth CSS transition animation (`transition-transform duration-700`)

#### Relevant Files:
- Model: `internet/models.py` → `CarouselImage`
- View: `internet/views.py` → `admin_panel` (actions: `add_carousel`, `delete_carousel`)
- Form: `internet/forms.py` → `ImageUploadForm`
- Context: `internet/context_processors.py` → passes `carousel_images` globally
- Templates: `templates/home.html`, `templates/admin_panel.html`

---

### 2. ⚡ Real-Time Speed Test

**Users can test their actual internet speed directly from the browser — no plugins needed.**

#### How it works (Client-Side Measurement):

| Phase    | Method                                                                 |
|----------|------------------------------------------------------------------------|
| **Ping** | 5 sequential requests to `/speedtest/ping/` — average round-trip time |
| **Download** | Fetches 5MB dummy data from `/speedtest/download/` using Fetch Streams API — measures throughput in real-time |
| **Upload** | POSTs 3MB of random bytes to `/speedtest/upload/` using `XMLHttpRequest` with `upload.onprogress` callback |
| **Save** | Results are saved to the database via POST to `/speedtest/save/` |

#### Live UI during test:
- Three **live speed cards** update in real-time:
  - 🔵 Download (Mbps)
  - 🟢 Upload (Mbps)
  - 🟣 Ping (ms)
- Animated **progress bar** with phase label ("Measuring latency...", "Downloading...", etc.)
- Final results are shown in colored gradient cards after test completes

#### API Endpoints:
| Endpoint                | Method | Description                              |
|-------------------------|--------|------------------------------------------|
| `/speedtest/ping/`      | GET    | Returns `{"success": true}` for latency  |
| `/speedtest/download/`  | GET    | Streams 5MB of `b'x'` bytes             |
| `/speedtest/upload/`    | POST   | Accepts binary upload, discards data     |
| `/speedtest/save/`      | POST   | Saves `{download, upload, ping}` to DB   |

#### Relevant Files:
- Model: `internet/models.py` → `SpeedTestResult`
- Views: `internet/views.py` → `speedtest_ping`, `speedtest_download`, `speedtest_upload`, `speedtest_save`
- URLs: `internet/urls.py`
- Template: `templates/home.html` → `{% block scripts %}` section

---

### 3. 📍 Branch Location Maps

**Every branch in the contact page can display an embedded Google Map.**

#### How it works:
- Admin goes to **Admin Panel → Branches** and edits a branch
- Pastes a **Google Maps Embed URL** (the `src` value from Google Maps → Share → Embed) into the **Map Link** field
- On the contact page, each branch card automatically shows a **Google Maps iframe** below the branch details

#### Branch Card shows:
- Branch name, address, city, state
- Phone number and email
- Website link (if set)
- 🗺️ **Google Maps iframe** (height: 176px, rounded corners, lazy-loaded)

#### Relevant Files:
- Model: `internet/models.py` → `Branch` (field: `map_link`)
- Form: `internet/forms.py` → `BranchForm`
- Template: `templates/contact.html` → branch loop with `{% if branch.map_link %}` iframe

---

### 4. 📞 Direct Phone Support

**The "Chat on WhatsApp" button on the contact page has been replaced with a direct call button.**

#### Details:
- **Removed:** WhatsApp `wa.me` link
- **Added:** Direct call link `tel:01883005575`
- Displays as a styled blue button: **"Call Support: 01883005575"**
- On mobile, tapping the button directly initiates a phone call

#### Relevant File:
- Template: `templates/contact.html` (lines ~86–92)

```html
<a href="tel:01883005575" class="inline-flex items-center space-x-3 bg-blue-600 hover:bg-blue-700 text-white px-6 py-3 rounded-lg transition-colors shadow">
    <span class="text-xl">📞</span>
    <span class="font-semibold">Call Support: 01883005575</span>
</a>
```

---

### 5. 🗺️ Footer Location Grid Maps

**Admin can add location map embeds that appear in a responsive grid in the site footer.**

#### How it works:
- Admin goes to **Admin Panel → Footer Locations**
- Adds a **location name** and **Google Maps Embed URL**
- Locations appear in the footer as a **responsive grid** of map embeds:
  - 📱 Mobile: 1 column
  - 💻 Tablet: 2 columns
  - 🖥️ Desktop: 3 columns
- Section is hidden if no active footer locations exist (`{% if footer_locations %}`)

#### Relevant Files:
- Model: `internet/models.py` → `FooterLocation`
- Form: `internet/forms.py` → `FooterLocationForm`
- Context: `internet/context_processors.py` → passes `footer_locations` globally
- Admin View: `internet/views.py` → `admin_panel` (actions: `add_footer_location`, `edit_footer_location`, `delete_footer_location`)
- Template: `templates/base.html` → footer section

---

### 6. 🔧 Admin Panel

**A custom admin dashboard accessible at `/admin/` for staff users.**

#### Sections managed:
| Section            | Actions Available                        |
|--------------------|------------------------------------------|
| **Carousel Images** | Add (max 5), Delete                     |
| **News Ticker**    | Add, Edit, Delete                        |
| **Packages**       | Add, Edit, Delete                        |
| **Branches**       | Add, Edit (with Map Link), Delete        |
| **Footer Locations** | Add, Edit, Delete                      |
| **Users**          | Add (Super Admin / Staff / Regular), Edit, Delete |
| **Contact Messages** | View, mark reply sent                  |
| **Business Quotes** | View                                    |
| **Speed Test Results** | View all recorded test results       |

#### Access:
- URL: `/admin/`
- Login required (`@login_required`)
- Must have `is_staff = True`

---

### 7. 📢 News Ticker

**A scrolling news ticker displayed at the top of every page.**

- Admin can add/edit/delete ticker messages from the Admin Panel
- Only the **latest active** message is shown
- Managed via `NewsTicker` model
- Passed to all templates via the global context processor

---

### 8. 📦 Internet Packages

**Residential and Business internet packages displayed on `/packages/`.**

- Each package has: Name, Type, Download Speed, Upload Speed, Price, Data Limit, Features
- Packages marked `is_popular = True` get a "Most Popular" badge and are scaled up
- Top 3 popular packages also appear on the **Home page** preview section
- Admin can add/edit/delete packages from the Admin Panel

---

### 9. 📬 Contact Form

**Users can send messages from the contact page.**

- Fields: Name, Email, Subject, Message
- Saved as `ContactMessage` in the database
- Admin can view all messages and mark replies as sent in the Admin Panel
- Also includes direct call support button and branch location cards with maps

---

### 10. 💼 Business Quote Request

**Businesses can request a custom internet quote from `/business/`.**

- Fields: Company Name, Contact Person, Email, Phone, Required Bandwidth, Requirements
- Saved as `BusinessQuoteRequest` in the database
- Admin can view all submissions from the Admin Panel

---

## 🚀 Installation & Setup

### 1. Clone the Repository

```bash
git clone https://github.com/Mahadinhasan/Skybiz-communication-network.git
cd Skybiz-communication-network
```

### 2. Create & Activate Virtual Environment

```bash
python -m venv env
# Windows
env\Scripts\activate
# Linux/macOS
source env/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Database

Create a PostgreSQL database named `skybiz_web` and update `skybiz/settings.py`:

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'skybiz_web',
        'USER': 'your_db_user',
        'PASSWORD': 'your_db_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

### 5. Run Migrations

```bash
cd skybiz
python manage.py makemigrations
python manage.py migrate
```

### 6. Create Superuser

```bash
python manage.py createsuperuser
```

### 7. Collect Static Files

```bash
python manage.py collectstatic
```

### 8. Run Development Server

```bash
python manage.py runserver
```

Visit: **http://127.0.0.1:8000/**

---

## 🔐 Environment Variables

Set these in your `settings.py` or a `.env` file:

| Variable          | Description                        |
|-------------------|------------------------------------|
| `SECRET_KEY`      | Django secret key                  |
| `DEBUG`           | `True` for development             |
| `DATABASE_NAME`   | PostgreSQL database name           |
| `DATABASE_USER`   | PostgreSQL username                |
| `DATABASE_PASSWORD` | PostgreSQL password              |
| `MEDIA_ROOT`      | Path for uploaded media files      |
| `MEDIA_URL`       | URL prefix for media files (`/media/`) |

---

## 🗄️ Database Models

| Model                | Description                                    |
|----------------------|------------------------------------------------|
| `NewsTicker`         | Scrolling news messages                        |
| `Package`            | Internet packages (residential/business)       |
| `ContactMessage`     | User contact form submissions                  |
| `BusinessQuoteRequest` | Business bandwidth quote requests           |
| `UserProfile`        | Extended user profile linked to packages       |
| `SpeedTestResult`    | Saved speed test measurements                  |
| `CarouselImage`      | Homepage slider images (max 5)                 |
| `Branch`             | Office/service branch with location map link   |
| `FooterLocation`     | Footer map embeds (admin-managed)              |

---

## 🔗 URL Routes

| URL                       | View                  | Name                  | Description                   |
|---------------------------|-----------------------|-----------------------|-------------------------------|
| `/`                       | `home`                | `home`                | Homepage with carousel & speed test |
| `/packages/`              | `packages`            | `packages`            | All internet packages         |
| `/services/`              | `services`            | `services`            | Services listing              |
| `/business/`              | `business`            | `business`            | Business solutions            |
| `/about/`                 | `about`               | `about`               | About us                      |
| `/contact/`               | `contact`             | `contact`             | Contact form & branches       |
| `/admin/`                 | `admin_panel`         | `admin_panel`         | Admin management dashboard    |
| `/admin/dashboard/`       | `admin_dashboard`     | `admin_dashboard`     | Admin stats dashboard         |
| `/speedtest/ping/`        | `speedtest_ping`      | `speedtest_ping`      | Ping latency endpoint         |
| `/speedtest/download/`    | `speedtest_download`  | `speedtest_download`  | 5MB download test endpoint    |
| `/speedtest/upload/`      | `speedtest_upload`    | `speedtest_upload`    | Upload test endpoint          |
| `/speedtest/save/`        | `speedtest_save`      | `speedtest_save`      | Save speed test results       |
| `/faq/`                   | `faq`                 | `faq`                 | FAQ page                      |

---

## 👨‍💻 Developer

**Mehedi Hasan**
- GitHub: [@Mahadinhasan](https://github.com/Mahadinhasan)
- Project: Skybiz Communication Network

---

> ⚡ Built with Django | Tailwind CSS | PostgreSQL | Vanilla JavaScript
