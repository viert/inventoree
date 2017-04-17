import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import FilterField from './FilterField'

export default class ListPageHeader extends Component {
    render() {
        return (
                <div className="pageheader">
                    <h1>{this.props.title}</h1>
                    <div className="pageheader-search">
                        <FilterField onChange={this.props.onFilterChanged} filter={this.props.filter} />
                    </div>
                    <div className="pageheader-buttons">
                        <Link to={this.props.createLink} className="btn btn-success">{this.props.createButtonText}</Link>
                    </div>
                </div>            
        )
    }
}