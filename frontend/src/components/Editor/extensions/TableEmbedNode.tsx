import { Node, mergeAttributes } from '@tiptap/core'
import { ReactNodeViewRenderer, NodeViewWrapper } from '@tiptap/react'
import { TableEmbed } from '../TableEmbed'

export interface TableEmbedOptions {
  HTMLAttributes: Record<string, unknown>
}

declare module '@tiptap/core' {
  interface Commands<ReturnType> {
    tableEmbed: {
      insertTableEmbed: (datasheetId: string, viewId?: string) => ReturnType
    }
  }
}

const TableEmbedComponent = ({ node, deleteNode }: { node: any; deleteNode: () => void }) => {
  return (
    <NodeViewWrapper className="table-embed-wrapper">
      <TableEmbed
        datasheetId={node.attrs.datasheetId}
        viewId={node.attrs.viewId}
        onRemove={deleteNode}
      />
    </NodeViewWrapper>
  )
}

export const TableEmbedNode = Node.create<TableEmbedOptions>({
  name: 'tableEmbed',
  group: 'block',
  atom: true,
  draggable: true,

  addOptions() {
    return {
      HTMLAttributes: {},
    }
  },

  addAttributes() {
    return {
      datasheetId: {
        default: null,
      },
      viewId: {
        default: null,
      },
    }
  },

  parseHTML() {
    return [
      {
        tag: 'div[data-table-embed]',
      },
    ]
  },

  renderHTML({ HTMLAttributes }) {
    return ['div', mergeAttributes(this.options.HTMLAttributes, HTMLAttributes, { 'data-table-embed': '' })]
  },

  addNodeView() {
    return ReactNodeViewRenderer(TableEmbedComponent)
  },

  addCommands() {
    return {
      insertTableEmbed:
        (datasheetId: string, viewId?: string) =>
        ({ commands }) => {
          return commands.insertContent({
            type: this.name,
            attrs: { datasheetId, viewId },
          })
        },
    }
  },
})
