import { extendObservable } from 'mobx'

class AppInfo {
    constructor() {
        extendObservable(this, {
            data: null
        })
    }

    getData() {
        return this.data
    }

    getVersion() { return this.data ? this.data.conductor_info.app.version : "" }
    getFlaskVersion() { return this.data ? this.data.conductor_info.flask_version : "" }
    getMongoVersion() { return this.data ? this.data.conductor_info.mongodb.version : "" }

    setData(data) {
        this.data = data
    }
}

var InfoInstance = new AppInfo()
export default InfoInstance