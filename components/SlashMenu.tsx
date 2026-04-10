import { useState, useEffect } from 'react';
import { Editor } from '@tiptap/react';

interface SlashMenuProps {
  editor: Editor | null;
  query: string;
  onSelect: (command: string) => void;
}

interface Command {
  id: string;
  title: string;
  description: string;
  icon: string;
  action: (editor: Editor) => void;
}

const commands: Command[] = [
  {
    id: 'text',
    title: 'Обычный текст',
    description: 'Параграф текста',
    icon: 'T',
    action: (editor) => editor.chain().focus().setParagraph().run(),
  },
  {
    id: 'h1',
    title: 'Заголовок 1',
    description: 'Большой заголовок',
    icon: 'H1',
    action: (editor) => editor.chain().focus().setHeading({ level: 1 }).run(),
  },
  {
    id: 'h2',
    title: 'Заголовок 2',
    description: 'Средний заголовок',
    icon: 'H2',
    action: (editor) => editor.chain().focus().setHeading({ level: 2 }).run(),
  },
  {
    id: 'h3',
    title: 'Заголовок 3',
    description: 'Маленький заголовок',
    icon: 'H3',
    action: (editor) => editor.chain().focus().setHeading({ level: 3 }).run(),
  },
  {
    id: 'ol',
    title: 'Маркированный список',
    description: 'Список с маркерами',
    icon: '•',
    action: (editor) => editor.chain().focus().toggleBulletList().run(),
  },
  {
    id: 'ul',
    title: 'Нумерованный список',
    description: 'Нумерованный список',
    icon: '1.',
    action: (editor) => editor.chain().focus().toggleOrderedList().run(),
  },
  {
    id: 'checklist',
    title: 'Чеклист',
    description: 'Список с чекбоксами',
    icon: '☐',
    action: (editor) => editor.chain().focus().toggleTaskList().run(),
  },
  {
    id: 'quote',
    title: 'Цитата',
    description: 'Блок цитаты',
    icon: '"',
    action: (editor) => editor.chain().focus().toggleBlockquote().run(),
  },
  {
    id: 'code',
    title: 'Код',
    description: 'Блок кода',
    icon: '</>',
    action: (editor) => editor.chain().focus().toggleCodeBlock().run(),
  },
  {
    id: 'image',
    title: 'Изображение',
    description: 'Вставить изображение',
    icon: '🖼',
    action: (editor) => {
      const url = window.prompt('URL изображения:');
      if (url) {
        editor.chain().focus().setImage({ src: url }).run();
      }
    },
  },
];

export function SlashMenu({ editor, query, onSelect }: SlashMenuProps) {
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [filteredCommands, setFilteredCommands] = useState(commands);

  useEffect(() => {
    const filtered = commands.filter((cmd) =>
      cmd.title.toLowerCase().includes(query.toLowerCase()) ||
      cmd.description.toLowerCase().includes(query.toLowerCase())
    );
    setFilteredCommands(filtered);
    setSelectedIndex(0);
  }, [query]);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowDown') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev + 1) % filteredCommands.length);
      } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        setSelectedIndex((prev) => (prev - 1 + filteredCommands.length) % filteredCommands.length);
      } else if (e.key === 'Enter') {
        e.preventDefault();
        const cmd = filteredCommands[selectedIndex];
        if (cmd && editor) {
          cmd.action(editor);
          onSelect(cmd.id);
        }
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [selectedIndex, filteredCommands, editor, onSelect]);

  if (filteredCommands.length === 0) {
    return null;
  }

  return (
    <div className="absolute bg-white content-stretch flex flex-col gap-[12px] items-start left-[358px] p-[24px] rounded-[12px] shadow-[0px_4px_24px_0px_rgba(0,0,0,0.12),0px_8px_16px_0px_rgba(0,0,0,0.08)] top-[327px] z-50">
      {filteredCommands.map((cmd, index) => (
        <div
          key={cmd.id}
          onClick={() => {
            if (editor) {
              cmd.action(editor);
              onSelect(cmd.id);
            }
          }}
          className={`content-stretch flex gap-[8px] h-[24px] items-center relative shrink-0 cursor-pointer px-[8px] rounded-[6px] ${
            index === selectedIndex ? 'bg-[#f0f1f3]' : ''
          }`}
        >
          <div className="bg-[#f0f1f3] relative rounded-[6px] shrink-0 size-[24px]">
            <div className="content-stretch flex items-center justify-center overflow-clip relative rounded-[inherit] size-full">
              <div className="font-['MTS_Compact:Regular',sans-serif] text-[12px] text-[#505762]">
                {cmd.icon}
              </div>
            </div>
            <div aria-hidden="true" className="absolute border border-[#d7d9dd] border-solid inset-0 pointer-events-none rounded-[6px]" />
          </div>
          <p className="font-['MTS_Compact:Regular',sans-serif] leading-[20px] not-italic relative shrink-0 text-[#1d2023] text-[14px] whitespace-nowrap">
            {cmd.title}
          </p>
        </div>
      ))}
    </div>
  );
}
