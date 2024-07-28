import React, { useState } from "react";
import { Container, Button } from "react-bootstrap";

function FilterByMaterial({ onMaterialsSelected }) {
    const [selectedMaterials, setSelectedMaterials] = useState([]);
    const [isMaterialFilterExpanded, setIsMaterialFilterExpanded] = useState(false);

    const handleMaterialChange = material => {
        const newMaterials = selectedMaterials.includes(material) ? 
            selectedMaterials.filter(m => m !== material) : [...selectedMaterials, material];
        setSelectedMaterials(newMaterials);
        onMaterialsSelected(newMaterials);
    };

    const toggleFilterBtn = () => setIsMaterialFilterExpanded(!isMaterialFilterExpanded);

    return (
        <Container fluid className="filters-section-wrapper">
            <Button onClick={toggleFilterBtn} className="expand-btn">
                Filter by material
                <span className="expand-icon">{isMaterialFilterExpanded ? "-" : "+"}</span>
            </Button>
            {isMaterialFilterExpanded && (
                <Container className="material-options">
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
