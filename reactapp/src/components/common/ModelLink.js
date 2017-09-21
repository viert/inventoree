import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

export default class ModelLink extends Component {
    render() {
        let viewPath = `/${this.props.modelName}s/${this.props.model._id}`
        return (
                <Link className="model-links-view-link" to={viewPath}>
                    { this.props.model[this.props.modelKey] }
                </Link>
        )
    }
}

ModelLink.propTypes = {
    model: PropTypes.object.isRequired,
    modelName: PropTypes.string.isRequired,
    modelKey: PropTypes.string.isRequired,
}