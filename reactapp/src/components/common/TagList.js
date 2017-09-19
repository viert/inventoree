import React, { Component } from 'react'
import Tag from './Tag'
import './TagList.css'

export default class TagList extends Component {
    render() {
        let tags = this.props.tags || []
        let tlClass = "tag-list" + (this.props.nowrap? " tag-list--nowrap" : "") 
        return (
            <div className={tlClass}>
                { tags.map( tag => <Tag key={tag} tag={tag} />)}
            </div>
        )
    }
}