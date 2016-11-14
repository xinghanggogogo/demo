模块加载器兼打包工具，把各种资源，例如JS（含JSX）、coffee、样式（含less/sass）、图片等都作为模块来使用和处理;
简而言之,打包并加载模块
可以直接使用 require(XXX) 的形式来引入各模块，即使它们可能需要经过编译（比如JSX和sass）
 webpack 有着各种健全的加载器（loader）来实现编译
 webpack由commonJS的形式来书写
 不仅仅能模块化js,比如打包、压缩混淆、图片转base64等
 --------
 var someModule = require("someModule");
 var anotherModule = require("anotherModule");    
 
 someModule.doTehAwesome();
 anotherModule.doMoarAwesome();
 
 exports.asplode = function (){
				someModule.doTehAwesome();
				anotherModule.doMoarAwesome();
 };
 --------
 一个通用的配置:
var webpack = require('webpack');
var commonsPlugin = new webpack.optimize.CommonsChunkPlugin('common.js');
 
module.exports = {
		//插件项
		plugins: [commonsPlugin],
		//页面入口文件配置
		entry: {
				index : './src/js/page/index.js'
		},
		//入口文件输出配置
		output: {
				path: 'dist/js/page',
				filename: '[name].js'
		},
		module: {
				//加载器配置
				loaders: [
						{ test: /\.css$/, loader: 'style-loader!css-loader' },
						{ test: /\.js$/, loader: 'jsx-loader?harmony' },
						{ test: /\.scss$/, loader: 'style!css!sass?sourceMap'},
						{ test: /\.(png|jpg)$/, loader: 'url-loader?limit=8192'}
				]
		},
		//解决方案配置
		resolve: {
			       //查找module的话从这里开始查找
				root: 'E:/github/flux-example/src', //绝对路径
				//自动扩展文件后缀名，意味着我们require模块可以省略不写后缀名
				extensions: ['', '.js', '.json', '.scss'],
				//模块别名定义，方便后续直接引用别名，无须多写长长的地址
				//后续直接 require('AppStores') 即可
				alias: {
						AppStore : 'js/stores/AppStores.js',
						ActionType : 'js/actions/ActionType.js',
						AppAction : 'js/actions/AppAction.js'
				}
		}
};
--------
//一般使用,直接在页面引入 webpack 最终生成的页面脚本即可，
//不用再写什么 data-main 或 seajs.use 了
//样式不用引入，脚本执行时会动态生成<style>并标签打到head里
// <html>
// <head lang="en">
//   	<meta charset="UTF-8">
//   	<title>demo</title>
// </head>
// <body>
//   	<script src="dist/js/page/common.js"></script>
//   	<script src="dist/js/page/index.js"></script>
// </body>
// </html>
