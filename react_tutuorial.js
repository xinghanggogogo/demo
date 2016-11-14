-------------
//复合组件
//上面例子中，Avatar 拥有 ProfilePic 和 ProfileLink 的实例。
//拥有者 就是给其它组件设置 props 的那个组件。更正式地说， 如果组件 Y 在 render() 方法是创建了组件 X，那么 Y 就拥有 X。
//上面讲过，组件不能修改自身的 props - 它们总是与它们拥有者设置的保持一致。
//这是保持用户界面一致性的关键性原则。
var Avatar = React.createClass({
	render: function() {
		return (
			<div>
				<ProfilePic username={this.props.username} />
				<ProfileLink username={this.props.username} />
			</div>
		);
	}
});

var ProfilePic = React.createClass({
	render: function() {
		return (
			<img src={'http://graph.facebook.com/' + this.props.username + '/picture'} />
		);
	}
});

var ProfileLink = React.createClass({
	render: function() {
		return (
			<a href={'http://www.facebook.com/' + this.props.username}>
				{this.props.username}
			</a>
		);
	}
});

React.render(
	<Avatar username="pwh" />,
	document.getElementById('example')
);

----------------------
//组件复用

//prop验证
var title = "菜鸟教程";
var MyTitle = React.createClass({
	propTypes: {
		title: React.PropTypes.string.isRequired,
	},

	render: function() {
		 return <h1> {this.props.title} </h1>;
	 }
});
ReactDOM.render(
		<MyTitle title={title} />,
		document.getElementById('example')
);

//prop验证2
var MyComponent = React.createClass({
	propTypes: {
		children: React.PropTypes.element.isRequired
	},

	render: function() {
		return (
			<div>
				{this.props.children} // 有且仅有一个元素，否则会抛异常。
			</div>
		);
	}

});

//默认prop
// 当父级没有传入 props 时，getDefaultProps() 可以保证 this.props.value 有默认值，注意 getDefaultProps 的结果会被 缓存。
// 得益于此，你可以直接使用 props，而不必写手动编写一些重复或无意义的代码
var ComponentWithDefaultProps = React.createClass({
	getDefaultProps: function() {
		return {
			value: 'default value'
		};
	}
	/* ... */
});

//一种传递prop的方式
var CheckLink = React.createClass({
	render: function() {
		return <a {...this.props}>{'√ '}{this.props.children}</a>;
	}
});

React.render(
	<CheckLink href="/checked.html">
		Click here!
	</CheckLink>,
	document.getElementById('example')
);

//关于mixin
var SetIntervalMixin = {
	componentWillMount: function() {
		this.intervals = [];
	},
	setInterval: function() {
		this.intervals.push(setInterval.apply(null, arguments));
	},
	componentWillUnmount: function() {
		this.intervals.map(clearInterval);
	}
};

var TickTock = React.createClass({
	mixins: [SetIntervalMixin], // 引用 mixin
	getInitialState: function() {
		return {seconds: 0};
	},
	componentDidMount: function() {
		this.setInterval(this.tick, 1000); // 调用 mixin 的方法
	},
	tick: function() {
		this.setState({seconds: this.state.seconds + 1});
	},
	render: function() {
		return (
			<p>
				React has been running for {this.state.seconds} seconds.
			</p>
		);
	}
});

React.render(
	<TickTock />,
	document.getElementById('example')
);
