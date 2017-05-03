import React, { Component } from 'react'
import PropTypes from 'prop-types'
import Autosuggest from 'react-autosuggest'
import './AutosuggestContainer.css'

export default class AutosuggestContainer extends Component {
    constructor(props) {
        super(props)
        this.state = {
            suggestions: [],
            value: this.props.value
        }
    }

    handleChange(event, { newValue }) {
        this.setState({
            value: newValue
        })
    }

    loadData(value, callback) {
    }

    handleSuggestionsFetchRequested({ value }) {
        this.loadData( value, data => {
            if (this.props.onDataClear) this.props.onDataClear()
            this.setState({
                suggestions: data
            })
        })
    }

    handleSuggestionsClearRequested() {
        this.setState({
            suggestions: []
        })
    }

    handleSuggestionSelected(event, { suggestion }) {
        this.props.onDataPicked(suggestion)
        if (this.props.clearOnPick) {
            this.setState({
                value: ""
            })
        }
    }

    handleBlur(event) {
        this.loadData(this.state.value, data => {
            let exactMatch = data.filter(item => this.getSuggestionValue(item) === this.state.value)
            if (exactMatch.length === 1) {
                this.props.onDataPicked(exactMatch[0])
            }
        })
    }

    getSuggestionValue(suggestion) {
        return suggestion[this.props.showField]
    }

    renderSuggestion(suggestion) {
        return (
            <div>{this.getSuggestionValue(suggestion)}</div>
        )
    }

    render() {
        const { value, suggestions } = this.state
        const inputProps = {
            placeholder: this.props.placeholder,
            id: 'inputDatacenterParent',
            className: 'form-control',
            value,
            onChange: this.handleChange.bind(this),
            onBlur: this.handleBlur.bind(this)
        }

        return (
            <Autosuggest
                suggestions={suggestions}
                onSuggestionsFetchRequested={this.handleSuggestionsFetchRequested.bind(this)}
                onSuggestionsClearRequested={this.handleSuggestionsClearRequested.bind(this)}
                onSuggestionSelected={this.handleSuggestionSelected.bind(this)}
                getSuggestionValue={this.getSuggestionValue.bind(this)}
                renderSuggestion={this.renderSuggestion.bind(this)}
                inputProps={inputProps} />
        )
    }
}

AutosuggestContainer.propTypes = {
    onDataPicked: PropTypes.func.isRequired,
    onDataClear: PropTypes.func,
    placeholder: PropTypes.string,
    showField: PropTypes.string,
    clearOnPick: PropTypes.bool
}

AutosuggestContainer.defaultProps = {
    showField: 'name',
    clearOnPick: false
}