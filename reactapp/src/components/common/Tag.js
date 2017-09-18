import React, { Component } from 'react'
import PropTypes from 'prop-types'

export default class Tag extends Component {
    constructor(props) {
        super(props)
        this.dynamic = (typeof this.props.onRemoveTag === "function")
    }

    onRemoveClick() {
        this.props.onRemoveTag(this.props.tag)
    }

    render() {
        let tagClass = "tag-editor_tag" + (this.props.derived ? " tag-editor_tag--derived": "")
            + (this.props.mini ? " tag-editor_tag--mini": "")
        let tagTitle = this.props.tag + (this.props.derived ? ": tag derived from parent": "")
        return (
            <div className={tagClass} title={tagTitle}>
                {this.props.tag}
                { 
                    this.dynamic ? <i className="fa fa-remove tag-editor_tag-remove" onClick={this.onRemoveClick.bind(this)}></i> : ""
                }
            </div>
        )
    }    
}

Tag.propTypes = {
    onRemoveTag: PropTypes.func,
    derived: PropTypes.bool,
    mini: PropTypes.bool
}