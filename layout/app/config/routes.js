import React from 'react';
import {
    HashRouter as Router,
    Route, 
    Link
} from 'react-router-dom';

import Main from '../components/Main';
import Projects from '../components/Projects';


const BasicExample = () => (
    <Router>
        <div>
            Here is Blah Minor;
            <Route path='/' component={Main}></Route>
            <Route path='/projects' component={Projects} />
        </div>
    </Router>
)

export default BasicExample;