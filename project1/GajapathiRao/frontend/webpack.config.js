const path = require("path");
const HtmlWebpackPlugin = require("html-webpack-plugin");

module.exports = {
    entry: "./src/main.jsx",

    output: {
        path: path.resolve(__dirname, "dist"),
        filename: "bundle.js",
        clean: true,
    },

   module: {
    rules: [
        {
            test: /\.(js|jsx)$/,
            exclude: /node_modules/,
            type: "javascript/auto",
            use: {
                loader: "babel-loader",
            },
        },
        {
            test: /\.scss$/,
            use: [
                "style-loader",
                "css-loader",
                "sass-loader",
            ],
        },
    ],
},

    resolve: {
        extensions: [".js", ".jsx"],
    },

    plugins: [
        new HtmlWebpackPlugin({
            template: "./index.html",
        }),
    ],

    devServer: {
        host: "0.0.0.0",
        port: 3000,
        hot: true,
        liveReload: true,
        historyApiFallback: true,
        static: {
            directory: path.resolve(__dirname, "dist"),
        },
        devMiddleware: {
            publicPath: "/",
        },
        client: {
            overlay: false,
        },
    },
};