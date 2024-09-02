import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

const Confirmation = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const { saleData } = location.state || {};

    if (!saleData) {
        return <p>データがありません。</p>;
    }

    const {
        sale_id, storecode, staffcode, deposit, sale_date, purchase_points,
        tax_10_percent, tax_8_percent, tax_amount, total_amount, change, saleproduct_set
    } = saleData;

    const handleNextTransaction = () => {
        navigate('/Register'); // 次の会計ページに遷移
    };

    return (
        <div className="container">
            <h1>会計完了</h1>
            <p>ご利用ありがとうございました。</p>
            <h2>会計情報</h2>
            <p>会計ID: {sale_id}</p>
            <p>店舗コード: {storecode}</p>
            <p>スタッフコード: {staffcode}</p>
            <p>預かり金: {deposit}円</p>
            <p>会計日時: {new Date(sale_date).toLocaleString()}</p>
            <p>購入点数: {purchase_points}点</p>
            <p>10%消費税: {tax_10_percent}円</p>
            <p>8%消費税: {tax_8_percent}円</p>
            <p>消費税合計: {tax_amount}円</p>
            <p>合計金額: {total_amount}円</p>
            <p>お釣り: {change}円</p>
            <h2>購入商品</h2>
            <ul>
                {saleproduct_set.map((product, index) => (
                    <li key={index}>
                        <p>商品名: {product.name}</p>
                        <p>価格: {product.price}円</p>
                        <p>税率: {product.tax}%</p>
                        <p>点数: {product.points}点</p>
                    </li>
                ))}
            </ul>
            <button onClick={handleNextTransaction}>次の会計に進む</button>
        </div>
    );
};

export default Confirmation;
