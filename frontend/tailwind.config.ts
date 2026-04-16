import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: 'class',
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#FFF9E6',
          100: '#FFF3CC',
          200: '#FFE799',
          300: '#FFDB66',
          400: '#FFCF33',
          500: '#FDB913', // Batman Yellow (Bat Signal)
          600: '#E6A711',
          700: '#CC940F',
          800: '#B3820D',
          900: '#99700B',
        },
        neutral: {
          50: '#F9FAFB',
          100: '#F5F5F5',
          200: '#E5E5E5',
          300: '#D4D4D4',
          400: '#A3A3A3',
          500: '#737373',
          600: '#525252',
          700: '#404040',
          800: '#262626',
          900: '#171717',
          950: '#0a0a0a',
        },
        // Batman/Gotham accents
        batman: {
          yellow: '#FDB913',    // Bat Signal yellow
          black: '#0A0A0A',     // Batman black
          gray: '#2D2D2D',      // Batsuit gray
          darkBlue: '#1A1F2E',  // Gotham night
          steel: '#5A6C7D',     // Steel/tech
          gold: '#D4AF37',      // Gold accent
        },
        gotham: '#1A1F2E',
        batSignal: '#FDB913',
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        serif: ['Newsreader', 'Georgia', 'serif'],
      },
      borderRadius: {
        '2xl': '1rem',
        '3xl': '1.5rem',
      },
      boxShadow: {
        'soft': '0 2px 10px -4px rgba(0, 0, 0, 0.05)',
        'card': '0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.03)',
        'bat-signal': '0 0 20px rgba(253, 185, 19, 0.4), 0 0 40px rgba(253, 185, 19, 0.2)',
        'bat-glow': '0 0 15px rgba(253, 185, 19, 0.5), 0 0 30px rgba(253, 185, 19, 0.3)',
        'gotham-glow': '0 0 15px rgba(26, 31, 46, 0.6)',
        'dark-steel': '0 0 10px rgba(90, 108, 125, 0.3)',
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out forwards',
        'slide-up': 'slideUp 0.4s ease-out forwards',
        'twinkle': 'twinkle 3s ease-in-out infinite',
        'float': 'float 6s ease-in-out infinite',
        'hyperspace': 'hyperspace 0.8s ease-in forwards',
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0', transform: 'translateY(10px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          '0%': { opacity: '0', transform: 'translateY(20px)' },
          '100%': { opacity: '1', transform: 'translateY(0)' },
        },
        twinkle: {
          '0%, 100%': { opacity: '0.3' },
          '50%': { opacity: '1' },
        },
        float: {
          '0%, 100%': { transform: 'translateY(0px)' },
          '50%': { transform: 'translateY(-10px)' },
        },
        hyperspace: {
          '0%': { transform: 'scale(1)', opacity: '1' },
          '100%': { transform: 'scale(20)', opacity: '0' },
        },
      },
    },
  },
  plugins: [],
};
export default config;
