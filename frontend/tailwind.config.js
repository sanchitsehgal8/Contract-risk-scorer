export default {
  content: [
    "./index.html",
    "./src/**/*.{js,jsx}",
  ],
  theme: {
    extend: {
      colors: {
        bg: '#0A0A0F',
        surface: '#111118',
        'surface-high': '#16161F',
        border: '#1E1E2E',
        blue: 'rgb(59 130 246 / <alpha-value>)',
        'blue-light': 'rgb(96 165 250 / <alpha-value>)',
        critical: '#EF4444',
        high: '#F97316',
        medium: '#EAB308',
        low: '#22C55E',
        text: '#F1F0FF',
        muted: '#6B7280',
        subtle: '#374151',
      },
      fontFamily: {
        inter: ['Inter', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      backdropBlur: {
        xs: '2px',
        sm: '4px',
        md: '8px',
        lg: '12px',
      }
    },
  },
  plugins: [],
}
