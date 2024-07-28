import React, { useState, useEffect } from "react";
import { Container } from "react-bootstrap";

function FilterByPrice({ selectedPriceRange, resetFilter, onPriceRangeSelected }) {
    useEffect(() => {
        if (resetFilter) {
            onPriceRangeSelected({ min: null, max: null });
        }
    }, [resetFilter, onPriceRangeSelected]);

    const handlePriceRangeChange = range => {
        let min_price, max_price;
        switch (range) {
            case "0-150": min_price = 0; max_price = 150; break;
            case "150-300": min_price = 150; max_price = 300; break;
            case "300-500": min_price = 300; max_price = 500; break;
            case "500+": min_price = 500; max_price = 1000000; break;
            default: console.error("Unhandled price range:", range); return;
        }
        onPriceRangeSelected({ min: min_price, max: max_price });
    };

    return (
        <Container fluid className="filters-section-wrapper">
            {["0-150", "150-300", "300-500", "500+"].map(range => (
                <label key={range}>
                    <input
                        type="radio"
                        name="priceRange"
                        value={range}
                        checked={selectedPriceRange && selectedPriceRange.min === parseInt(range.split("-")[0])}
                        onChange={() => handlePriceRangeChange(range)}
                    />
                    {range.includes("+") ? `${range.slice(0, -1)}+` : range.replace("-", " - ")}
                </label>
            ))}
        </Container>
    );
}

export default FilterByPrice;
