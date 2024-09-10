import React from 'react';

const TransactionDetails = ({ transactionData }) => {
    if (!transactionData) return null;

    return (
        <div>
            <h2>取引情報</h2>
            <table className="transaction-table">
                <tbody>
                    <tr>
                        <th>取引タイプ</th>
                        <td>{transactionData.sale_type}</td>
                        <th>取引ID</th>
                        <td>{transactionData.sale_id}</td>
                        <th>取引日</th>
                        <td>{new Date(transactionData.sale_date).toLocaleString()}</td>
                    </tr>
                    <tr>
                        <th>店舗コード</th>
                        <td>{transactionData.storecode}</td>
                        <th>スタッフコード</th>
                        <td>{transactionData.staffcode}</td>
                        <td colSpan="2"></td>
                    </tr>
                    <tr>
                        <th>合計金額</th>
                        <td>¥{transactionData.total_amount}</td>
                        <th>預かり金</th>
                        <td>¥{transactionData.deposit}</td>
                        <th>お釣り</th>
                        <td>¥{transactionData.change}</td>
                    </tr>
                    <tr>
                        <th>8%税</th>
                        <td>¥{transactionData.tax_8_percent}</td>
                        <th>10%税</th>
                        <td>¥{transactionData.tax_10_percent}</td>
                        <th>税額合計</th>
                        <td>¥{transactionData.tax_amount}</td>
                    </tr>
                    <tr>
                        <th>点数</th>
                        <td>{transactionData.purchase_points}</td>
                        <th>クーポンコード</th>
                        <td>{transactionData.coupon_code}</td>
                        <th>割引額</th>
                        <td>¥{transactionData.discount_amount}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    );
};

export default TransactionDetails;