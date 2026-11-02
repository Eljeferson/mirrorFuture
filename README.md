# Mirror Future

> **Empirical Causal Simulation Engine & Multi-Horizon Behavioral Digital Twin**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115.6-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Angular](https://img.shields.io/badge/Angular-18.2-DD0031?logo=angular&logoColor=white)](https://angular.dev)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white)](https://python.org)
[![Three.js](https://img.shields.io/badge/Three.js-WebGL-black?logo=threedotjs&logoColor=white)](https://threejs.org)
[![PostgreSQL](https://img.shields.io/badge/pgvector-384d-336791?logo=postgresql&logoColor=white)](https://github.com/pgvector/pgvector)
[![Meta Llama](https://img.shields.io/badge/Llama_3.3-70B_Reasoning-0467DF?logo=meta&logoColor=white)](https://ai.meta.com/llama/)

---

## 1. Project Title — Mirror Future

**Mirror Future** is an advanced open-source causal intelligence platform designed to project, simulate, and optimize human trajectories across time. By integrating empirical multi-source telemetry (WhatsApp communications, Google Calendar schedules, and GitHub developer activity) with stochastic Monte Carlo algorithms (NumPy) and state-of-the-art causal reasoning models (Meta Llama 3.2 Vision and Llama 3.3 70B), Mirror Future constructs an actuarial mirror of your life over 180-day horizons.

---

## 2. Professional Project Introduction

Traditional self-improvement tools rely on subjective self-reporting, generic advice, and linear extrapolations that ignore relational friction, cognitive fatigue, and systemic burnout. Mirror Future introduces an empirical alternative grounded in causal inference, semantic vector retrieval (pgvector 384d), and stochastic differential modeling.

Mirror Future analyzes the real-world constraints of an individual—measuring exact communication response latencies, nocturnal development rhythms, and real schedule densities—to project three divergence paths:
- **P90 (Optimal Scenario):** The golden upper bound achievable through optimal daily work caps and restorative sleep targets.
- **P50 (Probable Scenario):** The median trajectory dictated by uncorrected current habits.
- **P10 (Risk Scenario):** The lower bound characterized by burnout, cognitive stagnation, and relational decay.

---

## 3. Project Overview

Mirror Future operates through a bidirectional ingestion-simulation-actuation lifecycle:
1. **Empirical Ingestion:** Secure parsing of real WhatsApp chat exports (`.txt`/`.zip`), calendar feeds (`.ics`), and GitHub commits into structured behavioral metrics.
2. **Causal & Stochastic Simulation:** 1,000-path Monte Carlo simulations across 180 days paired with Meta Llama 3.3 reasoning for inverse engineering prescriptions.
3. **Multi-Modal Verification:** Computer vision inspection of media using EXIF forensic extraction and Llama 3.2 11B Vision for reputational and privacy risk auditing.
4. **Physical Actuation:** Direct compilation of optimal routines into RFC 5545 calendar subscriptions (`.ics`) and automated notification delivery via the WhatsApp Cloud API.

---

## 4. Vision and Mission

- **Vision:** To provide individuals with an empirical, scientifically rigorous foresight engine that eliminates cognitive blind spots and bridges the gap between daily habits and aspirational long-term goals.
- **Mission:** Democratize decision intelligence through transparent causal math, privacy-first vector architecture, and open standards.

---

## 5. Main Objectives

1. **Quantify Relational Dynamics:** Empirically model social interactions via response latencies, initiation ratios, and lexical patterns.
2. **Mitigate Burnout Proactively:** Identify critical habit inflection points (e.g., Days 48–52) before cognitive exhaustion occurs.
3. **Synthesize Inverse Prescriptions:** Calculate the exact daily caps on employment and project work required to hit target milestones with $\ge 95\%$ probability.
4. **Ensure Absolute Privacy:** Provide client-side anonymization and single-click irrevocable data purging across vector stores.

---

## 6. Key Features

### Stochastic Monte Carlo Engine (NumPy)
- Simulates 1,000 parallel trajectories over 180 days across four coupled metrics: project progress, cumulative fatigue, burnout risk, and relational capital.
- Renders percentile confidence bands (P10, P50, P90) with milestone callouts (Day 48 inflection, Day 120 goal attainment).

### Retrieval-Augmented Social Twin (RAG + pgvector)
- Vectorizes conversational exchanges into 384-dimensional dense embeddings (`all-MiniLM-L12-v2`).
- Simulates how specific real-world contacts would respond to prospective decisions, citing historical conversational episodes for transparent attribution.

### EXIF & Computer Vision Forensics (Llama 3.2 11B)
- Parses camera model, lens metadata, timestamps, and GPS coordinates from images.
- Evaluates reputational risk, privacy exposure, and visual scene context to generate preventive recommendations.

### Interactive 3D Multiverse Graph (Three.js WebGL)
- Displays an interactive spatial graph featuring a central ego node, radial contact nodes mapped by latency distance, and 3D bezier trajectory tubes.
- Includes a 180-day timeline scrubber and preset camera viewing angles.

### Production Actuators
- **RFC 5545 Calendar Writer:** Dynamically generates calendar subscription files (`.ics`) compatible with Google Calendar, Apple Calendar, and Microsoft Outlook.
- **WhatsApp Cloud API Integration:** Dispatches causal alerts, schedule reminders, and progress milestones directly to mobile devices.

---

## 7. Technology Stack

### Backend
- **Framework:** FastAPI (Python 3.11 / 3.13)
- **Causal Reasoning:** Meta Llama 3.3 (70B Instruct) via Meta / Groq APIs
- **Vision Inference:** Meta Llama 3.2 (11B Vision Instruct)
- **Numerical Simulation:** NumPy (vectorized Monte Carlo paths)
- **Vector Embeddings:** `sentence-transformers` (`all-MiniLM-L12-v2`, 384 dimensions)
- **Actuators & Parsing:** `icalendar` (RFC 5545), Pillow (EXIF), `httpx`, `pandas`

### Database & Storage
- **Engine:** PostgreSQL 15+
- **Vector Search:** `pgvector` extension (Cosine distance indexing)
- **Compatibility:** Supabase PostgreSQL or local Docker container

### Frontend
- **Framework:** Angular 18 (Standalone Components, Signals, Computed properties)
- **3D Visualization:** Three.js (WebGL rendering)
- **Styling:** Tailwind CSS, PostCSS, Autoprefixer
- **Charts:** Custom responsive mathematical SVG visualizations

---

## 8. System Architecture

```mermaid
flowchart TD
    subgraph Data_Sources ["Real Data Ingestion"]
        WA["WhatsApp Chat (.txt / .zip)"]
        CAL["Calendar (.ics)"]
        GH["GitHub Telemetry"]
    end

    subgraph Backend_Core ["FastAPI Causal Engine"]
        ING["Ingestion Pipeline & Profiler"]
        VEC["Embedding Engine (384d MiniLM)"]
        MC["Monte Carlo Simulator (NumPy 1,000 Paths)"]
        LLAMA["Meta Llama 3.3 (70B) & Llama 3.2 (11B Vision)"]
        ACT["Actuators (Calendar .ics & WhatsApp Cloud API)"]
    end

    subgraph Storage ["Database Layer"]
        PG[("PostgreSQL + pgvector")]
    end

    subgraph Frontend_App ["Angular 18 Frontend"]
        GL["Three.js 3D Multiverse Graph"]
        CHART["Interactive Monte Carlo SVG Charts"]
        TWIN["Social Twin Simulation Feed"]
        PANEL["Actuator & Routine Controls"]
    end

    Data_Sources --> ING
    ING --> VEC
    VEC --> PG
    PG --> LLAMA
    MC --> LLAMA
    LLAMA --> ACT
    MC --> CHART
    LLAMA --> TWIN
    MC --> GL
    ACT --> CAL
```

---

## 9. Project Structure

```
mirror-future/
├── backend/
│   ├── app/
│   │   ├── actuators/
│   │   │   ├── calendar_writer.py        # RFC 5545 .ics generation
│   │   │   └── whatsapp_sender.py        # WhatsApp Cloud API dispatcher
│   │   ├── causal_engine/
│   │   │   ├── exif_and_vision.py        # EXIF parser & Llama 3.2 Vision
│   │   │   ├── markov_mcts_math.py       # NumPy Monte Carlo 180-day engine
│   │   │   ├── meta_llama_api.py         # Llama 3.3 70B inference client
│   │   │   ├── rag_social_twin.py        # Behavioral digital twin simulation
│   │   │   ├── holistic_future_engine.py # Discovery interview & Life2Vec
│   │   │   └── future_media_generator.py # Synthetic media HUD generator
│   │   ├── ingestion/
│   │   │   ├── calendar_github.py        # Google Calendar & GitHub telemetry
│   │   │   ├── contact_profiler.py       # Statistical response latency profiler
│   │   │   ├── embedding_engine.py       # SentenceTransformers 384d vectorizer
│   │   │   ├── live_web_research_engine.py# Real-time macroeconomic queries
│   │   │   └── whatsapp_parser.py        # Android / iOS chat parser
│   │   ├── models/
│   │   │   └── schemas.py                # Strict Pydantic contracts
│   │   ├── routers/
│   │   │   ├── ingest_router.py          # Data ingestion endpoints
│   │   │   └── mirror_future_router.py   # Primary causal & simulation API
│   │   ├── config.py                     # Environment settings
│   │   └── main.py                       # FastAPI application factory
│   ├── .env.example                      # Sanitized environment template
│   └── requirements.txt                  # Python dependencies
├── database/
│   └── 01_production_pgvector.sql        # PostgreSQL pgvector schema
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── core/
│   │   │   │   ├── models/
│   │   │   │   │   └── mirror-future.model.ts    # TypeScript interface contracts
│   │   │   │   └── services/
│   │   │   │       ├── mirror-future.service.ts  # Central state management
│   │   │   │       └── mirror-future-api.service.ts # HTTP API client
│   │   │   ├── features/
│   │   │   │   ├── actuators/
│   │   │   │   │   └── actuators-control-panel.component.ts
│   │   │   │   ├── landing/
│   │   │   │   │   └── mirror-future-landing.component.ts
│   │   │   │   ├── multiverse-3d/
│   │   │   │   │   ├── dr-jef-causal-graph-3d.component.ts # Three.js WebGL scene
│   │   │   │   │   └── monte-carlo-chart.component.ts       # SVG curve visualization
│   │   │   │   ├── real-ingestion/
│   │   │   │   │   └── real-ingestion-panel.component.ts    # Upload & telemetry dashboard
│   │   │   │   └── real-twin-console/
│   │   │   │       └── forensic-and-whatsapp-twin.component.ts # Vision & Social Twin
│   │   │   ├── app.component.ts          # Root component & navigation
│   │   │   └── app.routes.ts             # Application routing table
│   ├── angular.json                      # Angular CLI workspace config
│   ├── package.json                      # Node.js dependencies
│   └── tsconfig.json                     # TypeScript compiler options
└── tests/
    └── test_ingestion_pipeline.py        # Comprehensive test suite
```

---

## 10. Prerequisites

Before installing Mirror Future, ensure your system meets the following requirements:
- **Operating System:** Linux, macOS, or Windows 10/11 (64-bit)
- **Python:** Python 3.11 or Python 3.13
- **Node.js:** Node.js v18.x or v20.x+ (tested on v22.x) with npm 9+
- **Database:** PostgreSQL 15+ with the `pgvector` extension installed
- **Git:** Git 2.30+

---

## 11. Installation Instructions

### 1. Clone Repository
```bash
git clone https://github.com/Eljeferson/mirroFuture.git
cd mirroFuture
```

### 2. Backend Environment Setup
```bash
# Navigate to backend directory
cd backend

# Create a Python virtual environment
python -m venv .venv

# Activate virtual environment
# Windows (PowerShell):
.venv\Scripts\Activate.ps1
# Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Environment Setup
```bash
# Navigate to frontend directory
cd ../frontend

# Install npm packages
npm install
```

---

## 12. Environment Configuration

Copy the example environment file in `backend/` and configure your API credentials:

```bash
cd backend
cp .env.example .env
```

### Key Environment Variables (`backend/.env`)

```ini
# Environment Mode
ENVIRONMENT=production
DEBUG=False

# Meta Llama API (Groq / Meta Cloud API)
GROQ_API_KEY=your_groq_api_key_here
LLAMA_MODEL_REASONING=llama-3.3-70b-versatile
LLAMA_MODEL_VISION=llama-3.2-11b-vision-preview

# Database (PostgreSQL with pgvector)
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your_supabase_anon_or_service_key
DATABASE_URL=postgresql://postgres:password@localhost:5432/mirror_future

# WhatsApp Cloud API (Optional Actuator)
WHATSAPP_API_TOKEN=your_whatsapp_cloud_token
WHATSAPP_PHONE_NUMBER_ID=your_phone_number_id

# Ingestion Security
MAX_CHAT_UPLOAD_SIZE_MB=50
LOCAL_EMBEDDING_DEVICE=cpu
```

---

## 13. Development Setup

### Database Migration
Execute the vector schema migration against your PostgreSQL instance:

```bash
psql -U postgres -d mirror_future -f database/01_production_pgvector.sql
```

This creates the required vector extension and tables:
- `user_real_profile` (Biographical data, sleep habits, thesis progress)
- `real_contacts` (Statistical contact profiles and lexical distributions)
- `real_chat_episodes` (Vectorized conversational chunks with 384d cosine indexing)
- `prediction_logs` (Audit trails of stochastic simulations)

---

## 14. Running the Application

### Start the Backend Server
```bash
cd backend
# With virtual environment activated:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
- API Swagger Documentation: `http://localhost:8000/docs`
- Health check: `http://localhost:8000/api/ingest/health`

### Start the Frontend Application
```bash
cd frontend
npm start
```
- Web Application UI: `http://localhost:4200`

---

## 15. API Documentation

Mirror Future provides an OpenAPI 3.0 compliant REST API:

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/causal/vision-forensics` | Analyzes image EXIF metadata and evaluates reputational risk via Llama 3.2 Vision |
| `POST` | `/api/causal/social-twin/simulate` | Simulates contact responses using RAG over pgvector chat history |
| `POST` | `/api/causal/oracle/simulate-monte-carlo` | Computes 1,000 Monte Carlo trajectories over 180 days with NumPy |
| `GET` | `/api/causal/actuators/download-calendar.ics` | Generates an RFC 5545 `.ics` calendar subscription with optimal daily blocks |
| `POST` | `/api/causal/actuators/send-whatsapp-prescription` | Transmits causal prescriptions via the WhatsApp Cloud API |
| `POST` | `/api/causal/future/holistic-projection` | Generates multi-horizon life projections (1 month, 6 months, 1 year) |
| `POST` | `/api/causal/future/discovery-interview` | Conversational discovery interview powered by Llama 3.3 70B |
| `POST` | `/api/causal/user/purge-all-data` | Permanently deletes all user records and embeddings |
| `POST` | `/api/ingest/whatsapp-chat` | Parses and vectorizes WhatsApp chat export files |
| `POST` | `/api/ingest/google-calendar` | Extracts schedule metrics from `.ics` calendar files |
| `POST` | `/api/ingest/github-activity` | Analyzes commit timestamps and nocturnal activity |
| `POST` | `/api/ingest/sync-telemetry` | Aggregates all sources into `user_real_profile` |
| `GET` | `/api/ingest/health` | Service health status and embedding model readiness check |

---

## 16. Database Configuration

The pgvector database schema (`database/01_production_pgvector.sql`) configures:

```sql
CREATE EXTENSION IF NOT EXISTS vector;

-- Table for semantic conversational memory
CREATE TABLE IF NOT EXISTS real_chat_episodes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    contact_id UUID REFERENCES real_contacts(id) ON DELETE CASCADE,
    episode_sequence INT NOT NULL,
    quoted_exchange TEXT NOT NULL,
    conversation_summary TEXT,
    behavioral_pattern_proven TEXT,
    conflict_or_support_tag VARCHAR(50),
    episode_start_time TIMESTAMPTZ,
    episode_end_time TIMESTAMPTZ,
    embedding vector(384)
);

CREATE INDEX IF NOT EXISTS idx_episodes_embedding 
ON real_chat_episodes USING ivfflat (embedding vector_cosine_ops);
```

---

## 17. Screenshots and Visual Demonstrations

- **Multiverse 3D Graph:** Interactive WebGL view rendering P10, P50, and P90 trajectories with radial contact nodes mapped by latency.
- **Monte Carlo Curve Visualizer:** High-precision SVG chart plotting 180-day progress against critical fatigue thresholds.
- **WhatsApp Social Twin:** Side-by-side simulation feed matching predicted messages against empirical chat evidence.
- **Actuator Control Panel:** Real-time sliders adjusting daily employment, research, sleep, and social hours with instant probability updates.

---

## 18. Usage Instructions

1. **Upload Telemetry:**
   - Navigate to **Data Ingestion** (`/real-ingestion`).
   - Upload your exported WhatsApp chat history (`.txt` or `.zip`), Google Calendar export (`.ics`), or enter your GitHub username.
   - Click **Synchronize Telemetry** to generate your empirical baseline.
2. **Explore 3D Trajectories:**
   - Open **Multiverse 3D** (`/multiverse-3d`).
   - Use the 180-day scrubber to inspect progress, burnout probability, and fatigue curves at any future date.
3. **Audit Images & Simulate Conversations:**
   - Go to **Image & Twin Console** (`/real-twin-console`).
   - Upload a photo to detect EXIF location tags and evaluate reputational exposure.
   - Type a prospective message to simulate how your key contacts will respond.
4. **Subscribe to Optimal Schedule:**
   - In **Actuator Controls** (`/actuators`), click **Download Optimal Schedule (.ICS)**.
   - Import the downloaded `.ics` file into your Google Calendar or Apple Calendar.

---

## 19. Testing Procedures

The project includes an automated test suite verifying parser robustness, mathematical profiling, embedding dimensions, and correlation routines.

### Execute Automated Pipeline Tests
```bash
# Run from repository root
python tests/test_ingestion_pipeline.py
```

Expected output:
```
--- TEST: WhatsApp Parser (Android Spanish/English 12h/24h + Multiline + Unicode) ---
✔ WhatsApp Parser Android verified successfully.

--- TEST: WhatsApp Parser (iOS .zip export with _chat.txt) ---
✔ WhatsApp Parser iOS .zip verified successfully.

--- TEST: Contact Profiler (Response Median, % Initiation, 0-23h, Top Words/Emojis) ---
✔ Contact Profiler mathematically verified.

--- TEST: Embedding Engine (Segmentation + 384d MiniLM-L12-v2 Vectorization) ---
✔ Embedding Engine 384d verified successfully.

--- TEST: Calendar .ics and GitHub Activity Analysis ---
✔ Calendar and GitHub Pipeline verified successfully.

========================================================
🚀 ALL MIRROR FUTURE INGESTION PIPELINE TESTS PASSED
========================================================
```

### Validate Frontend Compilation
```bash
cd frontend
npm run build
```

---

## 20. Deployment Instructions

### Production Frontend Build
```bash
cd frontend
npm run build -- --configuration production
```
The compiled output is located in `frontend/dist/mirror-future` and can be served via Nginx, Cloudflare Pages, or AWS S3.

### Production Backend Deployment
Run using Gunicorn with Uvicorn workers behind an Nginx reverse proxy:

```bash
cd backend
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

---

## 21. Security Considerations

- **Client-Side Anonymization:** Personal names, phone numbers, and identifying handles can be hashed or pseudonymized before transmission.
- **No Unsanitized Vector Exposure:** Embeddings stored in pgvector cannot be reversed into raw conversational text.
- **Immediate Data Purge (`POST /api/causal/user/purge-all-data`):** Drops all associated contact profiles, chat episodes, and telemetry records in a single database transaction.
- **Sanitized Secrets:** Production API keys and tokens are strictly loaded via `.env` files and never committed to source control.

---

## 22. Contribution Guidelines

We welcome contributions from the open-source community:
1. **Fork the repository** on GitHub.
2. **Create a feature branch:** `git checkout -b feature/causal-optimization`.
3. **Commit your changes:** Follow conventional commits (`feat: add Life2Vec sequence encoder`).
4. **Ensure all tests pass:** Run `python tests/test_ingestion_pipeline.py` and `npm run build`.
5. **Open a Pull Request** with a detailed explanation of your changes.

---

## 23. Roadmap

- [x] WhatsApp `.txt` and `.zip` parser with multiline and emoji support
- [x] 384-dimensional pgvector semantic retrieval (`all-MiniLM-L12-v2`)
- [x] 180-day NumPy Monte Carlo simulation with P10/P50/P90 trajectories
- [x] Llama 3.2 11B Vision EXIF and reputational risk analysis
- [x] RFC 5545 `.ics` optimal routine generation and WhatsApp Cloud API dispatch
- [x] Interactive Three.js WebGL 3D Multiverse graph
- [ ] Life2Vec self-attention career transformer model integration
- [ ] Direct Google Calendar OAuth 2.0 live bi-directional sync
- [ ] Multi-agent collaborative scenario simulations

---

## 24. License

Distributed under the **MIT License**. See `LICENSE` for more information.

---

## 25. Contact and Support

- **Project Lead & Architecture:** Mirror Future Team
- **Repository:** [https://github.com/Eljeferson/mirroFuture.git](https://github.com/Eljeferson/mirroFuture.git)
- **Issue Tracker:** [GitHub Issues](https://github.com/Eljeferson/mirroFuture/issues)
- **Discussion & Support:** [GitHub Discussions](https://github.com/Eljeferson/mirroFuture/discussions)
