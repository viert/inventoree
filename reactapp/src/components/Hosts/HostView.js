import React, { Component } from 'react'
import { Link } from 'react-router-dom'
import Axios from 'axios'

import Api from '../../library/Api'
import { SortCmp } from '../../library/Utils'
import HttpErrorHandler from '../../library/HttpErrorHandler'
import Loading from '../common/Loading'
import Tag from '../common/Tag'
import CustomField from '../common/CustomField'
import '../common/PropertiesPanel.css'

export default class HostView extends Component {

    constructor(props) {
        super(props)
        this.state = {
            host: {
                _id: "",
                fqdn: "",
                tags: [],
                all_tags: [],
                custom_fields: [],
                all_custom_fields: [],
                group: {
                    name: ""
                },
                datacenter: {
                    name: ""
                }
            },
            selfTags: [],
            derivedTags: [],
            selfCustomFields: [],
            derivedCustomFields: [],
            isLoading: true,
        }
    }

    onDataLoaded(response) {
        let host = response.data.data[0]
        if (!host.group) { host.group = { name: "" } }
        if (!host.datacenter) { host.datacenter = { name: "" }}

        let selfTags = host.tags.slice().sort()
        let derivedTags = host.all_tags.slice().filter(
            item => !selfTags.includes(item)
        ).sort()

        let selfCustomFields = host.custom_fields.slice().sort(SortCmp("key"))
        let selfCustomFieldsKeys = selfCustomFields.map(item => item.key)
        let derivedCustomFields = host.all_custom_fields.slice().filter(
            item => !selfCustomFieldsKeys.includes(item.key)
        ).sort(SortCmp("key"))

        this.setState({
            host,
            selfTags,
            derivedTags,
            selfCustomFields,
            derivedCustomFields,
            isLoading: false,
        })
    }

    componentDidMount() {
        let { id } = this.props.match.params
        let { ViewFields } = Api.Hosts
        ViewFields = ViewFields.join(",")

        Axios.get(`/api/v1/hosts/${id}?_fields=${ViewFields}`)
            .then( this.onDataLoaded.bind(this) )
            .catch( error => {
                HttpErrorHandler(error)
                this.props.history.push('/hosts')
            })
    }

    render() {
        return (
            <div className="max vertcenter">
            {
                this.state.isLoading ? <Loading /> :
                <div className="max">
                    <h2>View Host</h2>
                    <div className="row properties-panel">
                        <div className="col-sm-7">
                            <h4 className="object-form_title">Host Properties</h4>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-3">
                                    FQDN:
                                </div>
                                <div className="properties-value col-sm-9">
                                    {this.state.host.fqdn}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-3">
                                    Description:
                                </div>
                                <div className="properties-value col-sm-9">
                                    {this.state.host.description}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-3">
                                    Group:
                                </div>
                                <div className="properties-value col-sm-9">
                                    {
                                        this.state.host.group._id ?
                                        <Link to={`/groups/${this.state.host.group._id}`}>
                                            {this.state.host.group.name}
                                        </Link> :
                                        ""
                                    }
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-3">
                                    Location:
                                </div>
                                <div className="properties-value col-sm-9">
                                    {
                                        this.state.host.datacenter._id ?
                                        <span>
                                            <Link to={`/datacenters/${this.state.host.datacenter._id}`}>
                                                {this.state.host.datacenter.name}
                                            </Link> <small className="mute">({ this.state.host.datacenter.human_readable })</small>
                                        </span> :
                                        ""
                                    }
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-3">
                                    Tags:
                                </div>
                                <div className="properties-value col-sm-9">
                                    { this.state.derivedTags.map(
                                        tag => <Tag key={tag} tag={tag} derived={true} mini={true} />
                                    )}
                                    { this.state.selfTags.map(
                                        tag => <Tag key={tag} tag={tag} derived={false} mini={true} />
                                    )}
                                </div>
                            </div>
                            
                            <div className="row properties-line">
                                <div className="properties-key col-sm-3">
                                    Custom Fields:
                                </div>
                                <div className="properties-value col-sm-9">
                                    { this.state.derivedCustomFields.map(
                                        item => <CustomField key={item.key} field={item} derived={true} />
                                    )}
                                    { this.state.selfCustomFields.map(
                                        item => <CustomField key={item.key} field={item} derived={false} />
                                    )}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="col-sm-12 form-buttons">
                                    <Link to={`/hosts/${this.state.host._id}/edit`} type="submit" className="btn btn-primary">Edit Host</Link>
                                </div>
                            </div>

                        </div>
                        <div className="col-sm-5">
                        
                        </div>
                    </div>
                </div>
            }            
            </div>
        )
    }
}