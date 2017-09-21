import React, { Component } from 'react'
import PropTypes from 'prop-types'
import '../../Form.css'

import ChildItem from '../../Groups/GroupEdit/ChildItem'
import UserPicker from './UserPicker'

const preventSubmit = e => { e.preventDefault() }

export default class ProjectMembersForm extends Component {
    constructor(props) {
        super(props)
        let { members } = props.project
        members.forEach( item => { item.removed = false })
        this.state = {
            members,
            disableSelect: false
        }
        this.timeout = null
    }

    componentWillReceiveProps(props) {
        let { members } = props.project
        members.forEach( item => { item.removed = false })
        this.setState({ members })
    }

    handleMemberRemoveTrigger(user) {
        let { members } = this.state
        members.forEach( item => {
            if (item._id === user._id) {
                item.removed = !item.removed
            }
        })
        this.setState({ members })
    }

    memberAddPicked(user) {
        let { members } = this.state
        if ( members.filter( item => item._id === user._id).length === 0) {
            user.removed = false
            members.push(user)
            this.setState({ members })
        }
    }

    handleSubmitData() {
        let member_ids = this.state.members.filter( item => item.removed === false ).map( item => item._id )
        this.props.onSubmitData(member_ids)
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

    render() {
        return (
            <form className="object-form form-horizontal" onSubmit={preventSubmit}>
                <h4 className="object-form_title">Project Members</h4>
                <div className="row">
                    <div className="col-lg-6 col-sm-12">
                        <div className="form-group">
                            <div className="col-sm-12">
                                <UserPicker 
                                    value=""
                                    clearOnPick={true}
                                    placeholder="Add Project Member"
                                    showField="username"
                                    onDataPicked={this.memberAddPicked.bind(this)} />
                                <div className="children-list">
                                    {
                                    this.state.members.map( child => 
                                        <ChildItem 
                                            key={child._id}
                                            onRemoveTrigger={this.handleMemberRemoveTrigger.bind(this, child)} 
                                            text={child.username}
                                            removed={child.removed}
                                            disableSelect={this.state.disableSelect}
                                            onMouseEnter={this.onTriggerMouseEnter.bind(this)}
                                            onMouseLeave={this.onTriggerMouseLeave.bind(this)} /> )
                                    }
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="form-group">
                    <div className="col-sm-12 form-buttons">
                        <button type="button" onClick={this.handleSubmitData.bind(this)} className="btn btn-primary">
                        Save changes
                        </button>
                    </div>
                </div>

            </form>
        )
    }
}

ProjectMembersForm.propTypes = {
    project: PropTypes.shape({
        members: PropTypes.array.isRequired,
    }).isRequired,
    onSubmitData: PropTypes.func.isRequired
}