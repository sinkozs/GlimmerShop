import React, { useState, useEffect } from "react";
import axios from "axios";
import FilterByPrice from "./FilterByPrice";
import FilterByMaterial from "./FilterByMaterial";
import { Button, Container } from "react-bootstrap";
import "../styles/ProductFilters.css";

function ProductFilters({ category_id, onProductsFetched }) {
  const [selectedMaterials, setSelectedMaterials] = useState([]);
  const [selectedPriceRange, setSelectedPriceRange] = useState({
    min: 0,
    max: 1000000,
  });
  const [shouldFetch, setShouldFetch] = useState(false);
  const [resetFilter, setResetFilter] = useState(false);
  const [showAllFilters, setShowAllFilters] = useState(false);

  useEffect(() => {
    if (shouldFetch) {
      const fetchFilteredProducts = async () => {
        try {
          const postData = {
            materials: {
              materials: selectedMaterials,
            },
            price_range: {
              min_price: selectedPriceRange.min,
              max_price: selectedPriceRange.max,
            },
          };

          const response = await axios.post(
            `http://127.0.0.1:8000/products/filter_by_material_and_price?category_id=${category_id}`,
            postData
          );

          onProductsFetched(response.data);
        } catch (error) {
          console.error("Error fetching filtered products:", error);
          onProductsFetched([]);
        }
      };

      fetchFilteredProducts();
      setShouldFetch(false);
    }
  }, [
    selectedMaterials,
    selectedPriceRange,
    shouldFetch,
    category_id,
    onProductsFetched,
  ]);

  const fetchAllProducts = async () => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:8000/categories/products-by-category?category_id=${category_id}`
      );

      onProductsFetched(response.data);
    } catch (error) {
      console.error("Error fetching all products:", error);
      onProductsFetched([]);
    }
  };

  const clearAllFilters = () => {
    setSelectedMaterials([]);
    setSelectedPriceRange({ min: null, max: null });
    fetchAllProducts();
  };

  const applyFilters = () => {
    setShouldFetch(true);
  };

  const toggleAllFilters = () => {
    setShowAllFilters(!showAllFilters);
  };

  return (
    <Container fluid className="filters-wrapper">
      <Button onClick={toggleAllFilters} className="all-filters-btn">
        {showAllFilters ? "Hide Filters" : "All Filters"}
      </Button>
      <Button
        onClick={clearAllFilters}
        className="all-filters-btn"
        style={{ marginLeft: "10px" }}
      >
        Clear All Filters
      </Button>

      <Container
        fluid
        className={`all-filters-section ${showAllFilters ? "show" : ""}`}
      >
        {showAllFilters && (
          <>
            <Container fluid className="filters-header">
              <h3>Filters</h3>
              <Button
                className="close-filters-section-btn"
                onClick={toggleAllFilters}
              >
                X
              </Button>
            </Container>

            <Container fluid className="filter-category">
              <FilterByPrice
                selectedPriceRange={selectedPriceRange}
                resetFilter={resetFilter}
                onPriceRangeSelected={setSelectedPriceRange}
              />
            </Container>
            <Container fluid className="filter-category">
              <FilterByMaterial
                selectedMaterials={selectedMaterials}
                resetFilter={resetFilter}
                onMaterialsSelected={setSelectedMaterials}
              />
            </Container>
            <Button onClick={applyFilters} className="apply-filter-btn">
              Apply Filters
            </Button>
            <Button onClick={clearAllFilters} className="apply-filter-btn">
              Clear All Filters
            </Button>
          </>
        )}
      </Container>
    </Container>
  );
}

export default ProductFilters;
