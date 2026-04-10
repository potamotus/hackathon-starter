import { FileText, Plus, ChevronLeft, ChevronRight, Search } from 'lucide-react'

interface Page {
  id: string
  title: string
  content: string
  updatedAt: string
}

interface SidebarProps {
  pages: Page[]
  activePage: Page
  onPageSelect: (page: Page) => void
  onCreatePage: () => void
  isOpen: boolean
  onToggle: () => void
}

export function Sidebar({
  pages,
  activePage,
  onPageSelect,
  onCreatePage,
  isOpen,
  onToggle,
}: SidebarProps) {
  if (!isOpen) {
    return (
      <button
        onClick={onToggle}
        className="fixed left-0 top-1/2 -translate-y-1/2 z-50 bg-white border border-mws-gray-200 rounded-r-lg p-2 shadow-sm hover:bg-mws-gray-50"
      >
        <ChevronRight size={16} className="text-mws-gray-500" />
      </button>
    )
  }

  return (
    <aside className="w-[260px] h-full bg-mws-gray-50 border-r border-mws-gray-200 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-mws-gray-200 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center">
            <span className="text-white font-bold text-sm">W</span>
          </div>
          <span className="font-semibold text-mws-gray-700">WikiLive</span>
        </div>
        <button
          onClick={onToggle}
          className="p-1 hover:bg-mws-gray-100 rounded"
        >
          <ChevronLeft size={16} className="text-mws-gray-500" />
        </button>
      </div>

      {/* Search */}
      <div className="p-3">
        <div className="relative">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-mws-gray-400" />
          <input
            type="text"
            placeholder="Поиск..."
            className="w-full pl-9 pr-3 py-2 text-sm bg-white border border-mws-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary"
          />
        </div>
      </div>

      {/* New Page Button */}
      <div className="px-3 pb-2">
        <button
          onClick={onCreatePage}
          className="w-full flex items-center gap-2 px-3 py-2 text-sm text-mws-gray-600 hover:bg-mws-gray-100 rounded-lg transition-colors"
        >
          <Plus size={16} />
          <span>Новая страница</span>
        </button>
      </div>

      {/* Pages List */}
      <div className="flex-1 overflow-y-auto px-3">
        <div className="text-xs font-medium text-mws-gray-400 uppercase tracking-wider px-3 py-2">
          Страницы
        </div>
        <nav className="space-y-1">
          {pages.map((page) => (
            <button
              key={page.id}
              onClick={() => onPageSelect(page)}
              className={`w-full flex items-center gap-2 px-3 py-2 text-sm rounded-lg transition-colors text-left ${
                activePage.id === page.id
                  ? 'bg-primary/10 text-primary'
                  : 'text-mws-gray-600 hover:bg-mws-gray-100'
              }`}
            >
              <FileText size={16} />
              <span className="truncate">{page.title}</span>
            </button>
          ))}
        </nav>
      </div>

      {/* Footer */}
      <div className="p-3 border-t border-mws-gray-200">
        <div className="flex items-center gap-2 px-3 py-2 text-xs text-mws-gray-400">
          <div className="w-2 h-2 bg-green-500 rounded-full" />
          <span>Синхронизировано</span>
        </div>
      </div>
    </aside>
  )
}
