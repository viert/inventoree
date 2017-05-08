import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import PropTypes from 'prop-types'

import CheckBoxIcon from '../common/CheckBoxIcon'
export default class GroupListItem extends Component {

    selectItem() {
        let {selected} = this.props
        selected = !selected
        if (selected)
            this.props.onSelect(this.props.group)
        else 
            this.props.onDeselect(this.props.group)
        this.props.onSelectStarted()
    }

    render() {
        return (
            <tr>
                <td className="td-group-select">
                    <CheckBoxIcon checked={this.props.selected} className="fa" classNameChecked="fa-folder" classNameUnchecked="fa-folder-o" onTrigger={this.selectItem.bind(this)} />
                </td>
                <td>
                    <Link to={`/groups/${this.props.group._id}`}>
                    {this.props.group.name}
                    </Link>
                </td>
                <td>{this.props.group.project_name}</td>
                <td>{this.props.group.description}</td>
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
    onDeselect: PropTypes.func.isRequired
}