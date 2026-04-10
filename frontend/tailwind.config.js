/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // MWS Design Kit colors
        primary: {
          DEFAULT: '#7b67ee',
          hover: '#6952d9',
        },
        mws: {
          blue: '#0070e5',
          gray: {
            50: '#f6f7fa',
            100: '#f0f1f3',
            200: '#e0e3e9',
            300: '#d7d9dd',
            400: '#6d7482',
            500: '#505762',
            600: '#282c33',
            700: '#1d2023',
          }
        }
      },
      fontFamily: {
        'mts': ['MTS Compact', 'Roboto', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
