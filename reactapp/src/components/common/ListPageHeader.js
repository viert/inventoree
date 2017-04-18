import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import FilterField from './FilterField'
import './ListPageHeader.css'

export default class ListPageHeader extends Component {
    render() {
        return (
                <div className="listpage-header">
                    <h2>{this.props.title}</h2>
                    <div className="listpage-header_search">
                        { 
                            this.props.noFilter ? '' : <FilterField onChange={this.props.onFilterChanged} filter={this.props.filter} />
                        }
                    </div>
                    <div className="listpage-header_buttons">
                        <Link to={this.props.createLink} className="btn btn-success">{this.props.createButtonText}</Link>
                    </div>
                </div>            
        )
    }
}