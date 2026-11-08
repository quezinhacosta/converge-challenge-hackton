/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/**/*.{html,ts}",
  ],
  theme: {
    extend: {colors:{indigo:{50:'#f2ebff',100:'#ede5ff',200:'#e5d9fb',300:'#cbb3fa',400:'#a375f4',500:'#7d39eb',600:'#6429cc',700:'#5122a7',800:'#3c2469',900:'#211439'}}},
  },
  plugins: [],
}
