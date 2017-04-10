import React, { Component } from 'react';
import ProjectListItem from './ProjectListItem';

class ProjectListTable extends Component {
    render() {
        return (
            <table className="table">
                <thead>
                <tr>
                    <th onClick={this.props.onSortByName}>name</th>
                    <th onClick={this.props.onSortById}>id</th>
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