import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'
import './TableModelLink.css'

export default class TableModelLink extends Component {
    render() {
        let viewPath = `/${this.props.modelName}s/${this.props.modelId}`
        let editPath = `${viewPath}/edit`
        return (
            <span className="model-links">
                <span className="model-links-edit-link-wrapper">
                    { 
                        this.props.showEditLink ? 
                            <Link className="model-links-edit-link" to={editPath}>
                                <i className="fa fa-edit"></i>
                            </Link> : ""
                    }
                </span>
                <Link className="model-links-view-link" to={viewPath}>
                    { this.props.children }
                </Link>
            </span>
        )
    }
}

TableModelLink.propTypes = {
    showEditLink: PropTypes.bool,
    modelName: PropTypes.string.isRequired,
    modelId: PropTypes.string.isRequired
}