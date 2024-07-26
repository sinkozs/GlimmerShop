import React from "react";
import "../App.css";
import "../styles/Home.css";
import HeroSection from "../components/HeroSection";
import "../styles/HeroSection.css";

import CategoryGrid from "../components/CategoryGrid";
import "../styles/CategoryGrid.css";

import TrendingJewelry from "../components/TrendingJewelry";
import "../styles/TrendingJewelry.css";
import { Container } from "react-bootstrap";

function Home() {
  return (
    <Container fluid className="home-page">
      <HeroSection />
      <CategoryGrid />
      <h1 className="h1-section-title">TRENDING JEWELRY</h1>
      <TrendingJewelry />
    </Container>
  );
}

export default Home;
