import React from 'react';

const InputField = ({ name, value, onChange, onKeyPress, placeholder, maxLength }) => (
    <input
        type="text"
        name={name}
        value={value}
        onChange={onChange}
        onKeyPress={onKeyPress}
        placeholder={placeholder}
        maxLength={maxLength}
    />
);

export default InputField;