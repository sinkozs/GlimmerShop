import React, { useEffect, useState } from "react";
import { NavLink } from "react-router-dom";
import { FaUser, FaShoppingCart, FaBars } from "react-icons/fa";
import { Container, Button } from "react-bootstrap";
import { useCart } from "../context/CartContext";
import "../styles/Header.css";
import "../styles/Cart.css";
import "../styles/ProductFilters.css";
import "../styles/ProductDetails.css";
import Checkout from "./CheckoutButton";
import config from "../config";

function Header() {
  const {
    cart,
    removeFromCart,
    increaseQuantity,
    decreaseQuantity,
    calculateSubtotal,
    calculateTotalCartItemCount,
    deleteCart,
  } = useCart();
  const [isOpen, setIsOpen] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);

  const toggleCartDropdown = () => {
    if (cart.length > 0) {
      setIsCartOpen(!isCartOpen);
    }
  };

  const toggleHeaderSidebar = () => {
    setIsOpen(!isOpen);
  };

  useEffect(() => {
    if (cart.length === 0) {
      setIsCartOpen(false);
    }
  }, [cart.length]);

  return (
    <Container fluid className="main-header">
      <Container fluid className="left">
        <FaBars className="hamburger" onClick={toggleHeaderSidebar} />
        <NavLink to="/" className="logo">
          GLIMMER
        </NavLink>
      </Container>

      <nav className={`header-sidebar ${isOpen ? "open" : ""}`}>
        {isOpen && (
          <Container fluid className="header-sidebar-top">
            <h3>Glimmer</h3>
            <Button
              className="close-header-sidebar-btn"
              onClick={toggleHeaderSidebar}
            >
              X
            </Button>
          </Container>
        )}
        <NavLink
          to="/categories/earrings"
          className="sidebar-item"
          onClick={toggleHeaderSidebar}
        >
          EARRINGS
        </NavLink>
        <NavLink
          to="/categories/rings"
          className="sidebar-item"
          onClick={toggleHeaderSidebar}
        >
          RINGS
        </NavLink>
        <NavLink
          to="/categories/necklaces"
          className="sidebar-item"
          onClick={toggleHeaderSidebar}
        >
          NECKLACES
        </NavLink>
        <NavLink
          to="/categories/bracelets"
          className="sidebar-item"
          onClick={toggleHeaderSidebar}
        >
          BRACELETS
        </NavLink>
      </nav>

      <Container className="menu-icons">
        <>
          <Button
            onClick={() =>
              (window.location.href = "http://localhost:3001/")
            }
            className="sign-up-btn"
          >
            <h3>Seller Login</h3>
          </Button>
          <Container className="nav-link cart-container">
            <FaShoppingCart className="fa-icon" onClick={toggleCartDropdown} />
            {cart.length > 0 && (
              <span className="item-count">
                {calculateTotalCartItemCount()}
              </span>
            )}
          </Container>
        </>
      </Container>

      <Container className={`show-cart-sidebar ${isCartOpen ? "show" : ""}`}>
        {cart.length > 0 ? (
          <Container fluid className="cart-sidebar">
            <Container fluid className="filters-header">
              <h3>Your Bag ({calculateTotalCartItemCount()})</h3>
              <Button
                className="close-filters-section-btn"
                onClick={toggleCartDropdown}
              >
                X
              </Button>
            </Container>
            <Container fluid className="cart-items-list">
              {cart.map((item) => (
                <Container key={item.id} className="cart-item">
                  <Container fluid className="cart-item-section">
                    <Container fluid className="cart-item-section-header">
                      <span className="cart-item-name">{item.name}</span>
                      <span className="cart-item-info">${item.price}</span>
                    </Container>
                    <Container fluid className="cart-item-details">
                      <img
                        className="cart-item-image"
                        src={`${config.BACKEND_BASE_URL}/${item.image_path}`}
                        alt={item.image_path}
                      />
                      <Container className="cart-item-info">
                        <span className="cart-item-material">
                          {item.material}
                        </span>
                      </Container>
                    </Container>
                    <Container className="item-controls">
                      <Button
                        onClick={() => decreaseQuantity(item.id)}
                        aria-label="Decrease quantity"
                      >
                        -
                      </Button>
                      <span className="cart-item-info">{item.quantity}</span>
                      <Button
                        onClick={() => increaseQuantity(item.id)}
                        aria-label="Increase quantity"
                      >
                        +
                      </Button>
                      <Button
                        onClick={() => removeFromCart(item.id)}
                        aria-label="Remove item"
                      >
                        Remove
                      </Button>
                    </Container>
                  </Container>
                </Container>
              ))}
            </Container>
            <Container className="subtotal-section">
              <h3>Subtotal: </h3>
              <h3>${calculateSubtotal()}</h3>
            </Container>
            <Checkout userCart={cart} deleteCart={deleteCart} />
          </Container>
        ) : (
          <section>Your cart is empty.</section>
        )}
      </Container>
    </Container>
  );
}

export default Header;
