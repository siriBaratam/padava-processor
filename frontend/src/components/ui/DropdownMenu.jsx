/**
 * Custom Dropdown Menu — mirrors Radix UI's API surface.
 * Uses React state + CSS transitions; no extra dependency required.
 */
import React, { useState, useRef, useEffect, createContext, useContext } from 'react';

const DropdownContext = createContext(null);

export function DropdownMenu({ children }) {
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  useEffect(() => {
    function handleClickOutside(e) {
      if (ref.current && !ref.current.contains(e.target)) setOpen(false);
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <DropdownContext.Provider value={{ open, setOpen }}>
      <div ref={ref} className="relative inline-block">
        {children}
      </div>
    </DropdownContext.Provider>
  );
}

export function DropdownMenuTrigger({ children, asChild }) {
  const { open, setOpen } = useContext(DropdownContext);
  const child = asChild ? React.Children.only(children) : null;

  if (asChild && child) {
    return React.cloneElement(child, {
      onClick: (e) => {
        setOpen((v) => !v);
        child.props.onClick?.(e);
      },
      'aria-expanded': open,
      'aria-haspopup': 'menu',
    });
  }

  return (
    <button
      type="button"
      onClick={() => setOpen((v) => !v)}
      aria-expanded={open}
      aria-haspopup="menu"
    >
      {children}
    </button>
  );
}

export function DropdownMenuContent({ children, align = 'end', className = '' }) {
  const { open } = useContext(DropdownContext);

  const alignClass =
    align === 'end' ? 'right-0' : align === 'start' ? 'left-0' : 'left-1/2 -translate-x-1/2';

  return (
    <div
      role="menu"
      className={`
        absolute top-full mt-2 z-50 min-w-[180px]
        bg-[#0f1923]/95 backdrop-blur-xl
        border border-white/10 rounded-xl shadow-2xl shadow-black/40
        overflow-hidden
        transition-all duration-200 origin-top
        ${open ? 'opacity-100 scale-y-100 pointer-events-auto' : 'opacity-0 scale-y-95 pointer-events-none'}
        ${alignClass}
        ${className}
      `}
    >
      {children}
    </div>
  );
}

export function DropdownMenuLabel({ children, className = '' }) {
  return (
    <div className={`px-3 py-2 text-[10px] font-mono tracking-widest text-white/40 uppercase ${className}`}>
      {children}
    </div>
  );
}

export function DropdownMenuSeparator({ className = '' }) {
  return <div className={`h-px bg-white/10 mx-2 my-1 ${className}`} />;
}

export function DropdownMenuItem({ children, onClick, className = '', variant = 'default' }) {
  const { setOpen } = useContext(DropdownContext);

  const variantClass =
    variant === 'destructive'
      ? 'text-red-400 hover:bg-red-500/15 hover:text-red-300'
      : 'text-white/80 hover:bg-white/10 hover:text-white';

  return (
    <button
      role="menuitem"
      type="button"
      onClick={() => {
        onClick?.();
        setOpen(false);
      }}
      className={`
        w-full text-left flex items-center gap-2.5 px-3 py-2.5
        text-sm font-medium
        transition-colors duration-150 cursor-pointer
        ${variantClass}
        ${className}
      `}
    >
      {children}
    </button>
  );
}
