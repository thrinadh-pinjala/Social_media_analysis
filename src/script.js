// Network Animation
const canvas = document.getElementById("background-animation");
const ctx = canvas.getContext("2d");
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let nodes = [];
const numNodes = 50;
const connectionDistance = 150;
const mouse = { x: undefined, y: undefined };

// Node Class
class Node {
  constructor(x, y) {
    this.x = x;
    this.y = y;
    this.vx = Math.random() * 0.5 - 0.25;
    this.vy = Math.random() * 0.5 - 0.25;
    this.radius = 3;
    this.baseColor = `hsl(${Math.random() * 360}, 100%, 70%)`;
    this.glowColor = `hsl(${Math.random() * 360}, 100%, 50%)`;
  }

  draw() {
    ctx.beginPath();
    ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
    ctx.fillStyle = this.baseColor;
    ctx.shadowBlur = 10;
    ctx.shadowColor = this.glowColor;
    ctx.fill();
  }

  update() {
    this.x += this.vx;
    this.y += this.vy;

    // Bounce off walls
    if (this.x < 0 || this.x > canvas.width) this.vx *= -1;
    if (this.y < 0 || this.y > canvas.height) this.vy *= -1;

    // Mouse interaction
    if (mouse.x !== undefined && mouse.y !== undefined) {
      const dx = this.x - mouse.x;
      const dy = this.y - mouse.y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < 100) {
        this.vx += dx * 0.005;
        this.vy += dy * 0.005;
      }
    }
  }
}

// Create Nodes
function init() {
  nodes = [];
  for (let i = 0; i < numNodes; i++) {
    const x = Math.random() * canvas.width;
    const y = Math.random() * canvas.height;
    nodes.push(new Node(x, y));
  }
}

// Draw Connections
function drawConnections() {
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const dx = nodes[i].x - nodes[j].x;
      const dy = nodes[i].y - nodes[j].y;
      const dist = Math.sqrt(dx * dx + dy * dy);

      if (dist < connectionDistance) {
        ctx.beginPath();
        ctx.moveTo(nodes[i].x, nodes[i].y);
        ctx.lineTo(nodes[j].x, nodes[j].y);
        ctx.strokeStyle = `rgba(255, 107, 107, ${1 - dist / connectionDistance})`;
        ctx.lineWidth = 1;
        ctx.stroke();
      }
    }
  }
}

// Animate
function animate() {
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  drawConnections();
  nodes.forEach((node) => {
    node.update();
    node.draw();
  });

  requestAnimationFrame(animate);
}

// Handle Mouse Movement
window.addEventListener("mousemove", (e) => {
  mouse.x = e.x;
  mouse.y = e.y;
});

// Handle Window Resize
window.addEventListener("resize", () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  init();
});

// Theme Toggle
const userProfile = document.getElementById("userProfile");
const dropdownMenu = document.getElementById("dropdownMenu");

userProfile.addEventListener("click", () => {
  dropdownMenu.style.display = dropdownMenu.style.display === "block" ? "none" : "block";
});

// Hide dropdown when clicking outside
document.addEventListener("mousedown", (event) => {
  if (!userProfile.contains(event.target) && !dropdownMenu.contains(event.target)) {
    dropdownMenu.style.display = "none";
  }
});

// Logout button
document.getElementById("logoutBtn").addEventListener("click", () => {
  window.location.href = "/";
});

// Start Animation
init();
animate();
