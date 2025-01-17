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
    const handleSuccess = async () => {
      const query = new URLSearchParams(window.location.search);
      if (query.get("success") === "true" && !hasProcessedRef.current) {
        try {
          const checkoutData = JSON.parse(localStorage.getItem("checkoutData"));
          if (checkoutData) {
            console.log("call post checkout");
            await apiClient.post("/checkout/post-checkout", {
              orders: checkoutData.orders,
              guest_user_info: checkoutData.guest_user_info,
            });
            hasProcessedRef.current = true;
            localStorage.removeItem("checkoutData");
            setShowModal(true);
          }
        } catch (error) {
          console.error("Post-checkout error:", error);
        }
      }
    };

    handleSuccess();
  }, []);

  const closeModal = () => {
    setShowModal(false);
    const url = new URL(window.location);
    url.searchParams.delete("success");
    window.history.replaceState({}, document.title, url);
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