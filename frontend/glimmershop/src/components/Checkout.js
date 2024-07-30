import React, { useEffect } from "react";
import { Button } from "react-bootstrap";
import axios from "axios";
import { Elements } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";

const Checkout = ({ userCart, deleteCart }) => {
  const STRIPE_PUBLIC_KEY =
    "pk_test_51PUqvPIeh1QUOUnUzvMbKUAG4GiIQFHQLpEgV0DaYRzIZt6sxNwQdsxwXMh5O7DkVLqRTtJ551JhqfFeuVRAko4i00JDT5DFCV";
  const stripePromise = loadStripe(STRIPE_PUBLIC_KEY);
  const DOMAIN = "http://localhost:3000/";

  useEffect(() => {
    const query = new URLSearchParams(window.location.search);
    if (query.get('success') === 'true') {
      handleSuccessfulPayment();
      window.history.replaceState({}, document.title, DOMAIN);
    }
  }, []);

  const handleSuccessfulPayment = async () => {
    try {
      console.log("Update stock and delete cart...");
      await axios.put(
        "http://localhost:8000/checkout/update-stock/",
        JSON.stringify(userCart),
        {
          headers: {
            "Content-Type": "application/json",
          }
        }
      );
      deleteCart();
    } catch (error) {
      console.error("Failed to update stock and delete cart:", error);
    }
  };

  const handleCheckout = async () => {
    console.log("handleCheckout");
    console.log(JSON.stringify(userCart));

    try {
      const response = await axios.post(
        "http://localhost:8000/checkout/create-checkout-session/",
        JSON.stringify(userCart),
        {
          headers: {
            "Content-Type": "application/json",
          },
        }
      );
      const session_id = response.data.session_id;
      const stripe = await stripePromise;

      await stripe.redirectToCheckout({ sessionId: session_id });
      window.location.href = `${DOMAIN}?success=true`;
      
    } catch (error) {
      console.error("Failed to start checkout:", error);
    }
  };

  return (
    <Elements stripe={stripePromise}>
      <Button className="add-to-bag-btn" onClick={handleCheckout}>
        CHECKOUT
      </Button>
    </Elements>
  );
};

export default Checkout;
