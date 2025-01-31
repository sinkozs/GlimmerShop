import React, { useState, useContext } from "react";
import { NavLink } from "react-router-dom";
import { FaUser, FaBars } from "react-icons/fa";
import { Container, Button } from "react-bootstrap";
import { AuthContext } from "../context/AuthContext";
import "../styles/Header.css";
import "../styles/ProductDetails.css";

function Header() {
  const [isOpen, setIsOpen] = useState(false);
  const { isAuthenticated, logout } = useContext(AuthContext);

  const toggleHeaderSidebar = () => {
    setIsOpen(!isOpen);
  };

  const handleLogout = () => {
    logout();
  };

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
        {isAuthenticated && (
          <>
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
            <NavLink
              to="/products/new"
              className="sidebar-item"
              onClick={toggleHeaderSidebar}
            >
              ADD NEW PRODUCT
            </NavLink>
            <NavLink
              to="/statistics"
              className="sidebar-item"
              onClick={toggleHeaderSidebar}
            >
              STATISTICS
            </NavLink>
            {(() => {
              const id = localStorage.getItem("seller_id");
              return (
                <NavLink
                  to={`/seller/${id}`}
                  className="sidebar-item"
                  onClick={toggleHeaderSidebar}
                >
                  MY PRODUCTS
                </NavLink>
              );
            })()}
          </>
        )}
      </nav>

      {!isAuthenticated && (
        <Button
          onClick={() => (window.location.href = "http://localhost:3000/")}
          className="sign-up-btn"
        >
          <h3>I'm a customer</h3>
        </Button>
      )}

      {isAuthenticated && (
        <Container className="menu-icons">
          <NavLink className="nav-link" to="/profile/edit">
            <FaUser className="fa-icon" />
          </NavLink>
          <Button className="nav-link logout-btn" onClick={handleLogout}>
            Logout
          </Button>
        </Container>
      )}
    </Container>
  );
}

export default Header;
