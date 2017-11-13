import React, { Component } from 'react'
import './Login.css'
import { AlertBox } from '../../library/AlertBox'
import AuthState from '../../library/AuthState'
import { observer } from 'mobx-react'

const Login = observer(class Login extends Component {

    componentDidMount() {
        this.refs.username.focus()
    }

    handleSubmit(e) {
        e.preventDefault();
        var data = {
            username: this.refs.username.value,
            password: this.refs.password.value
        }
        this.props.onSubmit(data);
    }

    render() {
        const authUrl = AuthState.getAuthUrl()
        const authText = AuthState.getAuthText()
        return (
            <div className="login-wrapper">
                <div className="container">
                    <div className="row">
                        <div className="col-sm-6 col-sm-offset-3">
                            <form className="form-horizontal login-form" onSubmit={this.handleSubmit.bind(this)}>
                                <h3>Please Login</h3>
                                <div className="form-group">
                                    <div className="col-sm-10 col-sm-offset-1">
                                        <input ref="username" placeholder="Username" id="inputUsername" className="form-control" type="text" />
                                    </div>
                                </div>
                                <div className="form-group">
                                    <div className="col-sm-10 col-sm-offset-1">
                                        <input ref="password" placeholder="Password" id="inputPassword" className="form-control" type="password" />
                                    </div>
                                </div>
                                <div className="form-group buttons-group">
                                    <button className="btn btn-primary" type="submit">Login</button>
                                </div>
                                {
                                    authUrl !== null &&
                                    <div>
                                        <div className="form-group">
                                            <div className="col-sm-10 col-sm-offset-1">
                                                <hr/>
                                            </div>
                                        </div>
                                        <div className="form-group buttons-group">
                                            <a href={authUrl} className="btn btn-external">{authText}</a>
                                        </div>
                                    </div>
                                }
                            </form>
                        </div>
                    </div>
                </div>
                <div className="login-alertbox-wrapper">
                    <AlertBox />
                </div>
            </div>
        )
    }
})

export default Login;