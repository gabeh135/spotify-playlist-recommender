from dataclasses import dataclass

import numpy as np
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import CollectionTrack, Track

MIN_TRACKS = 10

@dataclass
class ClusterResult:
    track_ids: list[str]
    centroid: list[float]
    # TODO: store representative id for playlist naming

async def load_embeddings(user_id: str, db: AsyncSession) -> list[tuple[str, list[float]]]:
    result = await db.execute(
        select(Track.id, Track.embedding)
        .join(CollectionTrack, CollectionTrack.track_id == Track.id)
        .where(CollectionTrack.user_id == user_id)
        .where(Track.embedding.isnot(None))
    )
    return [(track_id, embedding) for track_id, embedding in result.all()]


def _find_optimal_k(matrix, max_k: int) -> int:
    best_k = None
    best_score = -1

    for k in range(2, max_k + 1):
        kmeans = KMeans(n_clusters=k, random_state=42)
        kmeans.fit(matrix)

        score = silhouette_score(matrix, kmeans.labels_)
        if score > best_score:
            best_k = k
            best_score = score
    
    return best_k


def _outlier_indices(matrix, labels, centroids, threshold_multiplier: float) -> set[int]:
    outliers = set()
    for c, centroid in enumerate(centroids):
        member_indices = np.where(labels == c)[0]
        distances = np.linalg.norm(matrix[member_indices] - centroid, axis=1)
        mean_dist = distances.mean()
        flagged = member_indices[distances > threshold_multiplier * mean_dist]
        outliers.update(flagged.tolist())
    return outliers


# TODO: move this call into an async Celery task
def cluster_collection(track_ids: list[str], matrix, outlier_threshold: float = 1.5,) -> list[ClusterResult]:
    n = len(track_ids)
    if n < MIN_TRACKS:
        raise ValueError(f"Need at least {MIN_TRACKS} tracks to cluster (got {n})")

    max_k = min(10, n // 5)
    k = _find_optimal_k(matrix, max_k)

    kmeans = KMeans(n_clusters=k, random_state=42)
    kmeans.fit(matrix)

    labels = kmeans.labels_
    centroids = kmeans.cluster_centers_
    outliers = _outlier_indices(matrix, labels, centroids, outlier_threshold)

    results = []
    for c in range(k):
        members = np.array([i for i, label in enumerate(labels) if label == c and i not in outliers])
        centroid = centroids[c]

        distances = np.linalg.norm(matrix[members] - centroid, axis=1)
        sorted_indices = np.argsort(distances)
        sorted_members = members[sorted_indices]

        ordered_ids = [track_ids[i] for i in sorted_members]
        results.append(ClusterResult(
            track_ids=ordered_ids,
            centroid=centroids[c].tolist(),
        ))

    return results
