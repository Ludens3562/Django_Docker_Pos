import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import Modal from 'react-modal';
import './Register.css';

const Register = () => {
    const [janCode, setJanCode] = useState('');
    const [cart, setCart] = useState([]);
    const [total, setTotal] = useState(0);
    const [couponCode, setCouponCode] = useState('');
    const [isCouponModalOpen, setIsCouponModalOpen] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const navigate = useNavigate();

    const handleAddProduct = async () => {
        const url = `http://localhost/api/items/?jan=${janCode}`;
        const key = "yxuyIpjq.w4Luq4TU8L4V0sY61z2ZOeSFgc1jaA2D";
        const headers = {
            "X-Api-Key": key,
            "Content-Type": "application/json"
        };

        try {
            const response = await axios.get(url, { headers });
            const product = response.data.results[0];

            const existingProductIndex = cart.findIndex(item => item.jan === product.jan);

            if (existingProductIndex !== -1) {
                const updatedCart = [...cart];
                updatedCart[existingProductIndex].quantity += 1;
                setCart(updatedCart);
            } else {
                setCart([...cart, { ...product, jan: janCode, quantity: 1 }]);
            }

            setTotal(total + parseFloat(product.price));
            setJanCode('');
            setErrorMessage('');  // エラーをクリア
        } catch (error) {
            setErrorMessage('商品情報の取得に失敗しました: ' + error.message);
        }
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            handleAddProduct();
        }
    };

    const handleQuantityChange = (index, delta) => {
        const updatedCart = [...cart];
        updatedCart[index].quantity += delta;
        if (updatedCart[index].quantity <= 0) {
            updatedCart.splice(index, 1);
        }
        setCart(updatedCart);
        setTotal(updatedCart.reduce((total, item) => total + item.price * item.quantity, 0));
    };

    const handleRemoveProduct = (index) => {
        const updatedCart = [...cart];
        updatedCart.splice(index, 1);
        setCart(updatedCart);
        setTotal(updatedCart.reduce((total, item) => total + item.price * item.quantity, 0));
    };

    const handleProceedToPayment = () => {
        navigate('/payment', {
            state: {
                cart,
                total,
                couponCode
            }
        });
    };

    const openCouponModal = () => {
        setIsCouponModalOpen(true);
    };

    const closeCouponModal = () => {
        setIsCouponModalOpen(false);
    };

    const handleJanCodeChange = (e) => {
        const value = e.target.value;
        // 数値のみを受け付ける
        if (/^\d*$/.test(value)) {
            setJanCode(value);
        }
    };

    return (
        <div className="container">
            <h1>商品登録</h1>
            {errorMessage && <div className="error-message">{errorMessage}</div>}
            <input
                type="text"
                value={janCode}
                onChange={handleJanCodeChange}
                onKeyPress={handleKeyPress}
                placeholder="JANコードを入力"
            />
            <h2>カート</h2>
            <table className="cart-table">
                <thead>
                    <tr>
                        <th>削除</th>
                        <th>商品名</th>
                        <th>価格</th>
                        <th>税率</th>
                        <th>数量</th>
                    </tr>
                </thead>
                <tbody>
                    {cart.map((item, index) => (
                        <tr key={index}>
                            <td><button onClick={() => handleRemoveProduct(index)}>削除</button></td>
                            <td>{item.name}</td>
                            <td>¥{parseInt(item.price, 10)}</td>
                            <td>{parseInt(item.tax)}%</td>
                            <td>
                                <button onClick={() => handleQuantityChange(index, -1)}>-</button>
                                {item.quantity}
                                <button onClick={() => handleQuantityChange(index, 1)}>+</button>
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
            <h2>合計: ¥{total.toFixed(0)}</h2>
            <button onClick={openCouponModal}>クーポン利用</button>
            <button onClick={handleProceedToPayment}>お会計に進む</button>
            <Modal
                isOpen={isCouponModalOpen}
                onRequestClose={closeCouponModal}
                contentLabel="クーポンコード入力"
                style={{
                    content: {
                        width: '300px',
                        height: '200px',
                        margin: 'auto'
                    }
                }}
            >
                <h2>クーポンコードを入力</h2>
                <input
                    type="text"
                    value={couponCode}
                    onChange={(e) => setCouponCode(e.target.value)}
                    placeholder="クーポンコードを入力"
                />
                <button onClick={closeCouponModal}>閉じる</button>
            </Modal>
        </div>
    );
};

export default Register;
