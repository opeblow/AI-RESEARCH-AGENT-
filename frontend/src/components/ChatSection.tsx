import { useState, useRef, useEffect } from 'react'
import ReactMarkdown from 'react-markdown'
import { Message } from '../types'

interface ChatSectionProps {
  messages: Message[]
  isLoading: boolean
  onSendMessage: (message: string) => void
}

export default function ChatSection({ messages, isLoading, onSendMessage }: ChatSectionProps) {
  const [input, setInput] = useState('')
  const messagesEndRef = useRef<HTMLDivElement>(null)
  
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }
  
  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    if (input.trim() && !isLoading) {
      onSendMessage(input.trim())
      setInput('')
    }
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSubmit(e)
    }
  }

  return (
    <section className="chat-section">
      <div className="chat-header">
        <h2>Research Assistant</h2>
        <span style={{ fontSize: '0.75rem', color: 'var(--text-secondary)' }}>
          Powered by CRAG
        </span>
      </div>
      
      <div className="chat-messages">
        {messages.length === 0 && (
          <div className="empty-state">
            <svg viewBox="0 0 100 100" fill="none" stroke="currentColor" strokeWidth="2">
              <circle cx="50" cy="50" r="40" />
              <path d="M30 50 L45 65 L70 35" />
            </svg>
            <h3>Welcome to CRAG</h3>
            <p>Ask me anything about your documents or general topics.<br />I'll search my knowledge base and the web if needed.</p>
          </div>
        )}
        
        {messages.map(message => (
          <div key={message.id} className={`message ${message.role}`}>
            <div className="message-avatar">
              {message.role === 'user' ? 'U' : 'AI'}
            </div>
            <div className="message-content">
              <ReactMarkdown>{message.content}</ReactMarkdown>
              
              {message.sources && message.sources.length > 0 && (
                <div className="sources-section">
                  <div className="sources-title">Sources</div>
                  {message.sources.map((source, idx) => (
                    <span key={idx} className="source-item">
                      {source.type === 'web' ? '🌐' : '📄'} {source.title || source.source}
                    </span>
                  ))}
                </div>
              )}
              
              {message.metadata && (
                <div style={{ 
                  marginTop: '0.75rem', 
                  paddingTop: '0.75rem', 
                  borderTop: '1px solid var(--border)',
                  fontSize: '0.7rem',
                  color: 'var(--text-secondary)',
                  display: 'flex',
                  gap: '1rem',
                  flexWrap: 'wrap'
                }}>
                  {message.metadata.processingTime && (
                    <span>⏱ {message.metadata.processingTime.toFixed(0)}ms</span>
                  )}
                  {message.metadata.confidence && (
                    <span>📊 {(message.metadata.confidence * 100).toFixed(0)}% confidence</span>
                  )}
                  {message.metadata.usedWebSearch && (
                    <span>🌐 Web search used</span>
                  )}
                </div>
              )}
            </div>
          </div>
        ))}
        
        {isLoading && (
          <div className="message assistant">
            <div className="message-avatar">AI</div>
            <div className="message-content">
              <div className="loading-indicator">
                <div className="spinner"></div>
                <span>Processing your query...</span>
              </div>
            </div>
          </div>
        )}
        
        <div ref={messagesEndRef} />
      </div>
      
      <form className="input-area" onSubmit={handleSubmit}>
        <div className="input-wrapper">
          <textarea
            className="query-input"
            placeholder="Ask me anything..."
            value={input}
            onChange={e => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            rows={1}
            disabled={isLoading}
          />
          <button 
            type="submit" 
            className="send-button"
            disabled={!input.trim() || isLoading}
          >
            {isLoading ? 'Sending...' : 'Send'}
          </button>
        </div>
      </form>
    </section>
  )
}
