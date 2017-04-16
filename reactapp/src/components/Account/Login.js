import React, { Component } from 'react'
import './Login.css'

class Login extends Component {

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
                            </form>
                        </div>
                    </div>
                </div>
            </div>
        )
    }
}

export default Login;