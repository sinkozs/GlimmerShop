import React, { useState, useEffect } from "react";
import axios from "axios";
import "../App.css";
import "../styles/AddNewProduct.css";
import "../styles/LoginAndSignup.css";
import "./AddNewCategory";
import Modal from "./Modal";
import { Container, Form, Button } from "react-bootstrap";
import { v4 as uuidv4 } from "uuid";
import config from "../config";

function AddNewProduct() {
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [description, setDescription] = useState("");
  const [stockQuantity, setStockQuantity] = useState("");
  const [material, setMaterial] = useState("");
  const [color, setColor] = useState("");
  const [image1, setImage1] = useState(null);
  const [image2, setImage2] = useState(null);
  const [productId, setProductId] = useState("");
  const [categoryList, setCategoryList] = useState([]);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchCategories = async () => {
      try {
        const response = await axios.get(
          `${config.BACKEND_BASE_URL}/categories`,
          {
            headers: { "Content-Type": "application/json" },
            withCredentials: true,
          }
        );
        const categories = response.data;
        setCategoryList(categories);
      } catch (error) {
        console.error("Failed to fetch categories:", error);
      }
    };

    fetchCategories();
  }, []);

  const generateUniqueFileName = (file) => {
    const fileExtension = file.name.split(".").pop();
    return `${uuidv4()}.${fileExtension}`;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();

    const productData = {
      name: name,
      description: description,
      price: price,
      stock_quantity: stockQuantity,
      material: material,
      color: color,
    };

    try {
      const response = await axios.post(
        `${config.BACKEND_BASE_URL}/products/new`,
        productData,
        {
          headers: { "Content-Type": "application/json" },
          withCredentials: true,
        }
      );

      const productId = response.data;
      setProductId(productId);

      if (image1) {
        const formData1 = new FormData();
        formData1.append("image", image1, generateUniqueFileName(image1));
        await axios.post(
          `${config.BACKEND_BASE_URL}/products/upload-image?product_id=${productId}&image_number=1`,
          formData1,
          {
            headers: { "Content-Type": "multipart/form-data" },
            withCredentials: true,
          }
        );
      }

      if (image2) {
        const formData2 = new FormData();
        formData2.append("image", image2, generateUniqueFileName(image2));
        await axios.post(
          `${config.BACKEND_BASE_URL}/products/upload-image?product_id=${productId}&image_number=2`,
          formData2,
          {
            headers: { "Content-Type": "multipart/form-data" },
            withCredentials: true,
          }
        );
      }

      setName("");
      setDescription("");
      setPrice("");
      setStockQuantity("");
      setMaterial("");
      setColor("");
      setImage1(null);
      setImage2(null);
      setShowModal(true);
    } catch (error) {
      console.error("There was an error adding the product!", error);
      setError(error.response?.data?.detail || "An unexpected error occurred");
    }
  };

  const closeModal = () => setShowModal(false);

  const handleImage1Change = (event) => setImage1(event.target.files[0]);
  const handleImage2Change = (event) => setImage2(event.target.files[0]);

  return (
    <Container fluid className="page-wrapper">
      <Container fluid className="login-form-container">
        <Container fluid className="login-form-content">
          <h1 className="login-form-h1">ADD NEW PRODUCT</h1>
          <Form onSubmit={handleSubmit} className="form">
            <Form.Group controlId="productName" className="form-group">
              <Form.Control
                type="text"
                placeholder="Product name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                required
              />
            </Form.Group>
            <Form.Group controlId="productDescription" className="form-group">
              <Form.Control
                type="text"
                placeholder="Description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                required
              />
            </Form.Group>
            <Form.Group controlId="productPrice" className="form-group">
              <Form.Control
                type="number"
                placeholder="Price"
                value={price}
                onChange={(e) => setPrice(e.target.value)}
                required
              />
            </Form.Group>
            <Form.Group controlId="productStockQuantity" className="form-group">
              <Form.Control
                type="number"
                placeholder="Stock Quantity"
                value={stockQuantity}
                onChange={(e) => setStockQuantity(e.target.value)}
                required
              />
            </Form.Group>
            <Form.Group controlId="productMaterial" className="form-group">
              <Form.Control
                type="text"
                placeholder="Material"
                value={material}
                onChange={(e) => setMaterial(e.target.value)}
                required
              />
            </Form.Group>
            <Form.Group controlId="productColor" className="form-group">
              <Form.Control
                type="text"
                placeholder="Color"
                value={color}
                onChange={(e) => setColor(e.target.value)}
                required
              />
            </Form.Group>

            <Form.Group controlId="image1" className="form-group">
              <Form.Control
                type="file"
                onChange={handleImage1Change}
                required
              />
            </Form.Group>
            <Form.Group controlId="image2" className="form-group">
              <Form.Control
                type="file"
                onChange={handleImage2Change}
                required
              />
            </Form.Group>

            <h3>Select category</h3>
            {categoryList.map((category) => (
              <Form.Check
                key={category.id}
                type="checkbox"
                label={category.category_name}
                id={`category-${category.id}`}
                className="category-checkbox"
              />
            ))}

            <Button variant="primary" type="submit" className="login-btn">
              SAVE
            </Button>
          </Form>

          <Modal show={showModal} onClose={closeModal} title="Yay!">
            <section>You successfully uploaded this product.</section>
          </Modal>
        </Container>
      </Container>
    </Container>
  );
}

export default AddNewProduct;
