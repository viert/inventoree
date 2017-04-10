import React, { Component } from 'react';
import Axios from 'axios';

import ProjectListTable from './ProjectListTable';

class ProjectList extends Component {
    constructor() {
        super();
        this.state = {
            projects: [],
            sorters: {
                id: 1,
                name: 1
            }
        }
    }
    componentDidMount() {
        Axios.get("/api/v1/projects/").then((data) => {
            var projectList = data.data.data;     // zombie-zombie-zombie
            projectList.sort((a, b) => ( a.name > b.name ));
            this.setState({
                projects: projectList
            });
        });
    }

    sortBy(field) {
        var projectList = this.state.projects.slice();
        var sorters = this.state.sorters;
        sorters[field] = -sorters[field];
        projectList.sort((a, b) => {
            if (sorters[field] > 0) {
                return a[field] > b[field];
            } else {
                return b[field] > a[field];
            }
        });
        this.setState({
            projects: projectList,
            sorters: sorters
        });
    }

    handleSortById(e) {
        e.preventDefault();
        this.sortBy('_id');
    }

    handleSortByName(e) {
        e.preventDefault();
        this.sortBy('name');
    }

    render() {
        return (
            <div>
                <h1>Project List</h1>
                <ProjectListTable onSortById={this.handleSortById.bind(this)} onSortByName={this.handleSortByName.bind(this)} projects={this.state.projects} />
            </div>
        )
    }
}

export default ProjectList;