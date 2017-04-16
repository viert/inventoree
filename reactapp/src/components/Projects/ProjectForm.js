import React, { Component } from 'react';
import '../Form.css';
import ConfirmButton from '../common/ConfirmButton'

class ProjectForm extends Component {
    constructor(props) {
        super(props);
        this.state = { project: props.project }
    }

    componentWillReceiveProps(props) {
        if (props.project) {
            this.setState({
                project: props.project
            })
        } else {
            this.setState({
                project: {
                    name: "",
                    email: "",
                    root_email: "",
                    description: ""
                }
            })
        }
    }

    componentDidMount() {
        this.refs.firstInput.focus();
    }

    handleFieldChange(e) {
        var state = this.state.project;
        switch (e.target.id) {
            case "inputProjectName":
                state.name = e.target.value;
                break;
            case "inputProjectEmail":
                state.email = e.target.value;
                break;
            case "inputProjectRootEmail":
                state.root_email = e.target.value;
                break;
            case "inputProjectDesc":
                state.description = e.target.value;
                break;
            default:
                break;
        }
        this.setState({
            project: state
        })
    }

    handleSubmit(e) {
        e.preventDefault();
        if (this.props.onSubmit) {
            this.props.onSubmit(this.state.project);
        }
    }

    handleDestroy(e) {
        e.preventDefault();
        if (this.props.onDestroy) {
            this.props.onDestroy(this.state.project)
        }
    }

    render() {
        return (
            <form onChange={this.handleFieldChange.bind(this)} onSubmit={this.handleSubmit.bind(this)} className="form-horizontal object-form">
                <div className="form-group">
                    <label htmlFor="inputProjectName" className="col-sm-3 control-label">
                        Name:
                    </label>
                    <div className="col-sm-9">
                        <input ref="firstInput" type="text" value={this.state.project.name} id="inputProjectName" className="form-control" placeholder="Project name" />
                    </div>
                </div>
                <div className="form-group">
                    <label htmlFor="inputProjectEmail" className="col-sm-3 control-label">
                        Email:
                    </label>
                    <div className="col-sm-9">
                        <input type="text" value={this.state.project.email} id="inputProjectEmail" className="form-control" placeholder="Email" />
                    </div>
                </div>
                <div className="form-group">
                    <label htmlFor="inputProjectRootEmail" className="col-sm-3 control-label">
                        Root Email:
                    </label>
                    <div className="col-sm-9">
                        <input type="text" value={this.state.project.root_email} id="inputProjectRootEmail" className="form-control" placeholder="Root Email" />
                    </div>
                </div>
                <div className="form-group">
                    <label htmlFor="inputProjectDesc" className="col-sm-3 control-label">
                        Description:
                    </label>
                    <div className="col-sm-9">
                        <input type="text" value={this.state.project.description} id="inputProjectDesc" className="form-control" placeholder="Description" />
                    </div>
                </div>
                <div className="form-group">
                    <div className="col-sm-9 col-sm-offset-3 form-buttons">
                        <button type="submit" className="btn btn-primary">Save</button>
                        { this.props.isNew ? '': <ConfirmButton onClick={this.handleDestroy.bind(this)} className="btn btn-danger">Destroy</ConfirmButton> }
                    </div>
                </div>
            </form> 
        )
    }
}

export default ProjectForm;