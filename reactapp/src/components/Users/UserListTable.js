import React, { Component } from 'react'
import PropTypes from 'prop-types'
import UserListItem from './UserListItem'

export default class UserListTable extends Component {
    render() {
        return (
            <table className="table listtable">
                <thead>
                <tr>
                    <th className="th-name">username</th>
                    <th className="th-email">first name</th>
                    <th className="th-email">last name</th>
                    <th className="">supervisor</th>
                </tr>
                </thead>
                <tbody>
                {
                    this.props.users.map((user) => {
                        return (
                            <UserListItem user={user} key={user._id} />
                        )
                    })
                }
                </tbody>
            </table>
        )
    }
}

UserListTable.propTypes = {
    users: PropTypes.array.isRequired
}
