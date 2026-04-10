import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Placeholder from '@tiptap/extension-placeholder'
import Link from '@tiptap/extension-link'
import Image from '@tiptap/extension-image'
import Underline from '@tiptap/extension-underline'
import TextAlign from '@tiptap/extension-text-align'
import TaskList from '@tiptap/extension-task-list'
import TaskItem from '@tiptap/extension-task-item'
import { useEffect, useState, useCallback } from 'react'
import { EditorToolbar } from './EditorToolbar'
import { SlashCommand } from './extensions/SlashCommand'
import { CommentsPanel } from '../Panels/CommentsPanel'
import { TimelinePanel } from '../Panels/TimelinePanel'

interface WikiEditorProps {
  initialContent?: string
  onUpdate?: (content: string) => void
  pageTitle?: string
}

export function WikiEditor({ initialContent, onUpdate, pageTitle }: WikiEditorProps) {
  const [isCommentsOpen, setIsCommentsOpen] = useState(false)
  const [isTimelineOpen, setIsTimelineOpen] = useState(false)
  const [saveStatus, setSaveStatus] = useState<'saved' | 'saving' | 'error'>('saved')

  const editor = useEditor({
    extensions: [
      StarterKit.configure({
        heading: {
          levels: [1, 2, 3],
        },
      }),
      Underline,
      TextAlign.configure({
        types: ['heading', 'paragraph'],
      }),
      TaskList,
      TaskItem.configure({
        nested: true,
      }),
      Placeholder.configure({
        placeholder: ({ node }) => {
          if (node.type.name === 'heading') {
            return 'Заголовок'
          }
          return 'Введите / для команд...'
        },
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-primary underline cursor-pointer hover:text-primary-hover',
        },
      }),
      Image.configure({
        HTMLAttributes: {
          class: 'max-w-full rounded-lg',
        },
      }),
      SlashCommand,
    ],
    content: initialContent || '',
    editorProps: {
      attributes: {
        class: 'prose prose-sm max-w-none focus:outline-none min-h-[400px]',
      },
    },
    onUpdate: ({ editor }) => {
      const html = editor.getHTML()
      setSaveStatus('saving')

      // Debounced save
      localStorage.setItem('wiki-editor-content', html)
      localStorage.setItem('wiki-editor-timestamp', new Date().toISOString())

      onUpdate?.(html)

      setTimeout(() => setSaveStatus('saved'), 500)
    },
    onCreate: ({ editor }) => {
      if (!initialContent) {
        const savedContent = localStorage.getItem('wiki-editor-content')
        if (savedContent) {
          editor.commands.setContent(savedContent)
        }
      }
    },
  })

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (!editor) return

      // Ctrl/Cmd + S - Save
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault()
        setSaveStatus('saving')
        const content = editor.getHTML()
        localStorage.setItem('wiki-editor-content', content)
        onUpdate?.(content)
        setTimeout(() => setSaveStatus('saved'), 500)
      }

      // Ctrl/Cmd + K - Insert link
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        const url = window.prompt('URL ссылки:')
        if (url) {
          editor.chain().focus().setLink({ href: url }).run()
        }
      }
    }

    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [editor, onUpdate])

  return (
    <div className="bg-white flex flex-col h-full relative">
      <EditorToolbar
        editor={editor}
        isCommentsOpen={isCommentsOpen}
        onToggleComments={() => setIsCommentsOpen(!isCommentsOpen)}
        isTimelineOpen={isTimelineOpen}
        onToggleTimeline={() => setIsTimelineOpen(!isTimelineOpen)}
        saveStatus={saveStatus}
      />

      <div className="flex-1 overflow-y-auto">
        <div className="max-w-[700px] mx-auto py-12 px-6">
          {/* Page Title */}
          {pageTitle && (
            <h1 className="text-3xl font-bold text-mws-gray-700 mb-6">
              {pageTitle}
            </h1>
          )}

          <EditorContent editor={editor} className="w-full" />
        </div>
      </div>

      <CommentsPanel
        isOpen={isCommentsOpen}
        onClose={() => setIsCommentsOpen(false)}
      />

      <TimelinePanel
        isOpen={isTimelineOpen}
        onClose={() => setIsTimelineOpen(false)}
      />

      {/* Save status indicator */}
      <div className="absolute bottom-4 right-4 text-xs text-mws-gray-400">
        {saveStatus === 'saving' && 'Сохранение...'}
        {saveStatus === 'saved' && '✓ Сохранено'}
        {saveStatus === 'error' && '✕ Ошибка сохранения'}
      </div>
    </div>
  )
}
