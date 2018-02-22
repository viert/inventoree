import React, { Component } from 'react'
import HttpErrorHandler from '../../library/HttpErrorHandler'
import Axios from 'axios'

import Api from '../../library/Api'
import Pagination from '../common/Pagination'
import Loading from '../common/Loading'
import FilterField from '../common/FilterField'
import './ActionLogList.css'

const formatDate = (d) => {
    d = new Date(d)
    return d.toLocaleDateString() + " " + d.toLocaleTimeString()
}


export default class ActionTypeList extends Component {
    constructor(props) {
        super(props);
        let search = new URLSearchParams(props.location.search)
        this.page = search.get("page") || 1
        this.state = {
            actions: [],
            loading: true,
            currentPage: 1,
            totalPages: 0,
            usernameFilter: search.get("username_filter") || "",
            actionTypeFilter: search.get("action_type_filter") || "",
        }
    }

    loadData(page, usernameFilter, actionTypeFilter) {
        const fieldList = Api.Actions.ListFields.join(",")
        this.setState({
            loading: true
        })
        Axios.get(`/api/v1/actions/?_page=${page}&_username_filter=${usernameFilter}&_action_type_filter=${actionTypeFilter}&_fields=${fieldList}`).then((response) => {
            var actions = response.data.data
            this.setState({
                actions,
                loading: false,
                currentPage: response.data.page,
                totalPages: response.data.total_pages,
            });
        })
        .catch(HttpErrorHandler)
    }

    componentDidMount() {
        let { usernameFilter, actionTypeFilter } = this.state
        this.loadData(this.page, usernameFilter, actionTypeFilter)
    }

    handlePageChanged(page) {
        this.page = page
        let { usernameFilter, actionTypeFilter } = this.state
        this.loadData(this.page, usernameFilter, actionTypeFilter)
        this.props.history.push({ 'search': `page=${this.page}&username_filter=${usernameFilter}&action_type_filter=${actionTypeFilter}` })
    }

    handleUsernameFilterChanged = (usernameFilter) => {
        let { actionTypeFilter } = this.state
        this.setState({ usernameFilter })
        this.loadData(this.page, usernameFilter, actionTypeFilter)
        this.props.history.push({ 'search': `page=${this.page}&username_filter=${usernameFilter}&action_type_filter=${actionTypeFilter}` })
    }

    handleActionTypeFilterChanged = (actionTypeFilter) => {
        let { usernameFilter } = this.state
        this.setState({ actionTypeFilter })
        this.loadData(this.page, usernameFilter, actionTypeFilter)
        this.props.history.push({ 'search': `page=${this.page}&username_filter=${usernameFilter}&action_type_filter=${actionTypeFilter}` })
    }


    render() {
        let { usernameFilter, actionTypeFilter, loading, actions } = this.state
        return (
            <div>
                <div className="row">
                    <div className="col-sm-12">
                        <div className="listpage-header">
                            <h2>Action Log</h2>
                            <div className="listpage-header_search listpage-header_search--mini">
                                <FilterField name="Username" onChange={this.handleUsernameFilterChanged} filter={usernameFilter} />
                            </div>
                            <div className="listpage-header_search listpage-header_search--mini">
                                <FilterField name="Action Type" onChange={this.handleActionTypeFilterChanged} filter={actionTypeFilter} />
                            </div>
                        </div>      
                    </div>
                </div>
                <div className="row">
                    <div className="col-sm-12">
                    { 
                        loading ? <div className="max vertcenter"><Loading /></div> :
                            
                        <table className="table">
                            <thead>
                                <tr>
                                    <th style={{ width: '200px' }}>DateTime</th>
                                    <th style={{ width: '240px' }}>Action</th>
                                    <th>Params</th>
                                    <th style={{ width: '240px' }}>User</th>
                                </tr>
                            </thead>
                            <tbody>
                            {
                                actions.map( action => (
                                    <tr key={action.created_at}>
                                        <td>{formatDate(action.created_at)}</td>
                                        <td className={`action_type--${action.status}`}>{action.action_type}</td>
                                        <td>{JSON.stringify(action.kwargs)}, {JSON.stringify(action.params)}</td>
                                        <td>{action.username}</td> 
                                    </tr>
                                ))   
                            }
                            </tbody>
                        </table>    
                    
                    }
                    </div>
                </div>
                <div className="row">
                    <div className="col-sm-12">
                        <Pagination className="text-center" current={this.state.currentPage} total={this.state.totalPages} onChangePage={this.handlePageChanged.bind(this)} />
                    </div>
                </div>
            </div>
        )
    }
}