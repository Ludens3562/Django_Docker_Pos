import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { fetchProductByJanCode, fetchTransactionData, sendReturnRequest } from './components/api.js';
import { CartProvider, useCart } from './components/CartContext.js';
import InputField from './components/InputField.js';
import CartTable from './components/CartTable.js';
import CouponModal from './components/CouponModal.js';
import TransactionDetails from './components/TransactionDetails.js';
import './Return.css';

const Return = () => {
    const [JANCode, setJanCode] = useState('');
    const [transactionId, setTransactionId] = useState('');
    const [couponCode, setCouponCode] = useState('');
    const [isCouponModalOpen, setIsCouponModalOpen] = useState(false);
    const [errorMessage, setErrorMessage] = useState('');
    const [transactionData, setTransactionData] = useState(null);
    const navigate = useNavigate();
    const { cart, total, addProductToCart, updateCart } = useCart();

    const handleAddProduct = async () => {
        try {
            if (!JANCode) throw new Error('JANコードを入力してください');
            const product = await fetchProductByJanCode(JANCode);
            addProductToCart(product, 'JAN');
            setJanCode('');
            setErrorMessage('');
        } catch (error) {
            setErrorMessage(`商品情報の取得に失敗しました: ${error.message}`);
        }
    };

    const handleFetchTransaction = async () => {
        try {
            if (!transactionId) throw new Error('取引IDを入力してください');
            const transaction = await fetchTransactionData(transactionId);
            const transactionResult = transaction.results[0];
            setTransactionData(transactionResult);
            const newCart = transactionResult.saleproduct_set.map(item => ({
                JAN: item.JAN,
                name: item.name,
                price: item.price,
                tax: item.tax,
                quantity: item.points,
                source: 'transaction',
                isDeleted: false,
                originalQuantity: item.points,
            }));
            updateCart([...cart, ...newCart]);
            setErrorMessage('');
        } catch (error) {
            setErrorMessage(`取引データの取得に失敗しました: ${error.message}`);
        }
    };

    const handleKeyPress = (event) => {
        if (event.key === 'Enter') {
            if (event.target.name === 'janCode') {
                handleAddProduct();
            } else if (event.target.name === 'transactionId') {
                handleFetchTransaction();
            }
        }
    };

    const handleChange = (setter, regex) => (e) => {
        const value = e.target.value;
        if (regex.test(value)) {
            setter(value);
        }
    };

    const proceedToPayment = async () => {
        try {
            await sendReturnRequest(transactionId);
            navigate('/payment', {
                state: { cart, total, couponCode },
            });
        } catch (error) {
            setErrorMessage(`返品リクエストの送信に失敗しました: ${error.message}`);
        }
    };

    const originalTotalAmount = transactionData ? transactionData.total_amount : 0;
    const difference = total - originalTotalAmount;

    return (
        <div className="container">
            <h1>返品登録</h1>
            {errorMessage && <div className="error-message">{errorMessage}</div>}
            <InputField
                name="transactionId"
                value={transactionId}
                onChange={handleChange(setTransactionId, /^[A-Z0-9]*$/)}
                onKeyPress={handleKeyPress}
                placeholder="取引IDを入力"
                maxLength={15}
            />
            <TransactionDetails transactionData={transactionData} />
            <h2>取引商品</h2>
            <InputField
                name="janCode"
                value={JANCode}
                onChange={handleChange(setJanCode, /^\d*$/)}
                onKeyPress={handleKeyPress}
                placeholder="追加商品のJANコードを入力"
                maxLength={13}
            />
            <CartTable />
            <h2>合計: ¥{total.toFixed(0)}</h2>
            <h3>元伝票との差額: ¥{difference.toFixed(0)}</h3>
            <div className="button-container">
                <button onClick={() => setIsCouponModalOpen(true)}>クーポン利用</button>
                <button onClick={proceedToPayment}>お会計に進む</button>
            </div>
            <CouponModal
                isOpen={isCouponModalOpen}
                onClose={() => setIsCouponModalOpen(false)}
                couponCode={couponCode}
                onCouponCodeChange={(e) => setCouponCode(e.target.value)}
            />
        </div>
    );
};

export default () => (
    <CartProvider>
        <Return />
    </CartProvider>
);
