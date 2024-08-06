import React, { useEffect, useState, useRef } from "react";
import { Container, Card } from "react-bootstrap";
import { useNavigate } from "react-router-dom";
import "../styles/ProductsByCategory.css";

import "../App.css";
import "../styles/Home.css";
import "../styles/TrendingJewelry.css";

function ProductsGrid({ products }) {
  const navigate = useNavigate();

  const handleCardClick = (productId) => {
    navigate(`/products/${productId}`);
  };

  if (!products || products.length === 0) {
    return <div>No products available.</div>;
  }

  return (
    <Container fluid className="category-products-wrapper">
      <Container fluid className="category-products-grid">
        {products.length > 0 ? (
          products.map((product, idx) => (
            <Card
              key={idx}
              className="category-products-card"
              onClick={() => handleCardClick(product.id)}
            >
              <Card.Body className="trending-card-body">
                <Container className="image-container">
                  <Card.Img
                    variant="top"
                    className="trending-card-image"
                    src={`http://localhost:8000/${product.image_path}`}
                  />
                  <Card.Img
                    variant="top"
                    className="trending-card-hover"
                    src={`http://localhost:8000/${product.image_path2}`}
                  />
                </Container>
              </Card.Body>
              <Card.Footer className="card-footer">
                <Card.Text className="footer-text">{product.name}</Card.Text>
                <Card.Text className="footer-text-price">
                  ${product.price}
                </Card.Text>
              </Card.Footer>
            </Card>
          ))
        ) : (
          <p>No products available.</p>
        )}
      </Container>
    </Container>
  );
}

export default ProductsGrid;
