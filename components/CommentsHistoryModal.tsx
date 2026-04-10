import { X } from 'lucide-react';

interface CommentsHistoryModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export function CommentsHistoryModal({ isOpen, onClose }: CommentsHistoryModalProps) {
  if (!isOpen) return null;

  const mockComments = [
    {
      id: 1,
      user: 'Иван Иванов',
      date: '27.10.25 в 18:03',
      text: 'Думаю этот параграф стоит переписать, слишком сложно',
      quote: 'Но стоит лишь на мгновение остановиться...',
      status: 'Удалена 29.10.25 в 13:32',
      threadsCount: 20,
    },
    {
      id: 2,
      user: 'Сергей Иванов',
      date: '27.10.25 в 18:03',
      text: 'Мое предложение вообще ничего не делать. Потому что лень.',
      quote: 'Порой кажется, что наша жизнь...',
      status: 'Решена 29.10.25 в 13:32',
      threadsCount: 2,
    },
    {
      id: 3,
      user: 'Иван Иванов',
      date: '27.10.25 в 18:03',
      text: '@sergeii заменить картинку',
      hasImage: true,
      status: 'Решена 29.10.25 в 13:32',
      threadsCount: 1,
      likes: 4,
    },
  ];

  return (
    <div className="fixed inset-0 bg-[rgba(29,32,35,0.4)] flex items-center justify-center z-50">
      <div className="bg-white rounded-[12px] shadow-[0px_0px_16px_0px_rgba(0,0,0,0.08),0px_4px_16px_0px_rgba(0,0,0,0.08)] w-[668px] max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="border-b border-[#e0e3e9] p-[24px] pb-[16px]">
          <div className="flex items-center justify-between">
            <div className="flex flex-col gap-[2px]">
              <p className="font-['Roboto:SemiBold',sans-serif] font-semibold text-[16px] leading-[24px] text-[#282c33]" style={{ fontVariationSettings: "'wdth' 100" }}>
                История комментариев
              </p>
              <p className="font-['Roboto:Regular',sans-serif] text-[12px] leading-[18px] text-[#6d7482]" style={{ fontVariationSettings: "'wdth' 100" }}>
                Отображаются удаленные или решенные ветки
              </p>
            </div>
            <button onClick={onClose} className="cursor-pointer">
              <X size={16} className="text-[#BEC4CF]" />
            </button>
          </div>
        </div>

        {/* Comments List */}
        <div className="flex-1 overflow-y-auto p-[24px] pt-0">
          {mockComments.map((comment) => (
            <div key={comment.id} className="border-b border-[#e0e3e9] py-[16px]">
              {/* User Info */}
              <div className="flex gap-[12px] items-start mb-[8px]">
                <div className="w-[40px] h-[40px] rounded-full bg-[#56CDFF] flex items-center justify-center text-white font-['Roboto:Regular',sans-serif] text-[20px]" style={{ fontVariationSettings: "'wdth' 100" }}>
                  {comment.user[0]}
                </div>
                <div className="flex-1">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-[8px]">
                      <p className="font-['Roboto:Regular',sans-serif] text-[14px] leading-[22px] text-[#282c33]" style={{ fontVariationSettings: "'wdth' 100" }}>
                        {comment.user}
                      </p>
                      {comment.status && (
                        <div className="bg-[#f6f7fa] px-[6px] py-[1px] rounded-[4px]">
                          <p className="font-['Roboto:Regular',sans-serif] text-[12px] leading-[18px] text-[#6d7482] text-center" style={{ fontVariationSettings: "'wdth' 100" }}>
                            {comment.status}
                          </p>
                        </div>
                      )}
                    </div>
                    {comment.likes && (
                      <div className="flex items-center gap-[4px]">
                        <p className="font-['Roboto:SemiBold',sans-serif] font-semibold text-[13px] leading-[20px] text-[#6d7482]" style={{ fontVariationSettings: "'wdth' 100" }}>
                          {comment.likes}
                        </p>
                        <svg className="w-[16px] h-[16px]" fill="none" viewBox="0 0 16 16">
                          <path d="M8 13.5L3.5 9.5C2.5 8.5 2.5 6.5 3.5 5.5C4.5 4.5 6.5 4.5 7.5 5.5L8 6L8.5 5.5C9.5 4.5 11.5 4.5 12.5 5.5C13.5 6.5 13.5 8.5 12.5 9.5L8 13.5Z" fill="#6D7482" />
                        </svg>
                      </div>
                    )}
                  </div>
                  <p className="font-['Roboto:Regular',sans-serif] text-[12px] leading-[18px] text-[#6d7482]" style={{ fontVariationSettings: "'wdth' 100" }}>
                    {comment.date}
                  </p>
                </div>
              </div>

              {/* Quote */}
              {comment.quote && (
                <div className="bg-[#f6f7fa] rounded-[8px] px-[12px] py-[8px] mb-[8px] ml-[52px]">
                  <p className="font-['Roboto:Regular',sans-serif] text-[12px] leading-[18px] text-[#6d7482] overflow-hidden text-ellipsis whitespace-nowrap" style={{ fontVariationSettings: "'wdth' 100" }}>
                    {comment.quote}
                  </p>
                </div>
              )}

              {/* Comment Text */}
              <div className="ml-[52px]">
                <p className="font-['Roboto:Regular',sans-serif] text-[13px] leading-[20px] text-[#282c33] mb-[8px]" style={{ fontVariationSettings: "'wdth' 100" }}>
                  {comment.text}
                </p>
                {comment.threadsCount && (
                  <p className="font-['Roboto:Regular',sans-serif] text-[13px] leading-[20px] text-[#907ff0] cursor-pointer" style={{ fontVariationSettings: "'wdth' 100" }}>
                    Показать {comment.threadsCount} {comment.threadsCount === 1 ? 'комментарий' : 'комментария'} ветки
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Pagination */}
        <div className="border-t border-[#e0e3e9] p-[24px] flex items-center justify-center gap-[8px]">
          {[1, 2, 3, '...', 10].map((page, idx) => (
            <div
              key={idx}
              className={`w-[32px] h-[32px] rounded-[6px] flex items-center justify-center cursor-pointer ${
                page === 1 ? 'bg-white border border-[#e0e3e9]' : ''
              }`}
            >
              <p className="font-['Roboto:Regular',sans-serif] text-[14px] leading-[22px] text-[#282c33]" style={{ fontVariationSettings: "'wdth' 100" }}>
                {page}
              </p>
            </div>
          ))}
          <div className="w-[32px] h-[32px] rounded-[6px] flex items-center justify-center cursor-pointer">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
              <path d="M9 6L15 12L9 18" stroke="#1D2023" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </div>
        </div>
      </div>
    </div>
  );
}
