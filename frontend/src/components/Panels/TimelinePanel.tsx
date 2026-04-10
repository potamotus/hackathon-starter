import { X, RotateCcw } from 'lucide-react'

interface TimelinePanelProps {
  isOpen: boolean
  onClose: () => void
}

interface Version {
  id: string
  action: string
  timestamp: string
  author: string
  avatar: string
}

export function TimelinePanel({ isOpen, onClose }: TimelinePanelProps) {
  const versions: Version[] = [
    {
      id: '1',
      action: 'Изменён раздел "Введение"',
      timestamp: '2025-04-10 15:53',
      author: 'Константин Иванов',
      avatar: 'КИ',
    },
    {
      id: '2',
      action: 'Добавлена таблица',
      timestamp: '2025-04-10 15:45',
      author: 'Анна Петрова',
      avatar: 'АП',
    },
    {
      id: '3',
      action: 'Создание страницы',
      timestamp: '2025-04-10 14:30',
      author: 'Константин Иванов',
      avatar: 'КИ',
    },
  ]

  if (!isOpen) return null

  return (
    <div className="fixed right-0 top-0 h-full w-[320px] bg-mws-gray-50 shadow-xl z-50 animate-slide-in flex flex-col m-4 rounded-xl border border-mws-gray-200">
      {/* Header */}
      <div className="flex items-center justify-between p-4 border-b border-mws-gray-200">
        <h2 className="font-semibold text-mws-gray-700">Машина времени</h2>
        <button onClick={onClose} className="p-1.5 hover:bg-mws-gray-100 rounded">
          <X size={16} className="text-mws-gray-500" />
        </button>
      </div>

      {/* Versions List */}
      <div className="flex-1 overflow-y-auto p-2">
        {versions.map((version, index) => (
          <div
            key={version.id}
            className={`p-3 rounded-lg cursor-pointer transition-colors ${
              index === 0 ? 'bg-white shadow-sm' : 'hover:bg-white'
            }`}
          >
            <div className="flex items-start justify-between">
              <p className="text-sm font-medium text-mws-gray-700">{version.action}</p>
              {index !== 0 && (
                <button
                  className="p-1 hover:bg-mws-gray-100 rounded text-mws-gray-400 hover:text-primary"
                  title="Восстановить эту версию"
                >
                  <RotateCcw size={14} />
                </button>
              )}
            </div>
            <div className="flex items-center justify-between mt-2">
              <span className="text-xs text-mws-gray-400">{version.timestamp}</span>
              <div className="flex items-center gap-1.5">
                <span className="text-xs text-mws-gray-400">{version.author}</span>
                <div className="w-5 h-5 rounded-full bg-primary/10 text-primary flex items-center justify-center text-[10px] font-medium">
                  {version.avatar}
                </div>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
