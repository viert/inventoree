import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import './DatacenterItem.css'

export default class DatacenterItem extends Component {
    render() {
        return (
            <div className="datacenter-tree_item" style={{ marginLeft: this.props.datacenter.level * 20 + 'px'}}>
                <div className="datacenter-tree_item-icon draggable-handle">
                    <i className="fa fa-database"></i>
                </div>
                <div className="datacenter-tree_item-text">
                    {
                        this.props.datacenter._id === "root" ? 
                                <b>{this.props.datacenter.name}</b> : 
                                <Link to={`/datacenters/${this.props.datacenter._id}`}>{this.props.datacenter.name}</Link>
                    }
                </div>
            </div>
        )
    }
}