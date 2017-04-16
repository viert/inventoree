import React, { Component } from 'react';
import Axios from 'axios';
import ProjectForm from './ProjectForm';
import HttpErrorHandler from '../../library/HttpErrorHandler'
import AlertStore from '../../library/AlertBox'

class ProjectEditor extends Component {
    constructor() {
        super();
        this.state = {
            title: "New Project",
            project: {},
            isNew: true
        }
    }

    componentDidMount() {
        var id = this.props.match.params.id;
        if (id && id !== "new") {
            Axios.get('/api/v1/projects/' + id)
                .then((response) => {
                    this.setState({
                        project: response.data.data[0],
                        title: "Edit project",
                        isNew: false
                    })
                })
                .catch(HttpErrorHandler);
        } 
    }

    handleSubmit(project) {
        var action;
        if (project._id) {
            action = Axios.put('/api/v1/projects/' + project._id, project)
        } else {
            action = Axios.post('/api/v1/projects/', project)
        }

        action.then((response) => {
            AlertStore.Notice("Project has been successfully saved")
            this.props.history.push('/projects')
        })
        .catch(HttpErrorHandler)
    }

    handleDestroy(project) {

        console.log('in handledestroy', project)
    }

    render() {
        return (
            <div>
                <h1>{this.state.title}</h1>
                <div className="row">
                    <div className="col-sm-6">
                        <ProjectForm isNew={this.state.isNew} 
                                    onDestroy={this.handleDestroy.bind(this)} 
                                    project={this.state.project} 
                                    onSubmit={this.handleSubmit.bind(this)} />
                    </div>
                </div>
            </div>
        )
    }
}

export default ProjectEditor;