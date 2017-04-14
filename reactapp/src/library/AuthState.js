import { extendObservable } from 'mobx'

class AuthState {
    constructor() {
        extendObservable(this, {
            authState: "authenticating",
            user: null
        })
    }

    setState(obj) {
        if ("authState" in obj) {
            this.authState = obj.authState
        }
        if ("user" in obj) {
            this.user = obj.user
        }
    }
}

export default new AuthState()