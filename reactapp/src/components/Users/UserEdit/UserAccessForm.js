import React, { Component } from 'react';
import PropTypes from 'prop-types'
import '../../Form.css';
import AlertStore from '../../../library/AlertBox'

export default class UserAccessForm extends Component {
    constructor(props) {
        super(props);
        let { user } = props
        this.state = { 
            user,
            password: "",
            password_confirm: ""
        }
    }

    componentWillReceiveProps(props) {
        let { user } = props
        if (user) {
            this.setState({ 
                user,
                password: "",
                password_confirm: ""
            })
        } else {
            this.setState({
                user: {
                    username: "",
                    first_name: "",
                    last_name: "",
                    supervisor: false,
                    supervisor_set_allowed: false
                },
                password: "",
                password_confirm: ""
            })
        }
    }

    handleFieldChange(e) {
        let { password, password_confirm } = this.state
        switch (e.target.id) {
            case "inputPassword":
                password = e.target.value;
                break;
            case "inputPasswordConfirm":
                password_confirm = e.target.value;
                break;
            default:
                break;
        }
        this.setState({ password, password_confirm })
    }

    handleSubmit(e) {
        e.preventDefault();
    }

    handleSubmitPassword() {
        let { password, password_confirm } = this.state
        if (password !== password_confirm) {
            AlertStore.Alert("Passwords don't match!")
            return
        }
        this.props.onSubmitPassword(password, password_confirm);
    }

    handleDestroy(e) {
        e.preventDefault();
        if (this.props.onDestroy) {
            this.props.onDestroy(this.state.user)
        }
    }

    render() {
        let { user } = this.state
        let supervisorToggleButtonClass = "btn" + (user.supervisor? " btn-danger" : " btn-success")
        let supervisorToggleButtonText = user.supervisor? "Revoke Supervisor" : "Grant Supervisor"

        return (
            <form onChange={this.handleFieldChange.bind(this)} onSubmit={this.handleSubmit.bind(this)} className="form-horizontal object-form max">
                <h4 className="object-form_title">User Access</h4>
                <div className="form-group">
                    <label htmlFor="inputPassword" className="col-sm-4 control-label">
                        Password:
                    </label>
                    <div className="col-sm-8">
                        <input type="password" value={this.state.password} id="inputPassword" className="form-control" placeholder="Password" />
                    </div>
                </div>
                <div className="form-group">
                    <label htmlFor="inputPasswordConfirm" className="col-sm-4 control-label">
                        Confirm Password:
                    </label>
                    <div className="col-sm-8">
                        <input type="password" value={this.state.password_confirm} id="inputPasswordConfirm" className="form-control" placeholder="Confirm Password" />
                    </div>
                </div>
                <div className="form-group">
                    <div className="col-sm-8 col-sm-offset-4 form-buttons">
                        <button type="button" className="btn btn-primary" onClick={this.handleSubmitPassword.bind(this)}>Set Password</button>
                    </div>
                </div>
                {
                    user.supervisor_set_allowed ?
                    <div className="form-group supervisor-button-wrapper">
                        <hr/>
                        <div className="col-sm-8 col-sm-offset-4">
                            <button onClick={this.props.onToggleSupervisor} className={supervisorToggleButtonClass}>
                                {supervisorToggleButtonText}
                            </button>
                        </div>
                    </div> : ""
                }
            </form> 
        )
    }
}

UserAccessForm.propTypes = {
    user: PropTypes.shape({
        username: PropTypes.string,
        first_name: PropTypes.string,
        last_name: PropTypes.string,
        supervisor: PropTypes.bool,
        supervisor_set_allowed: PropTypes.bool
    }),
    onSubmitPassword: PropTypes.func.isRequired,
    onToggleSupervisor: PropTypes.func.isRequired
}