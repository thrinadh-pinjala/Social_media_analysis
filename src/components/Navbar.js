import React from "react";
import { Link } from "react-router-dom";

function NavBar() {
  const styles = {
    navbar: {
      display: "flex",
      justifyContent: "space-between",
      alignItems: "center",
      padding: "15px 30px",
      backgroundColor: "#021B79",
      color: "white",
    },
    link: {
      color: "white",
      textDecoration: "none",
      marginLeft: "20px",
    },
  };

  return (
    <nav style={styles.navbar}>
      <h2>Social Media Tool</h2>
      <div>
        <Link to="/" style={styles.link}>Dashboard</Link>
        <Link to="/reports" style={styles.link}>Reports</Link>
      </div>
    </nav>
  );
}

export default NavBar;
