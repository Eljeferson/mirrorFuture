/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: 'class',
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
        brand: ['"Century Gothic"', 'Outfit', 'Montserrat', 'sans-serif'],
      },
      colors: {
        flame: {
          400: '#FF7A29',
          500: '#FF5500',
          600: '#E64A00',
          700: '#CC3D00',
        },
        ceramic: {
          50: '#FAF9F6',
          100: '#F4F4F6',
          200: '#EAEAEB',
          300: '#E0E0E4',
          400: '#D2D2D8',
        },
        obsidian: {
          800: '#27272A',
          900: '#18181B',
          950: '#09090B',
        },
        gold: {
          400: '#facc15',
          500: '#eab308',
          600: '#ca8a04',
          700: '#a16207',
        },
        primary: {
          50: '#f0f9ff',
          100: '#e0f2fe',
          500: '#0ea5e9',
          600: '#0284c7',
          700: '#0369a1',
        },
        slate: {
          850: '#151f32',
          900: '#0f172a',
          950: '#030712',
        }
      }
    },
  },
  plugins: [],
}
