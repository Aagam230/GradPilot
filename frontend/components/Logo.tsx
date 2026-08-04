export function LogoMark({ size = 28 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
      <circle cx="16" cy="16" r="14" stroke="rgb(var(--accent))" strokeWidth="2" opacity="0.35" />
      <path
        d="M16 4C9.373 4 4 9.373 4 16"
        stroke="rgb(var(--accent))"
        strokeWidth="2.4"
        strokeLinecap="round"
      />
      <circle cx="4" cy="16" r="2.2" fill="rgb(var(--accent))" />
      <path d="M16 11.5L20.5 16L16 20.5L11.5 16L16 11.5Z" fill="rgb(var(--accent))" />
    </svg>
  );
}

export function Logo({ size = 24 }: { size?: number }) {
  return (
    <div className="flex items-center gap-2">
      <LogoMark size={size} />
      <span className="font-semibold tracking-tight text-[17px]">GradPilot</span>
    </div>
  );
}
