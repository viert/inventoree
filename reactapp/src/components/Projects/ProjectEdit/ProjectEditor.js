import React, { Component } from 'react'
import Axios from 'axios'
import HttpErrorHandler from '../../../library/HttpErrorHandler'
import AlertStore from '../../../library/AlertBox'
import Loading from '../../common/Loading'

import Api from '../../../library/Api'
import ProjectForm from './ProjectForm'
import ProjectMembersForm from './ProjectMembersForm'

export default class ProjectEditor extends Component {
    constructor(props) {
        super(props)
        this.state = {
            title: "New Project",
            project: {
                name: ""
            },
            isNew: true,
            canModifyMembers: false,
            isLoading: true
        }
    }

    onDataLoaded(project) {
        console.log('data loaded', project)
        this.setState({
            project,
            title: "Edit Project",
            isNew: false,
            canModifyMembers: project.member_list_modification_allowed,
            isLoading: false
        })
    }

    loadData() {
        let { id } = this.props.match.params
        let { EditorFields } = Api.Projects
        EditorFields = EditorFields.join(",")
        if (id && id !== "new") {
            Axios.get(`/api/v1/projects/${id}?_fields=${EditorFields}`)
                .then( response => {
                    this.onDataLoaded(response.data.data[0])
                })
                .catch(HttpErrorHandler);
        } else {
            this.setState({
                isLoading: false
            })
        }
    }

    componentDidMount() {
        this.loadData()
    }

    handleSubmit(project) {
        let action = project._id ? 
            Axios.put(`/api/v1/projects/${project._id}`, project) :
            Axios.post('/api/v1/projects/', project)

        action.then((response) => {
            AlertStore.Notice(`Project ${project.name} has been successfully saved`)
            this.props.history.push('/projects')
        })
        .catch(HttpErrorHandler)
    }

    handleMembersSubmit(member_ids) {
        let { id } = this.props.match.params
        let { EditorFields } = Api.Projects
        EditorFields = EditorFields.join(",")
        Axios.post(`/api/v1/projects/${id}/set_members?_fields=${EditorFields}`, { member_ids })
            .then( response => {
                AlertStore.Notice('Project members have been successfully updated')
                this.onDataLoaded(response.data.data)
            })
            .catch(HttpErrorHandler)
    }

    handleOwnerSubmit(owner_id) {
        let { id } = this.props.match.params
        let { EditorFields } = Api.Projects
        Axios.post(`/api/v1/projects/${id}/switch_owner?_fields=${EditorFields}`, { owner_id })
            .then( response => {
                AlertStore.Notice('Project owner has been successfully updated')
                this.onDataLoaded(response.data.data)
            })
            .catch(HttpErrorHandler)
    }

    handleDestroy(project) {
        Axios.delete(`/api/v1/projects/${project._id}`)
            .then( response => {
                AlertStore.Notice(`Project ${project.name} has been successfully deleted`)

            })
            .catch(HttpErrorHandler)
    }

    render() {
        return (
            <div className="max vertcenter">
            {
                this.state.isLoading ? <Loading /> :
                <div className="max">
                    <h2>{this.state.title}</h2>
                    <div className="row">
                        <div className="col-sm-6">
                            <ProjectForm isNew={this.state.isNew} 
                                        onDestroy={this.handleDestroy.bind(this)} 
                                        project={this.state.project} 
                                        onSubmit={this.handleSubmit.bind(this)} />
                        </div>
                        <div className="col-sm-6">
                        {
                            this.state.isNew || !this.state.canModifyMembers ? "" :
                            <ProjectMembersForm 
                                project={this.state.project}
                                onSubmitMembers={this.handleMembersSubmit.bind(this)}
                                onSubmitOwner={this.handleOwnerSubmit.bind(this)} />
                        }
                        </div>
                    </div>
                </div>
            }
            </div>
        )
    }
}
