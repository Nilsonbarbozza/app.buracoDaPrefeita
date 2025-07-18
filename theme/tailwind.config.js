/** @type {import('tailwindcss').Config} */
module.exports = {
    content: [
      '../templates/**/*.html',
      './templates/**/*.html',
      './static/src/**/*.{js,css}',
    ],
    theme: {
      extend: {
        fontFamily: {
          raleway: ['Raleway', 'sans-serif'],
          opensans: ['Open Sans', 'sans-serif'],
        },
      },
    },
    plugins: [],
  }
  