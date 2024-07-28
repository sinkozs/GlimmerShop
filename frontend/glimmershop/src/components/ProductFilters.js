import React, { useState, useEffect } from "react";
import axios from "axios";
import FilterByPrice from "./FilterByPrice";
import FilterByMaterial from "./FilterByMaterial";
import { Button } from "react-bootstrap";

function ProductFilters({ category_id, onProductsFetched }) {
  const [selectedMaterials, setSelectedMaterials] = useState([]);
  const [selectedPriceRange, setSelectedPriceRange] = useState({ min: 0, max: 1000000 });
  const [shouldFetch, setShouldFetch] = useState(false);
  const [resetFilter, setResetFilter] = useState(false);

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
                max_price: selectedPriceRange.max
            }
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
  }, [selectedMaterials, selectedPriceRange, shouldFetch, category_id, onProductsFetched]);

  const fetchAllProducts = async () => {
    try {
        const response = await axios.get(`http://127.0.0.1:8000/categories/products-by-category?category_id=${category_id}`);
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

  return (
    <div>
      <FilterByPrice selectedPriceRange={selectedPriceRange} resetFilter={resetFilter} onPriceRangeSelected={setSelectedPriceRange} />
      <FilterByMaterial selectedMaterials={selectedMaterials} resetFilter={resetFilter} onMaterialsSelected={setSelectedMaterials} />
      <Button onClick={applyFilters}>Apply Filters</Button>
      <Button onClick={clearAllFilters}>Clear All Filters</Button>
    </div>
  );
}

export default ProductFilters;
