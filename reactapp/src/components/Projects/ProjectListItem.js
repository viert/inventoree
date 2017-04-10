import React, { Component } from 'react';

class ProjectListItem extends Component {
    render() {
        return (
            <tr>
                <td>{this.props.project.name}</td>
                <td>{this.props.project._id}</td>
            </tr>
        )
    }
}

export default ProjectListItem;