import { Editor } from '@tiptap/react'
import {
  Bold, Italic, Underline, Strikethrough,
  Heading1, Heading2, Heading3,
  List, ListOrdered, CheckSquare,
  MessageSquare, History, ChevronLeft, ChevronRight
} from 'lucide-react'

interface EditorToolbarProps {
  editor: Editor | null
  isCommentsOpen?: boolean
  onToggleComments?: () => void
  isTimelineOpen?: boolean
  onToggleTimeline?: () => void
  saveStatus?: 'saved' | 'saving' | 'error'
}

export function EditorToolbar({
  editor,
  isCommentsOpen = false,
  onToggleComments,
  isTimelineOpen = false,
  onToggleTimeline,
  saveStatus = 'saved',
}: EditorToolbarProps) {
  if (!editor) {
    return null
  }

  return (
    <div className="bg-mws-gray-50 h-[44px] border-b border-mws-gray-200 flex items-center px-4 gap-2">
      {/* Navigation */}
      <div className="flex items-center gap-1">
        <ToolbarButton onClick={() => {}} disabled>
          <ChevronLeft size={16} />
        </ToolbarButton>
        <ToolbarButton onClick={() => {}} disabled>
          <ChevronRight size={16} />
        </ToolbarButton>
      </div>

      <Divider />

      {/* Text formatting */}
      <div className="flex items-center">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBold().run()}
          isActive={editor.isActive('bold')}
          title="Жирный (Ctrl+B)"
        >
          <Bold size={16} />
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleItalic().run()}
          isActive={editor.isActive('italic')}
          title="Курсив (Ctrl+I)"
        >
          <Italic size={16} />
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleUnderline().run()}
          isActive={editor.isActive('underline')}
          title="Подчёркнутый (Ctrl+U)"
        >
          <Underline size={16} />
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleStrike().run()}
          isActive={editor.isActive('strike')}
          title="Зачёркнутый"
        >
          <Strikethrough size={16} />
        </ToolbarButton>
      </div>

      <Divider />

      {/* Headings */}
      <div className="flex items-center">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
          isActive={editor.isActive('heading', { level: 1 })}
          title="Заголовок 1"
        >
          <Heading1 size={16} />
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          isActive={editor.isActive('heading', { level: 2 })}
          title="Заголовок 2"
        >
          <Heading2 size={16} />
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
          isActive={editor.isActive('heading', { level: 3 })}
          title="Заголовок 3"
        >
          <Heading3 size={16} />
        </ToolbarButton>
      </div>

      <Divider />

      {/* Lists */}
      <div className="flex items-center">
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleBulletList().run()}
          isActive={editor.isActive('bulletList')}
          title="Маркированный список"
        >
          <List size={16} />
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleOrderedList().run()}
          isActive={editor.isActive('orderedList')}
          title="Нумерованный список"
        >
          <ListOrdered size={16} />
        </ToolbarButton>
        <ToolbarButton
          onClick={() => editor.chain().focus().toggleTaskList().run()}
          isActive={editor.isActive('taskList')}
          title="Чеклист"
        >
          <CheckSquare size={16} />
        </ToolbarButton>
      </div>

      <div className="flex-1" />

      {/* Right side: Comments, Timeline */}
      <div className="flex items-center gap-2">
        {onToggleComments && (
          <ToolbarButton
            onClick={onToggleComments}
            isActive={isCommentsOpen}
            title="Комментарии"
          >
            <MessageSquare size={16} />
          </ToolbarButton>
        )}
        {onToggleTimeline && (
          <ToolbarButton
            onClick={onToggleTimeline}
            isActive={isTimelineOpen}
            title="Машина времени"
            className="flex items-center gap-1"
          >
            <History size={16} />
            <span className="text-xs">Машина времени</span>
          </ToolbarButton>
        )}
      </div>
    </div>
  )
}

function ToolbarButton({
  onClick,
  isActive = false,
  disabled = false,
  title,
  children,
  className = '',
}: {
  onClick: () => void
  isActive?: boolean
  disabled?: boolean
  title?: string
  children: React.ReactNode
  className?: string
}) {
  return (
    <button
      onClick={onClick}
      disabled={disabled}
      title={title}
      className={`
        h-7 px-2 rounded flex items-center justify-center transition-colors
        ${isActive ? 'bg-primary text-white' : 'text-mws-gray-500 hover:bg-mws-gray-100'}
        ${disabled ? 'opacity-40 cursor-not-allowed' : 'cursor-pointer'}
        ${className}
      `}
    >
      {children}
    </button>
  )
}

function Divider() {
  return <div className="w-px h-4 bg-mws-gray-200 mx-2" />
}
