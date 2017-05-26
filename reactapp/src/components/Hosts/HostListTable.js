import React, { Component } from 'react'
import PropTypes from 'prop-types'
import HostListItem from './HostListItem'

export default class HostListTable extends Component {
    render() {
        return (
            <table className="table">
                <thead>
                <tr>
                    <th className="th-name">fqdn</th>
                    <th>datacenter</th>
                    <th>group</th>
                    <th>description</th>
                </tr>
                </thead>
                <tbody>
                {
                    this.props.hosts.map((host) => {
                        return (
                            <HostListItem host={host} key={host._id} />
                        )
                    })
                }
                </tbody>
            </table>
        )
    }
}

HostListTable.propTypes = {
    hosts: PropTypes.array.isRequired
}
