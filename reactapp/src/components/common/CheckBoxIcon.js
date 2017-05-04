import React, { Component } from 'react'
import PropTypes from 'prop-types'

export default class CheckBoxIcon extends Component {
    
    handleMouseEnter(e) {
        if (e.buttons === 1) {
            this.props.onTrigger()
        }
    }

    render() {
        let classList = []
        if (this.props.className) classList.push(this.props.className)
        classList.push( this.props.checked ? this.props.classNameChecked : this.props.classNameUnchecked )
        let classes = classList.join(" ")
        return (
            <i style={{ cursor: 'pointer' }} className={classes} onMouseEnter={this.handleMouseEnter.bind(this)} onMouseDown={this.props.onTrigger}></i>
        )
    }
}

CheckBoxIcon.propTypes = {
    classNameChecked: PropTypes.string,
    classNameUnchecked: PropTypes.string,
    onTrigger: PropTypes.func.isRequired,
    checked: PropTypes.bool.isRequired
}