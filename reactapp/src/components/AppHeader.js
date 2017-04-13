import React, { Component } from 'react';
import { Link } from 'react-router-dom';
import './AppHeader.css';

// brand should be printed as image using Days One font 25px size

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
