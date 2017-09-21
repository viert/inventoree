import React, { Component } from 'react';
import HttpErrorHandler from '../../library/HttpErrorHandler'
import Axios from 'axios';
import ListPageHeader from '../common/ListPageHeader'
import DatacenterListTree from './DatacenterListTree'

export default class DatacenterList extends Component {
    constructor(props) {
        super(props);
        this.state = {
            datacenters: [],
            loading: true
        }
    }

    loadData() {
        Axios.get("/api/v1/datacenters/?_nopaging=true").then((response) => {
            var dcList = response.data.data; 
            this.setState({
                datacenters: dcList,
                loading: false
            });
        })
        .catch(HttpErrorHandler)
    }

    componentDidMount() {
        this.loadData()
    }

    render() {
        return (
            <div>
                <ListPageHeader title="Location List" 
                                noFilter={true}
                                createButtonText="New Location" 
                                createLink="/datacenters/new/edit" />
                { 
                    this.state.loading ? 'Loading' :
                        <DatacenterListTree datacenters={this.state.datacenters} />
                }
            </div>
        )
    }
}