import React, { Component } from 'react'
import Tag from './Tag'
import './TagList.css'

export default class TagList extends Component {
    render() {
        let tags = this.props.tags || []
        return (
            <div className="tag-list">
                { tags.map( tag => <Tag key={tag} tag={tag} />)}
            </div>
        )
    }
}