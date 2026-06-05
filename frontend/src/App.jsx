import { useState } from 'react'
import ChatPanel from './components/ChatPanel'
import VideoCards from './components/VideoCards'
import { ingestVideos } from './lib/api'

export default function App() {
  const [youtubeUrl, setYoutubeUrl] = useState('')
  const [instagramUrl, setInstagramUrl] = useState('')
  const [videos, setVideos] = useState([])
  const [messages, setMessages] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  async function handleIngest(e) {
    e.preventDefault()
    setError('')
    setLoading(true)

    try {
      const data = await ingestVideos(
        youtubeUrl,
        instagramUrl
      )

      setVideos(data.videos || [])

      setMessages([
        {
          role: 'assistant',
          content:
            '✅ Videos processed successfully. Ask any comparison question about Video A and Video B.',
          citations: []
        }
      ])
    } catch (err) {
      setError(
        err?.message ||
          'Something went wrong'
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-100 p-6">
      <header className="mb-6 flex items-center justify-between rounded-2xl bg-white p-5 shadow-md">
        <div className="flex items-center gap-4">
          <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 text-white font-bold">
            CV
          </div>

          <div>
            <h1 className="text-2xl font-bold">
              Creator Video RAG Analyst
            </h1>

            <p className="text-sm text-slate-500">
              Compare YouTube and Instagram
              content performance using AI.
            </p>
          </div>
        </div>

        <span className="rounded-full bg-green-100 px-4 py-2 text-sm text-green-700">
          Ready
        </span>
      </header>

      <section className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          <form
            onSubmit={handleIngest}
            className="space-y-4 rounded-2xl bg-white p-6 shadow-md"
          >
            <input
              type="url"
              placeholder="YouTube Video URL"
              value={youtubeUrl}
              onChange={(e) =>
                setYoutubeUrl(e.target.value)
              }
              required
              className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-violet-500"
            />

            <input
              type="url"
              placeholder="Instagram Reel URL"
              value={instagramUrl}
              onChange={(e) =>
                setInstagramUrl(e.target.value)
              }
              required
              className="w-full rounded-xl border border-slate-300 px-4 py-3 outline-none focus:border-violet-500"
            />

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-violet-600 py-3 font-semibold text-white hover:bg-violet-700 transition"
            >
              {loading
                ? 'Ingesting...'
                : 'Analyze Videos'}
            </button>
          </form>

          {error && (
            <div className="rounded-xl bg-red-50 p-4 text-red-600">
              {error}
            </div>
          )}

          {videos.length > 0 ? (
            <VideoCards videos={videos} />
          ) : (
            <div className="rounded-xl border-2 border-dashed border-slate-300 p-10 text-center text-slate-500">
              Add a YouTube video and Instagram Reel
              to start analysis.
            </div>
          )}
        </div>

        <ChatPanel
          messages={messages}
          setMessages={setMessages}
          disabled={videos.length === 0}
        />
      </section>
    </main>
  )
}