import { useEffect, useState, useCallback } from 'react'

export interface SSEEvent {
  type: string
  [key: string]: any
}

export const useSSE = (reviewId: string | null, enabled = true) => {
  const [events, setEvents] = useState<SSEEvent[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!reviewId || !enabled) return

    setIsConnected(true)
    setError(null)
    setEvents([])

    const eventSource = new EventSource(`/api/v1/sse/reviews/${reviewId}`)

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setEvents((prev) => [...prev, data])
      } catch (e) {
        console.error('Failed to parse SSE event:', e)
      }
    }

    eventSource.onerror = () => {
      setIsConnected(false)
      setError('Connection lost')
      eventSource.close()
    }

    return () => {
      eventSource.close()
    }
  }, [reviewId, enabled])

  return { events, isConnected, error }
}
