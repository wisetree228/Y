import axios from 'axios';
import { API_BASE_URL, HOST_BASE_URL } from './config';


export const CheckAuthorization = async () =>{
    try{
        await axios.get(`${API_BASE_URL}/my_id`, {withCredentials: true})
    }
    catch{
        window.location.href=HOST_BASE_URL;
    }
    
}

export default CheckAuthorization;