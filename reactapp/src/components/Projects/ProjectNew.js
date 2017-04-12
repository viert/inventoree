import React, { Component } from 'react';
import Axios from 'axios';
import ProjectForm from './ProjectForm';
import HttpErrorHandler from '../../library/HttpErrorHandler'

class ProjectNew extends Component {
    handleSubmit(project) {
        Axios.post('/api/v1/projects/', project)
            .then((data) => {
                console.log(data);
            })
            .catch(HttpErrorHandler.bind(this));
        this.props.history.push('/projects');
    }

    render() {
        return (
            <div>
                <h1>Create Project</h1>
                <div className="row">
                    <div className="col-sm-6">
                        <ProjectForm onSubmit={this.handleSubmit.bind(this)} />
                    </div>
                </div>
            </div>
        )
    }
}

export default ProjectNew;