import React, { Component } from 'react'
import PropTypes from 'prop-types'

import GroupListItem from './GroupListItem'
import CheckBoxIcon from '../common/CheckBoxIcon'

export default class GroupListTable extends Component {
    constructor(props) {
        super(props)
        let selectedLen = props.groups.filter( group => group.selected === true ).length
        let allSelected = selectedLen === props.groups.length
        this.state = {
            allSelected
        }
    }

    componentWillReceiveProps(props) {
        let selectedLen = props.groups.filter( group => group.selected === true ).length
        let allSelected = selectedLen === props.groups.length
        this.setState({ allSelected })
    }

    triggerAll() {
        let {allSelected} = this.state
        allSelected = !allSelected
        if (allSelected) {
            let groupsToSelect = []
            this.props.groups.forEach( group => {
                if (!group.selected) {
                    groupsToSelect.push(group)
                }
            })
            this.props.onSelect(groupsToSelect)
        } else {
            let groupsToDeselect = []
            this.props.groups.forEach( group => {
                if (group.selected) {
                    groupsToDeselect.push(group)
                }
            })
            this.props.onDeselect(groupsToDeselect)
        }
    }

    render() {
        return (
            <table className="table">
                <thead>
                <tr>
                    <th className="th-group-select">
                        <CheckBoxIcon checked={this.state.allSelected} className="fa" classNameChecked="fa-folder" classNameUnchecked="fa-folder-o" onTrigger={this.triggerAll.bind(this)} />
                    </th>
                    <th className="th-group-name">name</th>
                    <th className="th-name">project</th>
                    <th>description</th>
                </tr>
                </thead>
                <tbody>
                {
                    this.props.groups.map((group) => {
                        return (
                            <GroupListItem onDeselect={this.props.onDeselect} onSelect={this.props.onSelect} group={group} key={group._id} />
                        )
                    })
                }
                </tbody>
            </table>
        )
    }
}

GroupListTable.propTypes = {
    groups: PropTypes.array.isRequired,
    onSelect: PropTypes.func.isRequired,
    onDeselect: PropTypes.func.isRequired,
}