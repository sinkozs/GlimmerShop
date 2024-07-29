import React, { Suspense, lazy } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route } from "react-router-dom";

import Header from "./components/Header";
import Footer from "./components/Footer";
import Home from "./routes/Home";
import { CartProvider } from "./context/CartContext";

const ProductDetails = lazy(() => import("./routes/ProductDetails"));
const ProductsByCategory = lazy(() => import("./routes/ProductsByCategory"));

function App() {
  return (
    <BrowserRouter>
      <CartProvider>
        <div className="app-container">
          <Header />
          <div className="content-container">
            <Routes>
              <Route path="/" element={<Home />} />
              <Route
                path="/products/:product_id"
                element={
                  <Suspense fallback={<div>Loading Product Details...</div>}>
                    <ProductDetails />
                  </Suspense>
                }
              />
              <Route
                path="categories/:category_name"
                element={
                  <Suspense fallback={<div>Loading Products...</div>}>
                    <ProductsByCategory />
                  </Suspense>
                }
              />
            </Routes>
          </div>
          <Footer />
        </div>
      </CartProvider>
    </BrowserRouter>
  );
}

export default App;
