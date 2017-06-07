import React, { Component } from 'react'

export default class Tag extends Component {
    constructor(props) {
        super(props)
        this.dynamic = (typeof this.props.onRemoveTag === "function")
    }

    onRemoveClick() {
        this.props.onRemoveTag(this.props.tag)
    }

    render() {
        return (
            <div className="tag-editor_tag">
                {this.props.tag}
                { 
                    this.dynamic ? <i className="fa fa-remove tag-editor_tag-remove" onClick={this.onRemoveClick.bind(this)}></i> : ""
                }
            </div>
        )
    }    
}