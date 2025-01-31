import React from 'react';
import '../styles/Modal.css';
import { Container } from 'react-bootstrap';

const Modal = ({ show, onClose, title, children }) => {
  if (!show) {
    return null;
  }

  return (
    <Container className="modal-overlay">
      <Container className="modal-content">
        <Container className="modal-header">
          <h4 className="modal-title">{title}</h4>
          <button className="close-button" onClick={onClose}>
            &times;
          </button>
        </Container>
        <Container className="modal-body">
          {children}
        </Container>
      </Container>
    </Container>
  );
};

export default Modal;
