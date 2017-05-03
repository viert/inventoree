import React, { Component } from 'react'
import PropTypes from 'prop-types'
import './TagEditor.css'

const Key = {
    BACKSPACE: 8,
    TAB: 9,
    ENTER: 13,
    SPACE: 32,
    DELETE: 46,
}

class Tag extends Component {
    onRemoveClick() {
        this.props.onRemoveTag(this.props.tag)
    }

    render() {
        return (
            <div className="tag-editor_tag">
                {this.props.tag} 
                <i className="fa fa-remove tag-editor_tag-remove" onClick={this.onRemoveClick.bind(this)}></i>
            </div>
        )
    }
}

export default class TagEditor extends Component {

    constructor(props) {
        super(props)
        this.state = {
            value: ""
        }
    }

    handleRemoveTag(tag) {
        this.props.onRemove(tag)
    }

    handleAddTag(tag) {
        if (this.props.tags.indexOf(tag) >= 0) {
            return
        }
        this.props.onAdd(tag)
    }

    handleInputChange(e) {
        let { value } = e.target
        this.setState({
            value
        })
    }

    handleInputKeyDown(e) {
        switch (e.keyCode) {
            case Key.ENTER:
            case Key.SPACE:
            case Key.TAB:
                e.preventDefault()
                this.handleAddTag(this.state.value)
                this.setState({ value: "" })
                break
            case Key.BACKSPACE:
                if (this.state.value === "" && this.props.tags.length > 0) {
                    let lastTag = this.props.tags[this.props.tags.length-1]
                    this.handleRemoveTag(lastTag)
                }
                break
        }
    }

    render() {
        return ( 
            <div className="tag-editor">
                {
                    this.props.tags.map( tag => <Tag key={tag} tag={tag} onRemoveTag={this.handleRemoveTag.bind(this)} /> )
                }
                <input size="4" className="tag-editor_input" type="text" value={this.state.value} onKeyDown={this.handleInputKeyDown.bind(this)} onChange={this.handleInputChange.bind(this)} />
            </div> 
        )
    }
}

TagEditor.propTypes = {
    tags: PropTypes.array.isRequired,
    onAdd: PropTypes.func.isRequired,
    onRemove: PropTypes.func.isRequired
}