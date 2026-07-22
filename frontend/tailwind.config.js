/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        ops: {
          bg: '#F2F4F3',
          surface: '#FAFBFA',
          sunken: '#EAEDEC',
          border: '#DCE1DF',
          ink: '#10201E',
          secondary: '#4B5A57',
          teal: '#0E6E6A',
          tealDim: '#E4EFEE',
          critical: '#B23A2E',
          criticalBg: '#F7E9E6',
          warning: '#B07A2C',
          warningBg: '#F5EDDF',
          safe: '#276A4E',
          safeBg: '#E4EEE8',
          navy: '#2B4C6F',
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['"JetBrains Mono"', 'monospace'],
      },
      animation: {
        'breathe': 'breathe 2s ease-in-out infinite',
        'pulse-banner': 'pulseBanner 2.5s ease-in-out infinite',
        'ticker': 'ticker 35s linear infinite',
      },
      keyframes: {
        breathe: {
          '0%, 100%': { opacity: '0.6' },
          '50%': { opacity: '1' },
        },
        pulseBanner: {
          '0%, 100%': { opacity: '0.7' },
          '50%': { opacity: '1' },
        },
        ticker: {
          '0%': { transform: 'translateX(0%)' },
          '100%': { transform: 'translateX(-50%)' },
        }
      }
    },
  },
  plugins: [],
};
