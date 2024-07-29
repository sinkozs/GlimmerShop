import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { FaUser, FaShoppingCart, FaBars } from "react-icons/fa";
import { Container, Button } from "react-bootstrap";
import { useCart } from "../context/CartContext";
import "../styles/Header.css";
import "../styles/Cart.css";
import "../styles/ProductFilters.css";
import "../styles/ProductDetails.css";

function Header() {
  const {
    cart,
    removeFromCart,
    increaseQuantity,
    decreaseQuantity,
    calculateSubtotal,
    calculateTotalCartItemCount
  } = useCart();
  const [isOpen, setIsOpen] = useState(false);
  const [isCartOpen, setIsCartOpen] = useState(false);

  const toggleCartDropdown = () => {
    setIsCartOpen(!isCartOpen);
  };

  return (
    <Container fluid className="main-header">
      <Container fluid className="left">
        <FaBars className="hamburger" onClick={() => setIsOpen(!isOpen)} />
        <NavLink to="/" className="logo">
          GLIMMER
        </NavLink>
      </Container>

      <nav className={`menu-items ${isOpen ? "open" : ""}`}>
        <NavLink to="/new" onClick={() => setIsOpen(false)}>
          NEW
        </NavLink>
        <NavLink to="/categories/earrings" onClick={() => setIsOpen(false)}>
          EARRINGS
        </NavLink>
        <NavLink to="/categories/rings" onClick={() => setIsOpen(false)}>
          RINGS
        </NavLink>
        <NavLink to="/categories/necklaces" onClick={() => setIsOpen(false)}>
          NECKLACES
        </NavLink>
        <NavLink to="/categories/bracelets" onClick={() => setIsOpen(false)}>
          BRACELETS
        </NavLink>
      </nav>

      <Container className="menu-icons">
        <NavLink className="nav-link" to="/login">
          <FaUser className="fa-icon" />
        </NavLink>
        <Container className="nav-link">
          <FaShoppingCart className="fa-icon" onClick={toggleCartDropdown} />
          {cart.length > 0 && <span className="item-count">{calculateTotalCartItemCount()}</span>}
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
                        <span className="cart-item-info">
                          ${item.price}
                        </span>
                      </Container>
                      <Container fluid className="cart-item-details">
                        <img
                          className="cart-item-image"
                          src={`http://localhost:8000/${item.image_path}`}
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
              <Button className="add-to-bag-btn">CHECKOUT</Button>
            </Container>
          ) : (
            <p>Your cart is empty.</p>
          )}
        </Container>
      </Container>
    </Container>
  );
}

export default Header;
