import React, { Component } from 'react';
import ProjectListItem from './ProjectListItem';

class ProjectListTable extends Component {
    render() {
        return (
            <table className="table">
                <thead>
                <tr>
                    <th>name</th>
                    <th>email</th>
                    <th>root email</th>
                    <th>description</th>
                </tr>
                </thead>
                <tbody>
                {
                    this.props.projects.map((project) => {
                        return (
                            <ProjectListItem project={project} key={project._id} />
                        )
                    })
                }
                </tbody>
            </table>
        )
    }
}

export default ProjectListTable;