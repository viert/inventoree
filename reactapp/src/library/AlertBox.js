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
        this.mType = mType
        this.value = value
        this.id = Date.now()
        this.className = MESSAGE_CLASSES[mType]
    }
}

export class AlertStore {
    constructor() {
        extendObservable(this, {
            messages: []
        })
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

    newMessage(value, mType) {
        var msg = new Message(value, mType);
        this.messages.push(msg);
        setTimeout(this.removeMessage.bind(this, msg.id), 10000)
    }
}

var Store = new AlertStore();

export const AlertBox = observer(class AlertBox extends Component {
    render() {
        return (
            <div className="alertbox-wrapper">
            {
                Store.messages.map((item) =>
                    (
                        <div key={item.id} className={"alert alert-" + item.className}> 
                            {item.value} 
                        </div>
                    )
                )
            }
            </div>
        )
    }
})

export default Store