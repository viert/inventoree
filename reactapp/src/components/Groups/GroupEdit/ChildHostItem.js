import React, { Component } from 'react'
import PropTypes from 'prop-types'
import './ChildItem.css'

export default class ChildHostItem extends Component {

    handleRemoveClick(e) {
        this.props.onRemoveTrigger(this.props.host)
    }

    handleMouseEnter(e) {
        if (e.buttons === 1) {
            this.handleRemoveClick()
        }
        return false
    }

    render() {
        return (
            <div className={'child-item' + (this.props.host.removed ? ' removed': '')}>
                <span onMouseEnter={this.handleMouseEnter.bind(this)} onMouseDown={this.handleRemoveClick.bind(this)} className="fa fa-remove child-item_delete-trigger"></span>
                <span className="child-item_text">
                    { this.props.host.fqdn }
                </span>
            </div>
        )
    }    
}

ChildHostItem.propTypes = {
    onRemoveTrigger: PropTypes.func.isRequired,
    host: PropTypes.shape({
        fqdn: PropTypes.string.isRequired,
        removed: PropTypes.bool.isRequired
    }),
}