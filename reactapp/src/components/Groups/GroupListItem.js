import React, { Component } from 'react';
import { Link } from 'react-router-dom';

export default class GroupListItem extends Component {
    render() {
        return (
            <tr>
                <td>
                    <Link to={`/groups/${this.props.group._id}`}>
                    {this.props.group.name}
                    </Link>
                </td>
                <td>{this.props.group.project_name}</td>
                <td>{this.props.group.description}</td>
            </tr>
        )
    }
}
