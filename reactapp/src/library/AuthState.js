import { extendObservable } from 'mobx'

const STATE = {
    authState: "authenticating",
    user: null,
    authUrl: null,
    authText: "external auth"
}
const STATE_FIELDS = Object.keys(STATE)

class AuthState {
    constructor() {
        extendObservable(this, STATE)
    }

    getCurrentUser() {
        return this.user
    }

    getAuthUrl() {
        return this.authUrl
    }

    getAuthText() {
        return this.authText
    }

    setAuthState(obj) {
        STATE_FIELDS.forEach(element => {
            if (obj.hasOwnProperty(element)) {
                this[element] = obj[element]
            }
        });
    }
}

var StateInstance = new AuthState() 
window.authState = StateInstance

export default StateInstance