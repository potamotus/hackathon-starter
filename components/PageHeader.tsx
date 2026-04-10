import svgPaths from "../../imports/svg-apd2yk5peo";

export function PageHeader({ title, description }: { title: string; description: string }) {
  return (
    <div className="relative shrink-0 w-full">
      <div aria-hidden="true" className="absolute border-[#e0e0e0] border-b border-solid inset-0 pointer-events-none" />
      <div className="content-stretch flex gap-[6px] items-start p-[16px] relative w-full">
        <div className="relative shrink-0 size-[16px]">
          <svg className="absolute block size-full" fill="none" preserveAspectRatio="none" viewBox="0 0 16 16">
            <g id="Frame 7">
              <path d={svgPaths.p7dd97b0} fill="var(--fill-0, #7B67EE)" id="Vector 2 (Stroke)" />
            </g>
          </svg>
        </div>
        <div className="content-stretch flex flex-col font-['MTS_Compact:Regular',sans-serif] gap-[6px] items-start justify-center leading-[20px] not-italic relative shrink-0 text-[14px] whitespace-nowrap">
          <p className="relative shrink-0 text-[#1d2023]">{title}</p>
          <p className="relative shrink-0 text-[#969fa8]">{description}</p>
        </div>
      </div>
    </div>
  );
}
