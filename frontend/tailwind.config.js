/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        vytal: {
          black: "#0A0A0C",
          dark: "#121118",
          surface: "#18181F",
          purple: "#7C3AED",
          purpleLight: "#8B5CF6",
          purpleDeep: "#4C1D95",
          lime: "#CCFF00",
          limeMuted: "#A3E635",
        },
      },
      fontFamily: {
        sans: ["'Plus Jakarta Sans'", "Inter", "-apple-system", "BlinkMacSystemFont", "sans-serif"],
        mono: ["'JetBrains Mono'", "monospace"],
      },
      boxShadow: {
        'neon-purple': '0 0 25px rgba(124, 58, 237, 0.25)',
        'neon-lime': '0 0 25px rgba(204, 255, 0, 0.35)',
        'glass': '0 8px 32px 0 rgba(0, 0, 0, 0.37)',
      },
    },
  },
  plugins: [],
}
