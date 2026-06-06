const API_BASE = 'https://vedio-ai-chatbot.onrender.com'

export async function ingestVideos(youtubeUrl, instagramUrl) {
  const res = await fetch(`${API_BASE}/api/ingest`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ youtube_url: youtubeUrl, instagram_url: instagramUrl })
  })

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Ingest failed' }))
    throw new Error(err.detail || 'Ingest failed')
  }

  return res.json()
}

export async function streamChat(question, sessionId, onEvent) {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, session_id: sessionId })
  })

  if (!response.ok || !response.body) {
    throw new Error('Chat request failed')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder('utf-8')
  let buffer = ''

  while (true) {
    const { value, done } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })

    const events = buffer.split('\n\n')
    buffer = events.pop() || ''

    for (const rawEvent of events) {
      const line = rawEvent
        .split('\n')
        .find((part) => part.startsWith('data: '))
      if (!line) continue
      const payload = JSON.parse(line.replace('data: ', ''))
      onEvent(payload)
    }
  }
}
