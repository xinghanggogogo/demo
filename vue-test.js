//vue的双向绑定
//定义一个对象,定义一个模板,然后用vue绑定
var object = {
	message: 'Hello World!'
}

<div id="example">
	{{ message }}
</div>

new Vue({
	el: '#example',
	data: object
})
// 看上去和渲染模板没什么两样。
// 那么当我们改动了 object 时，
// 如何更新视图呢？
// 答案是... 你什么都不用做。Vue 已经把 object 对象改造成了一个响应式对象
// 这就是响应式的概念
--------
var example = new Vue({
	data: {
		a: 1
	},
	computed: {
		b: function () {
			return this.a + 1
		}
	}
})
// example 实例会同时代理 a 和 b 这两个属性.
example.a // -> 1
example.b // -> 2
example.a++
example.b // -> 3
--------
//在如何组织复杂界面的问题上，Vue 和 React 可以说是异曲同工：
//一切都是组件,可以把一开始的那个例子做成一个可复用的组件：

var Example = Vue.extend({
	template: '<div>{{ message }}</div>',
	data: function () {
		return {
			message: 'Hello Vue.js!'
		}
	}
})

// 将该组件注册为 <example> 标签
Vue.component('example', Example)
//这样一来我们就可以在其他组件的模板里这样使用它：
<example></example>
--------
//一个标准的vue组件,这就叫做vue的组件概念
<style>
.message {
	color: pink;
}
</style>

<template>
	<div class="message">{{ message }}</div>
</template>

<script>
export default {
	props: ['message'],
	created() {
		console.log('MyComponent created!')
	}
}
</script>
---------
//在自定义组件中定义另外一个自定义组件,且只是在父组件中调用
//先定义一个userdefine组件
var userdefined = Vue.extend({
	template:'<div>{{message}}</div><button v-on:click="doSom">ALERT</bitton>',
	 data:function(){
		return{
			message:'Sth'
		}
	},
	methods:{
		 doSom:function(){
			 alert('u click this!');
		 }
	}
});  
//又定义一个other组件
 var other =  Vue.extend({
		 template:'<div>other<u></u></div>',
		 components:{
				 "u":userdefined//包含上述定义的组件
		 }
 });
 //注册
Vue.component('other',other);
//挂载
new Vue({
 el:"#app"
})
----------
// Vue的目标是实现响应式的数据绑定和组合的视图组件
----------
// 关于slot(插槽)
//如果子组件模板不包含 <slot>,父组件的内容将被抛弃.如果子组件模板只有一个没有特性的 slot，父组件的整个内容将插到 slot 所在的地方并替换它。
<!-- parent.vue -->
<template>
		<div>
				<child>
					<p>This is some original content</p>
				</child>
		</div>
</template>
<script>
import child from './child'
export default {
		components: {
				child
		}
}
</script>

<!-- child.vue -->
<template>
		<div>
			<h1>This is my component!</h1>
			<slot>
				如果没有分发内容则显示我。
			</slot>
		</div>
</template>

<!-- 渲染结果 -->
<div>
		<div>
			<h1>This is my component!</h1>
			<p>This is some original content</p>
		</div>
</div>
-----------
// 具名slot
// 子组件模板
<div>
	<slot name="one"></slot>
	<slot></slot>
	<slot name="two"></slot>
</div>
父组件模板：

<multi-insertion>
	<p slot="one">One</p>
	<p slot="two">Two</p>
	<p>Default A</p>
</multi-insertion>
渲染结果

<div>
	<p slot="one">One</p>
	<p>Default A</p>
	<p slot="two">Two</p>
</div>
----------
//使用$emit传递事件
<!-- parent.vue -->
<template>
		<div>
				<child @child-ready="handler"></child>
		</div>
</template>
<script>
import child from './child'
export default {
		components: {
				child
		},
		methods: {
				handler (msg) {
						console.log(msg)
				} 
		}
}
</script>

<!-- child.vue -->
<template>
		<div>
				it's child.vue
		</div>
</template>

<script>
		export default {
				ready () {
						this.sayReady()
				},
				methods: {
						sayReady () {
								this.$emit('child-ready', 'Hello!')
						}
				}
		}
</script>
