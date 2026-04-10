import { Extension } from '@tiptap/core';
import { ReactRenderer, Editor } from '@tiptap/react';
import Suggestion from '@tiptap/suggestion';
import tippy from 'tippy.js';
import { SlashMenuList } from './SlashMenuList';

export const SlashCommand = Extension.create({
  name: 'slashCommand',

  addOptions() {
    return {
      suggestion: {
        char: '/',
        command: ({ editor, range, props }: any) => {
          props.command({ editor, range });
        },
      },
    };
  },

  addProseMirrorPlugins() {
    return [
      Suggestion({
        editor: this.editor,
        ...this.options.suggestion,
      }),
    ];
  },
});

export const getSuggestionItems = ({ query }: { query: string }) => {
  const commands = [
    {
      id: 'text',
      title: 'Обычный текст',
      icon: 'T',
      command: ({ editor, range }: { editor: Editor; range: any }) => {
        editor.chain().focus().deleteRange(range).setParagraph().run();
      },
    },
    {
      id: 'h1',
      title: 'Заголовок 1',
      icon: 'H1',
      command: ({ editor, range }: { editor: Editor; range: any }) => {
        editor.chain().focus().deleteRange(range).setHeading({ level: 1 }).run();
      },
    },
    {
      id: 'h2',
      title: 'Заголовок 2',
      icon: 'H2',
      command: ({ editor, range }: { editor: Editor; range: any }) => {
        editor.chain().focus().deleteRange(range).setHeading({ level: 2 }).run();
      },
    },
    {
      id: 'h3',
      title: 'Заголовок 3',
      icon: 'H3',
      command: ({ editor, range }: { editor: Editor; range: any }) => {
        editor.chain().focus().deleteRange(range).setHeading({ level: 3 }).run();
      },
    },
    {
      id: 'bulletList',
      title: 'Маркированный список',
      icon: '•',
      command: ({ editor, range }: { editor: Editor; range: any }) => {
        editor.chain().focus().deleteRange(range).toggleBulletList().run();
      },
    },
    {
      id: 'orderedList',
      title: 'Нумерованный список',
      icon: '1.',
      command: ({ editor, range }: { editor: Editor; range: any }) => {
        editor.chain().focus().deleteRange(range).toggleOrderedList().run();
      },
    },
    {
      id: 'taskList',
      title: 'Чеклист',
      icon: '☐',
      command: ({ editor, range }: { editor: Editor; range: any }) => {
        editor.chain().focus().deleteRange(range).toggleTaskList().run();
      },
    },
    {
      id: 'quote',
      title: 'Цитата',
      icon: '"',
      command: ({ editor, range }: { editor: Editor; range: any }) => {
        editor.chain().focus().deleteRange(range).toggleBlockquote().run();
      },
    },
    {
      id: 'code',
      title: 'Код',
      icon: '</>',
      command: ({ editor, range }: { editor: Editor; range: any }) => {
        editor.chain().focus().deleteRange(range).toggleCodeBlock().run();
      },
    },
  ];

  return commands.filter((cmd) =>
    cmd.title.toLowerCase().includes(query.toLowerCase())
  );
};

export const renderItems = () => {
  let component: ReactRenderer | null = null;
  let popup: any[] = [];

  return {
    onStart: (props: any) => {
      component = new ReactRenderer(SlashMenuList, {
        props,
        editor: props.editor,
      });

      if (!props.clientRect) {
        return;
      }

      popup = tippy('body', {
        getReferenceClientRect: props.clientRect,
        appendTo: () => document.body,
        content: component.element,
        showOnCreate: true,
        interactive: true,
        trigger: 'manual',
        placement: 'bottom-start',
      });
    },

    onUpdate(props: any) {
      component?.updateProps(props);

      if (!props.clientRect) {
        return;
      }

      popup[0]?.setProps({
        getReferenceClientRect: props.clientRect,
      });
    },

    onKeyDown(props: any) {
      if (props.event.key === 'Escape') {
        popup[0]?.hide();
        return true;
      }

      return (component?.ref as any)?.onKeyDown(props) || false;
    },

    onExit() {
      popup[0]?.destroy();
      component?.destroy();
    },
  };
};

export const slashSuggestionOptions = {
  items: getSuggestionItems,
  render: renderItems,
};
