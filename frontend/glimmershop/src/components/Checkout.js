import React, { useEffect, useState, useRef } from "react";
import { Button } from "react-bootstrap";
import axios from "axios";
import { Elements } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import Modal from "../components/Modal";

const Checkout = ({ userCart, deleteCart }) => {
  const STRIPE_PUBLIC_KEY =
    "pk_test_51PUqvPIeh1QUOUnUzvMbKUAG4GiIQFHQLpEgV0DaYRzIZt6sxNwQdsxwXMh5O7DkVLqRTtJ551JhqfFeuVRAko4i00JDT5DFCV";
  const stripePromise = loadStripe(STRIPE_PUBLIC_KEY);
  const DOMAIN = "http://localhost:3000/";
  const [showModal, setShowModal] = useState(false);
  const effectRan = useRef(false);

  useEffect(() => {
    if (effectRan.current) return; 

    const query = new URLSearchParams(window.location.search);
    if (query.get('success') === 'true') {
      handleSuccessfulPayment();
      setShowModal(true);
    }

    effectRan.current = true;
  }, []);

  const closeModal = () => {
    setShowModal(false);
    const url = new URL(window.location);
    url.searchParams.delete('success');
    window.history.replaceState({}, document.title, url);
  };

  const handleSuccessfulPayment = async () => {
    try {
      await axios.put(
        "http://localhost:8000/checkout/update-stock/",
        JSON.stringify(userCart),
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      deleteCart();
    } catch (error) {
      console.error("Failed to update stock and delete cart:", error);
    }
  };

  const handleCheckout = async () => {
    try {
      const response = await axios.post(
        "http://localhost:8000/checkout/create-checkout-session/",
        JSON.stringify(userCart),
        {
          headers: {
            "Content-Type": "application/json",
          }
        }
      );
      const session_id = response.data.session_id;
      const stripe = await stripePromise;

      await stripe.redirectToCheckout({ sessionId: session_id });
      // Redirect to homepage with success query parameter
      window.location.href = `${DOMAIN}?success=true`;
    } catch (error) {
      console.error("Failed to start checkout:", error);
    }
  };

  return (
    <>
      <Elements stripe={stripePromise}>
        <Button className="add-to-bag-btn" onClick={handleCheckout}>
          CHECKOUT
        </Button>
      </Elements>
      <Modal show={showModal} onClose={closeModal} title="Yay!">
        <p>We received your order!</p>
      </Modal>
    </>
  );
};

export default Checkout;
