import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import Register from './sales/Register';
import Confirmation from './sales/Confirmation';
import Payment from './sales/Payment';
import Return from './return/Return';
import './App.css';

function App() {
    return (
        <Router>
            <Routes>
                <Route path="/register" element={<Register />} />
                <Route path="/confirmation" element={<Confirmation />} />
                <Route path="/payment" element={<Payment />} />
                <Route path="/return" element={<Return />} />
            </Routes>
        </Router>
    );
}

export default App;
