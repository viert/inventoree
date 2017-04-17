import React, { Component } from 'react'
import GroupListItem from './GroupListItem'

export default class GroupListTable extends Component {
    render() {
        return (
            <table className="table">
                <thead>
                <tr>
                    <th className="th-group-name">name</th>
                    <th className="th-name">project</th>
                    <th>description</th>
                </tr>
                </thead>
                <tbody>
                {
                    this.props.groups.map((group) => {
                        return (
                            <GroupListItem group={group} key={group._id} />
                        )
                    })
                }
                </tbody>
            </table>
        )
    }
}
