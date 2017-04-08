import React from 'react';
import { Component } from 'react';
import { Link } from 'react-router-dom';

class Main extends Component {
    render() {
        return (
            <div>
                <div>Main component</div>
                <Link to='/projects'>go to projects</Link>
                {this.props.children}
            </div>
        )
    }
}

export default Main