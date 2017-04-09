import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import './AppHeader.css';

class AppHeader extends Component {
    render() {
        return (
            <div className="appheader">
                <div className="appheader-logo">
                    <Link to="/">Conductor</Link>
                </div>
                <div className="appheader-account">
                    Logged in as viert
                </div>
            </div>
        )
    }
}

export default AppHeader;