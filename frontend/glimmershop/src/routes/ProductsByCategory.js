import React, { useEffect, useState } from "react";
import { Container, Card, Button } from "react-bootstrap";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";

import "../App.css";
import "../styles/Home.css";
import "../styles/ProductsByCategory.css";
import "../styles/TrendingJewelry.css";
import ProductFilters from "../components/ProductFilters";

function ProductsByCategory() {
  const [products, setProducts] = useState([]);
  const [categoryData, setCategoryData] = useState(null);
  const [error, setError] = useState(null);
  const { category_name } = useParams();
  const navigate = useNavigate();

  useEffect(() => {
    const fetchCategoryAndProducts = async () => {
      try {
        const categoryResponse = await axios.get(
          `http://localhost:8000/categories/category-by-identifier?category_identifier=${category_name}`
        );
        setCategoryData(categoryResponse.data);

        const productsResponse = await axios.get(
          `http://localhost:8000/categories/products-by-category/?category_id=${categoryResponse.data.category_record.id}`
        );
        setProducts(productsResponse.data);
      } catch (error) {
        console.error("Error fetching data:", error);
        setError("Failed to fetch data. Please try again later.");
      }
    };

    fetchCategoryAndProducts();
  }, [category_name]);

  const handleCardClick = (productId) => {
    navigate(`/products/${productId}`);
  };

  const handleProductsFetched = (fetchedProducts) => {
    setProducts(fetchedProducts);
  };

  if (!categoryData || !products) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
    <Container fluid className="category-products-wrapper">
      <Container className="category-products-header">
        <h1>
          {category_name.charAt(0).toUpperCase() + category_name.slice(1)}
        </h1>
        <h3>{categoryData.category_record.category_description}</h3>

        <ProductFilters
          category_id={categoryData.category_record.id}
          onProductsFetched={handleProductsFetched}
        />
        {error && (
          <p style={{ color: "red" }}>
            Error fetching products: {error.message}
          </p>
        )}
        
      </Container>

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

export default ProductsByCategory;
