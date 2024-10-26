import React, { useEffect, useRef } from "react";
import { Button } from "react-bootstrap";
import axios from "axios";
import { Elements } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import config from "../config";

const Checkout = ({ userCart, deleteCart }) => {
  const stripePromise = loadStripe(config.STRIPE_PUBLIC_KEY);
  const effectRan = useRef(false);

  useEffect(() => {
    if (effectRan.current) return;

    const query = new URLSearchParams(window.location.search);
    if (query.get("success") === "true") {
      handleSuccessfulPayment();
    }

    effectRan.current = true;
  }, []);

  const handleSuccessfulPayment = async () => {
    try {
      await axios.put(
        `${config.BACKEND_BASE_URL}/checkout/update-stock/`,
        JSON.stringify(userCart),
        {
          headers: {
            "Content-Type": "application/json",
          },
          withCredentials: true,
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
        `${config.BACKEND_BASE_URL}/checkout/create-checkout-session/`,
        JSON.stringify(userCart),
        {
          headers: {
            "Content-Type": "application/json",
          },
          withCredentials: true,
        }
      );
      const session_id = response.data.session_id;
      const stripe = await stripePromise;

      await stripe.redirectToCheckout({ sessionId: session_id });
      window.location.href = `${config.FRONTEND_BASE_URL}/?success=true`;
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
    </>
  );
};

export default Checkout;
