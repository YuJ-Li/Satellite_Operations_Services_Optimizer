import React from "react";

import { Outlet, Link } from "react-router-dom";

const Header = () => {
  return (
    <section className="header-container">
      <nav className="nav-container">
        <div className="logo">
          <img src="assets/logo.svg" alt="logo" />
        </div>
        <div className="nav-line"></div>
        <div className="nav-links-container">
          <Link to="/" className="nav-link-item show" id="home">
            <span>00</span>
            <span className="nav-link">Home</span>
          </Link>

          <Link to="/add-satellite" className="nav-link-item show" id="satellite">
            <span>01</span>
            <span className="nav-link">Satellites</span>
          </Link>

          <Link to="/add-groundstation" className="nav-link-item show" id="groundstation">
            <span>02</span>
            <span className="nav-link">Groundstations</span>
          </Link>

          <Link to="/add-task" className="nav-link-item show" id="technology">
            <span>03</span>
            <span className="nav-link">Tasks</span>
          </Link>

          <Link to="/view-data" className="nav-link-item show" id="technology">
            <span>04</span>
            <span className="nav-link">Data</span>
          </Link>
        </div>
      </nav>
      <Outlet />
    </section>
  );
};

export default Header;