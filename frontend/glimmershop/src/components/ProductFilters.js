import React, { useState, useEffect } from "react";
import { v4 as uuidv4, validate as isUuid } from "uuid";
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
      const fetchFilteredProducts = async () => {
        try {
          const sellerId =
            selectedSellerId && isUuid(selectedSellerId)
              ? selectedSellerId
              : null;

          const postData = {
            category_id: category_id,
            materials: {
              materials: selectedMaterials,
            },
            price_range: {
              min_price: selectedPriceRange.min,
              max_price: selectedPriceRange.max,
            },
            seller: {
              seller_id: sellerId,
            },
          };

          console.log(postData);
          const response = await apiClient.post(
            `/products/filter-by-material-price-and-seller`,
            postData,
            {
              headers: { "Content-Type": "application/json" },
            }
          );

          onProductsFetched(response.data);
          if (response.data.length === 0) {
            setShowFilterModal(true);
          }
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
    selectedSellerId,
    shouldFetch,
    category_id,
    onProductsFetched,
  ]);

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
