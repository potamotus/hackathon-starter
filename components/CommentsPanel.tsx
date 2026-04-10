import { X, MessageSquare, MoreVertical, History, Lock } from 'lucide-react';
import { useState } from 'react';
import CommentsUI from '../../imports/РедактированиеКомментария';
import { CommentsHistoryModal } from './CommentsHistoryModal';
import { CommentAccessModal } from './CommentAccessModal';

interface CommentsPanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CommentsPanel({ isOpen, onClose }: CommentsPanelProps) {
  const [showMenu, setShowMenu] = useState(false);
  const [showHistoryModal, setShowHistoryModal] = useState(false);
  const [showAccessModal, setShowAccessModal] = useState(false);

  if (!isOpen) return null;

  return (
    <>
      <div className="fixed right-0 top-0 h-full w-[400px] bg-white shadow-lg z-50 animate-slide-in">
        <div className="h-full overflow-y-auto relative">
          {/* Menu Button */}
          <button
            onClick={() => setShowMenu(!showMenu)}
            className="absolute top-[16px] right-[48px] z-10 cursor-pointer"
          >
            <MoreVertical size={16} className="text-[#6d7482]" />
          </button>

          {/* Dropdown Menu */}
          {showMenu && (
            <div className="absolute top-[40px] right-[40px] z-20 bg-white rounded-[12px] shadow-[0px_0px_16px_0px_rgba(0,0,0,0.08),0px_4px_16px_0px_rgba(0,0,0,0.08)] p-[4px] flex flex-col gap-[2px]">
              <button
                onClick={() => {
                  setShowHistoryModal(true);
                  setShowMenu(false);
                }}
                className="flex items-center gap-[6px] px-[8px] py-[6px] hover:bg-[#f6f7fa] rounded-[8px] cursor-pointer"
              >
                <History size={16} className="text-[#6d7482]" />
                <p className="font-['Roboto:Regular',sans-serif] text-[14px] leading-[22px] text-[#2a2a2a]" style={{ fontVariationSettings: "'wdth' 100" }}>
                  История комментариев
                </p>
              </button>
              <button
                onClick={() => {
                  setShowAccessModal(true);
                  setShowMenu(false);
                }}
                className="flex items-center gap-[6px] px-[8px] py-[6px] hover:bg-[#f6f7fa] rounded-[8px] cursor-pointer"
              >
                <Lock size={16} className="text-[#6d7482]" />
                <p className="font-['Roboto:Regular',sans-serif] text-[14px] leading-[22px] text-[#2a2a2a]" style={{ fontVariationSettings: "'wdth' 100" }}>
                  Доступ к комментариям
                </p>
              </button>
            </div>
          )}

          <CommentsUI />
        </div>
      </div>

      {/* Modals */}
      <CommentsHistoryModal
        isOpen={showHistoryModal}
        onClose={() => setShowHistoryModal(false)}
      />
      <CommentAccessModal
        isOpen={showAccessModal}
        onClose={() => setShowAccessModal(false)}
      />
    </>
  );
}

export function CommentsPanelToggle({ onToggle, isOpen }: { onToggle: () => void; isOpen: boolean }) {
  return (
    <button
      onClick={onToggle}
      className={`flex items-center justify-center h-[24px] px-[8px] rounded-[4px] cursor-pointer ${
        isOpen ? 'bg-[#7b67ee] text-white' : 'bg-[#f0f1f3] text-[#505762]'
      }`}
      title="Комментарии"
    >
      <MessageSquare size={14} />
    </button>
  );
}
