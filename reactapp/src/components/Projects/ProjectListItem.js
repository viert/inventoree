import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

export default class ProjectListItem extends Component {
    render() {
        return (
            <tr>
                <td>
                    <Link to={"/projects/" + this.props.project._id}>
                    {this.props.project.name}
                    </Link>
                </td>
                <td>{this.props.project.email}</td>
                <td>{this.props.project.root_email}</td>
                <td>{this.props.project.description}</td>
            </tr>
        )
    }
}

ProjectListItem.propTypes = {
    project: PropTypes.shape({
        _id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        email: PropTypes.string,
        root_email: PropTypes.string,
        description: PropTypes.string,
    })
}