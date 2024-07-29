import React, { useState, useEffect } from "react";
import { Container, Button } from "react-bootstrap";

function FilterByMaterial({ selectedMaterials, resetFilter, onMaterialsSelected }) {
    const [isMaterialFilterExpanded, setIsMaterialFilterExpanded] = useState(false);

    useEffect(() => {
        if (resetFilter) {
            onMaterialsSelected([]);
        }
    }, [resetFilter, onMaterialsSelected]);

    const handleMaterialChange = material => {
        const updatedMaterials = selectedMaterials.includes(material) ? 
            selectedMaterials.filter(m => m !== material) : [...selectedMaterials, material];
        onMaterialsSelected(updatedMaterials);
    };

    const toggleFilterBtn = () => setIsMaterialFilterExpanded(!isMaterialFilterExpanded);

    return (
        <Container fluid className="filters-section-wrapper">
            <Button onClick={toggleFilterBtn} className="filter-expand-btn">
                Material
                <span className="expand-icon">{isMaterialFilterExpanded ? "-" : "+"}</span>
            </Button>
            {isMaterialFilterExpanded && (
                <Container fluid className="filter-options">
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
                </Container>
            )}
        </Container>
    );
}

export default FilterByMaterial;
