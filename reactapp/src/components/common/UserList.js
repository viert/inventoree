import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'
import './UserList.css'

export class UserLink extends Component {
    render() {
        return <Link className="user_list-userlink" to={`/users/${this.props.user._id}`}>{this.props.user.username}</Link>
    }
}

UserLink.propTypes = {
    user: PropTypes.shape({
        _id: PropTypes.string.isRequired,
        username: PropTypes.string.isRequired
    })
}

export default class UserList extends Component {
    render() {
        return (
            <span className="user_list">
                {
                    this.props.users.map(
                        user => <span className="user_list-user" key={user._id}><UserLink user={user} /></span>
                    )
                }
            </span>
        )
    }
}