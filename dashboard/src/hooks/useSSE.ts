import { useEffect, useState, useCallback } from 'react'

export interface SSEEvent {
  type: string
  [key: string]: any
}

export interface ReviewStage {
  name: string
  status: 'pending' | 'in_progress' | 'completed'
  timestamp?: Date
  details?: any
}

export const STAGES: ReviewStage[] = [
  { name: 'Initialized', status: 'pending' },
  { name: 'PR Fetched', status: 'pending' },
  { name: 'Analyzing', status: 'pending' },
  { name: 'Aggregating', status: 'pending' },
  { name: 'Fixing', status: 'pending' },
  { name: 'Completed', status: 'pending' },
]

const STAGE_MAP: Record<string, number> = {
  'INITIALIZED': 0,
  'PR_FETCHED': 1,
  'ANALYSIS_COMPLETE': 3,
  'FIXING_START': 4,
  'FIXING_COMPLETE': 4,
  'COMPLETED': 5,
}

export const useSSE = (reviewId: string | null, enabled = true) => {
  const [events, setEvents] = useState<SSEEvent[]>([])
  const [isConnected, setIsConnected] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [stages, setStages] = useState<ReviewStage[]>(STAGES)
  const [currentStage, setCurrentStage] = useState<string>('pending')

  useEffect(() => {
    if (!reviewId || !enabled) return

    setIsConnected(true)
    setError(null)
    setEvents([])
    setStages(JSON.parse(JSON.stringify(STAGES)))

    const eventSource = new EventSource(`/api/v1/sse/reviews/${reviewId}`)

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        setEvents((prev) => [...prev, data])

        // Update stages based on event type
        if (data.type === 'stage_update' && data.stage) {
          const stageIndex = STAGE_MAP[data.stage]
          setStages((prev) => {
            const updated = [...prev]
            // Mark all stages up to this one as completed
            for (let i = 0; i <= stageIndex; i++) {
              if (updated[i]) {
                updated[i].status = 'completed'
                if (!updated[i].timestamp) {
                  updated[i].timestamp = new Date()
                }
              }
            }
            // Mark next stage as in_progress if exists
            if (updated[stageIndex + 1]) {
              updated[stageIndex + 1].status = 'in_progress'
            }
            return updated
          })
          setCurrentStage(data.stage)
        } else if (data.type === 'agent_completed') {
          // Update stages during analysis phase
          setStages((prev) => {
            const updated = [...prev]
            // Mark analyzing stage as in progress
            if (updated[2]) {
              updated[2].status = 'in_progress'
            }
            return updated
          })
        }
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

  return { events, isConnected, error, stages, currentStage }
}
