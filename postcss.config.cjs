// Root-level fallback for tools that resolve PostCSS from the workspace root.
module.exports = {
  plugins: {
    tailwindcss: { config: './frontend/tailwind.config.js' },
    autoprefixer: {},
  },
};
