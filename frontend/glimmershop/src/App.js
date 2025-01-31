import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import React, { useContext, useEffect, Suspense, lazy } from "react";
import Header from "./components/Header";
import Footer from "./components/Footer";
import Home from "./routes/Home";
import CheckoutPage from "./routes/CheckoutPage";
import { CartProvider } from "./context/CartContext";
import { Container } from "react-bootstrap";
import "./utils/apiConfig";
import "./App.css";

const ProductDetails = lazy(() => import("./routes/ProductDetails"));
const ProductsByCategory = lazy(() => import("./routes/ProductsByCategory"));

function App() {
  return (
    <BrowserRouter>
        <CartProvider>
          <Container className="app-container">
            <Header />
            <Container className="content-container">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/checkout" element={<CheckoutPage />} />  
                <Route
                  path="/products/:product_id"
                  element={
                    <Suspense
                      fallback={
                        <Container>Loading Product Details...</Container>
                      }
                    >
                      <ProductDetails />
                    </Suspense>
                  }
                />
                <Route
                  path="categories/:category_name"
                  element={
                    <Suspense
                      fallback={<Container>Loading Products...</Container>}
                    >
                      <ProductsByCategory />
                    </Suspense>
                  }
                />
              </Routes>
            </Container>
            <Footer />
          </Container>
        </CartProvider>
    </BrowserRouter>
  );
}

export default App;
