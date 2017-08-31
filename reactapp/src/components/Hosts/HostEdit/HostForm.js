import React, { Component } from 'react'
import PropTypes from 'prop-types'
import '../../Form.css';
import ConfirmButton from '../../common/ConfirmButton'
import TagEditor from '../../common/TagEditor'
import FieldsEditor from '../../common/FieldsEditor'
import GroupPicker from '../../Groups/GroupEdit/GroupPicker'
import DatacenterPicker from '../../Datacenters/DatacenterPicker'
import { hasValidPatterns } from '../../common/Permutation'

export default class HostForm extends Component {
    constructor(props) {
        super(props)
        let groupPicked = props.host.group._id ? true : false
        let datacenterPicked = (props.host.datacenter && props.host.datacenter._id) ? true : false
        let { host } = props
        host.datacenter = host.datacenter || { name: "" }
        this.state = {
            host,
            groupPicked,
            datacenterPicked,
            multiHost: false
        }
    }

    componentDidMount() {
        this.refs.firstInput.focus();
    }

    handleFieldChange(e) {
        let { host, multiHost } = this.state
        switch (e.target.id) {
            case "inputHostFqdn":
                host.fqdn = e.target.value
                let multiHost = hasValidPatterns(host.fqdn)
                if (multiHost) {
                    this.props.onSetPattern(host.fqdn)
                } else {
                    this.props.onClearPattern()
                }
                break
            case "inputHostShortname":
                host.short_name = e.target.value
                break
            case "inputHostDesc":
                host.description = e.target.value;
                break
            default:
                break
        }
        this.setState({
            host,
            multiHost
        })
    }

    addTag(tag) {
        let { host } = this.state
        host.tags.push(tag)
        this.setState({
            host
        })
    }

    removeTag(tag) {
        let { host } = this.state
        let ind = host.tags.indexOf(tag)
        if (ind >= 0) {
            host.tags.splice(ind,1)
            this.setState({
                host
            })
        }
    }

    handleSubmit(e) {
        e.preventDefault();
        this.props.onSubmit(this.state.host);
    }

    handleDestroy(e) {
        e.preventDefault();
        this.props.onDestroy(this.state.host)
    }

    handleGroupPicked(group) {
        let { host } = this.state
        host.group_id = group._id
        this.setState({
            host,
            groupPicked: true
        })
    }

    handleGroupClear() {
        let { host } = this.state
        host.group_id = null
        this.setState({
            host,
            groupPicked: false
        })
    }

    handleDatacenterPicked(datacenter) {
        let { host } = this.state
        host.datacenter_id = datacenter._id
        this.setState({
            host,
            datacenterPicked: true
        })
    }

    handleDatacenterClear() {
        let { host } = this.state
        host.datacenter_id = null
        this.setState({
            host,
            datacenterPicked: false
        })
    }

    handleFieldsChanged(fields) {
        let { host } = this.state
        host.custom_fields = fields
        this.setState({ host })
    }


    render() {
        let { description } = this.state.host
        description = description || ""
        return (
            <form onSubmit={this.handleSubmit.bind(this)} className="form-horizontal object-form">
                <h4 className="object-form_title">Host Properties</h4>
                <div className="form-group">
                    <label htmlFor="inputHostFqdn" className="col-sm-3 control-label">
                        FQDN:
                    </label>
                    <div className="col-sm-9">
                        <input onChange={this.handleFieldChange.bind(this)} ref="firstInput" type="text" value={this.state.host.fqdn} id="inputHostFqdn" className="form-control" placeholder="Host FQDN" />
                    </div>
                </div>
                <div className="form-group">
                    <label htmlFor="inputHostShortname" className="col-sm-3 control-label">
                        Short Name:
                    </label>
                    <div className="col-sm-9">
                        <input onChange={this.handleFieldChange.bind(this)} type="text" value={this.state.host.short_name} id="inputHostShortname" className="form-control" placeholder="Host short name" />
                    </div>
                </div>
                <div className="form-group">
                    <label htmlFor="inputHostDesc" className="col-sm-3 control-label">
                        Description:
                    </label>
                    <div className="col-sm-9">
                        <input onChange={this.handleFieldChange.bind(this)} type="text" value={description} id="inputHostDesc" className="form-control" placeholder="Description" />
                    </div>
                </div>
                <div className={"form-group" + (this.state.groupPicked ? " has-success": "")}>
                    <label className="col-sm-3 control-label">
                        Group:
                    </label>
                    <div className="col-sm-9">
                        <GroupPicker
                                    value={this.state.host.group.name}
                                    onDataPicked={this.handleGroupPicked.bind(this)}
                                    onDataClear={this.handleGroupClear.bind(this)}
                                    placeholder="Choose group" />
                    </div>
                </div>
                <div className={"form-group" + (this.state.datacenterPicked ? " has-success": "")}>
                    <label className="col-sm-3 control-label">
                        Datacenter:
                    </label>
                    <div className="col-sm-9">
                        <DatacenterPicker
                                    value={this.state.host.datacenter.name}
                                    onDataPicked={this.handleDatacenterPicked.bind(this)}
                                    onDataClear={this.handleDatacenterClear.bind(this)}
                                    placeholder="Choose datacenter" />
                    </div>
                </div>
                <div className="form-group">
                    <label className="col-sm-3 control-label">
                        Tags:
                    </label>
                    <div className="col-sm-9">
                        <TagEditor 
                                tags={this.state.host.tags}
                                onAdd={this.addTag.bind(this)}
                                onRemove={this.removeTag.bind(this)} />
                    </div>
                </div>
                <div className="form-group">
                    <label className="col-sm-3 control-label">
                        Fields:
                    </label>
                    <div className="col-sm-9">
                        <FieldsEditor
                                fields={this.state.host.custom_fields.slice()}
                                onChange={this.handleFieldsChanged.bind(this)} />
                    </div>
                </div>
                <div className="form-group">
                    <div className="col-sm-9 col-sm-offset-3 form-buttons">
                        <button type="submit" className="btn btn-primary">Save</button>
                        { this.props.isNew ? '': <ConfirmButton onClick={this.handleDestroy.bind(this)} className="btn btn-danger">Destroy</ConfirmButton> }
                    </div>
                </div>
            </form> 
        )
    }
}

HostForm.propTypes = {
    isNew: PropTypes.bool.isRequired,
    host: PropTypes.shape({
        fqdn: PropTypes.string,
        short_name: PropTypes.string,
        description: PropTypes.string,
        tags: PropTypes.array
    }),
    onSubmit: PropTypes.func.isRequired,
    onDestroy: PropTypes.func.isRequired,
    onSetPattern: PropTypes.func.isRequired,
    onClearPattern: PropTypes.func.isRequired
}