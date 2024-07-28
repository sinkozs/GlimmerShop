import React, { useEffect, useState } from "react";
import { Container, Card } from "react-bootstrap";
import { useNavigate, useParams } from "react-router-dom";
import axios from "axios";

import "../App.css";
import "../styles/Home.css";
import "../styles/ProductsByCategory.css";
import "../styles/TrendingJewelry.css";
import FilterByPrice from "../components/FilterByPrice";
import FilterByMaterial from "../components/FilterByMaterial";

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

            // Initially fetch all products for the category
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
    console.log("Navigating to product with ID:", productId);
    navigate(`/products/${productId}`);
  };

  const handleProductsFetched = (fetchedProducts) => {
    console.log("Fetched Products:", fetchedProducts);
    setProducts(fetchedProducts);
    console.log("Updated State:", products); 
};

  if (!categoryData || !products) {
    return <div>Loading...</div>;
  }

  if (error) {
    return <div>Error: {error}</div>;
  }

  return (
      <Container fluid className="category-products-wrapper">
      <h1>{category_name.charAt(0).toUpperCase() + category_name.slice(1)}</h1>
      <h3>{categoryData.category_record.category_description}</h3>
      <FilterByPrice category_id={categoryData.category_record.id} onProductsFetched={handleProductsFetched} />
      {error && <p style={{ color: "red" }}>Error fetching products: {error.message}</p>}
      <FilterByMaterial category_id={categoryData.category_record.id} onProductsFetched={handleProductsFetched} />
      {error && <p style={{ color: "red" }}>Error fetching products: {error.message}</p>}
        <Container fluid className="category-products-grid">
          {products.length > 0 ? (
            products.map((product, idx) => (
              <Card
                key={idx}
                className="category-products-card"
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
      </Container>
  );
}

export default ProductsByCategory;
