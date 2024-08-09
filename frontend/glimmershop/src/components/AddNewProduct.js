import React, { useState } from "react";
import axios from "axios";
import "../App.css";
import "../styles/AddNewProduct.css";
import "../styles/LoginAndSignup.css";
import Modal from "./Modal";
import { useNavigate } from "react-router-dom";
import { Container, Form, Button } from "react-bootstrap";
import { v4 as uuidv4 } from "uuid";

function AddNewProduct() {
  const [name, setName] = useState("");
  const [price, setPrice] = useState("");
  const [description, setDescription] = useState("");
  const [stockQuantiy, setStockQuantiy] = useState("");
  const [material, setMaterial] = useState("");
  const [color, setColor] = useState("");
  const [image1, setImage1] = useState(null);
  const [image2, setImage2] = useState(null);
  const [productId, setProductId] = useState("");
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState(null);
  const seller_id = localStorage.getItem("sellerId");
  const token = localStorage.getItem("token");
  const navigate = useNavigate();

  function generateUniqueFileName(file) {
    const fileExtension = file.name.split(".").pop();
    const uniqueFileName = `${uuidv4()}.${fileExtension}`;
    return uniqueFileName;
  }

  const handleSubmit = async (event) => {
    event.preventDefault();

    const productData = {
      name: name,
      description: description,
      price: price,
      stock_quantity: stockQuantiy,
      material: material,
      color: color,
    };

         try {
      const response = await axios.post(
        "http://127.0.0.1:8000/products/new",
        productData,
        {
          headers: {
            Authorization: `Bearer ${token}`,
            "Content-Type": "application/json",
          },
        }
      ); 

      const productId = response.data;
      setProductId(productId);

      if (image1) {
        const image1FileName = generateUniqueFileName(image1);

        const formData1 = new FormData();

        formData1.append("image", image1, image1FileName);

        await axios.post(
          `http://127.0.0.1:8000/products/upload-image?product_id=${productId}&image_number=1`,
          formData1,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "multipart/form-data",
            },
          }
        );
      }

      if (image2) {
        const image2FileName = generateUniqueFileName(image2);
        const formData2 = new FormData();
        formData2.append("image", image2, image2FileName);

        await axios.post(
          `http://127.0.0.1:8000/products/upload-image?product_id=${productId}&image_number=2`,
          formData2,
          {
            headers: {
              Authorization: `Bearer ${token}`,
              "Content-Type": "multipart/form-data",
            },
          }
        );
      }

      console.log("Product and images added successfully!");

      setName("");
      setDescription("");
      setPrice("");
      setStockQuantiy("");
      setMaterial("");
      setColor("");
      setImage1(null);
      setImage2(null);
    } catch (error) {
      console.error("There was an error adding the product!", error);
      setError(error.response?.data?.detail || "An unexpected error occurred");
      setShowModal(true);
    }
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
            <h1 className="login-form-h1">ADD NEW PRODUCT</h1>
            <Form onSubmit={handleSubmit} className="form">
              <Form.Group controlId="productName" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="Product name"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  required
                  className="form-control"
                />
              </Form.Group>
              <Form.Group controlId="productDescription" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="Description"
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  required
                  className="form-control"
                />
              </Form.Group>
              <Form.Group controlId="productPrice" className="form-group">
                <Form.Control
                  type="number"
                  placeholder="Price"
                  value={price}
                  onChange={(e) => setPrice(e.target.value)}
                  required
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
                  required
                  className="form-control"
                />
              </Form.Group>
              <Form.Group controlId="productMaterial" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="Material"
                  value={material}
                  onChange={(e) => setMaterial(e.target.value)}
                  required
                  className="form-control"
                />
              </Form.Group>

              <Form.Group controlId="productColor" className="form-group">
                <Form.Control
                  type="text"
                  placeholder="Color"
                  value={color}
                  onChange={(e) => setColor(e.target.value)}
                  required
                  className="form-control"
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

              <Button variant="primary" type="submit" className="login-btn">
                SAVE
              </Button>
            </Form>
          </>
        </Container>
      </Container>
    </Container>
  );
}

export default AddNewProduct;
