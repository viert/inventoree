import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import HttpErrorHandler from '../../library/HttpErrorHandler'
import Axios from 'axios';

import ProjectListTable from './ProjectListTable';

class ProjectList extends Component {
    constructor() {
        super();
        this.state = {
            projects: [],
            sorters: {
                _id: 1,
                name: 1
            },
            loading: true
        }
    }

    componentDidMount() {
        Axios.get("/api/v1/projects/").then((data) => {
            var projectList = data.data.data;     // zombie-zombie-zombie
            projectList.sort((a, b) => ( a.name > b.name ));
            this.setState({
                projects: projectList,
                loading: false
            });
        })
        .catch(HttpErrorHandler);
    }

    handleSortBy(field) {
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

    render() {
        return (
            <div>
                <h1>Project List</h1>
                <div className="control-buttons">
                    <Link to="/projects/new" className="btn btn-success uppercase">New Project</Link>
                </div>
                { 
                    this.state.loading ? 'Loading' :
                        <ProjectListTable onSortById={this.handleSortBy.bind(this, '_id')} onSortByName={this.handleSortBy.bind(this, 'name')} projects={this.state.projects} />
                }
            </div>
        )
    }
}

export default ProjectList;