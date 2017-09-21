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

export default class GroupView extends Component {
    constructor(props) {
        super(props)
        this.state = {
            group: {
                _id: "",
                name: "",
                description: "",
                tags: [],
                all_tags: [],
                custom_fields: [],
                all_custom_fields: [],
                parents: [],
                children: [],
                project: {
                    name: ""
                },
                modification_allowed: false
            },
            selfTags: [],
            derivedTags: [],
            selfCustomFields: [],
            derivedCustomFields: [],
            isLoading: true,
        }
    }

    onDataLoaded(response) {
        let group = response.data.data[0]

        let selfTags = group.tags.slice().sort()
        let derivedTags = group.all_tags.slice().filter(
            item => !selfTags.includes(item)
        ).sort()

        let selfCustomFields = group.custom_fields.slice().sort(SortCmp("key"))
        let selfCustomFieldsKeys = selfCustomFields.map(item => item.key)
        let derivedCustomFields = group.all_custom_fields.slice().filter(
            item => !selfCustomFieldsKeys.includes(item.key)
        ).sort(SortCmp("key"))

        this.setState({
            group,
            selfTags,
            derivedTags,
            selfCustomFields,
            derivedCustomFields,
            isLoading: false,
        })
    }

    componentDidMount() {
        let { id } = this.props.match.params
        let { ViewFields } = Api.Groups
        ViewFields = ViewFields.join(",")

        Axios.get(`/api/v1/groups/${id}?_fields=${ViewFields}`)
            .then( this.onDataLoaded.bind(this) )
            .catch( error => {
                HttpErrorHandler(error)
                this.props.history.push('/groups')
            })
    }

    render() {
        return (
            <div className="max vertcenter">
            {
                this.state.isLoading ? <Loading /> :
                <div className="max">
                    <h2>View Group</h2>
                    <div className="row properties-panel">
                        <div className="col-sm-6">
                            <h4 className="object-form_title">Group Properties</h4>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-3">
                                    Name:
                                </div>
                                <div className="properties-value col-sm-9">
                                    {this.state.group.name}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-3">
                                    Description:
                                </div>
                                <div className="properties-value col-sm-9">
                                    {this.state.group.description}
                                </div>
                            </div>

                            <div className="row properties-line">
                                <div className="properties-key col-sm-3">
                                    Project:
                                </div>
                                <div className="properties-value col-sm-9">
                                    <Link to={`/projects/${this.state.group.project._id}`}>
                                        {this.state.group.project.name}
                                    </Link>
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
                                {
                                    this.state.group.modification_allowed ?
                                        <Link to={`/groups/${this.state.group._id}/edit`} type="submit" className="btn btn-primary">Edit Group</Link> :
                                        ""
                                }
                                </div>
                            </div>

                        </div>
                        <div className="col-sm-6">
                            <h4 className="object-form_title">Group Relations</h4>
                            <div className="row properties-line">
                                <div className="properties-key col-sm-3">
                                    Parents:
                                </div>
                                <div className="properties-value col-sm-9">
                                    { this.state.group.parents.map(
                                        item => <div key={item._id}><Link to={`/groups/${item._id}`}>{item.name}</Link></div>
                                    )}
                                </div>
                            </div>
                            <div className="row properties-line">
                                <div className="properties-key col-sm-3">
                                    Children:
                                </div>
                                <div className="properties-value col-sm-9">
                                    { 
                                        this.state.group.children.map(
                                            item => <div key={item._id}><Link to={`/groups/${item._id}`}>{item.name}</Link></div>
                                        )
                                    }
                                </div>
                            </div>
                            <div className="row properties-line">
                                <div className="properties-key col-sm-3">
                                    Directly included Hosts:
                                </div>
                                <div className="properties-value col-sm-9">
                                    { 
                                        this.state.group.hosts.map(
                                            item => <div key={item._id}><Link to={`/hosts/${item._id}`}>{item.fqdn}</Link></div>
                                        )
                                    }
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