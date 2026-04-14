<div align="center">

# AnimeDivide · アニメ分断分析エンジン

**Mapping the fault lines of anime fandom — arc by arc, episode by episode**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111-009688?style=flat-square&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-15-black?style=flat-square&logo=next.js)](https://nextjs.org)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16-4169E1?style=flat-square&logo=postgresql&logoColor=white)](https://postgresql.org)
[![Groq](https://img.shields.io/badge/Groq-LLaMA_3-F55036?style=flat-square)](https://console.groq.com)
[![License](https://img.shields.io/badge/License-MIT-22c55e?style=flat-square)](LICENSE)

</div>

---

## What Is This?

AnimeDivide analyzes **why fanbases fracture** at specific points in a show's run.

Every long-running anime has "the moment" — the story arc, pacing shift, or creative decision that splits a previously unified fanbase into loyalists and drop-outs. AnimeDivide scrapes episode-level metadata, generates narrative arc embeddings with `sentence-transformers`, and uses a Groq-powered LLM to produce structured analysis of *exactly where the divide happened, why, and how deep it runs*.

**Example outputs:**
- *Bleach TYBW* — nostalgia cohort (2004–2012 readers) vs. new-anime-only fans: what they disagree on and why
- *Attack on Titan Final Season* — ideological split in the writing; which arcs each camp scores drastically differently
- *Vinland Saga S2* — pacing divide between manga readers and anime-only viewers

---

## Tech Stack

| Layer | Technology |
|---|---|
| **API** | [FastAPI](https://fastapi.tiangolo.com) + Uvicorn |
| **Database** | [PostgreSQL 16](https://postgresql.org) via SQLAlchemy |
| **Cache / Queue** | Redis |
| **Embeddings** | [sentence-transformers](https://sbert.net) (`paraphrase-multilingual-MiniLM-L12-v2`) |
| **LLM** | [Groq](https://console.groq.com) (`llama-3.1-8b-instant`) |
| **Anime Metadata** | MyAnimeList Jikan API |
| **Frontend** | [Next.js 15](https://nextjs.org) (App Router) |
| **Containerization** | Docker + Docker Compose |

---

## Project Structure

```
anime-divide/
├── README.md
├── docker-compose.yml          ← postgres + redis
├── .gitignore
│
├── backend/                    ← FastAPI service
│   ├── main.py                 ← app entry point, router wiring
│   ├── requirements.txt
│   ├── .env.example
│   ├── Dockerfile
│   │
│   ├── routers/
│   │   ├── shows.py            ← GET /shows, /shows/{slug}, /shows/{slug}/narrative
│   │   ├── scraper.py          ← POST /scrape/{slug}
│   │   └── pipeline.py         ← POST /pipeline/run/{slug}
│   │
│   ├── services/               ← business logic (scraper, embedder, analyser)
│   ├── models/                 ← SQLAlchemy ORM models
│   │
│   ├── data/
│   │   └── shows_seed.py       ← 10 seeded anime shows with MAL IDs
│   │
│   └── scripts/
│       └── seed_db.py          ← one-shot DB seeder
│
└── frontend/                   ← Next.js 15 app (coming soon)
```

---

## Quick Start

### Prerequisites

- Docker & Docker Compose
- Python 3.11+
- A free [Groq API key](https://console.groq.com)
- A free [MyAnimeList Client ID](https://myanimelist.net/apiconfig)

### 1 — Clone and configure

```bash
git clone https://github.com/yourname/anime-divide.git
cd anime-divide
cp backend/.env.example backend/.env
# Fill in GROQ_API_KEY and MAL_CLIENT_ID in backend/.env
```

### 2 — Start infrastructure

```bash
docker-compose up -d        # spins up PostgreSQL + Redis
```

### 3 — Run the backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs available at **http://localhost:8000/docs**

### 4 — Seed the database

```bash
python scripts/seed_db.py
```

---

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/shows` | Paginated list of all tracked shows |
| `GET` | `/shows/{slug}` | Metadata for a single show |
| `GET` | `/shows/{slug}/narrative` | Generated narrative arc analysis |
| `POST` | `/scrape/{slug}` | Trigger episode data scrape from MAL |
| `POST` | `/pipeline/run/{slug}` | Run full scrape → embed → analyse pipeline |

---

## Roadmap

- [x] Project scaffold + seed data
- [x] FastAPI skeleton with all route stubs
- [ ] SQLAlchemy models (`Show`, `Episode`, `Narrative`, `Job`)
- [ ] MAL Jikan scraper service
- [ ] sentence-transformers embedding service
- [ ] Groq narrative analysis service
- [ ] Next.js frontend — show detail + narrative arc visualisation
- [ ] Redis job queue (APScheduler → Celery)
- [ ] Docker production build

---

## License

MIT — built by [Kunal Bisht](https://github.com/Titankunal)
