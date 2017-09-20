import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import Axios from 'axios'

import Api from '../../library/Api'
import HttpErrorHandler from '../../library/HttpErrorHandler'
import UserList from '../common/UserList'
import Loading from '../common/Loading'
import '../common/PropertiesPanel.css'

export default class ProjectView extends Component {
    constructor(props) {
        super(props)
        this.state = {
            project: {
                _id: "",
                name: "",
                email: "",
                root_email: "",
            },
            isLoading: true,
        }
    }

    onDataLoaded(response) {
        let project = response.data.data[0]
        this.setState({
            project,
            isLoading: false
        })
    }

    componentDidMount() {
        let { id } = this.props.match.params
        let { ViewFields } = Api.Projects
        ViewFields = ViewFields.join(",")

        Axios.get(`/api/v1/projects/${id}?_fields=${ViewFields}`)
            .then( this.onDataLoaded.bind(this) )
            .catch( error => {
                HttpErrorHandler(error)
                this.props.history.push('/projects')
            })
    }

    render() {
        let { project } = this.state
        return (
            <div className="max vertcenter">
            {
                this.state.isLoading ? <Loading /> :
                <div className="max">
                    <h2>View Project</h2>
                    <div className="row properties-panel">
                        <div className="col-sm-12">
                            <h4 className="object-form_title">Project Properties</h4>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Name:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {project.name}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Description:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {project.description}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Email:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {project.email}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Root Email:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {project.root_email}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Groups Count:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {project.groups_count}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Owner:
                                </div>
                                <div className="properties-value col-sm-10">
                                    <Link to={`/users/${project.owner._id}`}>
                                        {project.owner.username}
                                    </Link>
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Members:
                                </div>
                                <div className="properties-value col-sm-10">
                                    <UserList users={project.members} />
                                </div>
                            </div>


                            <div className="row properties-line">
                                <div className="col-sm-12 form-buttons">
                                    <Link to={`/projects/${project._id}/edit`} type="submit" className="btn btn-primary">Edit Project</Link>
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