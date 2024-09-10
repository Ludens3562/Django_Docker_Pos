import React, { useState } from 'react';
import axios from 'axios';
import { useLocation, useNavigate } from 'react-router-dom';

const Payment = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const [deposit, setDeposit] = useState('');
    const { cart, total, couponCode } = location.state || { cart: [], total: 0, couponCode: '' };

    const handleConfirmPayment = async () => {
        // 入力された預かり金額を数値に変換
        const depositAmount = parseFloat(deposit);

        // 預かり金額が有効であることを確認
        if (isNaN(depositAmount) || depositAmount <= 0) {
            alert('有効な預かり金額を入力してください。');
            return;
        }

        const transactionData = {
            sale_type: 1,
            storecode: 781,
            staffcode: 1111,
            deposit: depositAmount,
            sale_products: cart.map(item => ({
                JAN: item.jan,
                points: item.quantity || 0
            })),
            coupon_code: couponCode || ''
        };

        const url = 'http://localhost/api/transactions/';
        const key = "yxuyIpjq.w4Luq4TU8L4V0sY61z2ZOeSFgc1jaA2D";
        const headers = {
            "X-Api-Key": key,
            "Content-Type": "application/json"
        };
        try {
            console.log(transactionData);
            const response = await axios.post(url, transactionData, { headers });
            console.log(`ステータスコード: ${response.status}`);
            console.log(response.data);
            navigate('/confirmation', { state: { saleData: response.data } });
        } catch (error) {
            console.error('会計情報の送信に失敗しました', error);
            if (error.response) {
                console.error(`ステータスコード: ${error.response.status}`);
                console.error(error.response.data);
            } else {
                console.error(error.message);
            }
        }
    };

    return (
        <div className="container">
            <h1>お預かり金額の入力</h1>
            <h2>合計金額: ¥{total}</h2>
            <input
                type="number"
                value={deposit}
                onChange={(e) => setDeposit(e.target.value)}
                placeholder="お預かり金額を入力"
            />
            <button onClick={handleConfirmPayment}>会計を確定する</button>
        </div>
    );
};

export default Payment;
