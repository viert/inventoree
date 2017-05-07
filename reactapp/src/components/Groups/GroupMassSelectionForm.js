import React, { Component } from 'react'
import PropTypes from 'prop-types'
import ChildGroupItem from './GroupEdit/ChildGroupItem'
import ProjectPicker from './GroupEdit/ProjectPicker'
import ConfirmButton from '../common/ConfirmButton'
import AlertStore from '../../library/AlertBox'

const PreventSubmit = e => { e.preventDefault() }

export default class GroupMassSelectionForm extends Component {
    constructor(props) {
        super(props)
        this.state = {
            project: { name: "" },
            projectPicked: false
        }
    }

    handleProjectPicked(project) {
        this.setState({ project, projectPicked: true })
    }

    handleProjectClear() {
        this.setState({ project: { name: "" }, projectPicked: false })
    }

    handleDestroy(e) {
        e.preventDefault()
        this.props.onDestroy()
    }

    handleMove(e) {
        e.preventDefault()
        if (!this.state.projectPicked) {
            AlertStore.Alert("You have to choose a project to move first")
        } else {
            this.props.onMoveToProject(this.state.project)
        }
    }

    render() {
        return (
            <div className="selection-table">
                <h3>Selected Groups</h3>
                {
                    this.props.groups.map( group => {
                        group.removed = false
                        return <ChildGroupItem key={group._id} onRemoveTrigger={this.props.onRemove} group={group} />
                    })
                }
                <div className="selection-actions">
                    <h4>Move to project</h4>
                    <form onSubmit={PreventSubmit} className="form-horizontal">
                        <div className={"row form-group" + (this.state.projectPicked ? " has-success": "")}>
                            <div className="col-sm-8">
                                <ProjectPicker
                                        value={this.state.project.name}
                                        onDataPicked={this.handleProjectPicked.bind(this)}
                                        onDataClear={this.handleProjectClear.bind(this)}
                                        placeholder="Choose project" />
                            </div>
                            <div className="col-sm-4 text-right">
                                <ConfirmButton onClick={this.handleMove.bind(this)} buttonType="submit" className="btn btn-primary">Move</ConfirmButton>
                            </div>
                        </div>
                    </form>
                    <h4>Destroy</h4>
                    <form onSubmit={PreventSubmit} className="form-horizontal">
                        <div className="row form-group">
                            <div className="col-sm-8">
                                <input type="text" ref="confirmText" placeholder="Type: I am sane" className="form-control" />
                            </div>
                            <div className="col-sm-4 text-right">
                                <ConfirmButton onClick={this.handleDestroy.bind(this)} buttonType="submit" className="btn btn-danger">Destroy</ConfirmButton>
                            </div>
                        </div>
                    </form>
                </div>
            </div>
        )
    }
}

GroupMassSelectionForm.propTypes = {
    groups: PropTypes.array.isRequired,
    onRemove: PropTypes.func.isRequired,
    onMoveToProject: PropTypes.func.isRequired,
    onDestroy: PropTypes.func.isRequired
}