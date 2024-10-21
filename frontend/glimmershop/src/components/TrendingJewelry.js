import React, { useEffect, useState, useRef } from "react";
import axios from "axios";
import { Container, Card } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

import "../App.css";
import "../styles/Home.css";
import "../styles/TrendingJewelry.css";

function TrendingJewelry() {
  const [products, setProducts] = useState([]);
  const [error, setError] = useState(null);
  const scrollRef = useRef(null);
  const navigate = useNavigate();

  useEffect(() => {
    getTopProducts();
  }, []);

  const getTopProducts = async () => {
    try {
      const response = await axios.get("http://127.0.0.1:8000/products");

      setProducts(response.data);
    } catch (error) {
      console.error("Error fetching products:", error);
      setError(error);
    }
  };

  const scrollLeft = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollBy({
        left: -scrollRef.current.offsetWidth * 0.5,
        behavior: "smooth",
      });
    }
  };

  const scrollRight = () => {
    if (scrollRef.current) {
      scrollRef.current.scrollBy({
        left: scrollRef.current.offsetWidth * 0.5,
        behavior: "smooth",
      });
    }
  };

  const handleCardClick = (productId) => {
    navigate(`/products/${productId}`);
  };

  return (
    <Container fluid className="trending-section-wrapper">
      {error && (
        <p style={{ color: "red" }}>Error fetching products: {error.message}</p>
      )}

      <Container fluid className="trending-section-grid" ref={scrollRef}>
        <Container className="arrow left-arrow" onClick={scrollLeft}>
          {"<"}
        </Container>
        {products.length > 0 ? (
          products.map((product, idx) => (
            <Card
              key={idx}
              className="trending-card"
              onClick={() => handleCardClick(product.id)}
            >
              <Card.Body className="trending-card-body">
                <div className="image-container">
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
                </div>
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
      <Container className="arrow right-arrow" onClick={scrollRight}>
        {">"}
      </Container>
    </Container>
  );
}

export default TrendingJewelry;
