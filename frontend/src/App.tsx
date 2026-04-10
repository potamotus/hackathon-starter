import { useState } from 'react'
import { WikiEditor } from './components/Editor/WikiEditor'
import { CollaborativeEditor } from './components/Editor/CollaborativeEditor'
import { Sidebar } from './components/Sidebar/Sidebar'

const ENABLE_COLLABORATION = true // Toggle to enable/disable collaboration

interface Page {
  id: string
  title: string
  content: string
  updatedAt: string
}

function App() {
  const [pages, setPages] = useState<Page[]>([
    { id: '1', title: 'Добро пожаловать', content: '', updatedAt: new Date().toISOString() },
  ])
  const [activePage, setActivePage] = useState<Page>(pages[0])
  const [isSidebarOpen, setIsSidebarOpen] = useState(true)

  const handlePageSelect = (page: Page) => {
    setActivePage(page)
  }

  const handleCreatePage = () => {
    const newPage: Page = {
      id: crypto.randomUUID(),
      title: 'Новая страница',
      content: '',
      updatedAt: new Date().toISOString(),
    }
    setPages([...pages, newPage])
    setActivePage(newPage)
  }

  const handleContentUpdate = (content: string) => {
    const updated = pages.map(p =>
      p.id === activePage.id
        ? { ...p, content, updatedAt: new Date().toISOString() }
        : p
    )
    setPages(updated)
    setActivePage({ ...activePage, content, updatedAt: new Date().toISOString() })
  }

  return (
    <div className="flex h-screen bg-white">
      <Sidebar
        pages={pages}
        activePage={activePage}
        onPageSelect={handlePageSelect}
        onCreatePage={handleCreatePage}
        isOpen={isSidebarOpen}
        onToggle={() => setIsSidebarOpen(!isSidebarOpen)}
      />

      <main className="flex-1 overflow-hidden">
        {ENABLE_COLLABORATION ? (
          <CollaborativeEditor
            key={activePage.id}
            documentId={activePage.id}
            pageTitle={activePage.title}
            userName={localStorage.getItem('userName') || undefined}
            onNavigateToPage={(pageName) => {
              const page = pages.find(p => p.title === pageName)
              if (page) {
                setActivePage(page)
              } else {
                // Create new page if not found
                const newPage: Page = {
                  id: crypto.randomUUID(),
                  title: pageName,
                  content: '',
                  updatedAt: new Date().toISOString(),
                }
                setPages([...pages, newPage])
                setActivePage(newPage)
              }
            }}
          />
        ) : (
          <WikiEditor
            key={activePage.id}
            initialContent={activePage.content}
            onUpdate={handleContentUpdate}
            pageTitle={activePage.title}
          />
        )}
      </main>
    </div>
  )
}

export default App
