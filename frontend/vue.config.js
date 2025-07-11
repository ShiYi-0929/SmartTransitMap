// const { defineConfig } = require("@vue/cli-service");
//
// module.exports = defineConfig({
//   transpileDependencies: true,
//   lintOnSave: false,
//   devServer: {
//     port: 8080,
//     open: true,
//     proxy: {
//       "/api": {
//         target: "http://localhost:3000",
//         changeOrigin: true,
//         pathRewrite: {
//           "^/api": "/api",
//         },
//       },
//     },
//   },
//   css: {
//     loaderOptions: {
//       postcss: {
//         postcssOptions: {
//           plugins: [require("tailwindcss"), require("autoprefixer")],
//         },
//       },
//     },
//   },
// });




const { defineConfig } = require("@vue/cli-service");
const path = require('path');

module.exports = defineConfig({
  transpileDependencies: true,
  lintOnSave: false,
  configureWebpack: {
    resolve: {
      alias: {
        '@': path.resolve(__dirname, 'src')
      }
    }
  },
  devServer: {
    port: 8082,
    open: true,
    proxy: {
      "/api": {
        target: "http://localhost:8000",
        changeOrigin: true,
        logLevel: 'debug',
        pathRewrite: {
          "^/api": "/api",
        },
      },
    },
  },
  css: {
    loaderOptions: {
      postcss: {
        postcssOptions: {
          plugins: [require("tailwindcss"), require("autoprefixer")],
        },
      },
    },
  },
});
