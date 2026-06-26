# Playlist Recommender — Project Context

## What this is
A music recommendation system built as a portfolio project for entry-level ML/engineering recruiting. Users populate a personal track collection by searching Spotify or importing playlists. Two features operate on that collection:
- **Feature A — Targeted playlist generation**: user writes a natural language prompt → system embeds it and similarity-searches their collection → returns a ranked playlist
- **Feature B — Library auto-sorting**: user imports a large unstructured collection → system clusters embeddings into cohesive playlists, filters outliers, and uses an LLM to name each cluster

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
| Track metadata | Spotify API (search + genres) + Last.fm API (tags) | No global catalog — tracks ingested on demand when users search or import playlists |

## Data approach

No global catalog. Tracks are ingested on demand:
- **Search**: user searches Spotify → selects a track → backend fetches metadata + Last.fm tags → embeds → stores in `tracks` (globally deduplicated by `spotify_id`) + `collection_tracks` (user's library)
- **Playlist import**: user provides a public Spotify playlist URL → backend fetches all tracks via client credentials → same enrich/embed/store flow per track
- **Liked Songs / private playlists**: requires Spotify OAuth (user connects their account) — this is a core planned feature, not an afterthought. The schema is designed for it from day one.

Embedding input: `"{title} by {artist}. Genres: {genres}. Tags: {tags}"` via `all-MiniLM-L6-v2` (384-dim).

### Anonymous sessions (Phase 1) vs Spotify OAuth (later phases)
Phase 1 uses an anonymous user UUID stored in localStorage — no login required. A `User` row is created on first visit. When Spotify OAuth is added, the same row gets `spotify_user_id` + tokens populated; the user's existing collection stays intact.

Spotify refresh tokens expire after **6 months** (policy introduced June 2026). Store `spotify_authorized_at` on the User row (Spotify doesn't expose token issuance timestamps) to detect expiry and prompt re-auth. Tokens stored as plaintext in Supabase; Supabase at-rest encryption is sufficient for portfolio scale.

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
      config.py           ✓ done — pydantic-settings, active_database_url property
      database.py         ✓ done — async SQLAlchemy engine, Base, get_db dependency
    services/
      spotify_client.py   ✓ done — search_tracks, get_artist_genres, get_playlist_tracks
      lastfm_client.py    ✓ done — get_track_tags, get_track_tags_batch
    models.py             ✓ done — redesigned schema (see data model section below)
    main.py               ✓ done — FastAPI app, CORS, /health endpoint with DB check
  alembic/                ✓ done — env.py wired to async engine + models
  alembic/versions/       ✗ stale — old migrations; drop DB and run fresh migration
  requirements.txt        ✓ done
docker-compose.yml        ✓ done
.env / .env.example       ✓ done
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

### Phase 1 — Data Foundation ← **in progress**
- [x] SQLAlchemy models: redesigned schema (Track, User, CollectionTrack, IntentSession, ClusteringRun, Playlist, PlaylistTrack, FeedbackEvent)
- [x] Alembic setup
- [x] spotify_client.py service (search_tracks, get_artist_genres, get_playlist_tracks)
- [x] lastfm_client.py service (get_track_tags, get_track_tags_batch)
- [ ] Drop DB, delete old alembic versions, run fresh migration
- [ ] Anonymous user creation endpoint (POST /users → returns UUID stored in localStorage)
- [ ] Track search endpoint (GET /tracks/search?q=... → Spotify search, returns candidates)
- [ ] Add-to-collection endpoint (POST /collection/tracks — dedup, enrich with Last.fm, embed, store)
- [ ] Playlist import endpoint (POST /collection/import/playlist — batch version of above)
- [ ] GET /collection — returns user's current track list (for frontend display)

### Phase 2 — Feature A: Targeted Playlist Generation
- [ ] embed.py service (sentence-transformers, all-MiniLM-L6-v2)
- [ ] retrieval.py (pgvector cosine similarity search scoped to user's collection)
- [ ] POST /playlists/generate — embed prompt, ANN search, create Playlist + PlaylistTrack rows
- [ ] GET /playlists/{id} — return playlist with tracks

### Phase 3 — Feature B: Library Clustering
- [ ] clustering.py (K-Means via sklearn, silhouette score for k estimation, outlier detection)
- [ ] LLM playlist naming (Claude Haiku — pass top 15 tracks per cluster, get name + description)
- [ ] POST /library/cluster — run clustering, write ClusteringRun + Playlists + PlaylistTracks

### Phase 4 — Frontend MVP
- [ ] Collection view (search + import UI, track list)
- [ ] Targeted generation UI (prompt input → playlist result)
- [ ] Clustering UI (trigger clustering → view generated playlists)
- [ ] Deploy backend to Fly.io, frontend to Vercel

### Phase 5 — Spotify OAuth
- [ ] Authorization code flow (connect Spotify account)
- [ ] Token storage + silent refresh (check expiry before every API call)
- [ ] Liked Songs import (POST /collection/import/liked-songs)
- [ ] Private playlist import

### Phase 6+
- pgvector HNSW index tuning
- Feedback loop (FeedbackEvent → preference signal)
- LightGBM ranker
- Rate limiting, pagination, tests, README, demo video

## Data model

### Track (global dedup by spotify_id)
- id (UUID PK), spotify_id (str, unique), title, artist, album, release_year
- genres (ARRAY str — from Spotify artist endpoint), tags (ARRAY str — from Last.fm)
- embedding (Vector(384) — from "{title} by {artist}. Genres: {genres}. Tags: {tags}")
- enriched_at (datetime — when Last.fm tags were fetched)

### User
- id (UUID PK), created_at
- spotify_user_id (str, nullable), spotify_access_token, spotify_refresh_token, spotify_token_expires_at
- spotify_authorized_at — stored because Spotify tokens don't expose issuance timestamp; needed to detect 6-month expiry

### CollectionTrack (user's personal library)
- id, user_id (FK), track_id (FK) — UNIQUE(user_id, track_id)
- added_at, source (enum: SEARCH | PLAYLIST_IMPORT | LIKED_SONGS)
- source_spotify_playlist_id (nullable — which playlist it came from)

### IntentSession (Feature A)
- id, user_id (FK), raw_prompt (str), intent_embedding (Vector(384)), created_at

### ClusteringRun (Feature B)
- id, user_id (FK), n_clusters, algorithm (str), outlier_threshold (float), run_at

### Playlist
- id, user_id (FK), name, generation_mode (enum: TARGETED | CLUSTERED), created_at
- intent_session_id (FK nullable — Feature A), clustering_run_id (FK nullable — Feature B)

### PlaylistTrack (ordered membership — replaces ARRAY on Playlist)
- id, playlist_id (FK), track_id (FK) — UNIQUE(playlist_id, track_id)
- position (int)

### FeedbackEvent
- id, user_id (FK), track_id (FK nullable), playlist_id (FK nullable)
- type (enum: LIKE | DISLIKE | SKIP | SAVE_PLAYLIST | DISMISS)
- position (int nullable), created_at

## User preferences
- Explain design decisions before writing code, not after
- Walk through pieces one at a time; user wants to understand each step
- Short concise responses preferred

## Documentation philosophy
A documentation pass is planned at the end of each phase — do not add comments during active development.

Style standard: personal/professional, not AI-generated. Specifically:
- Consistent, neutral tone throughout — no dramatic phrasing, no over-emphasis
- Explaining non-obvious library calls or API behavior is fine (e.g. what `scalar_one_or_none()` does, or why Last.fm returns a bare object instead of a list for single-tag results)
- Do not narrate control flow or restate what readable code already shows
- Do not comment every function — only where the intent, constraint, or tradeoff isn't obvious from the signature and body
- Docstrings should be terse; no boilerplate param/return blocks unless types are genuinely ambiguous
