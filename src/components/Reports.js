import React, { useState, useEffect } from "react";
import { saveAs } from "file-saver";
import { useLocation, useNavigate } from "react-router-dom";
import Calendar from "react-calendar";
import "react-calendar/dist/Calendar.css";
import NavBar from "./Navbar";

function Reports() {
  const [selectedDate, setSelectedDate] = useState("");
  const [selectedTime, setSelectedTime] = useState("");
  const [reportType, setReportType] = useState("Default Report");
  const [email, setEmail] = useState("");
  const [format, setFormat] = useState("pdf");
  const [emailFrequency, setEmailFrequency] = useState("daily");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  const [channelData, setChannelData] = useState(null);
  const navigate = useNavigate();
  const location = useLocation();

  const styles = {
    reportsContainer: {
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      minHeight: "100vh",
      background: "linear-gradient(to right, #001f3f, #003366)",
      padding: "40px",
      color: "white",
      gap: "50px",
    },
    calendarPanel: {
      background: "rgba(255, 255, 255, 0.1)",
      padding: "30px",
      borderRadius: "12px",
      boxShadow: "0 4px 10px rgba(255, 255, 255, 0.2)",
      width: "35%",
      textAlign: "center",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      justifyContent: "center",
      minHeight: "400px",
    },
    reportPanel: {
      background: "rgba(255, 255, 255, 0.1)",
      padding: "30px",
      borderRadius: "12px",
      boxShadow: "0 4px 10px rgba(255, 255, 255, 0.2)",
      width: "40%",
      textAlign: "center",
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
    },
    heading: {
      fontSize: "28px",
      fontWeight: "bold",
      textTransform: "uppercase",
      textAlign: "center",
      color: "#FFD700",
      textDecoration: "underline",
      marginBottom: "15px",
    },
    label: {
      fontSize: "18px",
      marginBottom: "5px",
      textAlign: "center",
      width: "100%",
    },
    inputBox: {
      width: "90%",
      padding: "10px",
      fontSize: "16px",
      border: "none",
      borderRadius: "8px",
      marginBottom: "20px",
      textAlign: "center",
      background: "white",
      color: "#001f3f",
    },
    dropdownContainer: {
      display: "flex",
      flexDirection: "column",
      alignItems: "center",
      width: "100%",
    },
    dropdown: {
      width: "90%",
      padding: "10px",
      fontSize: "16px",
      border: "none",
      borderRadius: "8px",
      background: "white",
      color: "#001f3f",
      marginBottom: "20px",
      cursor: "pointer",
    },
    buttonContainer: {
      display: "flex",
      justifyContent: "space-between",
      width: "90%",
    },
    button: {
      background: "#007bff",
      color: "white",
      border: "none",
      padding: "12px 20px",
      fontSize: "16px",
      borderRadius: "8px",
      cursor: "pointer",
      marginTop: "10px",
      transition: "background 0.3s ease-in-out",
      width: "48%",
    },
    buttonHover: {
      background: "#0056b3",
    },
    emailButton: {
      background: "#28a745",
      color: "white",
      border: "none",
      padding: "12px 20px",
      fontSize: "16px",
      borderRadius: "8px",
      cursor: "pointer",
      marginTop: "10px",
      transition: "background 0.3s ease-in-out",
      width: "48%",
    },
    emailButtonHover: {
      background: "#218838",
    },
  };

  useEffect(() => { 
    const savedReportType = location.state?.reportType || sessionStorage.getItem("reportType") || "Default Report";
    const savedChannelData = sessionStorage.getItem("channelData");
    
    setReportType(savedReportType);
    if (savedChannelData) {
      setChannelData(JSON.parse(savedChannelData));
    }
    
    sessionStorage.setItem("reportType", savedReportType);
  }, [location]);

  const handleDateChange = (date) => {
    const formattedDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000)
      .toISOString()
      .split("T")[0];
    setSelectedDate(formattedDate);
  };

  const handleTimeChange = (event) => {
    setSelectedTime(event.target.value);
  };

  const getFullDateTime = () => {
    return selectedDate && selectedTime ? `${selectedDate} ${selectedTime}` : "";
  };

  const handleDownload = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch("http://127.0.0.1:5000/send/download_report", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          reportType,
          format,
          channelData: channelData
        }),
      });

      if (!response.ok) {
        throw new Error("Failed to download report");
      }

      const data = await response.json();
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      saveAs(blob, `report.${format}`);
      setSuccess("Report downloaded successfully!");
    } catch (error) {
      setError("Failed to download report. Please try again.");
      console.error("Download error:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleSendEmail = async () => {
    if (!email) {
      setError("Please enter an email address.");
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const requestData = {
        email,
        reportType,
        scheduleTime: getFullDateTime(),
        frequency: emailFrequency,
        format,
        channelData: channelData
      };

      console.log("Sending request with data:", requestData); // Debug log

      const response = await fetch("http://127.0.0.1:5000/send/schedule-report", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();
      console.log("Server response:", data); // Debug log

      if (!response.ok) {
        throw new Error(data.error || "Failed to schedule report");
      }

      setSuccess(`Report has been scheduled and will be sent to ${email} (${emailFrequency})!`);
    } catch (error) {
      console.error("Schedule error details:", error); // Debug log
      setError(`Failed to schedule report: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <NavBar />
      <div style={styles.reportsContainer}>
        {/* Left Side - Calendar + Time Input */}
        <div style={styles.calendarPanel}>
          <h3 style={styles.heading}>📅 SELECT DATE & TIME</h3>
          <Calendar onClickDay={handleDateChange} />

          {/* Time Input */}
          <label style={styles.label}>⏰ Select Time</label>
          <input type="time" value={selectedTime} onChange={handleTimeChange} style={styles.inputBox} />
        </div>

        {/* Right Side - Report Options */}
        <div style={styles.reportPanel}>
          <h2 style={styles.heading}>📊 Download & Automate Report Delivery</h2>

          {error && <div style={{ color: "red", marginBottom: "10px" }}>{error}</div>}
          {success && <div style={{ color: "green", marginBottom: "10px" }}>{success}</div>}

          {/* Channel Name Display */}
          {channelData && (
            <>
              <label style={styles.label}>Channel Name</label>
              <input type="text" value={channelData.channelName} readOnly style={styles.inputBox} />
            </>
          )}

          {/* Report Type */}
          <label style={styles.label}>Report Type</label>
          <input type="text" value={reportType} readOnly style={styles.inputBox} />

          {/* Selected Date & Time Display */}
          <label style={styles.label}>Selected Date & Time</label>
          <input type="text" value={getFullDateTime()} readOnly style={styles.inputBox} />

          {/* Email Input Field */}
          <label style={styles.label}>Email ID</label>
          <input type="email" value={email} onChange={(e) => setEmail(e.target.value)} style={styles.inputBox} />

          {/* Email Frequency Selection */}
          <div style={styles.dropdownContainer}>
            <label style={styles.label}>Email Frequency</label>
            <select style={styles.dropdown} value={emailFrequency} onChange={(e) => setEmailFrequency(e.target.value)}>
              <option value="daily">Daily</option>
              <option value="weekly">Weekly</option>
              <option value="monthly">Monthly</option>
            </select>
          </div>

          {/* Report Format Selection */}
          <div style={styles.dropdownContainer}>
            <label style={styles.label}>Report Format</label>
            <select style={styles.dropdown} value={format} onChange={(e) => setFormat(e.target.value)}>
              <option value="pdf">PDF</option>
              <option value="csv">CSV</option>
            </select>
          </div>

          {/* Buttons */}
          <div style={styles.buttonContainer}>
            <button 
              style={{...styles.button, opacity: loading ? 0.7 : 1}} 
              onClick={handleDownload}
              disabled={loading || !channelData}
            >
              {loading ? "Processing..." : "📥 Download Report"}
            </button>
            <button 
              style={{...styles.emailButton, opacity: loading ? 0.7 : 1}} 
              onClick={handleSendEmail}
              disabled={loading || !channelData}
            >
              {loading ? "Scheduling..." : "📧 Send to Email"}
            </button>
          </div>
        </div>
      </div>
    </>
  );
}

export default Reports;