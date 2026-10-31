/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        forest: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d',
          950: '#052e16',
        },
        earth: {
          50: '#fbfaf8',
          100: '#f6f4ee',
          200: '#ebe6dc',
          300: '#dbd3c2',
          400: '#c5b79f',
          500: '#ad9b7f',
          600: '#948166',
          700: '#776652',
          800: '#615344',
          900: '#504539',
        }
      },
    },
  },
  plugins: [],
}

