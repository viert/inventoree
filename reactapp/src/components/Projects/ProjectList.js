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


    render() {
        return (
            <div>
                <div className="pageheader">
                    <h1>Project List</h1>
                    <div className="pageheader-search">
                        <div className="input-group">
                            <span className="input-group-addon">Filter</span>
                            <input type="text" className="form-control" />
                        </div>
                    </div>
                    <div className="pageheader-buttons">
                        <Link to="/create_project" className="btn btn-success">New Project</Link>
                    </div>
                </div>
                { 
                    this.state.loading ? 'Loading' :
                        <ProjectListTable projects={this.state.projects} />
                }
            </div>
        )
    }
}

export default ProjectList;