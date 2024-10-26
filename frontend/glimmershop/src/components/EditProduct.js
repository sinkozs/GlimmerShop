import React, { useState, useEffect } from "react";
import axios from "axios";
import "../App.css";
import "../styles/LoginAndSignup.css";
import Modal from "./Modal";
import { Container, Form, Button } from "react-bootstrap";
import { useParams } from "react-router-dom";
import config from "../config";

function EditProduct() {
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [description, setDescription] = useState("");
  const [stockQuantiy, setStockQuantiy] = useState("");
  const [material, setMaterial] = useState("");
  const [color, setColor] = useState("");
  const [image1, setImage1] = useState(null);
  const [image2, setImage2] = useState(null);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState(null);
  const { product_id } = useParams();

  useEffect(() => {
    const fetchProductData = async () => {
      try {
        const product = await axios.get(
          `${config.BACKEND_BASE_URL}/products/${product_id}`
        );
        setName(product.data.name);
        setPrice(product.data.price);
        setDescription(product.data.description);
        setStockQuantiy(product.data.setStockQuantiy);
        setColor(product.data.color);
        setMaterial(product.data.material);
        setStockQuantiy(product.data.stock_quantity);
      } catch (error) {
        console.error("Error fetching product information:", error);
        setError("Failed to fetch product details. Please try again later.");
      }
    };

    fetchProductData();
  }, []);

  const handleSubmit = async (event) => {
    event.preventDefault();

    const productData = {};

    if (name !== "") productData.name = name;
    if (description !== "") productData.description = description;
    if (price !== "") productData.price = price;
    if (stockQuantiy !== "") productData.stock_quantity = stockQuantiy;
    if (material !== "") productData.material = material;
    if (color !== "") productData.color = color;

    try {
      const response = await axios.put(
        `${config.BACKEND_BASE_URL}/products/edit?product_id=${product_id}`,
        productData,
        {
          headers: {
            "Content-Type": "application/json",
          },
          withCredentials: true,
        }
      );

      if (response.status === 200){
        setShowModal(true);

        setName("");
        setDescription("");
        setPrice("");
        setStockQuantiy("");
        setMaterial("");
        setColor("");
        setImage1(null);
        setImage2(null);

      }
    } catch (error) {
      console.error("There was an error editing the product!", error);
      setError(error.response?.data?.detail || "An unexpected error occurred");
    }
  };

  const closeModal = () => {
    setShowModal(false);
  };

  const handleImage1Change = (event) => {
    setImage1(event.target.files[0]);
  };

  const handleImage2Change = (event) => {
    setImage2(event.target.files[0]);
  };

  return (
    <Container fluid className="page-wrapper">
      <Container fluid className="login-form-container">
        <Container fluid className="login-form-content">
          <>
            <h1 className="login-form-h1">EDIT PRODUCT</h1>
            <Form onSubmit={handleSubmit} className="form">
              <Form.Group controlId="productName" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="Product name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="form-control"
                />
              </Form.Group>
              <Form.Group controlId="productDescription" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="Description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="form-control"
                />
              </Form.Group>
              <Form.Group controlId="productPrice" className="form-group">
                <Form.Control
                  type="number"
                  placeholder="Price"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}

                  className="form-control"
                />
              </Form.Group>
              <Form.Group
                controlId="productStockQuantity"
                className="form-group"
              >
                <Form.Control
                  type="number"
                  placeholder="Stock Quantity"
                  value={stockQuantiy}
                  onChange={(e) => setStockQuantiy(e.target.value)}

                  className="form-control"
                />
              </Form.Group>
              <Form.Group controlId="productMaterial" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="Material"
                  value={material}
                  onChange={(e) => setMaterial(e.target.value)}
                  className="form-control"
                />
              </Form.Group>

              <Form.Group controlId="productColor" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="Color"
                  value={color}
                  onChange={(e) => setColor(e.target.value)}
                  className="form-control"
                />
              </Form.Group>

              <Form.Group controlId="image1" className="form-group">
                <Form.Control
                  type="file"
                  onChange={handleImage1Change}
                />
              </Form.Group>

              <Form.Group controlId="image2" className="form-group">
                <Form.Control
                  type="file"
                  onChange={handleImage2Change}
                />
              </Form.Group>

              <Button variant="primary" type="submit" className="login-btn">
                SAVE
              </Button>
            </Form>
            <Modal show={showModal} onClose={closeModal} title="Yay!">
              <section>You successfully edited this product.</section>
            </Modal>
          </>
        </Container>
      </Container>
    </Container>
  );
}

export default EditProduct;
