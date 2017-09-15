import React, { Component } from 'react'
import PropTypes from 'prop-types'
import './ChildItem.css'

export default class ChildItem extends Component {

    handleRemoveClick(e) {
        this.props.onRemoveTrigger()
    }

    handleMouseEnter(e) {
        if (e.buttons === 1) {
            this.handleRemoveClick()
        }
        if (this.props.onMouseEnter) {
            this.props.onMouseEnter(e)
        }
        return false
    }

    handleMouseLeave(e) {
        if (this.props.onMouseLeave) {
            this.props.onMouseLeave(e)
        }
    }

    render() {
        const childClass = "child-item_text" + (this.props.disableSelect ? " noselect" : "" )
        return (
            <div className={'child-item' + (this.props.removed ? ' removed': '')}>
                <span onMouseEnter={this.handleMouseEnter.bind(this)} 
                      onMouseLeave={this.handleMouseLeave.bind(this)} 
                      onMouseDown={this.handleRemoveClick.bind(this)} 
                      className="fa fa-remove child-item_delete-trigger"></span>
                <span className={childClass}>{ this.props.text }</span>
            </div>
        )
    }    
}

ChildItem.propTypes = {
    onRemoveTrigger: PropTypes.func.isRequired,
    onMouseEnter: PropTypes.func,
    onMouseLeave: PropTypes.func,
    disableSelect: PropTypes.bool.isRequired,
    text: PropTypes.string.isRequired,
    removed: PropTypes.bool.isRequired
}
