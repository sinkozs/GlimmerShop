import React, { useState } from "react";
import { NavLink } from "react-router-dom";
import { FaUser, FaShoppingCart, FaBars } from "react-icons/fa";
import "../styles/Header.css";
import { Container } from "react-bootstrap";

function Header() {
  const [isOpen, setIsOpen] = useState(false);

  return (
    <Container fluid className="main-header">
      <Container fluid className="left">
        <FaBars className="hamburger" onClick={() => setIsOpen(!isOpen)} />
        <div className="logo">GLIMMER</div>
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

      <div className="menu-icons">
        <NavLink className="nav-link" to="/login">
          <FaUser className="fa-icon" />
        </NavLink>
        <NavLink className="nav-link" to="/cart">
          <FaShoppingCart className="fa-icon" />
        </NavLink>
      </div>
    </Container>
  );
}

export default Header;
