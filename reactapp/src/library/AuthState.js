import { extendObservable } from 'mobx'

class AuthState {
    constructor() {
        extendObservable(this, {
            authState: "authenticating",
            user: null
        })
    }

    getCurrentUser() {
        return this.user
    }

    setAuthState(obj) {
        console.log("setAuthState", obj)
        if (obj.hasOwnProperty("authState")) {
            this.authState = obj.authState
        }
        if (obj.hasOwnProperty("user")) {
            this.user = obj.user
        }
    }
}

var StateInstance = new AuthState() 
window.authState = StateInstance

export default StateInstance