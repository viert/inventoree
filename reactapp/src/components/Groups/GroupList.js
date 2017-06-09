import React, { Component } from 'react'
import HttpErrorHandler from '../../library/HttpErrorHandler'
import Axios from 'axios'

import ListPageHeader from '../common/ListPageHeader'
import GroupListTable from './GroupListTable'
import GroupMassSelectionForm from './GroupMassSelectionForm'
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
            filter: search.get("filter") || "",
            selectedGroupsMap: {},
            selectedGroupsCount: 0 
        }
    }

    loadData(page, filter) {
        Axios.get(`/api/v1/groups/?_page=${page}&_filter=${filter}&_fields=_id,name,description,project_name`).then((response) => {
            var groupList = response.data.data.map( item => { item.selected = false; return item });
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

    handleSelect(groupsToSelect) {
        let {selectedGroupsMap, selectedGroupsCount} = this.state
        if (!(groupsToSelect instanceof Array)) { groupsToSelect = [groupsToSelect] }

        groupsToSelect.forEach(function(group) {
            if (typeof selectedGroupsMap[group._id] === "undefined") {
                selectedGroupsMap[group._id] = group
                selectedGroupsCount++
            }
        }, this);
        this.setState({ selectedGroupsMap, selectedGroupsCount })
    }

    handleDeselect(groupsToDeselect) {
        let {selectedGroupsMap, selectedGroupsCount} = this.state
        if (!(groupsToDeselect instanceof Array)) { groupsToDeselect = [groupsToDeselect] }

        groupsToDeselect.forEach(function(group) {
            if (typeof selectedGroupsMap[group._id] !== "undefined") {
                delete(selectedGroupsMap[group._id])
                selectedGroupsCount--
            }
        }, this);
        this.setState({ selectedGroupsMap, selectedGroupsCount })
    }

    massDestroy() {
        console.log("massDestroy")
    }

    massMove(project) {
        console.log("massMove", project)
    }

    render() {
        let inSelectMode = this.state.selectedGroupsCount > 0
        let tableWrapperClass = inSelectMode ? "col-sm-8" : "col-sm-12"

        return (
            <div>
                <div className="row">
                    <div className="col-sm-12">
                        <ListPageHeader title="Group List" 
                                        onFilterChanged={this.handleFilterChanged.bind(this)} 
                                        filter={this.state.filter} 
                                        createButtonText="New Group" 
                                        createLink="/groups/new" />
                    </div>
                </div>
                <div className="row">
                    <div className={tableWrapperClass}>
                        { 
                            this.state.loading ? 'Loading' :
                                <GroupListTable onSelect={this.handleSelect.bind(this)} onDeselect={this.handleDeselect.bind(this)} groups={this.state.groups} selected={this.state.selectedGroupsMap} />
                        }
                    </div>
                    {
                        inSelectMode ? 
                        <div className="col-sm-4">
                            <GroupMassSelectionForm onDestroy={this.massDestroy.bind(this)} onMoveToProject={this.massMove.bind(this)} groups={this.state.selectedGroupsMap} onRemove={this.handleDeselect.bind(this)} />
                        </div> : ""
                    }
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