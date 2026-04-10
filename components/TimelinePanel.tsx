import { X, Clock } from 'lucide-react';

interface TimelinePanelProps {
  isOpen: boolean;
  onClose: () => void;
}

export function TimelinePanel({ isOpen, onClose }: TimelinePanelProps) {
  if (!isOpen) return null;

  const mockVersions = [
    {
      id: 1,
      action: 'Действие',
      date: '2025-11-14 15:53:57',
      user: 'Константин Иванов',
    },
    {
      id: 2,
      action: 'Действие',
      date: '2025-11-14 15:53:57',
      user: 'Константин Иванов',
    },
    {
      id: 3,
      action: 'Действие',
      date: '2025-11-14 15:53:57',
      user: 'Константин Иванов',
    },
    {
      id: 4,
      action: 'Действие',
      date: '2025-11-14 15:53:57',
      user: 'Константин Иванов',
    },
    {
      id: 5,
      action: 'Действие',
      date: '2025-11-14 15:53:57',
      user: 'Константин Иванов',
    },
  ];

  return (
    <div className="fixed right-0 top-0 h-full w-[320px] bg-[#f6f7fa] shadow-lg z-50 rounded-[12px] m-[16px] border border-[#e0e3e9]">
      <div className="flex flex-col h-full overflow-hidden rounded-[12px]">
        {/* Header */}
        <div className="border-b border-[#e0e3e9] p-[16px] flex items-center justify-between">
          <p className="font-['Roboto:SemiBold',sans-serif] font-semibold text-[16px] leading-[24px] text-[#282c33]" style={{ fontVariationSettings: "'wdth' 100" }}>
            Машина времени
          </p>
          <button onClick={onClose} className="cursor-pointer">
            <X size={16} className="text-[#6d7482]" />
          </button>
        </div>

        {/* Versions List */}
        <div className="flex-1 overflow-y-auto p-[8px]">
          {mockVersions.map((version, index) => (
            <div
              key={version.id}
              className={`px-[12px] py-[8px] flex flex-col gap-[4px] ${
                index === 1 ? 'bg-white rounded-[8px]' : ''
              } cursor-pointer`}
            >
              <p className="font-['Roboto:Regular',sans-serif] text-[14px] leading-[22px] text-[#282c33]" style={{ fontVariationSettings: "'wdth' 100" }}>
                {version.action}
              </p>
              <div className="flex items-center justify-between">
                <p className="font-['Roboto:Regular',sans-serif] text-[12px] leading-[18px] text-[#6d7482]" style={{ fontVariationSettings: "'wdth' 100" }}>
                  {version.date}
                </p>
                <div className="flex items-center gap-[6px]">
                  <p className="font-['Roboto:Regular',sans-serif] text-[12px] leading-[18px] text-[#6d7482]" style={{ fontVariationSettings: "'wdth' 100" }}>
                    {version.user}
                  </p>
                  <div className="w-[16px] h-[16px] rounded-full bg-[#56CDFF] flex items-center justify-center text-white font-['Roboto:Regular',sans-serif] text-[8px]" style={{ fontVariationSettings: "'wdth' 100" }}>
                    И
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

export function TimelinePanelToggle({ onToggle, isOpen }: { onToggle: () => void; isOpen: boolean }) {
  return (
    <button
      onClick={onToggle}
      className={`flex items-center justify-center gap-[5px] px-[8px] h-[24px] rounded-[4px] cursor-pointer ${
        isOpen ? 'bg-[#7b67ee] text-white' : 'bg-[#f0f1f3] text-[#505762]'
      }`}
    >
      <Clock size={14} />
      <p className="font-['Roboto:Regular',sans-serif] text-[13px] leading-[20px]" style={{ fontVariationSettings: "'wdth' 100" }}>
        Машина времени
      </p>
    </button>
  );
}
