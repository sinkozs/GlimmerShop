import React, { useEffect, useState } from "react";
import { Container } from "react-bootstrap";
import { useParams } from "react-router-dom";
import axios from "axios";

import "../App.css";
import "../styles/Home.css";
import "../styles/ProductsByCategory.css";
import "../styles/TrendingJewelry.css";
import ProductFilters from "../components/ProductFilters";
import ProductsGrid from "../components/ProductsGrid";
import config from "../config";

function ProductsByCategory() {
  const [products, setProducts] = useState([]);
  const [categoryData, setCategoryData] = useState(null);
  const [error, setError] = useState(null);
  const { category_name } = useParams();

  useEffect(() => {
    const fetchCategoryAndProducts = async () => {
      try {
        const categoryResponse = await axios.get(
          `${config.BACKEND_BASE_URL}/categories/category-by-identifier?category_identifier=${category_name}`
        );
        setCategoryData(categoryResponse.data);

        const productsResponse = await axios.get(
          `${config.BACKEND_BASE_URL}/categories/products-by-category/?category_id=${categoryResponse.data.category_record.id}`
        );
        setProducts(productsResponse.data);
      } catch (error) {
        console.error("Error fetching data:", error);
        setError("Failed to fetch data. Please try again later.");
      }
    };

    fetchCategoryAndProducts();
  }, [category_name]);

  const handleProductsFetched = (fetchedProducts) => {
    setProducts(fetchedProducts);
  };

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
        <h3>{categoryData.category_record.category_description}</h3>

        <ProductFilters
          category_id={categoryData.category_record.id}
          onProductsFetched={handleProductsFetched}
        />
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
