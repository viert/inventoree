import React, { Component } from 'react';
import Axios from 'axios';

class DatacenterList extends Component {
    componentDidMount() {
        Axios.get("/api/v1/datacenters");
        console.log('component did mount');
    }
    render() {
        return <h1>Datacenter List</h1>
    }
}

export default DatacenterList;