import React, { useEffect, useRef } from "react";
import { Button } from "react-bootstrap";
import { Elements } from "@stripe/react-stripe-js";
import { loadStripe } from "@stripe/stripe-js";
import config from "../config";
import apiClient from "../utils/apiConfig";

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
     await apiClient.put('/checkout/update-stock/', userCart);
     deleteCart();
   } catch (error) {
     console.error("Failed to update stock and delete cart:", error);
   }
 };

 const handleCheckout = async () => {
   try {
     const formattedCart = userCart.map(({ id, name, price, category, quantity, image_path }) => ({
       id, name, price, category, quantity, image_path
     }));

     const { data: { session_id } } = await apiClient.post(
       '/checkout/create-checkout-session/',
       formattedCart
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
     <Button className="add-to-bag-btn" onClick={handleCheckout}>
       CHECKOUT
     </Button>
   </Elements>
 );
};

export default Checkout;