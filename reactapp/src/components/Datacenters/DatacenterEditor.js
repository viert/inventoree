import React, { Component } from 'react'
import Axios from 'axios';
import HttpErrorHandler from '../../library/HttpErrorHandler'
import AlertStore from '../../library/AlertBox'
import Loading from '../common/Loading'

import DatacenterForm from './DatacenterForm'

export default class DatacenterEditor extends Component {
    constructor(props) {
        super(props)
        this.state = {
            title: "New Datacenter",
            datacenter: {},
            isNew: true,
            isLoading: true
        }
    }

    componentDidMount() {
        var id = this.props.match.params.id;
        if (id && id !== "new") {
            Axios.get('/api/v1/datacenters/' + id)
                .then((response) => {
                    this.setState({
                        datacenter: response.data.data[0],
                        title: "Edit Datacenter",
                        isNew: false,
                        isLoading: false
                    })
                })
                .catch(HttpErrorHandler);
        } else {
            this.setState({
                isLoading: false
            })
        }
    }

    handleSubmit(datacenter) {

    }

    handleDestroy(datacenter) {

    }

    render() {
        return (
            <div>
            {
                this.state.isLoading ? <Loading /> :
                <div>
                    <h2>{this.state.title}</h2>
                    <div className="row">
                        <div className="col-sm-6">
                            <DatacenterForm 
                                    datacenter={this.state.datacenter}
                                    isNew={this.state.isNew}
                                    onSubmit={this.handleSubmit.bind(this)}
                                    onDestroy={this.handleDestroy.bind(this)} />
                        </div>
                    </div>
                </div>
            }
            </div>
        )
    }
}