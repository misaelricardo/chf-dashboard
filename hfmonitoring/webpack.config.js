const path = require('path');

module.exports = {
  mode: 'development', // or 'production' for optimized build
  entry: './static/js/main.js',
  output: {
    filename: 'bundle.js',
    path: path.resolve(__dirname, 'static/dist'),
  },
  module: {
    rules: [
      {
        test: /\.js$/,
        exclude: /node_modules/,
        use: {
          loader: 'babel-loader', // optional, only if you're using ES6+
        },
      },
    ],
  },
};