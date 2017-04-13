import React, { Component } from 'react';
import { HashRouter as Router, Route } from 'react-router-dom';
import './App.css';
import Axios from 'axios';
import AppHeader from './components/AppHeader'
import Structure from './components/Structure'
import Login from './components/Account/Login'
import AlertStore from './library/AlertBox'

class App extends Component {
    constructor() {
        super();
        this.state = {
            stage: 'authenticating',
            user: null
        }
    }
    componentWillMount() {
        Axios.get('/api/v1/account/me')
            .then((response) => {
                this.setState({
                    stage: 'authenticated',
                    user: response.data.data
                })
            }).catch((err) => {
                this.setState({
                    stage: 'login',
                    user: null
                })
            });
    }

    userDataSubmit(userdata) {
        Axios.post('/api/v1/account/authenticate', userdata)
            .then( ((response) => {
                this.setState({
                    stage: 'authenticated',
                    user: response.data.data
                })
                AlertStore.Notice("You're successfully logged in");
            }).bind(this))
            .catch( (error) => {
                console.log(error.response);
            })
    } 

    getRenderContent() {
        switch (this.state.stage) {
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
}

export default App;
