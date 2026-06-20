import enum
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import ARRAY, JSON, Enum, Float, Integer, String, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import DateTime

from app.core.database import Base


class PreferenceSource(str, enum.Enum):
    QUESTIONNAIRE = "QUESTIONNAIRE"
    HISTORY = "HISTORY"
    HYBRID = "HYBRID"


class GenerationMode(str, enum.Enum):
    PLAYLIST_GEN = "PLAYLIST_GEN"
    RECOMMENDATION = "RECOMMENDATION"


class PlaylistFeedback(str, enum.Enum):
    SAVED = "SAVED"
    DISMISSED = "DISMISSED"
    EDITED = "EDITED"


class IntentSource(str, enum.Enum):
    QUESTIONNAIRE = "QUESTIONNAIRE"
    NLP_PROMPT = "NLP_PROMPT"


class FeedbackType(str, enum.Enum):
    LIKE = "LIKE"
    DISLIKE = "DISLIKE"
    SKIP = "SKIP"
    SAVE_PLAYLIST = "SAVE_PLAYLIST"
    EDIT_PLAYLIST = "EDIT_PLAYLIST"
    DISMISS = "DISMISS"


class Track(Base):
    __tablename__ = "tracks"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    spotify_id: Mapped[str] = mapped_column(String, unique=True, nullable=False)
    title: Mapped[str] = mapped_column(String, nullable=False)
    artist: Mapped[str] = mapped_column(String, nullable=False)
    album: Mapped[str] = mapped_column(String, nullable=False)
    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    popularity: Mapped[int | None] = mapped_column(Integer, nullable=True)

    energy: Mapped[float | None] = mapped_column(Float, nullable=True)
    valence: Mapped[float | None] = mapped_column(Float, nullable=True)
    tempo: Mapped[float | None] = mapped_column(Float, nullable=True)
    danceability: Mapped[float | None] = mapped_column(Float, nullable=True)
    acousticness: Mapped[float | None] = mapped_column(Float, nullable=True)
    instrumentalness: Mapped[float | None] = mapped_column(Float, nullable=True)
    liveness: Mapped[float | None] = mapped_column(Float, nullable=True)
    speechiness: Mapped[float | None] = mapped_column(Float, nullable=True)
    loudness: Mapped[float | None] = mapped_column(Float, nullable=True)
    mode: Mapped[int | None] = mapped_column(Integer, nullable=True)
    key: Mapped[int | None] = mapped_column(Integer, nullable=True)

    genres: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)
    indexed_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    spotify_user_id: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    preference_embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)
    preference_source: Mapped[str | None] = mapped_column(
        Enum(PreferenceSource, name="preference_source_enum"), nullable=True
    )
    preference_updated_at: Mapped[str | None] = mapped_column(DateTime(timezone=True), nullable=True)

    liked_track_ids: Mapped[list[str] | None] = mapped_column(ARRAY(UUID(as_uuid=False)), nullable=True)
    disliked_track_ids: Mapped[list[str] | None] = mapped_column(ARRAY(UUID(as_uuid=False)), nullable=True)


class IntentSession(Base):
    __tablename__ = "intent_sessions"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    source: Mapped[str] = mapped_column(Enum(IntentSource, name="intent_source_enum"), nullable=False)

    raw_input: Mapped[dict] = mapped_column(JSON, nullable=False)
    extracted_intent: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    intent_embedding: Mapped[list[float] | None] = mapped_column(Vector(384), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)


class Playlist(Base):
    __tablename__ = "playlists"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    intent_session_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)

    name: Mapped[str] = mapped_column(String, nullable=False)
    theme_label: Mapped[str | None] = mapped_column(String, nullable=True)
    track_ids: Mapped[list[str]] = mapped_column(ARRAY(UUID(as_uuid=False)), nullable=False)

    generation_mode: Mapped[str] = mapped_column(
        Enum(GenerationMode, name="generation_mode_enum"), nullable=False
    )
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    feedback: Mapped[str | None] = mapped_column(
        Enum(PlaylistFeedback, name="playlist_feedback_enum"), nullable=True
    )
    edited_track_ids: Mapped[list[str] | None] = mapped_column(ARRAY(UUID(as_uuid=False)), nullable=True)


class FeedbackEvent(Base):
    __tablename__ = "feedback_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=lambda: str(uuid4()))
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), nullable=False)
    track_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    playlist_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)

    type: Mapped[str] = mapped_column(Enum(FeedbackType, name="feedback_type_enum"), nullable=False)
    position: Mapped[int | None] = mapped_column(Integer, nullable=True)
    context_playlist_id: Mapped[str | None] = mapped_column(UUID(as_uuid=False), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
