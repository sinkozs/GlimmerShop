import React, { Suspense, lazy } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Header from "./components/Header";
import Footer from "./components/Footer";
import Home from "./routes/Home";
import LoginAndSignup from "./components/LoginAndSignup";
import SellerHome from "./routes/SellerHome";
import AddNewProduct from "./components/AddNewProduct";
import { CartProvider } from "./context/CartContext";
import { AuthProvider, AuthContext } from "./context/AuthContext";

const ProductDetails = lazy(() => import("./routes/ProductDetails"));
const ProductsByCategory = lazy(() => import("./routes/ProductsByCategory"));

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <CartProvider>
          <div className="app-container">
            <Header />
            <div className="content-container">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/sign-in" element={<LoginAndSignup />} />
                <Route
                  path="/products/new"
                  element={
                    <AuthContext.Consumer>
                      {({ isAuthenticated }) =>
                        isAuthenticated ? (
                          <Suspense
                            fallback={<div>Loading Add new product page...</div>}
                          >
                            <AddNewProduct />
                          </Suspense>
                        ) : (
                          <Navigate to="/" />
                        )
                      }
                    </AuthContext.Consumer>
                  }
                />
                <Route
                  path="/seller/:seller_id"
                  element={
                    <Suspense fallback={<div>Loading Seller Admin page...</div>}>
                      <SellerHome />
                    </Suspense>
                  }
                />
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
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
