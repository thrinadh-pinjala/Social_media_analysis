import React from 'react';

const About = () => {
  const teamMembers = [
    { 
      name: "A. D Sathyamurthy",
      role: "Back End Developer",
      education: "B.Tech CSE",
      emoji: "👨‍💻"
    },
    {
      name: "V Hemanth",
      role: "Scrum Master",
      education: "B.Tech CSE",
      emoji: "🧑🏻‍💼"
    },
    {
      name: "D L Prasad",
      role: "Front End Developer",
      education: "B.Tech CSE",
      emoji: "👨‍🎨"
    },
    {
      name: "M. Abhisree",
      role: "Q&A Engineer",
      education: "B.Tech CSE",
      emoji: "👮🏻‍♀  "
    },
    {
      name: "A. Gurusree",
      role: "Product Owner",
      education: "B.Tech CSE",
      emoji: "👩‍💼"
    }
  ];

  return (
    <div className="about-page">
      <div className="team-grid">
        {teamMembers.map((member, index) => (
          <div 
            key={member.name}
            className="team-card"
            style={{ animationDelay: `${index * 0.2}s` }}
          >
            <div className="avatar-circle">{member.emoji}</div>
            <h3 className="team-name">{member.name}</h3>
            <p className="team-role">{member.role}</p>
            <p className="team-education">{member.education}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default About;