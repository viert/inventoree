import React, { Component } from 'react';
import '../Form.css';

var EMPTY_PROJECT = {
    name: "",
    email: "",
    root_email: ""
}

class ProjectForm extends Component {
    componentWillMount() {
        if (this.props.project) {
            this.setState({
                project: this.props.project
            })
        } else {
            this.setState({
                project: EMPTY_PROJECT
            })
        }
    }
    componentDidMount() {
        this.refs.firstInput.focus();
    }

    handleFieldChange(e) {
        var project = this.state.project;
        switch (e.target.id) {
            case "inputProjectName":
                project.name = e.target.value;
                break;
            case "inputProjectEmail":
                project.email = e.target.value;
                break;
            case "inputProjectRootEmail":
                project.root_email = e.target.value;
                break;
            default:
                break;
        }
        this.setState({
            project: project
        })
    }

    handleSubmit(e) {
        e.preventDefault();
        if (this.props.onSubmit) {
            this.props.onSubmit(this.state.project);
        }
    }

    render() {
        return (
            <form onChange={this.handleFieldChange.bind(this)} onSubmit={this.handleSubmit.bind(this)} className="form-horizontal object-form">
                <div className="form-group">
                    <label htmlFor="inputProjectName" className="col-sm-2 control-label">
                        Name:
                    </label>
                    <div className="col-sm-10">
                        <input ref="firstInput" type="text" value={this.state.project.name} id="inputProjectName" className="form-control" placeholder="Project name" />
                    </div>
                </div>
                <div className="form-group">
                    <label htmlFor="inputProjectEmail" className="col-sm-2 control-label">
                        Email:
                    </label>
                    <div className="col-sm-10">
                        <input type="text" value={this.state.project.email} id="inputProjectEmail" className="form-control" placeholder="Email" />
                    </div>
                </div>
                <div className="form-group">
                    <label htmlFor="inputProjectRootEmail" className="col-sm-2 control-label">
                        Root Email:
                    </label>
                    <div className="col-sm-10">
                        <input type="text" value={this.state.project.root_email} id="inputProjectRootEmail" className="form-control" placeholder="Root Email" />
                    </div>
                </div>
                <div className="form-group">
                    <div className="col-sm-10 col-sm-offset-2">
                        <button type="submit" className="btn btn-primary uppercase">Save project</button>
                    </div>
                </div>
            </form> 
        )
    }
}

export default ProjectForm;