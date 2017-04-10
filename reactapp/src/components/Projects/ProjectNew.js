import React, { Component } from 'react';

import ProjectForm from './ProjectForm';

class ProjectNew extends Component {
    handleSubmit(project) {
        console.log(project);
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