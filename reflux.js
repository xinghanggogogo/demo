//定义了四个action
var TodoActions = Reflux.createActions([
	'getAll',
	'addItem',
	'deleteItem',
	'updateItem'
]);
//定义了一个store
var TodoStore = Reflux.createStore({
	items: [1, 2, 3],
	listenables: [TodoActions],	//将store还有action绑定起来
	//响应action,注意首字母大写
	onGetAll: function () {
		$.get('/all', function (data) {
			this.items = data;
			this.trigger(this.items);
		}.bind(this));
	},
	onAddItem: function (model) {
		$.post('/add', model, function (data) {
			this.items.unshift(data);
			this.trigger(this.items);
		}.bind(this));
	},
	onDeleteItem: function (model, index) {
		$.post('/delete', model, function (data) {
			this.items. (index, 1);
			this.trigger(this.items);
		}.bind(this));
	},
	onUpdateItem: function (model, index) {
		$.post('/update', model, function (data) {
			this.items[index] = data;
			this.trigger(this.items);
		}.bind(this));
	}
});
//定义react组件
var TodoComponent = React.createClass({
	//mixins: [Reflux.connect(TodoStore, 'list')] 将Store和组件关联起来，
	//这样该组件 state 上的 list 就和 TodoStore这个Store 连接起来了。
	//当 state.list 变化之后， render 方法就会被自动调用。
	mixins: [Reflux.connect(TodoStore, 'list')],
	getInitialState: function () {
		return {list: []};
	},
	componentDidMount: function () {
		TodoActions.getAll();
	},   
	render: function () {
		return (
			<div>
				{this.state.list.map(function(item){
					return <TodoItem data={item}/>
				})}
			</div>
		)
	}
});
//又一个react组件
var TodoItem = React.createClass({
	componentDidMount: function () {
		TodoActions.getAll();
	},
	handleAdd: function (model) {
		TodoActions.addItem(model);
	},
	handleDelete: function (model,index) {
		TodoActions.deleteItem(model,index);
	},
	handleUpdate: function (model) {
		TodoActions.updateItem(model);
	},
	render: function () {
		var item=this.props.data;
		return (
			<div>
				<p>{item.name}</p>
				<p>{item.email}</p>
				<p>/*操作按钮*/</p>
			</div>
		)
	}
});
React.render(<TodoComponent />, document.getElementById('container'));
--------------------
