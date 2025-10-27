import React, { useState, useEffect } from "react";
import FilterByPrice from "./FilterByPrice";
import FilterByMaterial from "./FilterByMaterial";
import FilterBySeller from "./FilterBySeller";
import { Button, Container } from "react-bootstrap";
import "../styles/ProductFilters.css";
import apiClient from "../utils/apiConfig";
import Modal from "./Modal";

function ProductFilters({ category_id, onProductsFetched }) {
  const [selectedMaterials, setSelectedMaterials] = useState([]);
  const [selectedSellerId, setSelectedSellerId] = useState([]);
  const [selectedPriceRange, setSelectedPriceRange] = useState({
    min: 0,
    max: 1000000,
  });
  const [shouldFetch, setShouldFetch] = useState(false);
  const [resetFilter, setResetFilter] = useState(false);
  const [showAllFilters, setShowAllFilters] = useState(false);
  const [showFilterModal, setShowFilterModal] = useState(false);

  useEffect(() => {
    if (shouldFetch) {
      fetchFilteredProducts();
      setShouldFetch(false);
    }
  }, [
    selectedMaterials,
    selectedPriceRange,
    selectedSellerId,
    shouldFetch,
    category_id,
    onProductsFetched,
  ]);

  const isPriceFilterActive = () => {
    return selectedPriceRange.min !== 0 || selectedPriceRange.max !== 1000000;
  };

  const isMaterialFilterActive = () => {
    return selectedMaterials.length > 0;
  };

  const isSellerFilterActive = () => {
    return selectedSellerId.length > 0;
  };

  const countActiveFilters = () => {
    let count = 0;
    if (isPriceFilterActive()) count++;
    if (isMaterialFilterActive()) count++;
    if (isSellerFilterActive()) count++;
    return count;
  };

  const fetchFilteredProducts = async () => {
    try {
      const activeFiltersCount = countActiveFilters();

      if (activeFiltersCount === 0) {
        await fetchAllProducts();
        return;
      }

      let response;

      if (activeFiltersCount > 1) {
        const postData = {
          category_id: category_id,
          materials: {
            materials: isMaterialFilterActive() ? selectedMaterials : [],
          },
          price_range: {
            min_price: selectedPriceRange.min,
            max_price: selectedPriceRange.max,
          },
          seller: {
            seller_id: isSellerFilterActive() ? selectedSellerId : null,
          },
        };

        response = await apiClient.post(
          `/products/filter-by-material-price-and-seller`,
          postData,
          {
            headers: { "Content-Type": "application/json" },
          }
        );
      } else if (isMaterialFilterActive()) {
        const postData = {
          materials: selectedMaterials,
        };

        response = await apiClient.post(
          `/products/filter-by-material?category_id=${category_id}`,
          postData,
          {
            headers: { "Content-Type": "application/json" },
          }
        );
      } else if (isPriceFilterActive()) {
        const postData = {
          min_price: selectedPriceRange.min,
          max_price: selectedPriceRange.max,
        };

        response = await apiClient.post(
          `/products/filter-by-price?category_id=${category_id}`,
          postData,
          {
            headers: { "Content-Type": "application/json" },
          }
        );
      } else if (isSellerFilterActive()) {
        response = await apiClient.post(
          `/products/filter-by-seller?category_id=${category_id}&seller_id=${selectedSellerId}`,
          {
            headers: { "Content-Type": "application/json" },
          }
        );
      }

      onProductsFetched(response.data);
      if (response.data.length === 0) {
        setShowFilterModal(true);
      }
    } catch (error) {
      console.error("Error fetching filtered products:", error);
      onProductsFetched([]);
    }
  };

  const handleSellerSelection = (sellerId) => {
    setSelectedSellerId(sellerId);
  };

  const closeFilterModal = () => {
    setShowFilterModal(false);
  };

  const fetchAllProducts = async () => {
    try {
      const response = await apiClient.get(
        `/categories/products-by-category/${category_id}`
      );

      onProductsFetched(response.data);
    } catch (error) {
      console.error("Error fetching all products:", error);
      onProductsFetched([]);
    }
  };

  const clearAllFilters = () => {
    setSelectedMaterials([]);
    setSelectedSellerId([]);
    setSelectedPriceRange({ min: 0, max: 1000000 });
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
              Filters
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
            <Container fluid className="filter-category">
              <FilterBySeller onSellerSelected={handleSellerSelection} />
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

      <Modal
        show={showFilterModal}
        onClose={closeFilterModal}
        title="No Products"
      >
        <section>No products found matching your criteria.</section>
        <Container className="modal-footer">
          <button className="modal-btn" onClick={closeFilterModal}>
            OK
          </button>
        </Container>
      </Modal>
    </Container>
  );
}

export default ProductFilters;
