import React, { Component } from 'react'
import './FieldsEditor.css'

const fieldIsEmpty = field => field.key ===  "" && field.value === ""

class FieldRow extends Component {

    handleChange(e) {
        let { field } = this.props
        switch(e.target) {
            case this.refs.cf_key:
                field.key = e.target.value
                break
            case this.refs.cf_value:
                field.value = e.target.value
                break
            default:
                break
        }
        this.props.onChange(field)
    }

    render() {
        return (
            <div className="row">
                <div className="col-sm-4">
                    <input placeholder="Key" ref="cf_key" value={this.props.field.key} className="form-control" type="text" 
                            onChange={this.handleChange.bind(this)} />
                </div>
                <div className="col-sm-8">
                    <input placeholder="Value" ref="cf_value" value={this.props.field.value} className="form-control" type="text" 
                            onChange={this.handleChange.bind(this)} />
                </div>
            </div>
        )
    }
}

export default class FieldsEditor extends Component {

    constructor(props) {
        super(props)
        this.state = {
            fields: this.prepareFields(props.fields)
        }
    }

    componentWillReceiveProps(props) {
        let fields = this.prepareFields(props.fields)
        this.setState({ fields })
    }

    prepareFields(fields) {
        if (fields.length === 0) {
            fields.push({ key: "", value: "" })
        } else {
            const last_field = fields[fields.length-1]
            if (!fieldIsEmpty(last_field)) {
                fields.push({ key: "", value: "" })
            }
        }
        return fields
    }


    onFieldChange(i, field) {
        let { fields } = this.state
        fields[i].key = field.key
        fields[i].value = field.value
        fields = fields.filter( field => !fieldIsEmpty(field) )
        this.props.onChange(fields)
    }

    render() {
        return (
            <div className="fields-editor">
                {
                    this.state.fields.map( (item, index) => 
                        <FieldRow field={item} key={index} onChange={this.onFieldChange.bind(this, index)} />
                    )
                }
            </div>
        )
    }
}