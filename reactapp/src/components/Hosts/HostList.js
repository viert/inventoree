import React, { Component } from 'react'
import HttpErrorHandler from '../../library/HttpErrorHandler'
import Axios from 'axios'

import AlertStore from '../../library/AlertBox'
import HostListTable from './HostListTable'
import Api from '../../library/Api'
import Pagination from '../common/Pagination'
import ListPageHeader from '../common/ListPageHeader'
import Loading from '../common/Loading'
import HostMassSelectionForm from './HostMassSelectionForm'


export default class HostList extends Component {
    constructor(props) {
        super(props);
        let search = new URLSearchParams(props.location.search)
        this.page = search.get("page") || 1
        this.state = {
            hosts: [],
            loading: true,
            currentPage: 1,
            totalPages: 0,
            filter: search.get("filter") || "",
            selectedHostsMap: {},
            selectedHostsCount: 0
        }
    }

    loadData(page, filter) {
        const fieldList = Api.Hosts.ListFields.join(",")
        this.setState({
            loading: true
        })
        Axios.get(`/api/v1/hosts/?_page=${page}&_filter=${filter}&_fields=${fieldList}`).then((response) => {
            var hostList = response.data.data
            this.setState({
                hosts: hostList,
                loading: false,
                currentPage: response.data.page,
                totalPages: response.data.total_pages,
            });
        })
        .catch(HttpErrorHandler)
    }

    resetSelectedHosts() {
        this.setState({
            selectedHostsMap: {},
            selectedHostsCount: 0
        })
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

    handleSelect(hostsToSelect) {
        let {selectedHostsMap, selectedHostsCount} = this.state
        if (!(hostsToSelect instanceof Array)) { hostsToSelect = [hostsToSelect] }

        hostsToSelect.forEach(host => {
            if (typeof selectedHostsMap[host._id] === "undefined") {
                selectedHostsMap[host._id] = host
                selectedHostsCount++
            }
        }, this);
        this.setState({ selectedHostsMap, selectedHostsCount })
    }

    handleDeselect(hostsToDeselect) {
        let {selectedHostsMap, selectedHostsCount} = this.state
        if (!(hostsToDeselect instanceof Array)) { hostsToDeselect = [hostsToDeselect] }

        hostsToDeselect.forEach(host => {
            if (typeof selectedHostsMap[host._id] !== "undefined") {
                delete(selectedHostsMap[host._id])
                selectedHostsCount--
            }
        })
        this.setState({ selectedHostsMap, selectedHostsCount })
    }

    massMove(group) {
        let group_id = group._id
        let host_ids = Object.keys(this.state.selectedHostsMap)
        Axios.post("/api/v1/hosts/mass_move", { host_ids, group_id })
            .then(response => {
                let { hosts, group } = response.data.data
                hosts = hosts.map( item => item.fqdn ).sort()
                AlertStore.Info(
                    <div>
                        <div>Following hosts were successfully moved to group <b>{group.name}</b>:</div>
                        <ul className="list-bold-no-style">
                            { hosts.map(host => <li key={host}>{host}</li>) }
                        </ul>
                    </div>
                )
                this.loadData(this.page, this.state.filter)
                this.resetSelectedHosts()
            })
            .catch(HttpErrorHandler)
    }

    massDestroy() {
        let host_ids = Object.keys(this.state.selectedHostsMap)
        Axios.post("/api/v1/hosts/mass_delete", { host_ids })
            .then(response => {
                let { hosts } = response.data.data
                hosts = hosts.map( item => item.fqdn ).sort()
                AlertStore.Info(
                    <div>
                        <div>Following hosts were successfully destroyed:</div>
                        <ul className="list-bold-no-style">
                            { hosts.map(host => <li key={host}>{host}</li>) }
                        </ul>
                    </div>
                )
                this.loadData(this.page, this.state.filter)
                this.resetSelectedHosts()
            })
            .catch(HttpErrorHandler)
    }

    massDetach() {
        let host_ids = Object.keys(this.state.selectedHostsMap)
        Axios.post("/api/v1/hosts/mass_detach", { host_ids })
            .then(response => {
                let { hosts } = response.data.data
                hosts = hosts.map( item => item.fqdn ).sort()
                AlertStore.Info(
                    <div>
                        <div>Following hosts were successfully detached from groups:</div>
                        <ul className="list-bold-no-style">
                            { hosts.map(host => <li key={host}>{host}</li>) }
                        </ul>
                    </div>
                )
                this.loadData(this.page, this.state.filter)
                this.resetSelectedHosts()
            })
            .catch(HttpErrorHandler)
    }

    render() {
        let inSelectMode = this.state.selectedHostsCount > 0
        let tableWrapperClass = inSelectMode ? "col-sm-8" : "col-sm-12"
        let includeDescription = !inSelectMode

        return (
            <div>
                <div className="row">
                    <div className="col-sm-12">

                        <ListPageHeader title="Host List" 
                                        onFilterChanged={this.handleFilterChanged.bind(this)} 
                                        filter={this.state.filter} 
                                        createButtonText="Add Host(s)" 
                                        createLink="/hosts/new/edit" />
                    </div>
                </div>
                <div className="row">
                    <div className={tableWrapperClass}>
                        { 
                        this.state.loading ? <div className="max vertcenter"><Loading /></div> :
                            <HostListTable 
                                        hosts={this.state.hosts} 
                                        onSelect={this.handleSelect.bind(this)} 
                                        onDeselect={this.handleDeselect.bind(this)} 
                                        selected={this.state.selectedHostsMap}
                                        includeDescription={includeDescription} />
                        }
                    </div>
                    {
                        inSelectMode ? 
                        <div className="col-sm-4">
                            <HostMassSelectionForm 
                                onDestroy={this.massDestroy.bind(this)} 
                                onMoveToGroup={this.massMove.bind(this)}
                                onDetach={this.massDetach.bind(this)}
                                hosts={this.state.selectedHostsMap} 
                                onRemove={this.handleDeselect.bind(this)} />
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