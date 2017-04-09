import React, { Component } from 'react';
import { HashRouter as Router, Route } from 'react-router-dom';
import './App.css';

import AppHeader from './components/AppHeader'
import Structure from './components/Structure'

class App extends Component {
    render() {
        return (
            <Router>
                <div>
                    <AppHeader />
                    <Route path="/" component={Structure} />
                </div>
            </Router>
        );
    }
}

export default App;
