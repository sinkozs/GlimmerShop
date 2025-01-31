import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import React, { useContext, useEffect, Suspense, lazy } from "react";
import Header from "./components/Header";
import Footer from "./components/Footer";
import LoginAndSignup from "./routes/LoginAndSignup";
import DeleteUser from "./routes/DeleteUser";
import EditUser from "./routes/EditUser";
import SellerHome from "./routes/SellerHome";
import AddNewProduct from "./routes/AddNewProduct";
import AddNewCategoryToProduct from "./routes/AddNewCategoryToProduct";
import EditProduct from "./routes/EditProduct";
import SellerStatistics from "./routes/SellerStatistics";
import { AuthProvider, AuthContext } from "./context/AuthContext";
import { Container } from "react-bootstrap";
import { setLogoutHandler } from "./utils/apiConfig";
import "./App.css";
import "./utils/apiConfig";

const ProductDetails = lazy(() => import("./routes/ProductDetails"));
const ProductsByCategory = lazy(() => import("./routes/ProductsByCategory"));

function LogoutHandler() {
  const { logout } = useContext(AuthContext);

  useEffect(() => {
    setLogoutHandler(logout);
  }, [logout]);

  return null;
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <LogoutHandler />
        <Container className="app-container">
          <Header />
          <Container className="content-container">
            <Routes>
              <Route path="/" element={<LoginAndSignup />} />
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
                    fallback={<Container>Loading Product Details...</Container>}
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
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
