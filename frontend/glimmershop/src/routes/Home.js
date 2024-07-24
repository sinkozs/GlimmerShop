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
    <Container fluid>
      <HeroSection />
      <CategoryGrid />
      <TrendingJewelry />
    </Container>
  );
}

export default Home;
