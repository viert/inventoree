import React, { Component } from 'react'
import PropTypes from 'prop-types'
import '../../Form.css'
import './GroupRelationsForm.css'

import ChildGroupItem from './ChildGroupItem'
import ChildHostItem from './ChildHostItem'
import GroupPicker from './GroupPicker'
import HostPicker from './HostPicker'

const preventSubmit = e => { e.preventDefault() }

export default class GroupRelationsForm extends Component {
    constructor(props) {
        super(props)
        let { children, hosts } = props.group
        children.forEach( item => { item.removed = false })
        hosts.forEach( item => { item.removed = false })
        this.state = {
            children,
            hosts
        }
    }

    handleGroupRemoveTrigger(group) {
        let { children } = this.state
        children.forEach( item => {
            if (item._id === group._id) {
                item.removed = !item.removed
            }
        })
        this.setState({
            children
        })
    }

    handleHostRemoveTrigger(host) {
        let { hosts } = this.state
        hosts.forEach( item => {
            if (item._id === host._id) {
                item.removed = !item.removed
            }
        })
        this.setState({
            hosts
        })
    }

    groupAddPicked(group) {
        let { children } = this.state
        if ( children.filter( item => item._id === group._id ).length === 0) {
            group.removed = false
            children.push(group)
            this.setState({
                children
            })
        }
    }

    hostAddPicked(host) {
        let { hosts } = this.state
        if ( hosts.filter( item => item._id === host._id).length === 0) {
            host.removed = false
            hosts.push(host)
            this.setState({
                hosts
            })
        }
    }

    handleSubmitData() {
        let child_ids = this.state.children.filter( item => item.removed === false ).map( item => item._id )
        let host_ids = this.state.hosts.filter( item => item.removed === false ).map( item => item._id )
        this.props.onSubmitData(child_ids, host_ids)
    }

    render() {
        return (
            <form className="object-form form-horizontal" onSubmit={preventSubmit}>
                <h3 className="object-form_title">Group Relations</h3>
                <div className="row">
                    <div className="col-lg-6 col-sm-12">
                        <div className="form-group">
                            <div className="col-sm-12">
                                <h4>Children</h4>
                                <GroupPicker 
                                    value=""
                                    clearOnPick={true}
                                    placeholder="Add Group"
                                    onDataPicked={this.groupAddPicked.bind(this)} />
                                <div className="children-list">
                                {
                                    this.state.children.map( child => <ChildGroupItem onRemoveTrigger={this.handleGroupRemoveTrigger.bind(this)} key={child._id} group={child} />)
                                }
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-lg-6 col-sm-12">
                        <div className="form-group">
                            <div className="col-sm-12">
                                <h4>Hosts</h4>
                                <HostPicker 
                                    value=""
                                    showField="fqdn"
                                    clearOnPick={true}
                                    placeholder="Add Host"
                                    onDataPicked={this.hostAddPicked.bind(this)} />
                                <div className="children-list">
                                {
                                    this.state.hosts.map( host => <ChildHostItem onRemoveTrigger={this.handleHostRemoveTrigger.bind(this)} key={host._id} host={host} />)
                                }
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
                <div className="form-group">
                    <div className="col-sm-12 form-buttons">
                        <button onClick={this.handleSubmitData.bind(this)} className="btn btn-primary">
                        Save changes
                        </button>
                    </div>
                </div>

            </form>
        )
    }
}

GroupRelationsForm.propTypes = {
    group: PropTypes.shape({
        children: PropTypes.array.isRequired,
        hosts: PropTypes.array.isRequired
    }).isRequired,
    onSubmitData: PropTypes.func.isRequired
}