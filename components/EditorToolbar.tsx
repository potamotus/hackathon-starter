import { Editor } from '@tiptap/react';
import svgPaths from "../../imports/svg-apd2yk5peo";
import { ChevronLeft, ChevronRight } from 'lucide-react';
import { CommentsPanelToggle } from './CommentsPanel';
import { TimelinePanelToggle } from './TimelinePanel';

interface EditorToolbarProps {
  editor: Editor | null;
  isCommentsOpen?: boolean;
  onToggleComments?: () => void;
  isTimelineOpen?: boolean;
  onToggleTimeline?: () => void;
}

export function EditorToolbar({ editor, isCommentsOpen = false, onToggleComments, isTimelineOpen = false, onToggleTimeline }: EditorToolbarProps) {
  if (!editor) {
    return null;
  }

  return (
    <div className="bg-[#f5f7fa] h-[38px] relative shrink-0 w-full">
      <div className="flex flex-row items-center overflow-clip rounded-[inherit] size-full">
        <div className="content-stretch flex gap-[16px] items-center px-[16px] relative size-full">
          {/* Navigation buttons */}
          <div className="content-stretch flex gap-[8px] items-center relative shrink-0">
            <div className="flex items-center justify-center relative shrink-0">
              <div className="-scale-y-100 flex-none rotate-180">
                <ChevronLeft size={16} className="text-[#505762]" />
              </div>
            </div>
            <ChevronRight size={16} className="text-[#505762]" />
          </div>

          <div className="bg-[#e0e0e0] h-[16px] shrink-0 w-[0.475px]" />

          {/* Formatting buttons */}
          <div className="content-stretch flex gap-[8px] items-center relative shrink-0">
            {/* Bold, Italic, Underline group */}
            <div className="content-stretch flex items-center pr-px relative shrink-0">
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleBold().run()}
                isActive={editor.isActive('bold')}
                icon="B"
                rounded="bl-[6px] tl-[6px]"
              />
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleItalic().run()}
                isActive={editor.isActive('italic')}
                icon="I"
              />
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleUnderline().run()}
                isActive={editor.isActive('underline')}
                icon="U"
              />
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleStrike().run()}
                isActive={editor.isActive('strike')}
                icon="S"
                rounded="br-[6px] tr-[6px]"
              />
            </div>

            {/* Heading buttons */}
            <div className="content-stretch flex items-center pr-px relative shrink-0">
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleHeading({ level: 1 }).run()}
                isActive={editor.isActive('heading', { level: 1 })}
                icon="H1"
                rounded="bl-[6px] tl-[6px]"
              />
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
                isActive={editor.isActive('heading', { level: 2 })}
                icon="H2"
              />
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleHeading({ level: 3 }).run()}
                isActive={editor.isActive('heading', { level: 3 })}
                icon="H3"
                rounded="br-[6px] tr-[6px]"
              />
            </div>

            {/* List buttons */}
            <div className="content-stretch flex items-center pr-px relative shrink-0">
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleBulletList().run()}
                isActive={editor.isActive('bulletList')}
                icon="•"
                rounded="bl-[6px] tl-[6px]"
              />
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleOrderedList().run()}
                isActive={editor.isActive('orderedList')}
                icon="1."
              />
              <ToolbarButton
                onClick={() => editor.chain().focus().toggleTaskList().run()}
                isActive={editor.isActive('taskList')}
                icon="☐"
                rounded="br-[6px] tr-[6px]"
              />
            </div>
          </div>

          <div className="bg-[#e0e0e0] h-[16px] shrink-0 w-[0.475px]" />

          {/* Comments button */}
          {onToggleComments && (
            <div className="content-stretch flex items-center gap-[12px] relative shrink-0">
              <CommentsPanelToggle onToggle={onToggleComments} isOpen={isCommentsOpen} />
              {onToggleTimeline && (
                <TimelinePanelToggle onToggle={onToggleTimeline} isOpen={isTimelineOpen} />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

function ToolbarButton({
  onClick,
  isActive,
  icon,
  rounded = ""
}: {
  onClick: () => void;
  isActive: boolean;
  icon: string;
  rounded?: string;
}) {
  return (
    <div
      onClick={onClick}
      className={`h-[24px] mr-[-1px] relative shrink-0 cursor-pointer ${rounded} ${
        isActive ? 'bg-[#7b67ee]' : 'bg-[#f0f1f3]'
      }`}
    >
      <div className="content-stretch flex h-full items-center overflow-clip relative rounded-[inherit]">
        <div className={`relative shrink-0 size-[24px] flex items-center justify-center font-['MTS_Compact:Regular',sans-serif] text-[12px] ${
          isActive ? 'text-white' : 'text-[#505762]'
        }`}>
          {icon}
        </div>
      </div>
      <div aria-hidden="true" className={`absolute border border-solid inset-0 pointer-events-none ${rounded} ${
        isActive ? 'border-[#7b67ee]' : 'border-[#d7d9dd]'
      }`} />
    </div>
  );
}
