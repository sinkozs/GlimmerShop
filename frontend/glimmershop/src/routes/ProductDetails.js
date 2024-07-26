import React, { useEffect, useState } from "react";
import axios from "axios";
import "../App.css";
import "../styles/Home.css";
import "../styles/ProductDetails.css";
import { Container, Button } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { FaTruck, FaRecycle, FaHandshake } from "react-icons/fa";

function ProductDetails() {
  const { product_id } = useParams();
  const [productData, setProductData] = useState(null);
  const [sellerData, setSellerData] = useState(null);
  const [currentImage, setCurrentImage] = useState(1);
  const [availability, setAvailability] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchProductData = async () => {
      try {
        const product = await axios.get(
          `http://localhost:8000/products/${product_id}`
        );
        setProductData(product.data);

        const seller = await axios.get(
          `http://127.0.0.1:8000/users/public/${product.data.seller_id}`
        );
        setSellerData(seller.data);
        setAvailability(product.data.stock_quantity > 0);
      } catch (error) {
        console.error("Error fetching event details:", error);
        setError("Failed to fetch product details. Please try again later.");
      }
    };
    fetchProductData();
  }, [product_id]);

  if (error) {
    return <div>Error: {error}</div>;
  }

  if (!productData || !sellerData) {
    return <div>Loading...</div>;
  }

  const handleImageClick = () => {
    if (window.innerWidth <= 768) {
      setCurrentImage(currentImage === 1 ? 2 : 1);
    }
  };

  return (
    <Container fluid className="product-detail-wrapper">
      <Container fluid className="product-grid">
        <Container className="image-section" onClick={handleImageClick}>
          <img
            src={`http://localhost:8000/${productData.image_path}`}
            alt={productData.name}
            className={`image-col-1 product-image ${currentImage === 1 ? "" : "hide-on-mobile"}`}
          />
          <img
            src={`http://localhost:8000/${productData.image_path2}`}
            alt={productData.name}
            className={`image-col-2 product-image ${currentImage === 2 ? "" : "hide-on-mobile"}`}
          />
        </Container>
        <Container fluid className="details-section">
          <h1 className="product-name">{productData.name}</h1>
          <p className="product-price">${productData.price}</p>
          <p className="product-material">{productData.material}</p>
          <p className="size-guide">Size Guide</p>
          <Container fluid className="stock-quantity-container">
            <p className="stock-quantity">
              {availability ? "✓ In Stock" : "✗ Out of Stock"}
            </p>
          </Container>
          <Button className="add-to-bag-btn">ADD TO BAG</Button>
          <Container fluid className="additional-info">
            <Container fluid className="icon-container">
              <FaTruck className="product-detail-fa-icon" />
              <p>Free Shipping on orders over $150</p>
            </Container>
            <Container fluid className="icon-container">
              <FaRecycle className="product-detail-fa-icon" />
              <p>Free 30 Day Returns</p>
            </Container>
            <Container fluid className="icon-container">
              <FaHandshake className="product-detail-fa-icon" />
              <p>2 Year Warranty</p>
            </Container>
          </Container>
        </Container>
      </Container>
    </Container>
  );
}

export default ProductDetails;
