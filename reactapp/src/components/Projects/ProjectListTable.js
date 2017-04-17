import React, { Component } from 'react';
import ProjectListItem from './ProjectListItem';

export default class ProjectListTable extends Component {
    render() {
        return (
            <table className="table">
                <thead>
                <tr>
                    <th className="th-name">name</th>
                    <th className="th-email">email</th>
                    <th className="th-email">root email</th>
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
