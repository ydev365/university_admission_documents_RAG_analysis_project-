import { useState, useEffect, useRef } from 'react'
import { chatAPI, historyAPI } from '../services/api'

interface Message {
  id: number
  type: 'user' | 'assistant'
  subject?: string
  content: string
  timestamp: Date
}

interface HistoryItem {
  id: number
  subject: string
  question: string
  answer: string
  created_at: string
}

const SUBJECTS = [
  "국어", "수학", "영어", "한국사",
  "통합사회", "통합과학", "과학탐구실험",
  "물리학I", "물리학II", "생명과학I", "생명과학II",
  "지구과학I", "지구과학II", "화학I", "화학II",
  "문학", "독서", "화법과작문", "언어와매체",
  "수학I", "수학II", "미적분", "확률과통계", "기하",
  "영어I", "영어II", "영어독해와작문", "영미문학읽기", "실용영어", "진로영어",
  "사회문화", "윤리와사상", "생활과윤리", "한국지리", "세계지리", "경제", "정치와법",
  "일본어I", "일본어II", "중국어I", "중국어II",
  "체육", "운동과건강", "스포츠생활",
  "미술", "미술감상과비평", "음악", "음악감상과비평",
  "정보", "기술가정", "심리학", "교육학", "사회문제탐구",
  "수학과제탐구", "고전과윤리", "생활과한문", "민주시민"
]

export default function ChatPage() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [messages, setMessages] = useState<Message[]>([])
  const [history, setHistory] = useState<HistoryItem[]>([])
  const [selectedSubject, setSelectedSubject] = useState(SUBJECTS[0])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    loadHistory()
  }, [])

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const loadHistory = async () => {
    try {
      const data = await historyAPI.getHistory({ limit: 50 })
      setHistory(data.histories)
    } catch (error) {
      console.error('Failed to load history:', error)
    }
  }

  const handleSend = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage: Message = {
      id: Date.now(),
      type: 'user',
      subject: selectedSubject,
      content: inputValue,
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      const response = await chatAPI.sendMessage({
        subject: selectedSubject,
        question: inputValue
      })

      const assistantMessage: Message = {
        id: response.id,
        type: 'assistant',
        content: response.answer,
        timestamp: new Date(response.created_at)
      }

      setMessages(prev => [...prev, assistantMessage])
      loadHistory()
    } catch (error) {
      console.error('Failed to send message:', error)
      const errorMessage: Message = {
        id: Date.now(),
        type: 'assistant',
        content: '죄송합니다. 답변을 생성하는 중 오류가 발생했습니다. 다시 시도해주세요.',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleHistoryClick = (item: HistoryItem) => {
    setMessages([
      {
        id: item.id,
        type: 'user',
        subject: item.subject,
        content: item.question,
        timestamp: new Date(item.created_at)
      },
      {
        id: item.id + 1,
        type: 'assistant',
        content: item.answer,
        timestamp: new Date(item.created_at)
      }
    ])
    setSelectedSubject(item.subject)
    if (window.innerWidth < 768) {
      setSidebarOpen(false)
    }
  }

  const handleNewChat = () => {
    setMessages([])
  }

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  return (
    <div className="h-screen flex bg-primary-50">
      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'w-80' : 'w-0'
        } bg-white border-r border-slate-200 flex flex-col transition-all duration-300 overflow-hidden`}
      >
        {/* Sidebar Header */}
        <div className="p-4 border-b border-slate-200">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-10 h-10 bg-primary-500 rounded-xl flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
              </svg>
            </div>
            <div>
              <h1 className="font-bold text-slate-800">세특 도우미</h1>
              <p className="text-xs text-slate-500">AI 기반 세특 작성 가이드</p>
            </div>
          </div>
          <button
            onClick={handleNewChat}
            className="w-full py-2.5 px-4 bg-primary-500 hover:bg-primary-600 text-white rounded-xl font-medium flex items-center justify-center gap-2 transition"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            새 대화
          </button>
        </div>

        {/* History List */}
        <div className="flex-1 overflow-y-auto p-2">
          <h3 className="px-3 py-2 text-xs font-semibold text-slate-400 uppercase">대화 기록</h3>
          {history.length === 0 ? (
            <p className="px-3 py-4 text-sm text-slate-400 text-center">
              아직 대화 기록이 없습니다
            </p>
          ) : (
            <div className="space-y-1">
              {history.map((item) => (
                <button
                  key={item.id}
                  onClick={() => handleHistoryClick(item)}
                  className="w-full text-left px-3 py-2.5 rounded-lg hover:bg-slate-100 transition group"
                >
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2 py-0.5 bg-primary-100 text-primary-700 rounded-full">
                      {item.subject}
                    </span>
                  </div>
                  <p className="text-sm text-slate-600 truncate mt-1">{item.question}</p>
                  <p className="text-xs text-slate-400 mt-1">
                    {new Date(item.created_at).toLocaleDateString('ko-KR')}
                  </p>
                </button>
              ))}
            </div>
          )}
        </div>

      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="h-16 bg-white border-b border-slate-200 flex items-center px-4 gap-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 hover:bg-slate-100 rounded-lg transition"
          >
            <svg className="w-6 h-6 text-slate-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <div>
            <h2 className="font-semibold text-slate-800">세부능력특기사항 작성 도우미</h2>
            <p className="text-xs text-slate-500">과목을 선택하고 질문해보세요</p>
          </div>
        </header>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-4 space-y-4">
          {messages.length === 0 ? (
            <div className="h-full flex items-center justify-center">
              <div className="text-center max-w-md">
                <div className="w-20 h-20 bg-primary-100 rounded-2xl flex items-center justify-center mx-auto mb-4">
                  <svg className="w-10 h-10 text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-slate-800 mb-2">
                  세특 작성이 고민이신가요?
                </h3>
                <p className="text-slate-500 mb-4">
                  과목을 선택하고 어떤 활동을 세특에 작성하면 좋을지 물어보세요.
                  실제 합격생들의 세특을 참고하여 맞춤형 조언을 드립니다.
                </p>
                <div className="flex flex-wrap gap-2 justify-center">
                  {['수학 과목에서 어떤 탐구활동이 좋을까요?', '영어 세특에 쓸 만한 활동 추천해주세요', '물리학 발표 주제 추천해주세요'].map((suggestion, i) => (
                    <button
                      key={i}
                      onClick={() => setInputValue(suggestion)}
                      className="px-3 py-1.5 bg-white border border-slate-200 rounded-full text-sm text-slate-600 hover:border-primary-300 hover:text-primary-600 transition"
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          ) : (
            <>
              {messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`message-bubble ${
                      message.type === 'user' ? 'message-user' : 'message-assistant'
                    }`}
                  >
                    {message.type === 'user' && message.subject && (
                      <span className="inline-block px-2 py-0.5 bg-primary-400 text-white text-xs rounded-full mb-2">
                        {message.subject}
                      </span>
                    )}
                    <p className="whitespace-pre-wrap">{message.content}</p>
                  </div>
                </div>
              ))}
              {isLoading && (
                <div className="flex justify-start">
                  <div className="message-bubble message-assistant">
                    <div className="flex items-center gap-2">
                      <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                      <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                      <div className="w-2 h-2 bg-primary-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
                    </div>
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="p-4 bg-white border-t border-slate-200">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-center gap-3 mb-3">
              <label className="text-sm font-medium text-slate-600">과목 선택:</label>
              <select
                value={selectedSubject}
                onChange={(e) => setSelectedSubject(e.target.value)}
                className="px-3 py-1.5 bg-slate-50 border border-slate-200 rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
              >
                {SUBJECTS.map((subject) => (
                  <option key={subject} value={subject}>
                    {subject}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex gap-3">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="세특에 대해 궁금한 것을 질문해보세요..."
                className="flex-1 px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none"
                rows={2}
              />
              <button
                onClick={handleSend}
                disabled={!inputValue.trim() || isLoading}
                className="px-6 bg-primary-500 hover:bg-primary-600 text-white rounded-xl transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
