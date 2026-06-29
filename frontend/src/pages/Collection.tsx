import { useState, useEffect } from "react"
import { useUser } from "@/hooks/useUser"
import { apiFetch } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"

interface TrackCandidate {
  spotify_id: string
  title: string
  artist: string
  album: string
  release_year: number | null
  album_art_url: string | null
}

interface CollectionTrack {
  track_id: string
  spotify_id: string
  title: string
  artist: string
  album: string
  release_year: number | null
  album_art_url: string | null
  added_at: string
  source: string
}

export default function Collection() {
  const userId = useUser()

  const [query, setQuery] = useState("")
  const [searchResults, setSearchResults] = useState<TrackCandidate[]>([])
  const [collection, setCollection] = useState<CollectionTrack[]>([])
  const [playlistUrl, setPlaylistUrl] = useState("")

  const [searching, setSearching] = useState(false)
  const [adding, setAdding] = useState<string | null>(null)
  const [importing, setImporting] = useState(false)

  useEffect(() => {
    if (!userId) return
    apiFetch<CollectionTrack[]>("/collection/tracks", userId)
      .then(setCollection)
      .catch(console.error)
  }, [userId])

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault()
    if (!userId || !query.trim()) return
    setSearching(true)
    try {
      const results = await apiFetch<TrackCandidate[]>(
        `/tracks/search?q=${encodeURIComponent(query)}`,
        userId
      )
      setSearchResults(results)
    } catch (err) {
      console.error(err)
    } finally {
      setSearching(false)
    }
  }

  async function handleAddTrack(track: TrackCandidate) {
    if (!userId) return
    setAdding(track.spotify_id)
    try {
      await apiFetch("/collection/tracks", userId, {
        method: "POST",
        body: JSON.stringify({ spotify_id: track.spotify_id }),
      })
      const updated = await apiFetch<CollectionTrack[]>("/collection/tracks", userId)
      setCollection(updated)
      setSearchResults((prev) => prev.filter((t) => t.spotify_id !== track.spotify_id))
    } catch (err) {
      console.error(err)
    } finally {
      setAdding(null)
    }
  }

  async function handleImport(e: React.FormEvent) {
    e.preventDefault()
    if (!userId || !playlistUrl.trim()) return
    setImporting(true)
    try {
      await apiFetch("/collection/import/playlist", userId, {
        method: "POST",
        body: JSON.stringify({ playlist_id: playlistUrl }),
      })
      const updated = await apiFetch<CollectionTrack[]>("/collection/tracks", userId)
      setCollection(updated)
      setPlaylistUrl("")
    } catch (err) {
      console.error(err)
    } finally {
      setImporting(false)
    }
  }

  return (
    <div className="space-y-10">
      <div className="space-y-6">
        <h2 className="text-lg font-semibold">Add tracks</h2>

        <form onSubmit={handleSearch} className="flex gap-2">
          <Input
            placeholder="Search Spotify..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
          <Button type="submit" disabled={searching || !userId}>
            {searching ? "Searching..." : "Search"}
          </Button>
        </form>

        {searchResults.length > 0 && (
          <ul className="space-y-1">
            {searchResults.map((track) => (
              <li
                key={track.spotify_id}
                className="flex items-center gap-3 justify-between px-3 py-2 rounded-md hover:bg-muted"
              >
                <div className="flex items-center gap-3 min-w-0">
                  {track.album_art_url ? (
                    <img
                      src={track.album_art_url}
                      alt={track.album}
                      className="w-10 h-10 rounded object-cover shrink-0"
                    />
                  ) : (
                    <div className="w-10 h-10 rounded bg-muted shrink-0" />
                  )}
                  <div className="min-w-0">
                    <p className="font-medium truncate">{track.title}</p>
                    <p className="text-sm text-muted-foreground truncate">
                      {track.artist} · {track.album}
                      {track.release_year ? ` · ${track.release_year}` : ""}
                    </p>
                  </div>
                </div>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleAddTrack(track)}
                  disabled={adding === track.spotify_id}
                  className="ml-4 shrink-0"
                >
                  {adding === track.spotify_id ? "Adding..." : "Add"}
                </Button>
              </li>
            ))}
          </ul>
        )}

        <form onSubmit={handleImport} className="flex gap-2">
          <Input
            placeholder="Spotify playlist URL or ID..."
            value={playlistUrl}
            onChange={(e) => setPlaylistUrl(e.target.value)}
          />
          <Button type="submit" disabled={importing || !userId}>
            {importing ? "Importing..." : "Import playlist"}
          </Button>
        </form>
      </div>

      <div className="space-y-4">
        <h2 className="text-lg font-semibold">
          Your tracks{collection.length > 0 ? ` (${collection.length})` : ""}
        </h2>

        {collection.length === 0 ? (
          <p className="text-muted-foreground text-sm">
            No tracks yet. Search or import a playlist to get started.
          </p>
        ) : (
          <ul className="space-y-1">
            {collection.map((track) => (
              <li
                key={track.track_id}
                className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted"
              >
                {track.album_art_url ? (
                  <img
                    src={track.album_art_url}
                    alt={track.album}
                    className="w-10 h-10 rounded object-cover shrink-0"
                  />
                ) : (
                  <div className="w-10 h-10 rounded bg-muted shrink-0" />
                )}
                <div className="min-w-0">
                  <p className="font-medium truncate">{track.title}</p>
                  <p className="text-sm text-muted-foreground truncate">
                    {track.artist} · {track.album}
                    {track.release_year ? ` · ${track.release_year}` : ""}
                  </p>
                </div>
              </li>
            ))}
          </ul>
        )}
      </div>
    </div>
  )
}
