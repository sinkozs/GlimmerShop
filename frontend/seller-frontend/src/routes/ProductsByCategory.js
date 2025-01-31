import React, { useEffect, useState } from "react";
import { Container } from "react-bootstrap";
import { useParams } from "react-router-dom";

import "../App.css";
import "../styles/Home.css";
import "../styles/ProductsByCategory.css";
import ProductsGrid from "../components/ProductsGrid";
import apiClient from "../utils/apiConfig";

function ProductsByCategory() {
  const [products, setProducts] = useState([]);
  const [categoryData, setCategoryData] = useState(null);
  const [error, setError] = useState(null);
  const { category_name } = useParams();

  useEffect(() => {
    const fetchCategoryAndProducts = async () => {
      try {
        let categoryRequest = { category_name: category_name };
        const categoryResponse = await apiClient.post(
          `/categories/category-by-identifier`,
          categoryRequest
        );
        setCategoryData(categoryResponse.data);
        const productsResponse = await apiClient.get(
          `/categories/products-by-category/${categoryResponse.data.id}`
        );
        setProducts(productsResponse.data);
      } catch (error) {
        console.error("Error fetching data:", error);
        setError("Failed to fetch data. Please try again later.");
      }
    };

    fetchCategoryAndProducts();
  }, [category_name]);

  if (!categoryData || !products) {
    return <Container>Loading...</Container>;
  }

  if (error) {
    return <Container>Error: {error}</Container>;
  }

  return (
    <Container fluid className="category-products-wrapper">
      <Container className="category-products-header">
        <h1>
          {category_name.charAt(0).toUpperCase() + category_name.slice(1)}
        </h1>
        {error && (
          <section style={{ color: "red" }}>
            Error fetching products: {error.message}
          </section>
        )}
      </Container>

      <ProductsGrid products={products} />
    </Container>
  );
}

export default ProductsByCategory;
