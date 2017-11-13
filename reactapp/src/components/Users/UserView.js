import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import Axios from 'axios'

import Api from '../../library/Api'
import HttpErrorHandler from '../../library/HttpErrorHandler'
import Loading from '../common/Loading'
import ModelLink from '../common/ModelLink'
import '../common/PropertiesPanel.css'

const selectText = (element) => {
    if (document.body.createTextRange) {
        let range = document.body.createTextRange()
        range.moveToElementText(element)
        range.select()
    } else if (window.getSelection) {
        let selection = window.getSelection()
        let range = document.createRange()
        range.selectNodeContents(element)
        selection.removeAllRanges()
        selection.addRange(range)
    }
} 

export default class UserView extends Component {
    constructor(props) {
        super(props)
        this.state = {
            user: {
                _id: "",
                username: "",
                first_name: "",
                last_name: "",
                email: "",
                supervisor: false,
                projects_owned: [],
                projects_included_into: [],
                modification_allowed: false
            },
            isLoading: true,
        }
    }

    onDataLoaded(response) {
        let user = response.data.data[0]
        this.setState({
            user,
            isLoading: false
        })
    }

    componentDidMount() {
        let { id } = this.props.match.params
        let { ViewFields } = Api.Users
        ViewFields = ViewFields.join(",")

        Axios.get(`/api/v1/users/${id}?_fields=${ViewFields}`)
            .then( this.onDataLoaded.bind(this) )
            .catch( error => {
                HttpErrorHandler(error)
                this.props.history.push('/users')
            })
    }

    selectAll(e) {
        selectText(e.target)
    }

    render() {
        let { user } = this.state
        return (
            <div className="max vertcenter">
            {
                this.state.isLoading ? <Loading /> :
                <div className="max">
                    <h2>View User</h2>
                    <div className="row properties-panel">
                        <div className="col-sm-12">
                            <h4 className="object-form_title">User Properties</h4>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Username:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {user.username}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    First Name:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {user.first_name}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Last Name:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {user.last_name}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Email:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {user.email}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Supervisor:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {user.supervisor ? <i className="fa fa-check"></i> : ""}
                                </div>
                            </div>

                            {
                                user.auth_token &&
                                <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Auth Token:
                                </div>
                                <div className="properties-value col-sm-10">
                                    <span onClick={this.selectAll.bind(this)}>{ user.auth_token }</span>
                                </div>
                            </div>
                            }

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Projects Owned:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {
                                        user.projects_owned.map(
                                            project => (
                                                <span className="comma_separated" key={project._id}>
                                                    <ModelLink model={project} modelName="project" modelKey="name" />
                                                </span>
                                            )
                                        )
                                    }
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Projects Participated In:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {
                                        user.projects_included_into.map(
                                            project => (
                                                <span className="comma_separated" key={project._id}>
                                                    <ModelLink model={project} modelName="project" modelKey="name" />
                                                </span>
                                            )
                                        )
                                    }
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="col-sm-12 form-buttons">
                                {
                                    this.state.user.modification_allowed ? 
                                        <Link to={`/users/${user._id}/edit`} type="submit" className="btn btn-primary">Edit User</Link> :
                                        ""
                                }
                                </div>
                            </div>

                        </div>
                    </div>
                </div>
            }            
            </div>
        )
    }
}