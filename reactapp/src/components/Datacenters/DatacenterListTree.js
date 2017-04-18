import React, { Component } from 'react'
import DatacenterItem from './DatacenterItem'

export default class DatacenterListTree extends Component {
    constructor(props) {
        super(props)
        let tree = this.buildTree(this.props.datacenters)
        this.state = {
            dcTree: tree
        }
    }

    componentWillReceiveProps(props) {
        let tree = this.buildTree(this.props.datacenters)
        this.setState({
            dcTree: tree
        })
    }

    _buildTreeRecursive(dcList, parent_id, level) {
        let result = []
        dcList
            .filter((item) => (item.parent_id === parent_id))
            .forEach((item) => {
                item.level = level
                result.push(item)
                let children = this._buildTreeRecursive(dcList, item._id, level+1)
                if (children.length > 0) {
                    result = result.concat(children)
                }
            })
        return result
    }

    buildTree(dcList) {
        let tree = [{ name: 'root', human_readable: 'Root Datacenter', _id: "root", level: 0 }]
        let children = this._buildTreeRecursive(dcList, null, 1)
        if (children.length > 0) {
            tree = tree.concat(children)
        }
        return tree
    }

    render() {
        return (
            <div className="datacenter-tree">
            {
                this.state.dcTree.map((item) => (
                    <DatacenterItem key={item._id} datacenter={item} />
                ))
            }
            </div>
        )
    }
}