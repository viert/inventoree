import React, { Component } from 'react'
import PropTypes from 'prop-types'
import ProjectListItem from './ProjectListItem'

export default class ProjectListTable extends Component {
    render() {
        return (
            <table className="table listtable">
                <thead>
                <tr>
                    <th className="th-name">name</th>
                    <th className="th-email">owner</th>
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

ProjectListTable.propTypes = {
    projects: PropTypes.array.isRequired
}
