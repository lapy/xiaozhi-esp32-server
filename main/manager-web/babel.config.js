module.exports = {
  presets: [
    ['@vue/cli-plugin-babel/preset', {
      useBuiltIns: 'usage',
      corejs: 3
    }]
  ],
  plugins: [
    '@babel/plugin-syntax-dynamic-import',  // Ensure support for dynamic imports (Lazy Loading)
    '@babel/plugin-transform-runtime'
  ]
}
