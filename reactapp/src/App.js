import React, { Component } from 'react';
import { HashRouter as Router, Route } from 'react-router-dom';
import './App.css';

import Axios from 'axios';
import AppHeader from './components/AppHeader'
import Structure from './components/Structure'
import Login from './components/Account/Login'
import AlertStore from './library/AlertBox'
import AuthState from './library/AuthState'
import HttpErrorHandler from './library/HttpErrorHandler'
import { observer } from 'mobx-react'


const App = observer(class App extends Component {
    constructor(props) {
        super(props);
        AuthState.setAuthState(
            {
                authState: 'authenticating',
                user: null
            }
        )
    }
    componentWillMount() {
        Axios.get('/api/v1/account/me')
            .then((response) => {
                AuthState.setAuthState({
                    authState: 'authenticated',
                    user: response.data.data
                })
            }).catch(HttpErrorHandler);
    }

    userDataSubmit(userdata) {
        Axios.post('/api/v1/account/authenticate', userdata)
            .then( (response) => {
                AuthState.setAuthState({
                    authState: 'authenticated',
                    user: response.data.data
                })
                AlertStore.Notice("You're successfully logged in");
            })
            .catch( (error) => {
                console.log(error.response);
            })
    } 

    getRenderContent() {
        switch (AuthState.authState) {
            case 'authenticating':
                return <div>Loading</div>
            case 'login':
                return <Login onSubmit={this.userDataSubmit.bind(this)} />
            case 'authenticated':
                return (
                    <div>
                        <AppHeader />
                        <Route path="/" component={Structure} />
                    </div>
                )
            default:
                return <div>default. WAT?</div>
        }
    }

    render() {
        return (
            <Router>
            {
                this.getRenderContent.bind(this)()
            }
            </Router>
        );
    }
})

export default App