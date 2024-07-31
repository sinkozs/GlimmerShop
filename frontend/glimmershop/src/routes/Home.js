import React, { useEffect, useState } from "react";
import "../App.css";
import "../styles/Home.css";
import HeroSection from "../components/HeroSection";
import "../styles/HeroSection.css";
import CategoryGrid from "../components/CategoryGrid";
import "../styles/CategoryGrid.css";
import Modal from "../components/Modal";
import TrendingJewelry from "../components/TrendingJewelry";
import "../styles/TrendingJewelry.css";
import { Container } from "react-bootstrap";

function Home() {
  const [showModal, setShowModal] = useState(false);

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);
    if (query.get('success') === 'true') {
      setShowModal(true);
    }
  }, []);

  const closeModal = () => {
    setShowModal(false);
    const url = new URL(window.location);
    url.searchParams.delete('success');
    window.history.replaceState({}, document.title, url);
  };

  return (
    <Container fluid className="home-page">
      <HeroSection />
      <CategoryGrid />
      <h1 className="h1-section-title">TRENDING JEWELRY</h1>
      <TrendingJewelry />

      <Modal show={showModal} onClose={closeModal} title="Yay!">
        <p>We received your order!</p>
      </Modal>
    </Container>
  );
}

export default Home;
