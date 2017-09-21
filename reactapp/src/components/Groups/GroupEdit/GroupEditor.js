import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import Axios from 'axios'
import HttpErrorHandler from '../../../library/HttpErrorHandler'
import AlertStore from '../../../library/AlertBox'
import Loading from '../../common/Loading'

import GroupForm from './GroupForm'
import GroupRelationsForm from './GroupRelationsForm'

export default class GroupEditor extends Component {
    constructor(props) {
        super(props)
        this.state = {
            title: "New Group",
            group: {
                name: "",
                description: "",
                tags: [],
                custom_fields: [],
                project: {
                    name: ""
                }                
            },
            isNew: true,
            isLoading: true
        }
    }

    componentWillReceiveProps(props) {
        let { id } = props.match.params
        if (id && id === "new") {
            this.setState({
                group: {
                    name: "",
                    description: "",
                    tags: [],
                    custom_fields: [],
                    project: {
                        name: "",
                        _id: null
                    }                
                },
                title: "New Group",
                isNew: true,
            })
        }
    }

    componentDidMount() {
        let { id } = this.props.match.params
        if (id && id !== "new") {
            Axios.get(`/api/v1/groups/${id}?_fields=children,name,description,project,tags,custom_fields,hosts`)
                .then( this.onDataLoaded.bind(this) )
                .catch( error => {
                    HttpErrorHandler(error)
                    this.props.history.push('/groups')
                })
        } else {
            this.setState({
                isLoading: false
            })
        }
    }

    onDataLoaded(response) {
        this.setState({
            group: response.data.data[0],
            title: "Edit Group",
            isNew: false,
            isLoading: false
        })        
    }

    handleSubmit(group) {
        if (this.state.isNew) {
            Axios.post("/api/v1/groups/", group)
                .then( response => {
                    let { _id, name } = response.data.data
                    AlertStore.Notice(`Group ${name} has been successfully created, you can now add group's relations`)
                    this.props.history.push(`/groups/${_id}`)
                    this.componentDidMount()
                })
                .catch(HttpErrorHandler)
        } else {
            let { id } = this.props.match.params
            Axios.put(`/api/v1/groups/${id}`, group)
                .then( response => {
                    let { name } = group
                    AlertStore.Notice(`Group ${name} has been successfully updated, be sure to save relations if you made changes`)
                })
        }
    }

    handleDestroy(group) {
        let { id } = this.props.match.params
        Axios.delete(`/api/v1/groups/${id}`)
            .then( response => {
                let { name } = group
                AlertStore.Notice(`Group ${name} has been successfully destroyed`)
                this.props.history.push("/groups")
            })
            .catch(HttpErrorHandler)
    }

    handleSubmitRelations(child_ids, host_ids) {
        let { id } = this.props.match.params;
        let { group } = this.state
        Axios.put(`/api/v1/groups/${id}/set_hosts?_fields=hosts`, { host_ids })
            .then( response => {
                let { hosts } = response.data.data
                group.hosts = hosts
                this.setState({
                    group
                })
                AlertStore.Notice("Hosts have been successfully updated")
            })
            .catch(HttpErrorHandler)
        Axios.put(`/api/v1/groups/${id}/set_children?_fields=children`, { child_ids })
            .then( response => {
                let { children } = response.data.data
                group.children = children
                this.setState({
                    group
                })
                AlertStore.Notice("Children have been successfully updated")
            })
            .catch(HttpErrorHandler)
    }

    render() {
        return (
            <div className="max vertcenter">
            {
                this.state.isLoading ? <Loading /> :
                <div className="max">
                    <div className="listpage-header">
                        <h2>{this.state.title}</h2>
                        { this.state.isNew ? "" : 
                            <div className="listpage-header_buttons">
                                <Link to="/groups/new/edit" className="btn btn-primary">New Group</Link>
                            </div>
                        }
                    </div>
                    <div className="row">
                        <div className="col-sm-5">
                            <GroupForm 
                                    group={this.state.group}
                                    isNew={this.state.isNew}
                                    onSubmit={this.handleSubmit.bind(this)}
                                    onDestroy={this.handleDestroy.bind(this)} />
                        </div>
                        <div className="col-sm-7">
                            {
                                this.state.isNew ? "" : 
                                <GroupRelationsForm
                                    group={this.state.group}
                                    onSubmitData={this.handleSubmitRelations.bind(this)} />
                            }
                        </div>
                    </div>
                </div>
            }            
            </div>
        )
    }

}