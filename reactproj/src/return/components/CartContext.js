import React, { createContext, useContext, useState } from 'react';

const CartContext = createContext();

export const useCart = () => useContext(CartContext);

export const calculateTotal = (cart) => {
    return cart.reduce((total, item) => total + (item.isDeleted ? 0 : item.price * item.quantity), 0);
};

export const CartProvider = ({ children }) => {
    const [cart, setCart] = useState([]);
    const [total, setTotal] = useState(0);

    const updateCart = (newCart) => {
        setCart(newCart);
        setTotal(calculateTotal(newCart));
    };

    const addProductToCart = (product, source, quantity = 1) => {
        const updatedCart = [...cart];
        const existingProductIndex = updatedCart.findIndex(item => item.JAN === product.JAN && item.source === source);

        if (existingProductIndex !== -1) {
            // 既存の商品が見つかった場合、数量を更新
            updatedCart[existingProductIndex].quantity += quantity;
        } else {
            // 新規の商品を追加
            const existingProduct = updatedCart.find(item => item.JAN === product.JAN);
            if (existingProduct) {
                existingProduct.quantity += quantity;
            } else {
                updatedCart.push({ ...product, quantity, source, isDeleted: false, originalQuantity: quantity });
            }
        }

        updateCart(updatedCart);
    };

    const changeProductQuantity = (index, delta) => {
        const updatedCart = [...cart];
        const newQuantity = updatedCart[index].quantity + delta;

        if (newQuantity > 0) {
            updatedCart[index].quantity = newQuantity;
        } else {
            if (updatedCart[index].source === 'transaction') {
                updatedCart[index].isDeleted = true;
                updatedCart[index].quantity = updatedCart[index].originalQuantity;
            } else {
                updatedCart.splice(index, 1);
            }
        }

        updateCart(updatedCart);
    };

    const removeProductFromCart = (index) => {
        const updatedCart = [...cart];
        if (updatedCart[index].source === 'transaction') {
            updatedCart[index].isDeleted = !updatedCart[index].isDeleted;
            updatedCart[index].quantity = updatedCart[index].originalQuantity;
        } else {
            updatedCart.splice(index, 1);
        }
        updateCart(updatedCart);
    };

    return (
        <CartContext.Provider value={{ cart, total, addProductToCart, changeProductQuantity, removeProductFromCart, updateCart }}>
            {children}
        </CartContext.Provider>
    );
};