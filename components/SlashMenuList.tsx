import { forwardRef, useEffect, useImperativeHandle, useState } from 'react';

interface SlashMenuListProps {
  items: any[];
  command: (item: any) => void;
}

export const SlashMenuList = forwardRef((props: SlashMenuListProps, ref) => {
  const [selectedIndex, setSelectedIndex] = useState(0);

  const selectItem = (index: number) => {
    const item = props.items[index];
    if (item) {
      props.command(item);
    }
  };

  const upHandler = () => {
    setSelectedIndex((selectedIndex + props.items.length - 1) % props.items.length);
  };

  const downHandler = () => {
    setSelectedIndex((selectedIndex + 1) % props.items.length);
  };

  const enterHandler = () => {
    selectItem(selectedIndex);
  };

  useEffect(() => {
    setSelectedIndex(0);
  }, [props.items]);

  useImperativeHandle(ref, () => ({
    onKeyDown: ({ event }: { event: KeyboardEvent }) => {
      if (event.key === 'ArrowUp') {
        upHandler();
        return true;
      }

      if (event.key === 'ArrowDown') {
        downHandler();
        return true;
      }

      if (event.key === 'Enter') {
        enterHandler();
        return true;
      }

      return false;
    },
  }));

  return (
    <div className="bg-white content-stretch flex flex-col gap-[12px] items-start p-[24px] rounded-[12px] shadow-[0px_4px_24px_0px_rgba(0,0,0,0.12),0px_8px_16px_0px_rgba(0,0,0,0.08)] max-h-[300px] overflow-y-auto">
      {props.items.length > 0 ? (
        props.items.map((item, index) => (
          <div
            key={item.id}
            onClick={() => selectItem(index)}
            className={`content-stretch flex gap-[8px] h-[24px] items-center relative shrink-0 cursor-pointer px-[8px] rounded-[6px] w-full ${
              index === selectedIndex ? 'bg-[#f0f1f3]' : ''
            }`}
          >
            <div className="bg-[#f0f1f3] relative rounded-[6px] shrink-0 size-[24px]">
              <div className="content-stretch flex items-center justify-center overflow-clip relative rounded-[inherit] size-full">
                <div className="font-['MTS_Compact:Regular',sans-serif] text-[12px] text-[#505762]">
                  {item.icon}
                </div>
              </div>
              <div aria-hidden="true" className="absolute border border-[#d7d9dd] border-solid inset-0 pointer-events-none rounded-[6px]" />
            </div>
            <p className="font-['MTS_Compact:Regular',sans-serif] leading-[20px] not-italic relative shrink-0 text-[#1d2023] text-[14px] whitespace-nowrap">
              {item.title}
            </p>
          </div>
        ))
      ) : (
        <div className="text-[#969fa8] text-[14px] px-[8px]">Команды не найдены</div>
      )}
    </div>
  );
});

SlashMenuList.displayName = 'SlashMenuList';
