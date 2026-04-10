import { X, MoreVertical, History, Lock, Send } from 'lucide-react'
import { useState } from 'react'

interface CommentsPanelProps {
  isOpen: boolean
  onClose: () => void
}

interface Comment {
  id: string
  author: string
  avatar: string
  text: string
  timestamp: string
  resolved?: boolean
}

export function CommentsPanel({ isOpen, onClose }: CommentsPanelProps) {
  const [showMenu, setShowMenu] = useState(false)
  const [newComment, setNewComment] = useState('')
  const [comments] = useState<Comment[]>([
    {
      id: '1',
      author: 'Константин Иванов',
      avatar: 'КИ',
      text: 'Нужно добавить больше деталей в этот раздел',
      timestamp: '15:30',
    },
    {
      id: '2',
      author: 'Анна Петрова',
      avatar: 'АП',
      text: 'Согласна, особенно про интеграцию с API',
      timestamp: '15:45',
    },
  ])

  if (!isOpen) return null

  return (
    <div className="fixed right-0 top-0 h-full w-[380px] bg-white shadow-xl z-50 animate-slide-in flex flex-col">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-mws-gray-200">
        <h2 className="font-semibold text-mws-gray-700">Комментарии</h2>
        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="p-1.5 hover:bg-mws-gray-100 rounded relative"
          >
            <MoreVertical size={16} className="text-mws-gray-500" />
          </button>
          <button onClick={onClose} className="p-1.5 hover:bg-mws-gray-100 rounded">
            <X size={16} className="text-mws-gray-500" />
          </button>
        </div>

        {/* Dropdown Menu */}
        {showMenu && (
          <div className="absolute top-12 right-12 bg-white rounded-lg shadow-lg border border-mws-gray-200 py-1 z-10">
            <button className="w-full flex items-center gap-2 px-4 py-2 text-sm text-mws-gray-700 hover:bg-mws-gray-50">
              <History size={14} />
              История комментариев
            </button>
            <button className="w-full flex items-center gap-2 px-4 py-2 text-sm text-mws-gray-700 hover:bg-mws-gray-50">
              <Lock size={14} />
              Доступ к комментариям
            </button>
          </div>
        )}
      </div>

      {/* Comments List */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {comments.map((comment) => (
          <div key={comment.id} className="flex gap-3">
            <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center text-xs font-medium flex-shrink-0">
              {comment.avatar}
            </div>
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <span className="font-medium text-sm text-mws-gray-700">
                  {comment.author}
                </span>
                <span className="text-xs text-mws-gray-400">{comment.timestamp}</span>
              </div>
              <p className="text-sm text-mws-gray-600 mt-1">{comment.text}</p>
            </div>
          </div>
        ))}
      </div>

      {/* Input */}
      <div className="p-4 border-t border-mws-gray-200">
        <div className="flex gap-2">
          <input
            type="text"
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            placeholder="Написать комментарий..."
            className="flex-1 px-3 py-2 text-sm border border-mws-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
          <button
            disabled={!newComment.trim()}
            className="px-3 py-2 bg-primary text-white rounded-lg hover:bg-primary-hover disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Send size={16} />
          </button>
        </div>
      </div>
    </div>
  )
}
