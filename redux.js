import { createStore } from 'redux';
 //这是一个 reducer，形式为 (state, action) => state 的纯函数。
 //描述了 action 如何把 state 转变成下一个 state。
 function counter(state = 0, action) {
	switch (action.type) {
	case 'INCREMENT':
		return state + 1;
	case 'DECREMENT':
		return state - 1;
	default:
		return state;
	}
}

let store = createStore(counter);
store.subscribe(() =>
	console.log(store.getState())
);

store.dispatch({ type: 'INCREMENT' });
store.dispatch({ type: 'INCREMENT' });
store.dispatch({ type: 'DECREMENT' });
--------------------
function inc() {
	return { type: 'INCREMENT' };
}
function dec() {
	return { type: 'DECREMENT' };
}

function reducer(state, action) {
	state = state || { counter: 0 };

	switch (action.type) {
		case 'INCREMENT':
			return { counter: state.counter + 1 };
		case 'DECREMENT':
			return { counter: state.counter - 1 };
		default:
			return state; // 无论如何都返回一个 state
	}
}

var store = Redux.createStore(reducer);

console.log( store.getState() ); // { counter: 0 }

store.dispatch(inc());
console.log( store.getState() ); // { counter: 1 }

store.dispatch(inc());
console.log( store.getState() ); // { counter: 2 }

store.dispatch(dec());
console.log( store.getState() ); // { counter: 1 }
