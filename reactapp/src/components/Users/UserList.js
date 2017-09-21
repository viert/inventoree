import React, { Component } from 'react'
import HttpErrorHandler from '../../library/HttpErrorHandler'
import Axios from 'axios'

import Api from '../../library/Api'
import UserListTable from './UserListTable'
import Pagination from '../common/Pagination'
import ListPageHeader from '../common/ListPageHeader'
import Loading from '../common/Loading'

export default class UserList extends Component {
    constructor(props) {
        super(props);
        let search = new URLSearchParams(props.location.search)
        this.page = search.get("page") || 1
        this.state = {
            users: [],
            loading: true,
            currentPage: 1,
            totalPages: 0,
            filter: search.get("filter") || "",
        }
    }

    loadData(page, filter) {
        this.setState({ loading: true })
        let { ListFields } = Api.Users
        ListFields = ListFields.join(',')
        Axios.get(`/api/v1/users/?_page=${page}&_filter=${filter}&_fields=${ListFields}`).then((response) => {
            var userList = response.data.data; 
            this.setState({
                users: userList,
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
                <ListPageHeader title="User List" 
                                onFilterChanged={this.handleFilterChanged.bind(this)} 
                                filter={this.state.filter} 
                                createButtonText="Add User" 
                                createLink="/users/new/edit" />
                { 
                    this.state.loading ? <Loading /> :
                        <UserListTable users={this.state.users} />
                }
                <Pagination className="text-center" current={this.state.currentPage} total={this.state.totalPages} onChangePage={this.handlePageChanged.bind(this)} />
            </div>
        )
    }
}