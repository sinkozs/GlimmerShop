import React, { Suspense, lazy } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";

import Header from "./components/Header";
import Footer from "./components/Footer";
import Home from "./routes/Home";
import LoginAndSignup from "./components/LoginAndSignup";
import DeleteUser from "./components/DeleteUser";
import EditUser from "./components/EditUser";
import SellerHome from "./routes/SellerHome";
import AddNewProduct from "./components/AddNewProduct";
import AddNewCategoryToProduct from "./components/AddNewCategoryToProduct";
import EditProduct from "./components/EditProduct";
import SellerStatistics from "./components/SellerStatistics";
import { CartProvider } from "./context/CartContext";
import { AuthProvider, AuthContext } from "./context/AuthContext";
import { Container } from "react-bootstrap";
import "./utils/apiConfig";

const ProductDetails = lazy(() => import("./routes/ProductDetails"));
const ProductsByCategory = lazy(() => import("./routes/ProductsByCategory"));

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <CartProvider>
          <Container className="app-container">
            <Header />
            <Container className="content-container">
              <Routes>
                <Route path="/" element={<Home />} />
                <Route path="/login" element={<LoginAndSignup />} />
                <Route
                  path="/products/new"
                  element={
                    <AuthContext.Consumer>
                      {({ isAuthenticated }) =>
                        isAuthenticated ? (
                          <Suspense
                            fallback={
                              <Container>
                                Loading Add new product page...
                              </Container>
                            }
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
                  path="/statistics"
                  element={
                    <AuthContext.Consumer>
                      {({ isAuthenticated }) =>
                        isAuthenticated ? (
                          <Suspense
                            fallback={
                              <Container>Loading statistics...</Container>
                            }
                          >
                            <SellerStatistics />
                          </Suspense>
                        ) : (
                          <Navigate to="/" />
                        )
                      }
                    </AuthContext.Consumer>
                  }
                />
                <Route
                  path="/profile/edit"
                  element={
                    <AuthContext.Consumer>
                      {({ isAuthenticated }) =>
                        isAuthenticated ? (
                          <Suspense
                            fallback={
                              <Container>Loading your profile...</Container>
                            }
                          >
                            <EditUser />
                          </Suspense>
                        ) : (
                          <Navigate to="/" />
                        )
                      }
                    </AuthContext.Consumer>
                  }
                />
                <Route
                  path="/profile/delete"
                  element={
                    <AuthContext.Consumer>
                      {({ isAuthenticated }) =>
                        isAuthenticated ? (
                          <Suspense
                            fallback={
                              <Container>Loading your profile...</Container>
                            }
                          >
                            <DeleteUser />
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
                    <Suspense
                      fallback={
                        <Container>Loading Seller Admin page...</Container>
                      }
                    >
                      <SellerHome />
                    </Suspense>
                  }
                />
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
                  path="/products/edit/:product_id"
                  element={
                    <AuthContext.Consumer>
                      {({ isAuthenticated }) =>
                        isAuthenticated ? (
                          <Suspense
                            fallback={
                              <Container>Loading product details...</Container>
                            }
                          >
                            <EditProduct />
                          </Suspense>
                        ) : (
                          <Navigate to="/" />
                        )
                      }
                    </AuthContext.Consumer>
                  }
                />

                <Route
                  path="/add-category-to-product/:product_id"
                  element={
                    <AuthContext.Consumer>
                      {({ isAuthenticated }) =>
                        isAuthenticated ? (
                          <Suspense
                            fallback={
                              <Container>Loading product details...</Container>
                            }
                          >
                            <AddNewCategoryToProduct />
                          </Suspense>
                        ) : (
                          <Navigate to="/" />
                        )
                      }
                    </AuthContext.Consumer>
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
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
