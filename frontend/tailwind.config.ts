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
          50: '#FFE5E8',
          100: '#FFCCD1',
          200: '#FF99A3',
          300: '#FF6675',
          400: '#FF3347',
          500: '#CE1126', // Superman Red
          600: '#B50E21',
          700: '#9C0C1C',
          800: '#830917',
          900: '#6A0712',
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
        // Superman/Metropolis accents
        superman: {
          red: '#CE1126',       // Superman red
          blue: '#0476F2',      // Superman blue
          yellow: '#FCD116',    // S shield yellow
          gold: '#FFD700',      // Gold accent
          sky: '#87CEEB',       // Sky blue
          white: '#FFFFFF',     // Clean white
        },
        metropolis: '#0476F2',
        sShield: '#FCD116',
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
        'super-glow': '0 0 20px rgba(206, 17, 38, 0.4), 0 0 40px rgba(206, 17, 38, 0.2)',
        'hero-glow': '0 0 15px rgba(4, 118, 242, 0.5), 0 0 30px rgba(4, 118, 242, 0.3)',
        'hope-glow': '0 0 15px rgba(252, 209, 22, 0.6), 0 0 30px rgba(252, 209, 22, 0.4)',
        'metropolis-glow': '0 0 10px rgba(4, 118, 242, 0.3)',
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
