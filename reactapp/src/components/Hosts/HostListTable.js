import React, { Component } from 'react'
import PropTypes from 'prop-types'

import HostListItem from './HostListItem'
import CheckBoxIcon from '../common/CheckBoxIcon'

export default class HostListTable extends Component {
    constructor(props) {
        super(props)
        let allSelected = this.allSelectedOnPage(props)
        this.state = {
            allSelected,
            selectionMode: false
        }
    }

    allSelectedOnPage(props) {
        for (var i = 0; i < props.hosts.length; i++) {
            let host = props.hosts[i]
            if (!(host._id in props.selected)) {
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
            let hostsToSelect = []
            this.props.hosts.forEach( host => {
                if (!(host._id in this.props.selected)) {
                    hostsToSelect.push(host)
                }
            })
            this.props.onSelect(hostsToSelect)
        } else {
            let hostsToDeselect = []
            this.props.hosts.forEach( host => {
                if (host._id in this.props.selected) {
                    hostsToDeselect.push(host)
                }
            })
            this.props.onDeselect(hostsToDeselect)
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
            <div className="table-wrapper">
                <table style={{userSelect}} className="table listtable">
                    <thead>
                    <tr>
                        <th className="th-select">
                            <CheckBoxIcon checked={this.state.allSelected} className="fa" classNameChecked="fa-folder" classNameUnchecked="fa-folder-o" onTrigger={this.triggerAll.bind(this)} />
                        </th>
                        <th className="th-host-fqdn">fqdn</th>
                        <th>location</th>
                        <th className="th-group-name">group</th>
                        <th className="th-tags">tags</th>
                        <th className="th-custom-fields">custom fields</th>
                        { 
                            this.props.includeDescription ? <th>description</th> : "" 
                        }
                    </tr>
                    </thead>
                    <tbody>
                    {
                        this.props.hosts.map((host) => {
                            let selected = typeof this.props.selected[host._id] !== "undefined"
                            return (
                                <HostListItem 
                                    selected={selected} 
                                    includeDescription={this.props.includeDescription} 
                                    onSelectStarted={this.handleSelectStarted.bind(this)} 
                                    onDeselect={this.props.onDeselect} 
                                    onSelect={this.props.onSelect} 
                                    host={host} 
                                    key={host._id} />
                            )
                        })
                    }
                    </tbody>
                </table>
            </div>
        )
    }
}

HostListTable.propTypes = {
    hosts: PropTypes.array.isRequired,
    includeDescription: PropTypes.bool
}
