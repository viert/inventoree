import React, { Component } from 'react'
import PropTypes from 'prop-types'
import HostListItem from './HostListItem'

export default class HostListTable extends Component {
    render() {
        return (
            <div className="table-wrapper">
                <table className="table">
                    <thead>
                    <tr>
                        <th className="th-host-fqdn">fqdn</th>
                        <th>location</th>
                        <th>group</th>
                        <th>tags</th>
                        <th>custom fields</th>
                        { this.props.includeDescription ? <th>description</th> : "" }
                    </tr>
                    </thead>
                    <tbody>
                    {
                        this.props.hosts.map((host) => {
                            return (
                                <HostListItem includeDescription={this.props.includeDescription} host={host} key={host._id} />
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
