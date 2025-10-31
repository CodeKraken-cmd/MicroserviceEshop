/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html","./src/**/*.{ts,tsx}"],
  theme: { extend: { colors: { brand: { 600: "#4f46e5", 700:"#4338ca" } } } },
  plugins: []
}
