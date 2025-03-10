import React from "react";
import { useNavigate } from 'react-router-dom';

import "../App.css";
import "../styles/CategoryGrid.css";
import necklace1 from "../images/category-necklace1.jpg";
import necklace2 from "../images/category-necklace2.jpg";
import ring1 from "../images/category-ring1.jpg";
import ring2 from "../images/category-ring2.jpg";
import bracelet1 from "../images/category-bracelet1.jpg";
import bracelet2 from "../images/category-bracelet2.jpg";
import earrings1 from "../images/category-earring1.jpg";
import earrings2 from "../images/category-earring2.jpg";
import men1 from "../images/men5.jpg";
import men2 from "../images/men2.jpg";
import { Container, Card } from "react-bootstrap";

const categories = [
  { name: "NECKLACES", img: necklace1, hoverImg: necklace2 },
  { name: "RINGS", img: ring1, hoverImg: ring2 },
  { name: "BRACELETS", img: bracelet1, hoverImg: bracelet2 },
  { name: "EARRINGS", img: earrings1, hoverImg: earrings2 },
  { name: "MEN'S", img: men1, hoverImg: men2 },
];

function CategoryGrid() {
  const navigate = useNavigate();

  const handleCategoryClick = (categoryName) => {
    navigate(`/categories/${categoryName}`);
  };

  return (
    <Container fluid className="category-grid-wrapper">
      <Container fluid className="category-grid">
        {categories.map((category, idx) => (
          <Card key={idx} className="category-card" onClick={() => handleCategoryClick(category.name.toLowerCase())}>
            <Card.Body className="card-body">
              <Container className="card-content" style={{ backgroundImage: `url(${category.img})` }}>
                <Container className="hover-overlay" style={{ backgroundImage: `url(${category.hoverImg})` }}></Container>
              </Container>
            </Card.Body>
            <Card.Footer className="card-footer">
              <Card.Text className="footer-text">{category.name}</Card.Text>
            </Card.Footer>
          </Card>
        ))}
      </Container>
    </Container>
  );
}

export default CategoryGrid;