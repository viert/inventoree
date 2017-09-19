import React, { Component } from 'react'
import PropTypes from 'prop-types'
import TagList from '../common/TagList'
import CustomFieldList from '../common/CustomFieldList'
import TableModelLink from '../common/TableModelLink'

export default class HostListItem extends Component {
    render() {
        return (
            <tr>
                <td>
                    <TableModelLink modelName="host" modelId={this.props.host._id} showEditLink={this.props.host.modification_allowed}>
                        {this.props.host.fqdn}
                    </TableModelLink>
                </td>
                <td>{this.props.host.datacenter_name}</td>
                <td>{this.props.host.group_name}</td>
                <td><TagList tags={this.props.host.all_tags} nowrap={true} /></td>
                <td><CustomFieldList fields={this.props.host.all_custom_fields} mini={true} /></td>
            </tr>
        )
    }
}

HostListItem.propTypes = {
    host: PropTypes.shape({
        _id: PropTypes.string.isRequired,
        fqdn: PropTypes.string.isRequired,
        group_name: PropTypes.string,
    })
}