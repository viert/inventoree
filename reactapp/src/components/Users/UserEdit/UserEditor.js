import React, { Component } from 'react'
import Axios from 'axios'
import HttpErrorHandler from '../../../library/HttpErrorHandler'
import Api from '../../../library/Api'
import AlertStore from '../../../library/AlertBox'
import Loading from '../../common/Loading'

import UserForm from './UserForm'
import UserAccessForm from './UserAccessForm'

export default class UserEditor extends Component {
    constructor(props) {
        super(props)
        this.state = {
            title: "Add User",
            user: {
                username: "",
                first_name: "",
                last_name: "",
                supervisor: false,
                supervisor_set_allowed: false,
                modification_allowed: false
            },
            isNew: true,
            isLoading: true
        }
    }

    componentDidMount() {
        this.loadData()
    }

    loadData() {
        let { id } = this.props.match.params
        let { EditorFields } = Api.Users
        EditorFields = EditorFields.join(",")
        if (id && id !== "new") {
            Axios.get(`/api/v1/users/${id}?_fields=${EditorFields}`)
                .then( this.onDataLoaded.bind(this) )
                .catch( error => {
                    HttpErrorHandler(error)
                    this.props.history.push('/users')
                })
        } else {
            this.setState({
                isLoading: false
            })
        }
    }

    onDataLoaded(response) {
        let user = response.data.data[0]
        this.setState({
            user,
            title: "Edit User",
            isNew: false,
            isLoading: false
        })
    }

    handleSubmit(user) {
        let { id } = this.props.match.params
        let { username } = user
        let action = this.state.isNew ? Axios.post("/api/v1/users/", user) : Axios.put(`/api/v1/users/${id}`, user)
        let message = `User ${username} has been successfully ` + (this.state.isNew ? "created" : "updated")
        action.then( response => {
            AlertStore.Notice(message)
            this.props.history.push("/users")
        })
        .catch(HttpErrorHandler)
    }

    handleDestroy(user) {
        let { id } = this.props.match.params
        Axios.delete(`/api/v1/users/${id}`)
            .then( response => {
                let { username } = response.data.user
                AlertStore.Notice(`User ${username} has been successfully destroyed`)
                this.props.history.push("/users")
            })
            .catch(HttpErrorHandler)
    }

    handleSubmitPassword(password, password_confirm) {
        let { id } = this.props.match.params
        Axios.put(`/api/v1/users/${id}/set_password`, { password_raw: password, password_raw_confirm: password_confirm })
            .then( response => {
                AlertStore.Notice("Password has been changed successfully")
                this.props.history.push("/users")
            })
            .catch(HttpErrorHandler)
    }

    toggleSupervisor() {
        let { supervisor, _id } = this.state.user
        supervisor = !supervisor
        Axios.put(`/api/v1/users/${_id}/set_supervisor`, { supervisor })
            .then(this.loadData.bind(this))
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
                            <UserForm 
                                    user={this.state.user}
                                    isNew={this.state.isNew}
                                    onSubmit={this.handleSubmit.bind(this)}
                                    onDestroy={this.handleDestroy.bind(this)} />
                        </div>
                        <div className="col-sm-6">
                            {
                                this.state.user.modification_allowed?
                                    <UserAccessForm
                                            user={this.state.user}
                                            onSubmitPassword={this.handleSubmitPassword.bind(this)}
                                            onToggleSupervisor={this.toggleSupervisor.bind(this)} /> :
                                    ""
                            }
                        </div>
                    </div>
                </div>
            }            
            </div>
        )
    }
}