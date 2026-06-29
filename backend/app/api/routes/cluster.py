from datetime import datetime, timezone

import numpy as np
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.ml.clustering.clustering import cluster_collection, load_embeddings, MIN_TRACKS
from app.models import ClusteringRun, GenerationMode, Playlist, PlaylistTrack, User

router = APIRouter(prefix="/cluster", tags=["cluster"])


@router.post("", status_code=201)
async def create_cluster(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    outlier_threshold = 1.5

    embeddings = await load_embeddings(user.id, db)
    if len(embeddings) < MIN_TRACKS:
        raise HTTPException(status_code=400, detail=f"At least {MIN_TRACKS} tracks required to cluster (collection has {len(embeddings)})")

    track_ids, vectors = zip(*embeddings)
    track_ids = list(track_ids)
    matrix = np.array(vectors)

    results = cluster_collection(track_ids, matrix, outlier_threshold)

    run = ClusteringRun(
        user_id=user.id,
        n_clusters=len(results),
        algorithm="kmeans",
        outlier_threshold=outlier_threshold,
        run_at=datetime.now(timezone.utc), # TODO: gather this  as part of cluster collection not here
    )
    db.add(run)

    playlists = []
    tracks_placed = 0

    # TODO: rework with generated playlist names
    for i, result in enumerate(results):
        playlist = Playlist(
            user_id=user.id,
            clustering_run_id=run.id,
            name=f"Playlist {i + 1}",
            generation_mode=GenerationMode.CLUSTERED,
        )
        db.add(playlist)

        tracks = []
        for position, track_id in enumerate(result.track_ids):
            tracks.append(PlaylistTrack(
                playlist_id=playlist.id, 
                track_id=track_id, 
                position=position
            ))
        db.add_all(tracks)

        tracks_placed += len(tracks)
        playlists.append({"id": playlist.id, "name": playlist.name, "track_count": len(tracks)})

    await db.commit()

    return {
        "clustering_run_id": run.id,
        "n_clusters": run.n_clusters,
        "playlists": playlists,
        "tracks_placed": tracks_placed,
        "outliers_excluded": len(track_ids) - tracks_placed,
    }
