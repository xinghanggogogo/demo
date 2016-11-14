//react-route-tutorial
import React from 'react'
import { Router, Route, Link } from 'react-router'

const App = React.createClass({/*...*/})

const About = React.createClass({/*...*/})

const Users = React.createClass({
	render() {
		return (
			<div>
				<h1>Users</h1>
				<div className="master">
					<ul>
						{/* 在应用中用 Link 去链接路由 */}
						{this.state.users.map(user => (
							<li key={user.id}><Link to={`/user/${user.id}`}>{user.name}</Link></li>
						))}
					</ul>
				</div>
				<div className="detail">
					{this.props.children}
				</div>
			</div>
		)
	}
})

const User = React.createClass({
	componentDidMount() {
		this.setState({
			// 路由应该通过有用的信息来呈现，例如 URL 的参数
			user: findUserById(this.props.params.userId)
		})
	},

	render() {
		return (
			<div>
				<h2>{this.state.user.name}</h2>
			</div>
		)
	}
})

React.render((
	<Router>
		<Route path="/" component={App}>
			<Route path="about" component={About}/>
			<Route path="users" component={Users}>
				<Route path="/user/:userId" component={User}/>
			</Route>
			<Route path="*" component={NoMatch}/>
		</Route>
	</Router>
), document.body)
-------------
//tutorial-2
import React from 'react'
import { Router, Route, Link } from 'react-router'

const App = React.createClass({
	render() {
		return (
			<div>
				<h1>App</h1>
				<ul>
					<li><Link to="/about">About</Link></li>
					<li><Link to="/inbox">Inbox</Link></li>
				</ul>
				{this.props.children}
			</div>
		)
	}
})

const About = React.createClass({
	render() {
		return <h3>About</h3>
	}
})

const Inbox = React.createClass({
	render() {
		return (
			<div>
				<h2>Inbox</h2>
				{this.props.children || "Welcome to your Inbox"}
			</div>
		)
	}
})

const Message = React.createClass({
	render() {
		return <h3>Message {this.props.params.id}</h3>
	}
})

React.render((
	<Router>
		<Route path="/" component={App}>
			<Route path="about" component={About} />
			<Route path="inbox" component={Inbox}>
				<Route path="messages/:id" component={Message} />
			</Route>
		</Route>
	</Router>
), document.body)

/*
URL								组件
/									App
/about							App -> About
/inbox							App -> Inbox
/inbox/messages/:id	App -> Inbox -> Message
*/
--------------------
//上边的例子,试想,直接访问/,this.prop.children并没有定义所以,设置一个默认的组件
import { IndexRoute } from 'react-router'

const Dashboard = React.createClass({
	render() {
		return <div>Welcome to the app!</div>
	}
})

React.render((
	<Router>
		<Route path="/" component={App}>
			{/* 当 url 为/时渲染 Dashboard */}
			<IndexRoute component={Dashboard} />
			<Route path="about" component={About} />
			<Route path="inbox" component={Inbox}>
				<Route path="messages/:id" component={Message} />
			</Route>
		</Route>
	</Router>
), document.body)