import React, { Component } from 'react';
import PropTypes from 'prop-types'
import '../../Form.css';
import ConfirmButton from '../../common/ConfirmButton'

export default class UserForm extends Component {
    constructor(props) {
        super(props);
        let { user } = props
        this.state = { user }
    }

    componentWillReceiveProps(props) {
        let { user } = props
        if (user) {
            this.setState({ user })
        } else {
            this.setState({
                user: {
                    username: "",
                    first_name: "",
                    last_name: "",
                    supervisor: false,
                    supervisor_set_allowed: false
                }
            })
        }
    }

    componentDidMount() {
        this.refs.firstInput.focus();
    }

    handleFieldChange(e) {
        let { user } = this.state
        switch (e.target.id) {
            case "inputUsername":
                user.username = e.target.value;
                break;
            case "inputFirstName":
                user.first_name = e.target.value;
                break;
            case "inputLastName":
                user.last_name = e.target.value;
                break;
            default:
                break;
        }
        this.setState({ user })
    }

    handleSubmit(e) {
        e.preventDefault();
        if (this.props.onSubmit) {
            this.props.onSubmit(this.state.user);
        }
    }

    handleDestroy(e) {
        e.preventDefault();
        if (this.props.onDestroy) {
            this.props.onDestroy(this.state.user)
        }
    }

    render() {
        let { user } = this.state
        return (
            <form onChange={this.handleFieldChange.bind(this)} onSubmit={this.handleSubmit.bind(this)} className="form-horizontal object-form max">
                <h4 className="object-form_title">User Properties</h4>
                <div className="form-group">
                    <label htmlFor="inputUsername" className="col-sm-3 control-label">
                        Username:
                    </label>
                    <div className="col-sm-9">
                        <input ref="firstInput" type="text" value={user.username} id="inputUsername" className="form-control" placeholder="Username" />
                    </div>
                </div>
                <div className="form-group">
                    <label htmlFor="inputFirstName" className="col-sm-3 control-label">
                        First Name:
                    </label>
                    <div className="col-sm-9">
                        <input type="text" value={user.first_name} id="inputFirstName" className="form-control" placeholder="First Name" />
                    </div>
                </div>
                <div className="form-group">
                    <label htmlFor="inputLastName" className="col-sm-3 control-label">
                        Last Name:
                    </label>
                    <div className="col-sm-9">
                        <input type="text" value={user.last_name} id="inputLastName" className="form-control" placeholder="Last Name" />
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

UserForm.propTypes = {
    isNew: PropTypes.bool.isRequired,
    user: PropTypes.shape({
        username: PropTypes.string,
        first_name: PropTypes.string,
        last_name: PropTypes.string,
        supervisor: PropTypes.bool,
        supervisor_set_allowed: PropTypes.bool
    }),
    onSubmit: PropTypes.func.isRequired,
    onDestroy: PropTypes.func
}