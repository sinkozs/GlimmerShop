import axios from "axios";
import { useState, useRef } from "react";
import { Container, Button } from "react-bootstrap";
import "../styles/FilterByPrice.css";

function FilterByPrice({ category_id, onProductsFetched }) {
  const [selectedPriceRange, setSelectedPriceRange] = useState("");
  const [isFilterExpanded, setIsFilterExpanded] = useState(false);
  const filtersRef = useRef(null);

  const handlePriceRangeChange = async (range) => {
    setSelectedPriceRange(range);
    let min_price, max_price;

    switch (range) {
      case "0-150":
        min_price = 0;
        max_price = 150;
        break;
      case "150-300":
        min_price = 150;
        max_price = 300;
        break;
      case "300-500":
        min_price = 300;
        max_price = 500;
        break;
      case "500+":
        min_price = 500;
        max_price = 1000000;
        break;
      default:
        console.error("Unhandled price range:", range);
        return;
    }

    try {
      const response = await axios.post(
        `http://127.0.0.1:8000/products/filter_by_price?category_id=${category_id}`,
        {
          min_price: min_price,
          max_price: max_price,
        }
      );
      onProductsFetched(response.data);
    } catch (error) {
      console.error("Error fetching products:", error);
      onProductsFetched([]);
    }
  };

  const toggleFilterBtn = () => {
    setIsFilterExpanded(!isFilterExpanded);
  };

  return (
    <Container fluid className="filters-section-wrapper">
      <Container fluid className="filters-section" ref={filtersRef}>
        <Container fluid className="expandable-section">
          <Button onClick={toggleFilterBtn} className="expand-btn">
            <span className="filters">Filter by price</span>
            <span className="expand-icon">{isFilterExpanded ? "-" : "+"}</span>
          </Button>
          {isFilterExpanded && (
            <Container className="price-ranges">
              <form>
                <label>
                  <input
                    type="radio"
                    name="priceRange"
                    value="0-150"
                    checked={selectedPriceRange === "0-150"}
                    onChange={() => handlePriceRangeChange("0-150")}
                  />
                  Under 150
                </label>
                <label>
                  <input
                    type="radio"
                    name="priceRange"
                    value="150-300"
                    checked={selectedPriceRange === "150-300"}
                    onChange={() => handlePriceRangeChange("150-300")}
                  />
                  150 - 300
                </label>
                <label>
                  <input
                    type="radio"
                    name="priceRange"
                    value="300-500"
                    checked={selectedPriceRange === "300-500"}
                    onChange={() => handlePriceRangeChange("300-500")}
                  />
                  300 - 500
                </label>
                <label>
                  <input
                    type="radio"
                    name="priceRange"
                    value="500+"
                    checked={selectedPriceRange === "500+"}
                    onChange={() => handlePriceRangeChange("500+")}
                  />
                  500+
                </label>
              </form>
            </Container>
          )}
        </Container>
      </Container>
    </Container>
  );
}

export default FilterByPrice;
