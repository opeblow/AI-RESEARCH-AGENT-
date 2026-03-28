export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Source[]
  metadata?: {
    model?: string
    processingTime?: number
    confidence?: number
    usedWebSearch?: boolean
  }
  timestamp: Date
}

export interface Source {
  source: string
  type: string
  title?: string
  score?: number
}

export interface QueryRequest {
  question: string
  conversation_id?: string
}

export interface QueryResponse {
  answer: string
  sources: Source[]
  conversation_id: string
  model: string
  processing_time_ms: number
  confidence: number
  retrieved_chunks: number
  used_web_search: boolean
}

export interface Stats {
  totalQueries: number
  webSearchUsed: number
  avgConfidence: number
  avgProcessingTime: number
}
