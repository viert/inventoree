import React, { Component } from 'react'
import Tag from './Tag'
import './TagList.css'

export default class TagList extends Component {
    render() {
        return (
            <div className="tag-list">
                { this.props.tags.map( tag => <Tag id={tag} tag={tag} />)}
            </div>
        )
    }
}