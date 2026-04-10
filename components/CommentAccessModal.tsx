import { useState } from 'react';

interface CommentAccessModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CommentAccessModal({ isOpen, onClose }: CommentAccessModalProps) {
  const [accessType, setAccessType] = useState<'all' | 'creator'>('all');

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-[rgba(29,32,35,0.4)] flex items-center justify-center z-50">
      <div className="bg-white rounded-[12px] shadow-[0px_0px_16px_0px_rgba(0,0,0,0.08),0px_4px_16px_0px_rgba(0,0,0,0.08)] w-[460px] p-[24px]">
        {/* Header */}
        <div className="mb-[16px]">
          <p className="font-['Roboto:SemiBold',sans-serif] font-semibold text-[14px] leading-[22px] text-[#282c33] mb-[2px]" style={{ fontVariationSettings: "'wdth' 100" }}>
            Доступ к комментариям
          </p>
          <p className="font-['Roboto:Regular',sans-serif] text-[12px] leading-[18px] text-[#6d7482]" style={{ fontVariationSettings: "'wdth' 100" }}>
            Укажите, кто может комментировать
          </p>
        </div>

        {/* Radio Options */}
        <div className="flex flex-col gap-[8px]">
          {/* All Users Option */}
          <div
            className="flex gap-[4px] items-center cursor-pointer"
            onClick={() => setAccessType('all')}
          >
            <div className="w-[16px] h-[16px] flex items-center justify-center">
              <div className={`w-[12px] h-[12px] rounded-full ${accessType === 'all' ? 'bg-[#7b67ee]' : 'border-[1.5px] border-[#868d9c]'} flex items-center justify-center`}>
                {accessType === 'all' && (
                  <div className="w-[6px] h-[6px] rounded-full bg-white" />
                )}
              </div>
            </div>
            <p className="font-['Roboto:Regular',sans-serif] text-[14px] leading-[22px] text-[#282c33]" style={{ fontVariationSettings: "'wdth' 100" }}>
              Все пользователи
            </p>
          </div>

          {/* Creator Only Option */}
          <div
            className="flex gap-[4px] items-center cursor-pointer"
            onClick={() => setAccessType('creator')}
          >
            <div className="w-[16px] h-[16px] flex items-center justify-center">
              <div className={`w-[12px] h-[12px] rounded-full ${accessType === 'creator' ? 'bg-[#7b67ee]' : 'border-[1.5px] border-[#868d9c]'} flex items-center justify-center`}>
                {accessType === 'creator' && (
                  <div className="w-[6px] h-[6px] rounded-full bg-white" />
                )}
              </div>
            </div>
            <p className="font-['Roboto:Regular',sans-serif] text-[14px] leading-[22px] text-[#282c33]" style={{ fontVariationSettings: "'wdth' 100" }}>
              Только создатель страницы
            </p>
          </div>
        </div>

        {/* Close Button (optional) */}
        <div className="mt-[24px] flex justify-end">
          <button
            onClick={onClose}
            className="bg-[#907ff0] text-white px-[16px] py-[9px] rounded-[4px] font-['Roboto:Regular',sans-serif] text-[14px] leading-[22px] cursor-pointer"
            style={{ fontVariationSettings: "'wdth' 100" }}
          >
            Применить
          </button>
        </div>
      </div>
    </div>
  );
}
