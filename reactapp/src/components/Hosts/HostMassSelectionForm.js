import React, { Component } from 'react'
import PropTypes from 'prop-types'
import ChildItem from '../Groups/GroupEdit/ChildItem'
import GroupPicker from '../Groups/GroupEdit/GroupPicker'
import ConfirmButton from '../common/ConfirmButton'
import AlertStore from '../../library/AlertBox'

import '../common/MassSelectionForm.css'

const PreventSubmit = e => { e.preventDefault() }

export default class HostMassSelectionForm extends Component {

    constructor(props) {
        super(props)
        this.state = {
            group: { name: "" },
            groupPicked: false,
            disableSelect: false
        }
        this.timeout = null
    }

    handleGroupPicked(group) {
        this.setState({ group, groupPicked: true })
    }

    handleGroupClear() {
        this.setState({ group: { name: "" }, groupPicked: false })
    }

    handleDestroy(e) {
        e.preventDefault()
        this.props.onDestroy()
    }

    handleMove(e) {
        e.preventDefault()
        if (!this.state.groupPicked) {
            AlertStore.Alert("You have to choose a group to move to")
        } else {
            this.props.onMoveToGroup(this.state.group)
        }
    }

    handleDetach(e) {
        e.preventDefault()
        this.props.onDetach()
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
                <h3>Selected Hosts</h3>
                {
                    Object.values(this.props.hosts).map( host => 
                        <ChildItem key={host._id}
                                    text={host.fqdn}
                                    removed={false}
                                    onRemoveTrigger={this.onRemove.bind(this, host)}
                                    disableSelect={this.state.disableSelect}
                                    onMouseEnter={this.onTriggerMouseEnter.bind(this)}
                                    onMouseLeave={this.onTriggerMouseLeave.bind(this)} />
                    )
                }
                <div className="selection-actions">
                    <h4>Move to group</h4>
                    <form onSubmit={PreventSubmit} className="form-horizontal">
                        <div className={"row form-group" + (this.state.projectPicked ? " has-success": "")}>
                            <div className="col-sm-8">
                                <GroupPicker
                                        value={this.state.group.name}
                                        onDataPicked={this.handleGroupPicked.bind(this)}
                                        onDataClear={this.handleGroupClear.bind(this)}
                                        placeholder="Choose group" />
                            </div>
                            <div className="col-sm-4 text-right">
                                <ConfirmButton onClick={this.handleMove.bind(this)} buttonType="submit" className="btn btn-primary">Move</ConfirmButton>
                            </div>
                        </div>
                    </form>
                    <h4>Detach hosts</h4>
                    <form onSubmit={PreventSubmit} className="form-horizontal">
                        <div className={"row form-group" + (this.state.projectPicked ? " has-success": "")}>
                            <div className="col-sm-12 text-right">
                                <ConfirmButton onClick={this.handleDetach.bind(this)} buttonType="submit" className="btn btn-danger">Detach</ConfirmButton>
                            </div>
                        </div>
                    </form>
                    <h4>Destroy hosts</h4>
                    <form onSubmit={PreventSubmit} className="form-horizontal">
                        <div className={"row form-group" + (this.state.projectPicked ? " has-success": "")}>
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

HostMassSelectionForm.propTypes = {
    hosts: PropTypes.object.isRequired,
    onRemove: PropTypes.func.isRequired,
    onMoveToGroup: PropTypes.func.isRequired,
    onDetach: PropTypes.func.isRequired,
    onDestroy: PropTypes.func.isRequired
}