import React from 'react';
import Modal from 'react-modal';

const CouponModal = ({ isOpen, onClose, couponCode, onCouponCodeChange }) => (
    <Modal
        isOpen={isOpen}
        onRequestClose={onClose}
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
            onChange={onCouponCodeChange}
            placeholder="クーポンコードを入力"
        />
        <button onClick={onClose}>閉じる</button>
    </Modal>
);

export default CouponModal;