import React, { Component } from 'react'
import { extendObservable } from 'mobx'
import { observer } from 'mobx-react'
import './AlertBox.css'

const MESSAGE_CLASSES = {
    alert: 'danger',
    notice: 'success',
    info: 'info',
    warning: 'warning'
}

class InvalidMessageType {
    constructor(message) {
        this.name = "InvalidMessageType"
        this.message = message
    }
}

class Message {
    value 
    mType
    id
    constructor(value, mType) {
        if (!(mType in MESSAGE_CLASSES)) {
            throw InvalidMessageType(mType + ' is not one of allowed types');
        }
        extendObservable(
            this, {
                disappearing: false
            }
        )
        this.mType = mType
        this.value = value
        this.id = Date.now()
        this.className = MESSAGE_CLASSES[mType]
    }
}

export class AlertStore {
    constructor(ttl, hideAnimationTime) {
        extendObservable(this, {
            messages: []
        })
        this.SetTTL(ttl ? ttl : 10000)
        this.SetAnimationTime(hideAnimationTime ? hideAnimationTime : 1000)
    }

    SetTTL(value) {
        this.ttl = value
    }

    SetAnimationTime(value) {
        this.hideAnimationTime = value
        this.cssAnimationTime = `${this.hideAnimationTime / 1000}s`
    }

    Alert(message) {
        this.newMessage(message, 'alert')
    }

    Notice(message) {
        this.newMessage(message, 'notice')
    }

    Info(message) {
        this.newMessage(message, 'info')
    }

    Warning(message) {
        this.newMessage(message, 'warning')
    }

    removeMessage(id) {
        var remaining = this.messages.filter( (item) => {
            return item.id !== id;
        })
        this.messages.replace(remaining)
    }

    hideMessage(id) {
        this.messages.find( item => item.id === id ).disappearing = true
        setTimeout(this.removeMessage.bind(this, id), 500)
    }

    newMessage(value, mType) {
        var msg = new Message(value, mType);
        this.messages.push(msg);
        setTimeout(this.hideMessage.bind(this, msg.id), this.ttl)
    }
}

var Store = new AlertStore();

export const AlertBox = observer(class AlertBox extends Component {
    render() {
        return (
            <div className="alertbox-wrapper">
            {
                Store.messages.map(item => {
                    const itemClass = `alert alert-${item.className}`
                    let itemStyle = {}
                    if (item.disappearing) {
                        itemStyle.opacity = "0"
                        itemStyle.transition = `opacity ${Store.cssAnimationTime} ease`
                    }
                    return (
                        <div key={item.id} style={itemStyle} className={itemClass}> 
                            {item.value} 
                        </div>
                    )                
                })
            }
            </div>
        )
    }
})

export default Store