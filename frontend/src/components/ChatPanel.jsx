import {
  useState,
  useRef,
  useEffect
} from 'react'
import { streamChat } from '../lib/api'

export default function ChatPanel({
  messages,
  setMessages,
  disabled
}) {
  const [question, setQuestion] =
    useState('')

  const [loading, setLoading] =
    useState(false)

  const messagesRef = useRef(null)

  async function askQuestion(e) {
    e.preventDefault()

    const q = question.trim()

    if (!q || loading || disabled)
      return

    setQuestion('')
    setLoading(true)

    const sessionId = 'demo-session'

    setMessages((prev) => [
      ...prev,
      { role: 'user', content: q },
      {
        role: 'assistant',
        content: '',
        citations: []
      }
    ])

    try {
      await streamChat(
        q,
        sessionId,
        (event) => {
          setMessages((prev) => {
            const copy = [...prev]

            const lastIndex =
              copy.length - 1

            if (
              copy[lastIndex]?.role !==
              'assistant'
            )
              return prev

            if (
              event.type === 'token'
            ) {
              copy[lastIndex] = {
                ...copy[lastIndex],
                content:
                  copy[lastIndex]
                    .content +
                  event.token
              }
            }

            if (
              event.type === 'done'
            ) {
              copy[lastIndex] = {
                ...copy[lastIndex],
                citations:
                  event.citations ||
                  []
              }
            }

            return copy
          })
        }
      )
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: `Error: ${err.message}`,
          citations: []
        }
      ])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    if (messagesRef.current) {
      messagesRef.current.scrollTop =
        messagesRef.current
          .scrollHeight
    }
  }, [messages])

  return (
    <section className="flex flex-col h-[750px] rounded-2xl bg-white shadow-lg overflow-hidden">
      <div className="border-b p-4">
        <h3 className="font-semibold">
          AI Video Analyst
        </h3>

        <p className="text-xs text-slate-500">
          Ask performance questions
          about Video A & B
        </p>
      </div>

      <div
        ref={messagesRef}
        className="flex-1 overflow-y-auto bg-slate-50 p-4 space-y-4"
      >
        {messages.map((msg, idx) => (
          <div
            key={idx}
            className="flex gap-3"
          >
            <div
              className={`h-10 w-10 rounded-full flex items-center justify-center text-white ${
                msg.role === 'user'
                  ? 'bg-violet-600'
                  : 'bg-emerald-600'
              }`}
            >
              {msg.role === 'user'
                ? '👤'
                : '🤖'}
            </div>

            <div className="flex-1">
              <div
                className={`rounded-2xl p-4 ${
                  msg.role === 'user'
                    ? 'bg-violet-600 text-white'
                    : 'bg-white border'
                }`}
              >
                {msg.content}
              </div>

              {msg.citations
                ?.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-2">
                  {msg.citations.map(
                    (c, i) => (
                      <span
                        key={i}
                        className="rounded-full bg-blue-100 px-3 py-1 text-xs text-blue-700"
                      >
                        Video{' '}
                        {c.video_id}{' '}
                        • Chunk{' '}
                        {
                          c.chunk_index
                        }
                      </span>
                    )
                  )}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="text-sm text-slate-500 animate-pulse">
            🤖 Thinking...
          </div>
        )}
      </div>

      <form
        onSubmit={askQuestion}
        className="flex gap-3 border-t p-4"
      >
        <input
          value={question}
          onChange={(e) =>
            setQuestion(
              e.target.value
            )
          }
          placeholder="Why did Video A outperform Video B?"
          disabled={
            disabled || loading
          }
          className="flex-1 rounded-xl border px-4 py-3 outline-none focus:ring-2 focus:ring-violet-500"
        />

        <button
          type="submit"
          disabled={
            disabled || loading
          }
          className="rounded-xl bg-violet-600 px-6 text-white hover:bg-violet-700"
        >
          Send
        </button>
      </form>
    </section>
  )
}