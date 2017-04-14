import React, { Component } from 'react';

class ProjectListItem extends Component {
    render() {
        return (
            <tr>
                <td>{this.props.project.name}</td>
                <td>{this.props.project.email}</td>
                <td>{this.props.project.root_email}</td>
                <td>{this.props.project.description}</td>
            </tr>
        )
    }
}

export default ProjectListItem;