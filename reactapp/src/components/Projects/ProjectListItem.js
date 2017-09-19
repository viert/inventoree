import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import TableModelLink from '../common/TableModelLink'
import { UserLink } from '../common/UserList'

export default class ProjectListItem extends Component {
    render() {
        let { project } = this.props
        return (
            <tr>
                <td>
                    <TableModelLink 
                        modelName="project" 
                        modelId={project._id} 
                        showEditLink={project.modification_allowed}>
                        { project.name }
                    </TableModelLink>
                </td>
                <td><UserLink user={project.owner} /></td>
                <td>{project.email}</td>
                <td>{project.root_email}</td>
                <td>{project.description}</td>
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