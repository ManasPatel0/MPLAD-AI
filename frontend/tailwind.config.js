/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        gov: {
          navy: {
            DEFAULT: '#0F172A',
            dark: '#0A0F1D',
            light: '#1E293B',
            muted: '#334155',
          },
          saffron: {
            DEFAULT: '#D97706',
            light: '#F59E0B',
            soft: '#FEF3C7',
          },
          green: {
            DEFAULT: '#059669',
            light: '#10B981',
            soft: '#D1FAE5',
          },
          chakra: {
            DEFAULT: '#1D4ED8',
            light: '#3B82F6',
            soft: '#EFF6FF',
          },
        },
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', '-apple-system', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
