import React from "react";
import { Button } from "react-bootstrap";
import { useNavigate } from "react-router-dom";

const CheckoutButton = () => {
  const navigate = useNavigate();

  return (
    <Button 
      className="add-to-bag-btn" 
      onClick={() => navigate('/checkout')}
    >
      CHECKOUT
    </Button>
  );
};

export default CheckoutButton;