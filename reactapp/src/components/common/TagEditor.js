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
            value: "",
            size: 5,
            focused: false
        }
    }

    handleInputFocus() {
        this.setState({
            focused: true
        })
    }

    handleInputBlur() {
        this.setState({
            focused: false
        })
    }

    handleRemoveTag(tag) {
        this.props.onRemove(tag)
    }

    handleAddTag(tag) {
        tag = tag.trim()
        if (tag.length === 0) return
        if (this.props.tags.indexOf(tag) >= 0) return
        this.props.onAdd(tag)
    }

    handleInputChange(e) {
        let { value } = e.target
        let targetSize = value.length + 5
        let currentSize = this.refs.tagInput.size
        let size = targetSize
        if (targetSize > currentSize) {
            let inputWidth = this.refs.tagInput.clientWidth
            let parentWidth = this.refs.tagInput.parentElement.clientWidth
            if (inputWidth + 48 > parentWidth) {
                size = currentSize
            }
        }
        this.setState({
            value,
            size
        })
    }

    handleInputKeyDown(e) {
        switch (e.keyCode) {
            case Key.ENTER:
            case Key.SPACE:
                e.preventDefault()
                this.handleAddTag(this.state.value)
                this.setState({ value: "", size: 5 })
                break
            case Key.TAB:
                if (this.state.value.length > 0) {
                    e.preventDefault()
                    this.handleAddTag(this.state.value)
                    this.setState({ value: "", size: 5 })
                }
                break;
            case Key.BACKSPACE:
                if (this.state.value === "" && this.props.tags.length > 0) {
                    let lastTag = this.props.tags[this.props.tags.length-1]
                    this.handleRemoveTag(lastTag)
                }
                break
            default:
                break
        }
    }

    handleEditorDefaultClick(e) {
        if (e.target === e.currentTarget) {
            this.refs.tagInput.focus()
        }
    }

    render() {
        let classNames = "tag-editor" + (this.state.focused ? " has-focus": "")
        return ( 
            <div className={classNames} onClick={this.handleEditorDefaultClick.bind(this)}>
                {
                    this.props.tags.map( tag => <Tag key={tag} tag={tag} onRemoveTag={this.handleRemoveTag.bind(this)} /> )
                }
                <input  
                    size={this.state.size} 
                    ref="tagInput" 
                    className="tag-editor_input" 
                    type="text" 
                    value={this.state.value} 
                    onKeyDown={this.handleInputKeyDown.bind(this)} 
                    onChange={this.handleInputChange.bind(this)} 
                    onFocus={this.handleInputFocus.bind(this)}
                    onBlur={this.handleInputBlur.bind(this)}
                    />
            </div> 
        )
    }
}

TagEditor.propTypes = {
    tags: PropTypes.array.isRequired,
    onAdd: PropTypes.func.isRequired,
    onRemove: PropTypes.func.isRequired
}