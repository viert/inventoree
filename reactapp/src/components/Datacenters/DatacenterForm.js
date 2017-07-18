import React, { Component } from 'react'
import PropTypes from 'prop-types'
import '../Form.css';
import ConfirmButton from '../common/ConfirmButton'
import DatacenterPicker from './DatacenterPicker'

export default class DatacenterForm extends Component {
    constructor(props) {
        super(props);
        const picked = props.datacenter.parent_id ? true : false
        this.state = {
            datacenter: props.datacenter,
            picked: picked
        }
    }

    componentWillReceiveProps(props) {
        if (props.datacenter) {
            this.setState({
                datacenter: props.datacenter,
                picked: true
            })
        } else {
            this.setState({
                datacenter: {
                    name: "",
                    human_readable: "",
                    parent_id: ""
                },
                picked: false
            })
        }
    }

    componentDidMount() {
        this.refs.firstInput.focus();
    }

    handleFieldChange(e) {
        let state = this.state.datacenter;
        switch (e.target.id) {
            case "inputDatacenterName":
                state.name = e.target.value;
                break;
            case "inputDatacenterHumanReadable":
                state.human_readable = e.target.value;
                break;
            default:
                break;
        }
        this.setState({
            datacenter: state
        })
    }

    handleSubmit(e) {
        e.preventDefault();
        this.props.onSubmit(this.state.datacenter);
    }

    handleDestroy(e) {
        e.preventDefault();
        this.props.onDestroy(this.state.datacenter)
    }

    parentSelected(parent) {
        let datacenter = this.state.datacenter
        datacenter.parent_id = parent._id
        this.setState({
            datacenter: datacenter,
            picked: true
        })
    }

    parentClear() {
        let datacenter = this.state.datacenter
        datacenter.parent_id = ""
        this.setState({
            datacenter: datacenter,
            picked: false
        })
    }

    getParentName() {
        if (this.state.datacenter.parent && this.state.datacenter.parent.name) {
            return this.state.datacenter.parent.name
        } else {
            return ""
        }
    }

    render() {
        return (
            <form onChange={this.handleFieldChange.bind(this)} onSubmit={this.handleSubmit.bind(this)} className="form-horizontal object-form">
                <div className={"form-group" + (this.state.picked ? " has-success" : "")}>
                    <label htmlFor="inputDatacenterParent" className="col-sm-3 control-label">
                        Parent:
                    </label>
                    <div className="col-sm-9">
                        <DatacenterPicker 
                                    value={this.getParentName()} 
                                    onDataClear={this.parentClear.bind(this)} 
                                    onDataPicked={this.parentSelected.bind(this)} 
                                    placeholder="Parent Location" />
                    </div>
                </div>
                <div className="form-group">
                    <label htmlFor="inputDatacenterName" className="col-sm-3 control-label">
                        Name:
                    </label>
                    <div className="col-sm-9">
                        <input ref="firstInput" type="text" value={this.state.datacenter.name} id="inputDatacenterName" className="form-control" placeholder="Location name" />
                    </div>
                </div>
                <div className="form-group">
                    <label htmlFor="inputDatacenterHumanReadable" className="col-sm-3 control-label">
                        Human Readable:
                    </label>
                    <div className="col-sm-9">
                        <input type="text" value={this.state.datacenter.human_readable} id="inputDatacenterHumanReadable" className="form-control" placeholder="Description" />
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

DatacenterForm.propTypes = {
    isNew: PropTypes.bool.isRequired,
    datacenter: PropTypes.shape({
        name: PropTypes.string,
        human_readable: PropTypes.string
    }),
    onSubmit: PropTypes.func.isRequired,
    onDestroy: PropTypes.func.isRequired
}