import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

export default class HostListItem extends Component {
    render() {
        return (
            <tr>
                <td>
                    <Link to={"/hosts/" + this.props.host._id}>
                    {this.props.host.fqdn}
                    </Link>
                </td>
                <td>{this.props.host.datacenter_name}</td>
                <td>{this.props.host.group_name}</td>
                <td>{this.props.host.description}</td>
            </tr>
        )
    }
}

HostListItem.propTypes = {
    host: PropTypes.shape({
        _id: PropTypes.string.isRequired,
        fqdn: PropTypes.string.isRequired,
        short_name: PropTypes.string,
        group_name: PropTypes.string,
    })
}