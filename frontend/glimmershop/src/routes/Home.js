import React, { useEffect, useState, useRef } from "react";
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
import apiClient from "../utils/apiConfig";

function Home() {
  const [showModal, setShowModal] = useState(false);
  const hasProcessedRef = useRef(false);

  useEffect(() => {
    async function processCheckout(checkoutData) {
      try {
        const processed = localStorage.getItem('checkoutProcessed');
        if (processed) return;
        
        localStorage.setItem('checkoutProcessed', 'true');
        
        await apiClient.post("/checkout/post-checkout", {
          orders: checkoutData.orders,
          guest_user_info: checkoutData.guest_user_info,
        });
        
        localStorage.removeItem("checkoutData");
        setShowModal(true);
      } catch (error) {
        console.error("Post-checkout error:", error);
        localStorage.removeItem('checkoutProcessed');
      }
    }

    const query = new URLSearchParams(window.location.search);
    try {
      const checkoutData = localStorage.getItem("checkoutData");
      if (query.get("success") === "true" && checkoutData) {
        const parsedData = JSON.parse(checkoutData);
        processCheckout(parsedData);
      }
    } catch (error) {
      console.error("Error parsing checkout data:", error);
    }

    return () => {
      hasProcessedRef.current = false;
    };
  }, []);

  const closeModal = () => {
    setShowModal(false);
    const url = new URL(window.location);
    url.searchParams.delete("success");
    window.history.replaceState({}, document.title, url);
    localStorage.removeItem('checkoutProcessed');
    hasProcessedRef.current = false;
  };

  return (
    <Container fluid className="home-page">
      <HeroSection />
      <CategoryGrid />
      <h1 className="h1-section-title">TRENDING JEWELRY</h1>
      <TrendingJewelry />

      <Modal show={showModal} onClose={closeModal} title="Yay!">
        <section>We received your order!</section>
      </Modal>
    </Container>
  );
}

export default Home;