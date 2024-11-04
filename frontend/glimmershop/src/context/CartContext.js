import React, { createContext, useContext, useReducer, useEffect } from "react";
import axios from "axios";
import Modal from "../components/Modal";
import { Container } from "react-bootstrap";
import config from "../config";

const CartContext = createContext();

export const useCart = () => useContext(CartContext);

const cartReducer = (state, action) => {
  switch (action.type) {
    case "ADD_TO_CART":
      const existingItemIndex = state.cart.findIndex(
        (i) => i.id === action.payload.id
      );
      if (existingItemIndex > -1) {
        const updatedCart = [...state.cart];
        updatedCart[existingItemIndex].quantity += action.payload.quantity;
        return { ...state, cart: updatedCart };
      } else {
        return { ...state, cart: [...state.cart, action.payload] };
      }
    case "REMOVE_FROM_CART":
      return {
        ...state,
        cart: state.cart.filter((item) => item.id !== action.payload),
      };
    case "INCREASE_QUANTITY":
      return {
        ...state,
        cart: state.cart.map((item) =>
          item.id === action.payload.itemId &&
          item.quantity < state.stockQuantity
            ? { ...item, quantity: item.quantity + 1 }
            : item
        ),
        showModal: state.cart.some(
          (item) =>
            item.id === action.payload.itemId &&
            item.quantity >= state.stockQuantity
        ),
      };
    case "DECREASE_QUANTITY":
      return {
        ...state,
        cart: state.cart.map((item) =>
          item.id === action.payload
            ? { ...item, quantity: Math.max(0, item.quantity - 1) }
            : item
        ),
      };
    case "SET_STOCK_QUANTITY":
      return { ...state, stockQuantity: action.payload };
    case "DELETE_CART":
      return { ...state, cart: [] };
    case "CLOSE_MODAL":
      return { ...state, showModal: false };
    default:
      return state;
  }
};

export const CartProvider = ({ children }) => {
  const [state, dispatch] = useReducer(cartReducer, {
    cart: JSON.parse(localStorage.getItem("cart")) || [],
    stockQuantity: null,
    showModal: false,
  });

  useEffect(() => {
    localStorage.setItem("cart", JSON.stringify(state.cart));
  }, [state.cart]);

  const addToCart = async (item) => {
    try {
      const product = await axios.get(
        `${config.BACKEND_BASE_URL}/products/${item.id}`
      );
      const newItem = {
        ...item,
        image_path: product.data.image_path,
        quantity: item.quantity,
      };
      dispatch({
        type: "SET_STOCK_QUANTITY",
        payload: product.data.stock_quantity,
      });
      dispatch({ type: "ADD_TO_CART", payload: newItem });
    } catch (error) {
      console.error("Failed to add product to cart:", error);
    }
  };

  const removeFromCart = (itemId) => {
    dispatch({ type: "REMOVE_FROM_CART", payload: itemId });
  };

  const increaseQuantity = (itemId) => {
    dispatch({ type: "INCREASE_QUANTITY", payload: { itemId } });
  };

  const decreaseQuantity = (itemId) => {
    dispatch({ type: "DECREASE_QUANTITY", payload: itemId });
  };

  const calculateSubtotal = () => {
    return state.cart.reduce(
      (acc, item) => acc + item.price * item.quantity,
      0
    );
  };

  const calculateTotalCartItemCount = () => {
    return state.cart.reduce((acc, item) => acc + item.quantity, 0);
  };

  const deleteCart = () => {
    dispatch({ type: "DELETE_CART" });
  };

  const closeModal = () => {
    dispatch({ type: "CLOSE_MODAL" });
  };

  return (
    <CartContext.Provider
      value={{
        cart: state.cart,
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
      <Modal show={state.showModal} onClose={closeModal} title="Sorry!">
        <Container>
          We currently have only {state.stockQuantity}{" "}
          {state.stockQuantity === 1 ? "unit" : "units"} of this product in
          stock. Please adjust the quantity in your cart accordingly.
        </Container>
      </Modal>
    </CartContext.Provider>
  );
};
