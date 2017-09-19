import React, { Component } from 'react'

import CustomField from './CustomField'
import './CustomFieldList.css'

export default class CustomFieldList extends Component {
    render() {
        let cflClass = "custom_field_list" + (this.props.mini? " custom_field_list--mini" : "");
        return (
            <div className={cflClass}>
            {
                this.props.fields.map(
                    item => <CustomField key={item.key} field={item} desaturate={true} />
                )
            }
            </div>
        )
    }
}