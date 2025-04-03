import React, { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

function Signup() {
  const [username, setUsername] = useState("");
  const [gmail, setGmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  const handleSignup = (e) => {
    e.preventDefault();

    // Username validation
    if (username.length < 8) {
      setError("Username must be at least 8 characters long.");
      return;
    }

    // Gmail validation
    const gmailRegex = /^[a-zA-Z0-9._%+-]+@gmail\.com$/;
    if (!gmailRegex.test(gmail)) {
      setError("Please enter a valid Gmail address.");
      return;
    }

    // Password validation
    if (password.length < 8) {
      setError("Password must be at least 8 characters long.");
      return;
    }

    // Save user data (can be saved to localStorage or backend)
    localStorage.setItem("user", JSON.stringify({ username, gmail, password }));

    alert("Signup successful! Redirecting to login...");
    navigate("/");
  };

  // Styles
  const styles = {
    container: {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      height: "100vh",
      background: "linear-gradient(135deg, #1e3c72, #2a5298)",
      color: "white",
      fontFamily: "Arial, sans-serif",
    },
    formBox: {
      background: "white",
      padding: "30px",
      borderRadius: "10px",
      boxShadow: "0px 4px 8px rgba(0, 0, 0, 0.2)",
      textAlign: "center",
      color: "black",
      width: "350px",
    },
    input: {
      width: "90%",
      padding: "10px",
      margin: "10px 0",
      borderRadius: "5px",
      border: "1px solid #ccc",
    },
    button: {
      width: "100%",
      padding: "10px",
      backgroundColor: "#007bff",
      color: "white",
      border: "none",
      borderRadius: "5px",
      cursor: "pointer",
      fontSize: "1rem",
    },
    buttonHover: {
      backgroundColor: "#0056b3",
    },
    errorText: {
      color: "red",
      marginBottom: "10px",
    },
    link: {
      textDecoration: "none",
      color: "#007bff",
      marginTop: "10px",
      display: "block",
    },
  };

  return (
    <div style={styles.container}>
      <div style={styles.formBox}>
        <h2>Sign Up</h2>
        {error && <p style={styles.errorText}>{error}</p>}
        <form onSubmit={handleSignup}>
          <input
            type="text"
            placeholder="Username (min 8 chars)"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            style={styles.input}
          />
          <input
            type="email"
            placeholder="Enter Gmail"
            value={gmail}
            onChange={(e) => setGmail(e.target.value)}
            style={styles.input}
          />
          <input
            type="password"
            placeholder="Password (min 8 chars)"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            style={styles.input}
          />
          <button type="submit" style={styles.button}>
            Sign Up
          </button>
        </form>
        <p>
          Already have an account?{" "}
          <Link to="/" style={styles.link}>
            Login here
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Signup;
