import React, { useState, useRef } from "react";
import { Container, Button } from "react-bootstrap";
import axios from "axios";

import "../App.css";
import "../styles/Home.css";
import "../styles/ProductsByCategory.css";
import "../styles/FilterByPrice.css";


function FilterByMaterial({ category_id, onProductsFetched }) {
    const [selectedMaterials, setSelectedMaterials] = useState([]);
    const [isMaterialFilterExpanded, setIsMaterialFilterExpanded] = useState(false);
    const materialsFiltersRef = useRef(null);
  
    const handleMaterialChange = (material) => {
      setSelectedMaterials(prevMaterials => {
        if (prevMaterials.includes(material)) {
          return prevMaterials.filter(m => m !== material);
        } else {
          return [...prevMaterials, material];
        }
      });
    };
  
    const handleSubmit = async (event) => {
        event.preventDefault();
        try {
          const response = await axios.post(
            `http://127.0.0.1:8000/products/filter_by_material?category_id=${category_id}`,
            { materials: selectedMaterials }
          );
          onProductsFetched(response.data);
          console.log(response.data);
        } catch (error) {
          console.error("Error fetching products:", error);
          onProductsFetched([]);
        }
      };
  
    const toggleFilterBtn = () => {
      setIsMaterialFilterExpanded(!isMaterialFilterExpanded);
    };
  
    return (
      <Container fluid className="filters-section-wrapper">
        <Container fluid className="filters-section" ref={materialsFiltersRef}>
          <Container fluid className="expandable-section">
            <Button onClick={toggleFilterBtn} className="expand-btn">
              <span className="filters">Filter by material</span>
              <span className="expand-icon">{isMaterialFilterExpanded ? "-" : "+"}</span>
            </Button>
            {isMaterialFilterExpanded && (
              <Container className="material-options">
                <form onSubmit={handleSubmit}>
                  {["14k White Gold", "14k Yellow Gold", "Gold Vermeil", "Sterling Silver"].map(material => (
                    <label key={material}>
                      <input
                        type="checkbox"
                        name="materialOption"
                        value={material}
                        checked={selectedMaterials.includes(material)}
                        onChange={() => handleMaterialChange(material)}
                      />
                      {material}
                    </label>
                  ))}
                  <Button type="submit">Apply Filter</Button>
                </form>
              </Container>
            )}
          </Container>
        </Container>
      </Container>
    );
  }
  
  export default FilterByMaterial;
  