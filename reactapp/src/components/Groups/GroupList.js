import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import HttpErrorHandler from '../../library/HttpErrorHandler'
import Axios from 'axios'

import FilterField from '../common/FilterField'
import ListPageHeader from '../common/ListPageHeader'
import GroupListTable from './GroupListTable'
import Pagination from '../common/Pagination'

export default class GroupList extends Component {
    constructor(props) {
        super(props);
        let search = new URLSearchParams(props.location.search)
        this.page = search.get("page") || 1
        this.state = {
            groups: [],
            loading: true,
            currentPage: 1,
            totalPages: 0,
            filter: search.get("filter") || ""
        }
    }

    loadData(page, filter) {
        Axios.get(`/api/v1/groups/?_page=${page}&_filter=${filter}`).then((response) => {
            var groupList = response.data.data; 
            this.setState({
                groups: groupList,
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
                <ListPageHeader title="Group List" 
                                onFilterChanged={this.handleFilterChanged.bind(this)} 
                                filter={this.state.filter} 
                                createButtonText="New Group" 
                                createLink="/groups/new" />
                { 
                    this.state.loading ? 'Loading' :
                        <GroupListTable groups={this.state.groups} />
                }
                <Pagination className="text-center" current={this.state.currentPage} total={this.state.totalPages} onChangePage={this.handlePageChanged.bind(this)} />
            </div>
        )
    }

}