import { useState } from "react"
import { useUser } from "@/hooks/useUser"
import { apiFetch } from "@/lib/api"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Slider } from "@/components/ui/slider"

interface PlaylistTrack {
  position: number
  score: number
  spotify_id: string
  title: string
  artist: string
  album: string
  album_art_url: string | null
}

interface GenerateResponse {
  playlist_id: string
  name: string
  tracks: PlaylistTrack[]
}

export default function Generate() {
  const userId = useUser()

  const [prompt, setPrompt] = useState("")
  const [limit, setLimit] = useState(15)
  const [loading, setLoading] = useState(false)
  const [result, setResult] = useState<GenerateResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  async function handleGenerate(e: React.FormEvent) {
    e.preventDefault()
    if (!userId || !prompt.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const data = await apiFetch<GenerateResponse>("/playlists/generate", userId, {
        method: "POST",
        body: JSON.stringify({ prompt, limit }),
      })
      setResult(data)
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : "Something went wrong"
      setError(msg.includes("422") ? "Your collection doesn't have enough tracks yet. Add some first." : msg)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-10">
      <div className="space-y-6">
        <h2 className="text-lg font-semibold">Generate a playlist</h2>

        <form onSubmit={handleGenerate} className="space-y-5">
          <Input
            placeholder="e.g. late night drive, rainy day studying, upbeat workout..."
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />

          <div className="space-y-2">
            <p className="text-sm text-muted-foreground">{limit} tracks</p>
            <Slider
              min={5}
              max={30}
              step={1}
              value={[limit]}
              onValueChange={([val]) => setLimit(val)}
              className="w-48"
            />
          </div>

          <Button type="submit" disabled={loading || !userId || !prompt.trim()}>
            {loading ? "Generating..." : "Generate"}
          </Button>
        </form>

        {error && <p className="text-sm text-destructive">{error}</p>}
      </div>

      {result && (
        <div className="space-y-4">
          <h2 className="text-lg font-semibold">{result.name}</h2>
          <ul className="space-y-1">
            {result.tracks.map((track) => (
              <li
                key={track.spotify_id}
                className="flex items-center gap-3 px-3 py-2 rounded-md hover:bg-muted"
              >
                <span className="text-sm text-muted-foreground w-5 shrink-0 text-right">
                  {track.position + 1}
                </span>
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
                  </p>
                </div>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  )
}
