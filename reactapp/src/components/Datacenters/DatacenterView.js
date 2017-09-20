import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import Axios from 'axios'

import Api from '../../library/Api'
import HttpErrorHandler from '../../library/HttpErrorHandler'
import Loading from '../common/Loading'
import '../common/PropertiesPanel.css'

export default class DatacenterView extends Component {
    constructor(props) {
        super(props)
        this.state = {
            datacenter: {
                name: "",
                human_readable: ""
            },
            isLoading: true
        }
    }

    onDataLoaded(response) {
        let datacenter = response.data.data[0]
        this.setState({
            datacenter,
            isLoading: false
        })

    }

    componentDidMount() {
        let { id } = this.props.match.params
        let { ViewFields } = Api.Datacenters
        ViewFields = ViewFields.join(",")

        Axios.get(`/api/v1/datacenters/${id}?_fields=${ViewFields}`)
            .then( this.onDataLoaded.bind(this) )
            .catch( error => {
                HttpErrorHandler(error)
                this.props.history.push('/projects')
            })

    }

    render() {
        let { datacenter } = this.state
        return (
            <div className="max vertcenter">
            {
                this.state.isLoading ? <Loading /> :
                <div className="max">
                    <h2>View Location</h2>
                    <div className="row properties-panel">
                        <div className="col-sm-12">
                            <h4 className="object-form_title">Datacenter Properties</h4>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Name:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {datacenter.name}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Human Readable:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {datacenter.human_readable}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Root Location:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {
                                        datacenter.root ? 
                                            <Link to={`/datacenters/${datacenter.root._id}`}>
                                                { datacenter.root.name }
                                            </Link> : ""
                                    }
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Parent Location:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {
                                        datacenter.parent ? 
                                            <Link to={`/datacenters/${datacenter.parent._id}`}>
                                                { datacenter.parent.name }
                                            </Link> : ""
                                    }
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-2">
                                    Child Locations:
                                </div>
                                <div className="properties-value col-sm-10">
                                    {
                                        datacenter.children.map(
                                            item => <div key={item._id}>
                                                <Link to={`/datacenters/${item._id}`}>
                                                    { item.name }
                                                </Link>
                                            </div>
                                        )
                                    }
                                </div>
                            </div>


                            <div className="row properties-line">
                                <div className="col-sm-12 form-buttons">
                                    <Link to={`/datacenters/${datacenter._id}/edit`} type="submit" className="btn btn-primary">Edit Location</Link>
                                </div>
                            </div>

                        </div>
                    </div>
                </div>
            }            
            </div>
        )
    }
}