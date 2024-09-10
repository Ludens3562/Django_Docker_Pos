import React from 'react';
import { useCart } from './CartContext';

const CartTable = () => {
    const { cart, changeProductQuantity, removeProductFromCart } = useCart();

    return (
        <div className="cart-table-container">
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
                        <tr key={index} className={`${item.isDeleted ? 'deleted' : ''} ${item.source === 'JAN' ? 'JAN-added' : ''} ${item.quantity !== item.originalQuantity ? 'modified' : ''}`}>
                            <td><button onClick={() => removeProductFromCart(index)}>{item.isDeleted ? '取消' : '削除'}</button></td>
                            <td>{item.name}</td>
                            <td>¥{parseInt(item.price, 10)}</td>
                            <td>{parseInt(item.tax)}%</td>
                            <td>
                                {item.isDeleted ? (
                                    item.quantity
                                ) : (
                                    <>
                                        <button onClick={() => changeProductQuantity(index, -1)}>-</button>
                                        {item.quantity}
                                        <button onClick={() => changeProductQuantity(index, 1)}>+</button>
                                    </>
                                )}
                            </td>
                        </tr>
                    ))}
                </tbody>
            </table>
        </div>
    );
};

export default CartTable;
