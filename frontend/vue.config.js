const { defineConfig } = require('@vue/cli-service');
const CssMinimizerPlugin = require('css-minimizer-webpack-plugin');


module.exports = defineConfig({
  transpileDependencies: true,
  devServer: {
    port: 3001,
  },
  configureWebpack: {
    optimization: {
      minimize: false,
      minimizer: [new CssMinimizerPlugin()],
    },
  },
});