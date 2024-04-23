import React from "react";

import { Outlet, Link } from "react-router-dom";

// import SideMenu from "./SideMenu";

const Header = () => {
  return (
    <section className="header-container">
      <nav className="nav-container">
        <div className="logo">
          <img src="assets/logo.svg" alt="logo" />
        </div>
        <div className="nav-line"></div>
        <div className="nav-links-container">
          <div className="nav-link-item show" to="/" id="home">
            <span>00</span>
            <Link to="/" className="nav-link">Home</Link>
          </div>

          <div className="nav-link-item show" to="destination" id="destination">
            <span>01</span>
            <Link to="/add-satellite" className="nav-link">Satellites</Link>
          </div>

          <div className="nav-link-item show" to="/crew" id="crew">
            <span>02</span>
            <Link to="/add-groundstation" className="nav-link">Groundstations</Link>
          </div>

          <div className="nav-link-item show" to="/technology" id="technology">
            <span>03</span>
            <Link to="/add-task" className="nav-link">Tasks</Link>
          </div>

          <div className="nav-link-item show" to="/technology" id="technology">
            <span>04</span>
            <Link to="/view-data" className="nav-link">Data</Link>
          </div>

          <div className="nav-link-item hidden menu" id="hamburger">
            <img src="/assets/shared/icon-hamburger.svg" alt="menu" />
          </div>
        </div>
      </nav>
      <Outlet />
    </section>
  );
};

export default Header;