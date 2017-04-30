import React, { Component } from 'react'
import PropTypes from 'prop-types'
import './ChildItem.css'

export default class ChildGroupItem extends Component {

    handleRemoveClick(e) {
        this.props.onRemoveTrigger(this.props.group)
    }

    render() {
        return (
            <div className={'child-item' + (this.props.group.removed ? ' removed': '')}>
                <span onClick={this.handleRemoveClick.bind(this)} className="fa fa-remove child-item_delete-trigger"></span>
                <span className="child-item_text">
                    { this.props.group.name }
                </span>
            </div>
        )
    }    
}

ChildGroupItem.propTypes = {
    onRemoveTrigger: PropTypes.func.isRequired,
    group: PropTypes.shape({
        name: PropTypes.string.isRequired,
        removed: PropTypes.bool.isRequired
    }),
}