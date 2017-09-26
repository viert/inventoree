import React, { Component } from 'react'
import PropTypes from 'prop-types'
import { Link } from 'react-router-dom'

import CheckBoxIcon from '../common/CheckBoxIcon'
import TagList from '../common/TagList'
import TableModelLink from '../common/TableModelLink'
import CustomFieldList from '../common/CustomFieldList'

export default class HostListItem extends Component {

    selectItem() {
        let { selected, host } = this.props
        selected = !selected
        if (selected)
            this.props.onSelect(host)
        else 
            this.props.onDeselect(host)
        this.props.onSelectStarted()
    }

    render() {
        let { host } = this.props
        return (
            <tr>
                <td className="td-select">
                    <CheckBoxIcon checked={this.props.selected} className="fa" classNameChecked="fa-folder" classNameUnchecked="fa-folder-o" onTrigger={this.selectItem.bind(this)} />
                </td>
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