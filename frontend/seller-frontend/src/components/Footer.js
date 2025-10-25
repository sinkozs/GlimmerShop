import { Container, Row, Col } from "react-bootstrap";
import { Link } from "react-router-dom";
import { FaInstagram, FaTwitter, FaFacebook } from "react-icons/fa";
import "../styles/Footer.css";

function Footer() {
  return (
    <footer className="footer-container">
      <Container fluid>
        <Row className="social-icons">
          <Col className="text-center">
            <Link to="https://www.instagram.com/">
              <FaInstagram className="footer-icon" />
            </Link>
          </Col>
          <Col className="text-center">
            <Link to="https://twitter.com/">
              <FaTwitter className="footer-icon" />
            </Link>
          </Col>
          <Col className="text-center">
            <Link to="https://www.facebook.com/">
              <FaFacebook className="footer-icon" />
            </Link>
          </Col>
        </Row>
      </Container>
      <Container fluid>
        <Container className="footer-content">
          <section className="text-center">
            <a href="https://github.com/sinkozs">© Zsofia Sinko</a>
          </section>
        </Container>
      </Container>
    </footer>
  );
}

export default Footer;
