import React, { Component } from 'react';
import PropTypes from 'prop-types'
import '../Form.css';
import ConfirmButton from '../common/ConfirmButton'

export default class DatacenterForm extends Component {
    constructor(props) {
        super(props);
        this.state = { datacenter: props.datacenter }
    }

    componentWillReceiveProps(props) {
        if (props.datacenter) {
            this.setState({
                datacenter: props.datacenter
            })
        } else {
            this.setState({
                datacenter: {
                    name: "",
                    human_readable: ""
                }
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
        if (this.props.onSubmit) {
            this.props.onSubmit(this.state.datacenter);
        }
    }

    handleDestroy(e) {
        e.preventDefault();
        if (this.props.onDestroy) {
            this.props.onDestroy(this.state.datacenter)
        }
    }

    render() {
        return (
            <form onChange={this.handleFieldChange.bind(this)} onSubmit={this.handleSubmit.bind(this)} className="form-horizontal object-form">
                <div className="form-group">
                    <label htmlFor="inputDatacenterName" className="col-sm-3 control-label">
                        Name:
                    </label>
                    <div className="col-sm-9">
                        <input ref="firstInput" type="text" value={this.state.datacenter.name} id="inputDatacenterName" className="form-control" placeholder="Datacenter name" />
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
    onDestroy: PropTypes.func
}