import React from "react";
import "../App.css";
import "../styles/Home.css";
import HeroSection from "../components/HeroSection";
import "../styles/HeroSection.css";

import CategoryGrid from "../components/CategoryGrid";
import "../styles/CategoryGrid.css";

import { Container } from "react-bootstrap";

function Home() {
  return (
    <>
      <HeroSection />
      <CategoryGrid />
    </>
  );
}

export default Home;
