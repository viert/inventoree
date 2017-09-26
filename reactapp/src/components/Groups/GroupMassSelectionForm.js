import React, { Component } from 'react'
import PropTypes from 'prop-types'
import ChildItem from './GroupEdit/ChildItem'
// import ProjectPicker from './GroupEdit/ProjectPicker'
import ConfirmButton from '../common/ConfirmButton'
import AlertStore from '../../library/AlertBox'

const PreventSubmit = e => { e.preventDefault() }

export default class GroupMassSelectionForm extends Component {
    constructor(props) {
        super(props)
        this.state = {
            project: { name: "" },
            projectPicked: false,
            disableSelect: false
        }
        this.timeout = null
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
            AlertStore.Alert("You have to choose a project to move to")
        } else {
            this.props.onMoveToProject(this.state.project)
        }
    }

    onTriggerMouseEnter(e) {
        if (this.timeout) {
            clearTimeout(this.timeout)
            this.timeout = null
        }
        this.setState({ disableSelect: true })
    }

    onTriggerMouseLeave(e) {
        this.timeout = setTimeout(
            this.setState.bind(this, { disableSelect: false }),
            50
        )
    }

    onRemove(group) {
        this.props.onRemove(group)
    }

    render() {
        return (
            <div className="selection-table">
                <h3>Selected Groups</h3>
                {
                    Object.values(this.props.groups).map( group => {
                        group.removed = false
                        return <ChildItem key={group._id}
                                    text={group.name}
                                    removed={group.removed}
                                    onRemoveTrigger={this.onRemove.bind(this, group)}
                                    disableSelect={this.state.disableSelect}
                                    onMouseEnter={this.onTriggerMouseEnter.bind(this)}
                                    onMouseLeave={this.onTriggerMouseLeave.bind(this)} />
                    })
                }
                <div className="selection-actions">
                {
                //     <h4>Move to project</h4>
                //     <form onSubmit={PreventSubmit} className="form-horizontal">
                //         <div className={"row form-group" + (this.state.projectPicked ? " has-success": "")}>
                //             <div className="col-sm-8">
                //                 <ProjectPicker
                //                         value={this.state.project.name}
                //                         onDataPicked={this.handleProjectPicked.bind(this)}
                //                         onDataClear={this.handleProjectClear.bind(this)}
                //                         placeholder="Choose project" />
                //             </div>
                //             <div className="col-sm-4 text-right">
                //                 <ConfirmButton onClick={this.handleMove.bind(this)} buttonType="submit" className="btn btn-primary">Move</ConfirmButton>
                //             </div>
                //         </div>
                //     </form>
                }
                    <h4>Destroy</h4>
                    <form onSubmit={PreventSubmit} className="form-horizontal">
                        <div className="row form-group">
                            <div className="col-sm-12 text-right">
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
    groups: PropTypes.object.isRequired,
    onRemove: PropTypes.func.isRequired,
    onMoveToProject: PropTypes.func.isRequired,
    onDestroy: PropTypes.func.isRequired
}