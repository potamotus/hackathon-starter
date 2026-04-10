import { useEditor, EditorContent } from '@tiptap/react';
import StarterKit from '@tiptap/starter-kit';
import Placeholder from '@tiptap/extension-placeholder';
import Link from '@tiptap/extension-link';
import Image from '@tiptap/extension-image';
import Underline from '@tiptap/extension-underline';
import TextAlign from '@tiptap/extension-text-align';
import TaskList from '@tiptap/extension-task-list';
import TaskItem from '@tiptap/extension-task-item';
import { useEffect, useState } from 'react';
import { EditorToolbar } from './EditorToolbar';
import { CommentsPanel } from './CommentsPanel';
import { TimelinePanel } from './TimelinePanel';

interface WikiEditorProps {
  initialContent?: string;
  onUpdate?: (content: string) => void;
}

export function WikiEditor({ initialContent, onUpdate }: WikiEditorProps) {
  const [isCommentsOpen, setIsCommentsOpen] = useState(false);
  const [isTimelineOpen, setIsTimelineOpen] = useState(false);

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
            return 'Заголовок';
          }
          return 'Начните вводить содержимое или нажмите / чтобы использовать команды';
        },
      }),
      Link.configure({
        openOnClick: false,
        HTMLAttributes: {
          class: 'text-[#0070e5] underline cursor-pointer',
        },
      }),
      Image.configure({
        HTMLAttributes: {
          class: 'max-w-full rounded-[4px]',
        },
      }),
    ],
    content: initialContent || '',
    editorProps: {
      attributes: {
        class: 'prose prose-sm max-w-none focus:outline-none min-h-[400px]',
      },
    },
    onUpdate: ({ editor }) => {
      const html = editor.getHTML();
      onUpdate?.(html);

      // Auto-save to localStorage
      localStorage.setItem('wiki-editor-content', html);
      localStorage.setItem('wiki-editor-timestamp', new Date().toISOString());
    },
    onCreate: ({ editor }) => {
      // Load from localStorage if no initial content
      if (!initialContent) {
        const savedContent = localStorage.getItem('wiki-editor-content');
        if (savedContent) {
          editor.commands.setContent(savedContent);
        }
      }
    },
  });

  useEffect(() => {
    // Auto-save interval (every 3 seconds)
    const interval = setInterval(() => {
      if (editor && editor.getHTML() !== initialContent) {
        const content = editor.getHTML();
        localStorage.setItem('wiki-editor-content', content);
        localStorage.setItem('wiki-editor-timestamp', new Date().toISOString());
        onUpdate?.(content);
      }
    }, 3000);

    return () => clearInterval(interval);
  }, [editor, initialContent, onUpdate]);

  return (
    <div className="bg-white content-stretch flex flex-col items-center relative size-full">
      <EditorToolbar
        editor={editor}
        isCommentsOpen={isCommentsOpen}
        onToggleComments={() => setIsCommentsOpen(!isCommentsOpen)}
        isTimelineOpen={isTimelineOpen}
        onToggleTimeline={() => setIsTimelineOpen(!isTimelineOpen)}
      />

      <div className="flex-[1_0_0] min-h-px min-w-px relative w-full overflow-y-auto">
        <div className="flex flex-col items-center size-full">
          <div className="content-stretch flex flex-col items-center py-[56px] relative w-full">
            <div className="content-stretch flex flex-col gap-[24px] items-start relative shrink-0 w-[700px]">
              <EditorContent editor={editor} className="w-full" />
            </div>
          </div>
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
    </div>
  );
}
