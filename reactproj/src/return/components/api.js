import axios from 'axios';

const API_KEY = "yxuyIpjq.w4Luq4TU8L4V0sY61z2ZOeSFgc1jaA2D";
const API_HEADERS = {
    "X-Api-Key": API_KEY,
    "Content-Type": "application/json"
};

export const fetchProductByJanCode = async (JANCode) => {
    const url = `http://localhost/api/items/?jan=${JANCode}`;
    const response = await axios.get(url, { headers: API_HEADERS });
    return response.data.results[0];
};

export const fetchTransactionData = async (transactionId) => {
    const url = `http://localhost/api/transactions/?sale_id=${transactionId}`;
    const response = await axios.get(url, { headers: API_HEADERS });
    return response.data;
};

export const sendReturnRequest = async (transactionId) => {
    const requestBody = {
        return_type: "1",
        originSaleid: transactionId,
        staffcode: 1111,
        reason: "1",
        return_products: [],
    };

    const response = await axios.post('http://localhost/api/returntransactions/', requestBody, { headers: API_HEADERS });
    return response.data;
};
