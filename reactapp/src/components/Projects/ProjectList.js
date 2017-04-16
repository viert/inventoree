import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import HttpErrorHandler from '../../library/HttpErrorHandler'
import Axios from 'axios';

import ProjectListTable from './ProjectListTable';
import Pagination from '../common/Pagination'

class ProjectList extends Component {
    constructor() {
        super();
        this.state = {
            projects: [],
            loading: true,
            currentPage: 1,
            totalPages: 0
        }
    }

    componentDidMount() {
        Axios.get("/api/v1/projects/").then((response) => {
            var projectList = response.data.data; 
            this.setState({
                projects: projectList,
                loading: false,
                currentPage: response.data.page,
                totalPages: response.data.total_pages
            });
        })
        .catch(HttpErrorHandler);
    }

    handlePageChanged(page) {
        console.log(page)
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
                        <Link to="/projects/new" className="btn btn-success">New Project</Link>
                    </div>
                </div>
                { 
                    this.state.loading ? 'Loading' :
                        <ProjectListTable projects={this.state.projects} />
                }
                <Pagination current={this.state.currentPage} total={this.state.totalPages} onChangePage={this.handlePageChanged.bind(this)} />
            </div>
        )
    }
}

export default ProjectList;