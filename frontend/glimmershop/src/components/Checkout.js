import React, { useEffect, useRef, useState } from "react";
import { Button } from "react-bootstrap";
import { Elements } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import config from "../config";
import CheckoutForm from "./CheckoutForm";

const Checkout = ({ userCart, deleteCart }) => {
  const stripePromise = loadStripe(config.STRIPE_PUBLIC_KEY);
  const [showForm, setShowForm] = useState(false);



  const handleCheckoutStart = () => {
    setShowForm(true);
  };

  return (
    <Elements stripe={stripePromise}>
      {showForm ? (
        <CheckoutForm userCart={userCart} onCancel={() => setShowForm(false)} />
      ) : (
        <Button className="add-to-bag-btn" onClick={handleCheckoutStart}>
          CHECKOUT
        </Button>
      )}
    </Elements>
  );
};

export default Checkout;
