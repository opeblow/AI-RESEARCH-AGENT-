import { useState, useCallback } from 'react'
import { Toaster } from 'react-hot-toast'
import Header from './components/Header'
import ChatSection from './components/ChatSection'
import Sidebar from './components/Sidebar'
import { Message, QueryResponse } from './types'
import { sendQuery } from './api/crag'

function App() {
  const [messages, setMessages] = useState<Message[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [stats, setStats] = useState({
    totalQueries: 0,
    webSearchUsed: 0,
    avgConfidence: 0,
    avgProcessingTime: 0
  })

  const handleSendMessage = useCallback(async (question: string) => {
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: 'user',
      content: question,
      timestamp: new Date()
    }
    
    setMessages(prev => [...prev, userMessage])
    setIsLoading(true)
    
    try {
      const response = await sendQuery(question)
      
      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.answer,
        sources: response.sources,
        metadata: {
          model: response.model,
          processingTime: response.processing_time_ms,
          confidence: response.confidence,
          usedWebSearch: response.used_web_search
        },
        timestamp: new Date()
      }
      
      setMessages(prev => [...prev, assistantMessage])
      
      setStats(prev => ({
        totalQueries: prev.totalQueries + 1,
        webSearchUsed: prev.webSearchUsed + (response.used_web_search ? 1 : 0),
        avgConfidence: (prev.avgConfidence * prev.totalQueries + response.confidence) / (prev.totalQueries + 1),
        avgProcessingTime: (prev.avgProcessingTime * prev.totalQueries + response.processing_time_ms) / (prev.totalQueries + 1)
      }))
      
    } catch (error) {
      console.error('Query failed:', error)
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: 'I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }, [])

  return (
    <div className="app">
      <Toaster 
        position="top-right"
        toastOptions={{
          style: {
            background: '#1a1a2e',
            color: '#fff',
            border: '1px solid #2d2d44'
          }
        }}
      />
      <Header />
      <main className="main-content">
        <ChatSection
          messages={messages}
          isLoading={isLoading}
          onSendMessage={handleSendMessage}
        />
        <Sidebar stats={stats} />
      </main>
    </div>
  )
}

export default App
