import React, { Component } from 'react'
import PropTypes from 'prop-types'
import '../../Form.css'

import ChildGroupItem from './ChildGroupItem'
import ChildHostItem from './ChildHostItem'

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

    }

    render() {
        return (
            <div className="object-form">
                <h3 className="object-form_title">Group Relations</h3>
                <div className="row">
                    <div className="col-lg-6 col-sm-12">
                        <h4>Children</h4>
                        {
                            this.state.children.map( child => <ChildGroupItem onRemoveTrigger={this.handleGroupRemoveTrigger.bind(this)} key={child._id} group={child} />)
                        }
                    </div>
                    <div className="col-lg-6 col-sm-12">
                        <h4>Hosts</h4>
                        {
                            this.state.hosts.map( host => <ChildHostItem onRemoveTrigger={this.handleHostRemoveTrigger.bind(this)} key={host._id} host={host} />)
                        }
                    </div>
                </div>
            </div>
        )
    }
}

GroupRelationsForm.propTypes = {
    group: PropTypes.shape({
        children: PropTypes.array.isRequired,
        hosts: PropTypes.array.isRequired
    }).isRequired
}