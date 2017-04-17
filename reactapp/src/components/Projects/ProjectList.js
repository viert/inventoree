import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import HttpErrorHandler from '../../library/HttpErrorHandler'
import Axios from 'axios';

import ProjectListTable from './ProjectListTable';
import Pagination from '../common/Pagination'
import FilterField from '../common/FilterField'

class ProjectList extends Component {
    constructor(props) {
        super(props);
        let search = new URLSearchParams(props.location.search)
        this.page = search.get("page") || 1
        this.state = {
            projects: [],
            loading: true,
            currentPage: 1,
            totalPages: 0,
            filter: search.get("filter") || ""
        }
    }

    loadData(page, filter) {
        Axios.get(`/api/v1/projects/?_page=${page}&_filter=${filter}`).then((response) => {
            var projectList = response.data.data; 
            this.setState({
                projects: projectList,
                loading: false,
                currentPage: response.data.page,
                totalPages: response.data.total_pages,
            });
        })
        .catch(HttpErrorHandler)
    }

    componentDidMount() {
        this.loadData(this.page, this.state.filter)
    }

    handlePageChanged(page) {
        this.page = page
        this.loadData(this.page, this.state.filter)
        this.props.history.push({ 'search': `page=${this.page}&filter=${this.state.filter}` })
    }

    handleFilterChanged(filter) {
        this.setState({
            filter: filter
        })
        this.loadData(this.page, filter)
        this.props.history.push({ 'search': `page=${this.page}&filter=${filter}` })
    }

    render() {
        return (
            <div>
                <div className="pageheader">
                    <h1>Project List</h1>
                    <div className="pageheader-search">
                        <FilterField onChange={this.handleFilterChanged.bind(this)} filter={this.state.filter} />
                    </div>
                    <div className="pageheader-buttons">
                        <Link to="/projects/new" className="btn btn-success">New Project</Link>
                    </div>
                </div>
                { 
                    this.state.loading ? 'Loading' :
                        <ProjectListTable projects={this.state.projects} />
                }
                <Pagination className="text-center" current={this.state.currentPage} total={this.state.totalPages} onChangePage={this.handlePageChanged.bind(this)} />
            </div>
        )
    }
}

export default ProjectList;