import React, { Component } from 'react'
import PropTypes from 'prop-types'
import '../../Form.css';
import ConfirmButton from '../../common/ConfirmButton'
import TagEditor from '../../common/TagEditor'
import ProjectPicker from './ProjectPicker'

export default class GroupForm extends Component {
    constructor(props) {
        super(props)
        let projectPicked = props.group.project._id ? true : false
        this.state = {
            group: props.group,
            projectPicked
        }
    }

    handleFieldChange(e) {
        let group = this.state.group;
        switch (e.target.id) {
            case "inputGroupName":
                group.name = e.target.value;
                break;
            case "inputGroupDesc":
                group.description = e.target.value;
                break;
            default:
                break;
        }
        this.setState({
            group
        })
    }

    addTag(tag) {
        let { group } = this.state
        group.tags.push(tag)
        this.setState({
            group
        })
    }

    removeTag(tag) {
        let { group } = this.state
        let ind = group.tags.indexOf(tag)
        if (ind >= 0) {
            group.tags.splice(ind,1)
            this.setState({
                group
            })
        }
    }


    handleSubmit(e) {
        e.preventDefault();
        this.props.onSubmit(this.state.group);
    }

    handleDestroy(e) {
        e.preventDefault();
        this.props.onDestroy(this.state.group)
    }

    handleProjectPicked(project) {
        let { group } = this.state
        group.project_id = project._id
        this.setState({
            group,
            projectPicked: true
        })
    }

    handleProjectClear(project) {
        let { group } = this.state
        group.project_id = null
        this.setState({
            group,
            projectPicked: false
        })
    }


    render() {
        return (
            <form onSubmit={this.handleSubmit.bind(this)} className="form-horizontal object-form">
                <h4 className="object-form_title">Group Properties</h4>
                <div className="form-group">
                    <label htmlFor="inputGroupName" className="col-sm-3 control-label">
                        Name:
                    </label>
                    <div className="col-sm-9">
                        <input onChange={this.handleFieldChange.bind(this)} ref="firstInput" type="text" value={this.state.group.name} id="inputGroupName" className="form-control" placeholder="Group name" />
                    </div>
                </div>
                <div className="form-group">
                    <label htmlFor="inputGroupDesc" className="col-sm-3 control-label">
                        Description:
                    </label>
                    <div className="col-sm-9">
                        <input onChange={this.handleFieldChange.bind(this)} type="text" value={this.state.group.description} id="inputGroupDesc" className="form-control" placeholder="Description" />
                    </div>
                </div>
                <div className="form-group">
                    <label htmlFor="inputGroupDesc" className="col-sm-3 control-label">
                        Tags:
                    </label>
                    <div className="col-sm-9">
                        <TagEditor 
                                tags={this.state.group.tags}
                                onAdd={this.addTag.bind(this)}
                                onRemove={this.removeTag.bind(this)} />
                    </div>
                </div>
                <div className={"form-group" + (this.state.projectPicked ? " has-success": "")}>
                    <label className="col-sm-3 control-label">
                        Project:
                    </label>
                    <div className="col-sm-9">
                        <ProjectPicker
                                    value={this.state.group.project.name}
                                    onDataPicked={this.handleProjectPicked.bind(this)}
                                    onDataClear={this.handleProjectClear.bind(this)}
                                    placeholder="Choose project" />
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

GroupForm.propTypes = {
    isNew: PropTypes.bool.isRequired,
    group: PropTypes.shape({
        name: PropTypes.string,
        description: PropTypes.string,
        tags: PropTypes.array
    }),
    onSubmit: PropTypes.func.isRequired,
    onDestroy: PropTypes.func.isRequired
}