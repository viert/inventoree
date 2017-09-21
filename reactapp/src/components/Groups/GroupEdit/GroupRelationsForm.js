import React, { Component } from 'react'
import PropTypes from 'prop-types'
import '../../Form.css'
import './GroupRelationsForm.css'

import ChildItem from './ChildItem'
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
            hosts,
            disableSelect: false
        }
        this.timeout = null
    }

    componentWillReceiveProps(props) {
        let { children, hosts } = props.group
        children.forEach( item => { item.removed = false })
        hosts.forEach( item => { item.removed = false })
        this.setState({ children, hosts })
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
                <h4 className="object-form_title">Group Relations</h4>
                <div className="row">
                    <div className="col-lg-6 col-sm-12">
                        <div className="form-group">
                            <div className="col-sm-12">
                                <GroupPicker 
                                    value=""
                                    clearOnPick={true}
                                    placeholder="Add Child Group"
                                    onDataPicked={this.groupAddPicked.bind(this)} />
                                <div className="children-list">
                                    <h5>Children</h5>
                                    {
                                    this.state.children.map( child => 
                                        <ChildItem 
                                            key={child._id}
                                            onRemoveTrigger={this.handleGroupRemoveTrigger.bind(this, child)} 
                                            text={child.name}
                                            removed={child.removed}
                                            disableSelect={this.state.disableSelect}
                                            onMouseEnter={this.onTriggerMouseEnter.bind(this)}
                                            onMouseLeave={this.onTriggerMouseLeave.bind(this)} /> )
                                    }
                                </div>
                            </div>
                        </div>
                    </div>
                    <div className="col-lg-6 col-sm-12">
                        <div className="form-group">
                            <div className="col-sm-12">
                                <HostPicker 
                                    value=""
                                    showField="fqdn"
                                    clearOnPick={true}
                                    placeholder="Add Host"
                                    onDataPicked={this.hostAddPicked.bind(this)} />
                                <div className="children-list">
                                    <h5>Hosts</h5>
                                    {
                                    this.state.hosts.map( host =>
                                        <ChildItem
                                            key={host._id}
                                            onRemoveTrigger={this.handleHostRemoveTrigger.bind(this, host)}
                                            text={host.fqdn}
                                            removed={host.removed}
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

GroupRelationsForm.propTypes = {
    group: PropTypes.shape({
        children: PropTypes.array.isRequired,
        hosts: PropTypes.array.isRequired
    }).isRequired,
    onSubmitData: PropTypes.func.isRequired
}