import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'
import TagList from '../common/TagList'
import CustomFieldList from '../common/CustomFieldList'
import TableModelLink from '../common/TableModelLink'

export default class HostListItem extends Component {
    render() {
        let { host } = this.props
        return (
            <tr>
                <td>
                    <TableModelLink modelName="host" modelId={host._id} showEditLink={host.modification_allowed}>
                        {host.fqdn}
                    </TableModelLink>
                </td>
                <td>{host.datacenter_name}</td>
                <td>
                    {
                        host.group ? 
                        <Link to={`/groups/${this.props.host.group._id}`}>
                            {this.props.host.group.name}
                        </Link> : ""
                    }
                </td>
                <td><TagList tags={host.all_tags} nowrap={true} /></td>
                <td><CustomFieldList fields={host.all_custom_fields} mini={true} /></td>
                {
                    this.props.includeDescription ? <td>{ host.description } </td> : ""
                }
            </tr>
        )
    }
}

HostListItem.propTypes = {
    host: PropTypes.shape({
        _id: PropTypes.string.isRequired,
        fqdn: PropTypes.string.isRequired,
        group_name: PropTypes.string,
    }),
    includeDescription: PropTypes.bool
}