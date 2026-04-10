import { Extension } from '@tiptap/core'
import { ReactRenderer } from '@tiptap/react'
import Suggestion, { SuggestionProps, SuggestionKeyDownProps } from '@tiptap/suggestion'
import tippy, { Instance as TippyInstance } from 'tippy.js'
import { forwardRef, useEffect, useImperativeHandle, useState } from 'react'

interface CommandItem {
  id: string
  title: string
  description: string
  icon: string
  command: (props: { editor: any; range: any }) => void
}

const commands: CommandItem[] = [
  {
    id: 'text',
    title: 'Текст',
    description: 'Обычный параграф',
    icon: 'T',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setParagraph().run()
    },
  },
  {
    id: 'h1',
    title: 'Заголовок 1',
    description: 'Большой заголовок',
    icon: 'H1',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setHeading({ level: 1 }).run()
    },
  },
  {
    id: 'h2',
    title: 'Заголовок 2',
    description: 'Средний заголовок',
    icon: 'H2',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setHeading({ level: 2 }).run()
    },
  },
  {
    id: 'h3',
    title: 'Заголовок 3',
    description: 'Маленький заголовок',
    icon: 'H3',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setHeading({ level: 3 }).run()
    },
  },
  {
    id: 'bullet',
    title: 'Маркированный список',
    description: 'Список с точками',
    icon: '•',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleBulletList().run()
    },
  },
  {
    id: 'numbered',
    title: 'Нумерованный список',
    description: 'Список с цифрами',
    icon: '1.',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleOrderedList().run()
    },
  },
  {
    id: 'task',
    title: 'Чеклист',
    description: 'Список задач',
    icon: '☐',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleTaskList().run()
    },
  },
  {
    id: 'quote',
    title: 'Цитата',
    description: 'Блок цитаты',
    icon: '❝',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleBlockquote().run()
    },
  },
  {
    id: 'code',
    title: 'Код',
    description: 'Блок кода',
    icon: '</>',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).toggleCodeBlock().run()
    },
  },
  {
    id: 'divider',
    title: 'Разделитель',
    description: 'Горизонтальная линия',
    icon: '―',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).setHorizontalRule().run()
    },
  },
  {
    id: 'image',
    title: 'Изображение',
    description: 'Вставить картинку',
    icon: '🖼',
    command: ({ editor, range }) => {
      const url = window.prompt('URL изображения:')
      if (url) {
        editor.chain().focus().deleteRange(range).setImage({ src: url }).run()
      }
    },
  },
  {
    id: 'table',
    title: 'Таблица MWS',
    description: 'Вставить таблицу из MWS Tables',
    icon: '📊',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).run()
      const onOpenTablePicker = editor.storage.slashCommand?.onOpenTablePicker
      if (onOpenTablePicker) {
        onOpenTablePicker()
      }
    },
  },
  {
    id: 'ai-summarize',
    title: 'AI: Резюме',
    description: 'Создать краткое изложение',
    icon: '🤖',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).run()
      const onOpenAICommand = editor.storage.slashCommand?.onOpenAICommand
      if (onOpenAICommand) {
        onOpenAICommand('summarize')
      }
    },
  },
  {
    id: 'ai-translate',
    title: 'AI: Перевод',
    description: 'Перевести текст',
    icon: '🌐',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).run()
      const onOpenAICommand = editor.storage.slashCommand?.onOpenAICommand
      if (onOpenAICommand) {
        onOpenAICommand('translate')
      }
    },
  },
  {
    id: 'ai-improve',
    title: 'AI: Улучшить',
    description: 'Улучшить написание текста',
    icon: '✨',
    command: ({ editor, range }) => {
      editor.chain().focus().deleteRange(range).run()
      const onOpenAICommand = editor.storage.slashCommand?.onOpenAICommand
      if (onOpenAICommand) {
        onOpenAICommand('improve')
      }
    },
  },
]

interface CommandListProps {
  items: CommandItem[]
  command: (item: CommandItem) => void
}

interface CommandListRef {
  onKeyDown: (props: SuggestionKeyDownProps) => boolean
}

const CommandList = forwardRef<CommandListRef, CommandListProps>(
  ({ items, command }, ref) => {
    const [selectedIndex, setSelectedIndex] = useState(0)

    useEffect(() => {
      setSelectedIndex(0)
    }, [items])

    useImperativeHandle(ref, () => ({
      onKeyDown: ({ event }: SuggestionKeyDownProps) => {
        if (event.key === 'ArrowUp') {
          setSelectedIndex((prev) => (prev - 1 + items.length) % items.length)
          return true
        }
        if (event.key === 'ArrowDown') {
          setSelectedIndex((prev) => (prev + 1) % items.length)
          return true
        }
        if (event.key === 'Enter') {
          const item = items[selectedIndex]
          if (item) {
            command(item)
          }
          return true
        }
        return false
      },
    }))

    if (items.length === 0) {
      return null
    }

    return (
      <div className="bg-white rounded-xl shadow-lg border border-mws-gray-200 p-2 min-w-[280px] max-h-[300px] overflow-y-auto">
        {items.map((item, index) => (
          <button
            key={item.id}
            onClick={() => command(item)}
            className={`w-full flex items-center gap-3 px-3 py-2 rounded-lg text-left transition-colors ${
              index === selectedIndex
                ? 'bg-primary/10 text-primary'
                : 'hover:bg-mws-gray-50 text-mws-gray-700'
            }`}
          >
            <div className="w-8 h-8 bg-mws-gray-100 rounded-lg flex items-center justify-center text-sm">
              {item.icon}
            </div>
            <div>
              <div className="font-medium text-sm">{item.title}</div>
              <div className="text-xs text-mws-gray-400">{item.description}</div>
            </div>
          </button>
        ))}
      </div>
    )
  }
)

CommandList.displayName = 'CommandList'

interface SlashCommandOptions {
  onOpenTablePicker?: () => void
  onOpenAICommand?: (command: string) => void
}

export const SlashCommand = Extension.create<SlashCommandOptions>({
  name: 'slashCommand',

  addOptions() {
    return {
      onOpenTablePicker: undefined,
      onOpenAICommand: undefined,
      suggestion: {
        char: '/',
        command: ({ editor, range, props }: { editor: any; range: any; props: CommandItem }) => {
          props.command({ editor, range })
        },
      },
    }
  },

  addStorage() {
    return {
      onOpenTablePicker: this.options.onOpenTablePicker,
      onOpenAICommand: this.options.onOpenAICommand,
    }
  },

  addProseMirrorPlugins() {
    return [
      Suggestion({
        editor: this.editor,
        ...this.options.suggestion,
        items: ({ query }: { query: string }) => {
          return commands.filter(
            (item) =>
              item.title.toLowerCase().includes(query.toLowerCase()) ||
              item.description.toLowerCase().includes(query.toLowerCase())
          )
        },
        render: () => {
          let component: ReactRenderer<CommandListRef> | null = null
          let popup: TippyInstance[] | null = null

          return {
            onStart: (props: SuggestionProps<CommandItem>) => {
              component = new ReactRenderer(CommandList, {
                props,
                editor: props.editor,
              })

              if (!props.clientRect) return

              popup = tippy('body', {
                getReferenceClientRect: props.clientRect as () => DOMRect,
                appendTo: () => document.body,
                content: component.element,
                showOnCreate: true,
                interactive: true,
                trigger: 'manual',
                placement: 'bottom-start',
              })
            },
            onUpdate: (props: SuggestionProps<CommandItem>) => {
              component?.updateProps(props)

              if (!props.clientRect || !popup) return

              popup[0].setProps({
                getReferenceClientRect: props.clientRect as () => DOMRect,
              })
            },
            onKeyDown: (props: SuggestionKeyDownProps) => {
              if (props.event.key === 'Escape') {
                popup?.[0].hide()
                return true
              }
              return component?.ref?.onKeyDown(props) ?? false
            },
            onExit: () => {
              popup?.[0].destroy()
              component?.destroy()
            },
          }
        },
      }),
    ]
  },
})
