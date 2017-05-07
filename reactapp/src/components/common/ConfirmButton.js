import React, { Component } from 'react'
import PropTypes from 'prop-types'

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
            this.setState({
                counter: 0
            })
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
            <button type={this.props.buttonType} onClick={this.handleClick.bind(this)} className={this.props.className}>
                {this.props.children} { this.state.counter === 0 ? '' : '(' + this.state.counter + ')' }
            </button>
        )
    }
}

ConfirmButton.propTypes = {
    buttonType: PropTypes.string
}

ConfirmButton.defaultProps = {
    buttonType: "button"
}