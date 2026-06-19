# Playlist Recommender — Project Context

## What this is
A hybrid music recommendation system built as a portfolio project for entry-level ML/engineering recruiting. Two modes share a single user preference vector:
- **Playlist generation**: questionnaire or NLP prompt → clustered playlists
- **Song recommendation**: Spotify listening history → ranked song list

## Agreed tech stack
| Layer | Choice | Why |
|---|---|---|
| Backend | FastAPI + uvicorn | async-first, native OpenAPI docs |
| DB | PostgreSQL + pgvector | relational schema + ANN search in one system |
| Migrations | Alembic | keeps schema in sync with SQLAlchemy models |
| Embeddings | sentence-transformers (all-MiniLM-L6-v2) | pre-trained, 384-dim, no training required |
| Ranker | LightGBM (impressive) / weighted cosine (MVP) | tree model on feedback features |
| Task queue | Celery + Redis | async preference vector updates after feedback |
| LLM | Claude API | NLP intent extraction from free-text prompts |
| Frontend | React + Vite + Tailwind | fast to build, easy to deploy |
| Hosting | Fly.io / Railway (backend), Supabase (DB), Vercel (frontend) | low ops overhead |

## Infrastructure
- **Docker Compose** runs local Postgres (pgvector/pgvector:pg16) + Redis for development
- **Supabase** is production Postgres — `DATABASE_URL` in `.env` points there
- `LOCAL_DATABASE_URL` points to Docker Postgres; `config.py` picks the right one based on `ENVIRONMENT`
- **WSL gotcha**: system PostgreSQL 14 was pre-installed and claimed port 5432. Disabled via `sudo systemctl disable postgresql@14-main`. Docker now owns 5432.
- Docker Compose project name is `playlist-recommender` (set explicitly to avoid collisions)

## Environment
- `.env` lives in `backend/` (uvicorn runs from there)
- `ENVIRONMENT=development` → uses `LOCAL_DATABASE_URL`
- `ENVIRONMENT=production` → uses `DATABASE_URL` (Supabase)

## Current file state
```
backend/
  app/
    core/
      config.py       ✓ done — pydantic-settings, active_database_url property
      database.py     ✓ done — async SQLAlchemy engine, Base, get_db dependency
    main.py           ✓ done — FastAPI app, CORS, /health endpoint with DB check
  requirements.txt    ✓ done
docker-compose.yml    ✓ done
.env / .env.example   ✓ done
frontend/
  src/
    App.tsx                        ✓ done — BrowserRouter, layout route, 4 page routes
    components/Layout/Layout.tsx   ✓ done — nav bar + Outlet
    pages/                         ✓ done — Home, Generate, Results, Recommendations (stubs)
    index.css                      ✓ done — Tailwind directives only
  tailwind.config.js               ✓ done
  package.json                     ✓ done — react-router-dom, tailwindcss@3
```

## Node version
nvm installed, Node 22.23.0 active. nvm loads automatically in new terminals via ~/.bashrc.
In existing terminals: `export NVM_DIR="$HOME/.nvm" && source "$NVM_DIR/nvm.sh"`

## Phase checklist
### Phase 0 — Setup ✓
- [x] Repo, .gitignore, .env
- [x] Spotify developer app registered
- [x] Supabase project created, pgvector enabled
- [x] docker-compose.yml (postgres + redis)
- [x] FastAPI scaffold (config, database, main, health check)
- [x] React scaffold (Vite + Tailwind + React Router, Node 22 via nvm)

### Phase 1 — Data Foundation (Days 2–5) ← **next**
- [ ] SQLAlchemy models: Track, User, Playlist, FeedbackEvent, IntentSession
- [ ] Alembic setup + initial migration
- [ ] spotify_client.py service
- [ ] scripts/ingest_catalog.py (10–20k tracks)
- [ ] pgvector column on tracks table

### Phase 2 — MVP Pipeline (Days 6–10)
- [ ] intent_extractor.py (questionnaire → structured dict)
- [ ] retrieval.py (cosine on audio features)
- [ ] ranker.py (weighted scoring)
- [ ] playlist_builder.py (single playlist, energy arc)
- [ ] Routes: POST /intent/questionnaire, POST /playlists/generate

### Phase 3 — Frontend MVP (Days 11–14)
- [ ] Questionnaire component
- [ ] PlaylistView + TrackRow
- [ ] FeedbackButtons
- [ ] Deploy backend to Fly.io, frontend to Vercel

### Phase 4–8
- Phase 4: sentence-transformer track embeddings, pgvector HNSW index, ANN retrieval
- Phase 5: K-Means multi-playlist clustering, Spotify OAuth, history-based user embeddings
- Phase 6: feedback loop — FeedbackEvent storage + online preference vector updates
- Phase 7: LLM intent extraction (Claude API), LightGBM ranker, evaluation metrics
- Phase 8: rate limiting, pagination, tests, README architecture diagram, demo video

## Potential data model (reference for Phase 1)

### Track
- id (UUID PK), spotify_id (str, unique), title, artist, album, release_year, popularity
- audio features: energy, valence, tempo, danceability, acousticness, instrumentalness, liveness, speechiness, loudness, mode, key
- genres (ARRAY of str), embedding (Vector(384) — null until Phase 4), indexed_at

### User
- id (UUID PK), spotify_user_id (str, nullable — null for anonymous users), created_at
- preference_embedding (Vector(384)), preference_source (enum: QUESTIONNAIRE/HISTORY/HYBRID), preference_updated_at
- liked_track_ids (ARRAY UUID), disliked_track_ids (ARRAY UUID)

### IntentSession
- id (UUID PK), user_id (FK), source (enum: QUESTIONNAIRE/NLP_PROMPT)
- raw_input (JSON — questionnaire answers or prompt string)
- extracted_intent (JSON — structured: {energy, valence, genres, tempo_range, ...})
- intent_embedding (Vector(384)), created_at

### Playlist
- id (UUID PK), user_id (FK), intent_session_id (FK nullable)
- name, theme_label, track_ids (ARRAY UUID — ordered)
- generation_mode (enum: PLAYLIST_GEN/RECOMMENDATION), created_at
- feedback (enum: SAVED/DISMISSED/EDITED), edited_track_ids (ARRAY UUID nullable)

### FeedbackEvent
- id (UUID PK), user_id (FK), track_id (FK nullable), playlist_id (FK nullable)
- type (enum: LIKE/DISLIKE/SKIP/SAVE_PLAYLIST/EDIT_PLAYLIST/DISMISS)
- position (int nullable — rank position when feedback occurred)
- context_playlist_id (FK nullable), created_at

## User preferences
- Explain design decisions before writing code, not after
- No comments in code files — explain in chat instead
- Walk through pieces one at a time; user wants to understand each step
- Short concise responses preferred
