import HttpErrorHandler from '../../../library/HttpErrorHandler'
import AutosuggestContainer from '../../common/AutosuggestContainer'
import Axios from 'axios'

export default class HostPicker extends AutosuggestContainer {
    loadData(value, callback) {
        Axios.get(`/api/v1/hosts/?_filter=${value}&_limit=5`)
            .then( response => { callback(response.data.data) })
            .catch(HttpErrorHandler)
    }
}