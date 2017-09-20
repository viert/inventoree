import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'

import CheckBoxIcon from '../common/CheckBoxIcon'
import TagList from '../common/TagList'
import TableModelLink from '../common/TableModelLink'
import CustomFieldList from '../common/CustomFieldList'

export default class GroupListItem extends Component {

    selectItem() {
        let { selected, group } = this.props
        selected = !selected
        if (selected)
            this.props.onSelect(group)
        else 
            this.props.onDeselect(group)
        this.props.onSelectStarted()
    }

    render() {
        let { group } = this.props
        return (
            <tr>
                <td className="td-group-select">
                    <CheckBoxIcon checked={this.props.selected} className="fa" classNameChecked="fa-folder" classNameUnchecked="fa-folder-o" onTrigger={this.selectItem.bind(this)} />
                </td>
                <td>
                    <TableModelLink modelName="group" modelId={group._id} showEditLink={group.modification_allowed}>
                        {group.name}
                    </TableModelLink>
                </td>
                <td>
                    <Link to={group.project._id}>{group.project.name}</Link>
                </td>
                <td>
                    <TagList tags={group.all_tags} nowrap={true} />
                </td>
                <td>
                    <CustomFieldList fields={group.all_custom_fields} mini={true} />
                </td>
                {
                    this.props.includeDescription ? <td>{group.description}</td> : ""
                }
            </tr>
        )
    }
}

GroupListItem.propTypes = {
    group: PropTypes.shape({
        _id: PropTypes.string,
        name: PropTypes.string,
        description: PropTypes.string,
        project_name: PropTypes.string
    }).isRequired,
    selected: PropTypes.bool.isRequired,
    onSelectStarted: PropTypes.func.isRequired,
    onSelect: PropTypes.func.isRequired,
    onDeselect: PropTypes.func.isRequired,
    includeDescription: PropTypes.bool
}