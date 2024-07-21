import React from "react";
import "../App.css";
import "../styles/Home.css";
import heroImage from "../images/hero5.jpg";

import { Container, Card } from "react-bootstrap";


function Home() {
  return (
    <Container fluid className="page-wrapper">
      <Container fluid className="hero-container" style={{ backgroundImage: `url(${heroImage})` }}>
        <Container fluid className="hero-section-text">
          <h1>SILVER STORY</h1>
          <h3>SHOP NOW</h3>
        </Container>
      </Container>
    </Container>
  );
}

export default Home;
