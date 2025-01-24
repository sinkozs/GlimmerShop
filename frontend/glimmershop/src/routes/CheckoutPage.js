import React, { useState, useContext } from "react";
import { loadStripe } from "@stripe/stripe-js";
import { Elements } from "@stripe/react-stripe-js";
import { Container, Form, Button } from "react-bootstrap";
import apiClient from "../utils/apiConfig";
import config from "../config";
import { useCart } from "../context/CartContext";
import "../styles/Form.css";

const CheckoutPage = () => {
  const { cart: userCart } = useCart();

  const [formData, setFormData] = useState({
    firstName: "",
    lastName: "",
    email: "",
    phone: "",
    address: "",
    city: "",
    state: "",
    zipCode: "",
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const stripePromise = loadStripe(config.STRIPE_PUBLIC_KEY);

  const validateForm = () => {
    const newErrors = {};

    if (!formData.email) {
      newErrors.email = "Email is required";
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = "Invalid email format";
    }

    if (!formData.phone) {
      newErrors.phone = "Phone number is required";
    } else if (!/^\+?[\d\s-]{10,}$/.test(formData.phone)) {
      newErrors.phone = "Invalid phone number";
    }

    ["firstName", "lastName", "address", "city", "state", "zipCode"].forEach(
      (field) => {
        if (!formData[field].trim()) {
          newErrors[field] = `${
            field.charAt(0).toUpperCase() + field.slice(1)
          } is required`;
        }
      }
    );

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
  };

  const handleCheckout = async (e) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsLoading(true);

    try {
      const cart_items = userCart.map(
        ({ id, name, price, category, quantity, image_path }) => ({
          id,
          name,
          price,
          category,
          quantity,
          image_path,
        })
      );

      const guest_user_info = {
        first_name: formData.firstName,
        last_name: formData.lastName,
        email: formData.email,
        phone: formData.phone,
        shipping_address: `${formData.address}, ${formData.city}, ${formData.state} ${formData.zipCode}`,
      };

      let response = await apiClient.post(
        "/checkout/create-checkout-session",
        cart_items
      );

      let session_id = response.data.session_id;
      let orders = response.data.order_data;

      if (session_id) {
        localStorage.setItem(
          "checkoutData",
          JSON.stringify({
            orders: orders,
            guest_user_info: guest_user_info,
          })
        );

        const stripe = await stripePromise;
        await stripe.redirectToCheckout({ sessionId: session_id });
      }
    } catch (error) {
      console.error("Checkout error:", error);
      setErrors({ submit: "Failed to create checkout session" });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Elements stripe={stripePromise}>
      <Container fluid className="page-wrapper">
        <Container fluid className="form-container">
          <Container fluid className="form-content">
            <h1 className="form-h1">BILLING INFORMATION</h1>
            <Form onSubmit={handleCheckout} className="form" autoComplete="on">
              <Form.Group controlId="formFirstName" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="First Name"
                  name="firstName"
                  autoComplete="given-name"
                  value={formData.firstName}
                  onChange={handleChange}
                  className="form-control"
                />
              </Form.Group>
              <Form.Group controlId="formLastName" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="Last Name"
                  name="lastName"
                  autoComplete="family-name"
                  value={formData.lastName}
                  onChange={handleChange}
                  className="form-control"
                />
              </Form.Group>
              <Form.Group controlId="formEmail" className="form-group">
                <Form.Control
                  type="email"
                  placeholder="Email address"
                  name="email"
                  autoComplete="email"
                  value={formData.email}
                  onChange={handleChange}
                  className="form-control"
                />
              </Form.Group>
              <Form.Group controlId="formPassword" className="form-group">
                <Form.Control
                  type="tel"
                  placeholder="Phone"
                  name="phone"
                  autoComplete="tel"
                  value={formData.phone}
                  onChange={handleChange}
                  className="form-control"
                />
              </Form.Group>
              <Form.Group controlId="formAddress" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="Street Address"
                  name="address"
                  autoComplete="street-address"
                  value={formData.address}
                  onChange={handleChange}
                  className="form-control"
                />
              </Form.Group>
              <Form.Group controlId="formCity" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="City"
                  name="city"
                  autoComplete="address-level2"
                  value={formData.city}
                  onChange={handleChange}
                  className="form-control"
                />
              </Form.Group>
              <Form.Group controlId="formState" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="State"
                  name="state"
                  autoComplete="address-level1"
                  value={formData.state}
                  onChange={handleChange}
                  className="form-control"
                />
              </Form.Group>
              <Form.Group controlId="formZIP" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="ZIP Code"
                  name="zipCode"
                  autoComplete="postal-code"
                  value={formData.zipCode}
                  onChange={handleChange}
                  className="form-control"
                />
              </Form.Group>

              <Button variant="primary" type="submit" className="login-btn">
                Proceed to Payment
              </Button>
            </Form>
          </Container>
        </Container>
      </Container>
    </Elements>
  );
};

export default CheckoutPage;
