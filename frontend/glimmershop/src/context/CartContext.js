import React, { createContext, useContext, useState, useEffect } from "react";
import axios from "axios";
import Modal from "../components/Modal";
import { Container } from "react-bootstrap";

const CartContext = createContext();

export const useCart = () => useContext(CartContext);

export const CartProvider = ({ children }) => {
  const [cart, setCart] = useState(() => {
    const localData = localStorage.getItem("cart");
    return localData ? JSON.parse(localData) : [];
  });
  const [stockQuantity, setStockQuantity] = useState(null);
  const [showModal, setShowModal] = useState(false);

  const closeModal = () => {
    setShowModal(false);
  };

  useEffect(() => {
    localStorage.setItem("cart", JSON.stringify(cart));
  }, [cart]);

  const addToCart = async (item) => {
    try {
      const product = await axios.get(
        `http://localhost:8000/products/${item.id}`
      );

      const newItem = {
        ...item,
        image_path: product.data.image_path,
      };
      setStockQuantity(product.data.stock_quantity);

      setCart((prevCart) => {
        const existingItemIndex = prevCart.findIndex(
          (i) => i.id === newItem.id
        );
        if (existingItemIndex > -1) {
          const newCart = [...prevCart];
          newCart[existingItemIndex].quantity += newItem.quantity;
          return newCart;
        } else {
          return [...prevCart, newItem];
        }
      });
    } catch (error) {
      console.error("Failed to add product to cart:", error);
    }
  };

  const removeFromCart = (itemId) => {
    setCart((prevCart) => prevCart.filter((item) => item.id !== itemId));
  };

  const increaseQuantity = (itemId) => {
    setCart((prevCart) => {
      const item = prevCart.find((item) => item.id === itemId);
      if (item && item.quantity + 1 <= stockQuantity) {
        return prevCart.map((item) =>
          item.id === itemId ? { ...item, quantity: item.quantity + 1 } : item
        );
      } else {
        setShowModal(true);
        return prevCart;
      }
    });
  };

  const decreaseQuantity = (itemId) => {
    setCart((prevCart) =>
      prevCart.map((item) =>
        item.id === itemId
          ? { ...item, quantity: Math.max(0, item.quantity - 1) }
          : item
      )
    );
  };

  const calculateSubtotal = () => {
    return cart.reduce((acc, item) => acc + item.price * item.quantity, 0);
  };

  const calculateTotalCartItemCount = () => {
    return cart.reduce((acc, item) => acc + item.quantity, 0);
  };

  const deleteCart = () => {
    setCart([]);
  };

  return (
    <CartContext.Provider
      value={{
        cart,
        addToCart,
        removeFromCart,
        increaseQuantity,
        decreaseQuantity,
        calculateSubtotal,
        calculateTotalCartItemCount,
        deleteCart,
      }}
    >
      {children}
      <Modal show={showModal} onClose={closeModal} title="Sorry!">
        <Container>
          We currently have only {stockQuantity}{" "}
          {stockQuantity === 1 ? "unit" : "units"} of this product in stock.
          Please adjust the quantity in your cart accordingly.
        </Container>
      </Modal>
    </CartContext.Provider>
  );
};
