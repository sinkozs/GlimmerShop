import React, { useEffect, useState, useRef, useContext } from "react";

import axios from "axios";
import "../App.css";
import "../styles/Home.css";
import "../styles/ProductDetails.css";
import TrendingJewelry from "../components/TrendingJewelry";
import Modal from "../components/Modal";
import "../styles/TrendingJewelry.css";
import { Container, Button } from "react-bootstrap";
import { useParams } from "react-router-dom";
import { FaTruck, FaRecycle, FaHandshake } from "react-icons/fa";
import { useCart } from "../context/CartContext";
import { AuthContext } from "../context/AuthContext";
import config from "../config";

function ProductDetails() {
  const { product_id } = useParams();
  const { cart, addToCart, increaseQuantity } = useCart();
  const [productData, setProductData] = useState(null);
  const [productCategory, setProductCategory] = useState(null);
  const [sellerData, setSellerData] = useState(null);
  const [currentImage, setCurrentImage] = useState(1);
  const [isDescriptionExpanded, setIsDescriptionExpanded] = useState(false);
  const [isDetailsExpanded, setIsDetailsExpanded] = useState(false);
  const [availability, setAvailability] = useState(false);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState(null);
  const detailsRef = useRef(null);
  const { isAuthenticated } = useContext(AuthContext);

  useEffect(() => {
    const fetchProductData = async () => {
      try {
        const product = await axios.get(
          `${config.BACKEND_BASE_URL}/products/${product_id}`
        );
        const productResponse = product.data.product;
        setProductData(productResponse);
        
        const category = await axios.get(
          `${config.BACKEND_BASE_URL}/categories/product-categories?product_id=${product_id}`
        );
        setProductCategory(category.data[0]);
  
        const seller = await axios.get(
          `${config.BACKEND_BASE_URL}/users/${productResponse.seller_id}`
        );
        setSellerData(seller.data.user);
        setAvailability(productResponse.stock_quantity > 0);
        
      } catch (error) {
        console.error("Error fetching product details:", error);
        setError("Failed to fetch product details. Please try again later.");
      }
    };
  
    if (product_id) {
      fetchProductData();
    }
  }, [product_id]);


  const handleAddToCart = () => {
    if (productData && availability) {
      const existingItem = cart.find((item) => item.id === productData.id);
      if (existingItem) {
        increaseQuantity(productData.id);
      } else {
        addToCart({
          id: productData.id,
          name: productData.name,
          price: productData.price,
          category: productCategory,
          quantity: 1,
        });
      }
    } else if (!availability) {
      setShowModal(true);
    }
  };

  const closeModal = () => {
    setShowModal(false);
  };

  if (error) {
    return <Container>Error: {error}</Container>;
  }

  if (!productData || !sellerData) {
    return <Container>Loading...</Container>;
  }

  const handleImageClick = () => {
    if (window.innerWidth <= 768) {
      setCurrentImage(currentImage === 1 ? 2 : 1);
    }
  };

  const toggleDescription = () => {
    setIsDescriptionExpanded(!isDescriptionExpanded);
  };

  const toggleDetails = () => {
    setIsDetailsExpanded(!isDetailsExpanded);
  };

  return (
    <>
      <Container fluid className="product-details-page">
        <Container fluid className="product-detail-wrapper">
          <Container fluid className="product-grid">
            <Container className="image-section" onClick={handleImageClick}>
              <img
                src={`${config.BACKEND_BASE_URL}/${productData.image_path}`}
                alt={productData.name}
                className={`image-col-1 product-image ${
                  currentImage === 1 ? "" : "hide-on-mobile"
                }`}
              />
              <img
                src={`${config.BACKEND_BASE_URL}/${productData.image_path2}`}
                alt={productData.name}
                className={`image-col-2 product-image ${
                  currentImage === 2 ? "" : "hide-on-mobile"
                }`}
              />
              <Container className="image-indicators">
                <span
                  className={`indicator ${currentImage === 1 ? "active" : ""}`}
                ></span>
                <span
                  className={`second-image indicator ${
                    currentImage === 2 ? "active" : ""
                  }`}
                ></span>
              </Container>
            </Container>

            <Container fluid className="details-section" ref={detailsRef}>
              <h1 className="product-name">{productData.name}</h1>
              <section className="product-price">${productData.price}</section>
              <section className="seller">
                Seller: {sellerData.first_name} {sellerData.last_name}
              </section>
              <section className="product-material">
                {productData.material}
              </section>
              <section className="size-guide">Size Guide</section>
              <Container fluid className="stock-quantity-container">
                <section className="stock-quantity">
                  {availability ? "✓ In Stock" : "✗ Out of Stock"}
                </section>
              </Container>
              {!isAuthenticated && (
                <Button onClick={handleAddToCart} className="add-to-bag-btn">
                  ADD TO BAG
                </Button>
              )}

              <Modal show={showModal} onClose={closeModal} title="Sorry!">
                <section>This product is currently out of stock.</section>
              </Modal>
              <Container fluid className="additional-info">
                <Container fluid className="icon-container">
                  <FaTruck className="product-detail-fa-icon" />
                  <section>Free Shipping on orders over $150</section>
                </Container>
                <Container fluid className="icon-container">
                  <FaRecycle className="product-detail-fa-icon" />
                  <section>Free 30 Day Returns</section>
                </Container>
                <Container fluid className="icon-container">
                  <FaHandshake className="product-detail-fa-icon" />
                  <section>2 Year Warranty</section>
                </Container>
              </Container>
              <Container fluid className="expandable-section">
                <Button onClick={toggleDescription} className="expand-btn">
                  <span className="details-text">Description</span>
                  <span className="expand-icon">
                    {isDescriptionExpanded ? "-" : "+"}
                  </span>
                </Button>
                {isDescriptionExpanded && (
                  <Container className="product-description">
                    <section>{productData.description}</section>
                  </Container>
                )}

                <Button onClick={toggleDetails} className="expand-btn">
                  <span className="details-text">Details</span>
                  <span className="expand-icon">
                    {isDetailsExpanded ? "-" : "+"}
                  </span>
                </Button>
                {isDetailsExpanded && (
                  <Container className="product-description">
                    <section>{productData.description}</section>
                  </Container>
                )}
              </Container>
            </Container>
          </Container>
        </Container>
        <Container fluid className="h1-section-container">
          <h1 className="h1-section-title">YOU MIGHT ALSO LIKE</h1>
        </Container>
      </Container>
      <TrendingJewelry />
    </>
  );
}

export default ProductDetails;
