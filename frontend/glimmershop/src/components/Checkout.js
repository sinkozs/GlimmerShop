import React, { useEffect, useRef, useState } from "react";
import { Button } from "react-bootstrap";
import { Elements } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import config from "../config";
import apiClient from "../utils/apiConfig";
import CheckoutForm from "./CheckoutForm";

const Checkout = ({ userCart, deleteCart }) => {
  const stripePromise = loadStripe(config.STRIPE_PUBLIC_KEY);
  const effectRan = useRef(false);
  const [showForm, setShowForm] = useState(false);

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
      // await apiClient.put('/checkout/update-stock/', userCart);
      deleteCart();
    } catch (error) {
      console.error("Failed to update stock and delete cart:", error);
    }
  };

  const handleCheckoutStart = () => {
    setShowForm(true);
  };

  const handleCheckout = async (customerInfo) => {
    try {
      const formattedCart = userCart.map(({ id, name, price, category, quantity, image_path }) => ({
        id, name, price, category, quantity, image_path
      }));
      console.log("AAAAAAAAA")
      console.log(formattedCart)
      const { data: { session_id } } = await apiClient.post(
        '/checkout/create-checkout-session/',
        {
          cart: formattedCart,
          guest_user_info: customerInfo
        }
      );

      const stripe = await stripePromise;
      await stripe.redirectToCheckout({ sessionId: session_id });
      window.location.href = `${config.FRONTEND_BASE_URL}/?success=true`;
    } catch (error) {
      console.error("Failed to start checkout:", error);
    }
  };

  return (
    <Elements stripe={stripePromise}>
      {showForm ? (
        <CheckoutForm 
          userCart={userCart} 
          onSubmit={handleCheckout}
          onCancel={() => setShowForm(false)}
        />
      ) : (
        <Button className="add-to-bag-btn" onClick={handleCheckoutStart}>
          CHECKOUT
        </Button>
      )}
    </Elements>
  );
};

export default Checkout;