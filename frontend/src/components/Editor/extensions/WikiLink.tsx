import { Node, mergeAttributes } from '@tiptap/core'
import { Plugin, PluginKey } from '@tiptap/pm/state'
import { Decoration, DecorationSet } from '@tiptap/pm/view'

export interface WikiLinkOptions {
  HTMLAttributes: Record<string, unknown>
  onNavigate?: (pageName: string) => void
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    wikiLink: {
      setWikiLink: (pageName: string) => ReturnType
    }
  }
}

export const WikiLink = Node.create<WikiLinkOptions>({
  name: 'wikiLink',
  group: 'inline',
  inline: true,
  atom: true,

  addOptions() {
    return {
      HTMLAttributes: {},
      onNavigate: undefined,
    }
  },

  addAttributes() {
    return {
      pageName: {
        default: null,
        parseHTML: element => element.getAttribute('data-page'),
        renderHTML: attributes => ({
          'data-page': attributes.pageName,
        }),
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'span[data-wiki-link]',
      },
    ]
  },

  renderHTML({ HTMLAttributes, node }) {
    return [
      'span',
      mergeAttributes(
        this.options.HTMLAttributes,
        HTMLAttributes,
        {
          'data-wiki-link': '',
          class: 'wiki-link bg-mws-blue-50 text-mws-blue-600 px-1 rounded cursor-pointer hover:bg-mws-blue-100 hover:underline',
        }
      ),
      `[[${node.attrs.pageName}]]`,
    ]
  },

  addCommands() {
    return {
      setWikiLink:
        (pageName: string) =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            attrs: { pageName },
          })
        },
    }
  },

  addProseMirrorPlugins() {
    const extension = this

    return [
      // Input rule: convert [[text]] to wiki link
      new Plugin({
        key: new PluginKey('wikiLinkInput'),
        props: {
          handleTextInput(view, from, to, text) {
            if (text !== ']') return false

            const { state } = view
            const $from = state.doc.resolve(from)
            const textBefore = $from.parent.textBetween(
              Math.max(0, $from.parentOffset - 100),
              $from.parentOffset,
              undefined,
              '\ufffc'
            )

            // Check for [[pageName] pattern (waiting for second ])
            const match = textBefore.match(/\[\[([^\[\]]+)$/)
            if (!match) return false

            const pageName = match[1]
            const start = from - match[0].length
            const end = to

            const tr = state.tr
              .delete(start, end)
              .insert(
                start,
                state.schema.nodes.wikiLink.create({ pageName })
              )

            view.dispatch(tr)
            return true
          },
        },

        // Click handler
        view() {
          return {
            update(view) {
              const handleClick = (e: MouseEvent) => {
                const target = e.target as HTMLElement
                if (target.hasAttribute('data-wiki-link')) {
                  e.preventDefault()
                  const pageName = target.getAttribute('data-page')
                  if (pageName && extension.options.onNavigate) {
                    extension.options.onNavigate(pageName)
                  }
                }
              }
              view.dom.addEventListener('click', handleClick)
            },
          }
        },
      }),

      // Preview decoration: show [[...]] as typed with highlighting
      new Plugin({
        key: new PluginKey('wikiLinkPreview'),
        props: {
          decorations(state) {
            const decorations: Decoration[] = []
            const { doc, selection } = state
            const { from } = selection

            doc.descendants((node, pos) => {
              if (!node.isText) return

              const text = node.text || ''
              // Find incomplete wiki links being typed
              const incompleteMatch = text.match(/\[\[([^\[\]]*?)$/)

              if (incompleteMatch) {
                const start = pos + text.lastIndexOf('[[')
                const end = pos + text.length

                // Only decorate if cursor is at or after the match
                if (from >= start && from <= end + 1) {
                  decorations.push(
                    Decoration.inline(start, end, {
                      class: 'wiki-link-typing text-mws-blue-500 bg-mws-blue-50/50',
                    })
                  )
                }
              }
            })

            return DecorationSet.create(doc, decorations)
          },
        },
      }),
    ]
  },
})
