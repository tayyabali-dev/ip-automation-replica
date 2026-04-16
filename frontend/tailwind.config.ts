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
          50: '#FEE2E2',
          100: '#FECACA',
          200: '#FCA5A5',
          300: '#F87171',
          400: '#EF4444',
          500: '#DC0A2D', // Pokemon Red (Pokeball)
          600: '#B91C1C',
          700: '#991B1B',
          800: '#7F1D1D',
          900: '#450A0A',
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
        // Pokemon accents
        pokemon: {
          red: '#DC0A2D',      // Pokeball red
          yellow: '#FFCB05',   // Pikachu yellow
          blue: '#3B4CCA',     // Pokemon blue
          white: '#FFFFFF',    // Pokeball white
          electric: '#F7D02C', // Electric type
          fire: '#FF9C54',     // Fire type
          water: '#4A90E2',    // Water type
          grass: '#78C850',    // Grass type
        },
        pikachu: '#FFCB05',
        pokeball: '#DC0A2D',
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
        'pokemon-glow': '0 0 15px rgba(220, 10, 45, 0.3), 0 0 30px rgba(220, 10, 45, 0.1)',
        'pikachu-glow': '0 0 15px rgba(255, 203, 5, 0.4), 0 0 30px rgba(255, 203, 5, 0.2)',
        'pokeball-glow': '0 0 15px rgba(220, 10, 45, 0.4)',
        'electric-glow': '0 0 20px rgba(247, 208, 44, 0.5)',
        'fire-glow': '0 0 15px rgba(255, 156, 84, 0.4)',
        'water-glow': '0 0 15px rgba(74, 144, 226, 0.4)',
        'grass-glow': '0 0 15px rgba(120, 200, 80, 0.4)',
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
