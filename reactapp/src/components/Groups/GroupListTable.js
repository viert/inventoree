import React, { Component } from 'react'
import PropTypes from 'prop-types'

import GroupListItem from './GroupListItem'
import CheckBoxIcon from '../common/CheckBoxIcon'

export default class GroupListTable extends Component {
    constructor(props) {
        super(props)
        let allSelected = this.allSelectedOnPage(props)
        this.state = {
            allSelected,
            selectionMode: false
        }
    }

    allSelectedOnPage(props) {
        for (var i = 0; i < props.groups.length; i++) {
            let group = props.groups[i]
            if (!(group._id in props.selected)) {
                return false
            }
        }
        return true
    }

    componentWillReceiveProps(props) {
        let allSelected = this.allSelectedOnPage(props)
        this.setState({ allSelected })
    }

    triggerAll() {
        let {allSelected} = this.state
        allSelected = !allSelected
        if (allSelected) {
            let groupsToSelect = []
            this.props.groups.forEach( group => {
                if (!(group._id in this.props.selected)) {
                    groupsToSelect.push(group)
                }
            })
            this.props.onSelect(groupsToSelect)
        } else {
            let groupsToDeselect = []
            this.props.groups.forEach( group => {
                if (group._id in this.props.selected) {
                    groupsToDeselect.push(group)
                }
            })
            this.props.onDeselect(groupsToDeselect)
        }
    }

    handleSelectStarted() {
        this.setState({
            selectionMode: true
        })
    }

    handleSelectFinished() {
        this.setState({
            selectionMode: false
        })
    }

    render() {
        let userSelect = this.state.selectionMode ? "none" : "inherit"
        return (
            <table style={{userSelect}} className="table" onMouseUp={this.handleSelectFinished.bind(this)}>
                <thead>
                <tr>
                    <th className="th-group-select">
                        <CheckBoxIcon checked={this.state.allSelected} className="fa" classNameChecked="fa-folder" classNameUnchecked="fa-folder-o" onTrigger={this.triggerAll.bind(this)} />
                    </th>
                    <th className="th-group-name">name</th>
                    <th className="th-name">project</th>
                    <th>tags</th>
                    <th>custom fields</th>
                </tr>
                </thead>
                <tbody>
                {
                    this.props.groups.map((group) => {
                        let selected = typeof this.props.selected[group._id] !== "undefined"
                        return (
                            <GroupListItem selected={selected} onSelectStarted={this.handleSelectStarted.bind(this)} onDeselect={this.props.onDeselect} onSelect={this.props.onSelect} group={group} key={group._id} />
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
    selected: PropTypes.object.isRequired,
    onSelect: PropTypes.func.isRequired,
    onDeselect: PropTypes.func.isRequired,
}