import React, { Component } from 'react'
import PropTypes from 'prop-types'

import TableModelLink from '../common/TableModelLink'

export default class UserListItem extends Component {
    render() {
        let { user } = this.props
        return (
            <tr>
                <td>
                    <TableModelLink 
                        modelName="user" 
                        modelId={user._id} 
                        showEditLink={user.modification_allowed}>
                        { user.username }
                    </TableModelLink>
                </td>
                <td>{user.first_name}</td>
                <td>{user.last_name}</td>
                <td>
                {
                    user.supervisor ? <i className="fa fa-check"></i> : ""
                }
                </td>
            </tr>
        )
    }
}

UserListItem.propTypes = {
    project: PropTypes.shape({
        _id: PropTypes.string.isRequired,
        username: PropTypes.string.isRequired,
        first_name: PropTypes.string.isRequired,
        last_name: PropTypes.string.isRequired,
        supervisor: PropTypes.bool.isRequired,
    })
}