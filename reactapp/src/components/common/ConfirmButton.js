import React, { Component } from 'react'

export default class ConfirmButton extends Component {
    constructor(props) {
        super(props)
        this.state = {
            counter: 0
        }
    }

    handleClick(e) {
        if (this.state.counter === 0) {
            this.setState(
                { counter: this.props.count || 5 }
            )
            this.interval = setInterval(this.tick.bind(this), 1000)
        } else {
            clearInterval(this.interval)
            this.props.onClick(e)
        }
    }

    tick() {
        var counter = this.state.counter - 1;
        this.setState(
            { counter: counter }
        )
        if (counter === 0) {
            clearInterval(this.interval);
            this.interval = null;
        }
    }

    render() {
        return (
            <button type="button" onClick={this.handleClick.bind(this)} className={this.props.className}>
                {this.props.children} { this.state.counter === 0 ? '' : '(' + this.state.counter + ')' }
            </button>
        )
    }
}