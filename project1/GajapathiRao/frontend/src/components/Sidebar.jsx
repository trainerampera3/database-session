import React from "react";

import {
    MdDashboard,
    MdCloud,
    MdAccessTime,
    MdSearch,
    MdListAlt,
    MdArticle
} from "react-icons/md";

import { NavLink } from "react-router-dom";
import { MdAir } from "react-icons/md";
import logo from "../../assests/amper.jpg";

import "../styles/sidebar.scss";

function Sidebar() {

    return (

        <aside className="sidebar">

            <div className="sidebar__brand">

                <div className="sidebar__logo">
                    <img src={logo} alt="Weather ETL Logo" className="sidebar__logo-img" width={150} height={150}/>
                </div>

                {/* <div>
                    <h2>Weather ETL</h2>
                    <span>Analytics Platform</span>
                </div> */}

            </div>



            <nav className="sidebar__nav">

                <NavLink
                    to="/"
                    className={({ isActive }) =>
                        `sidebar__link ${
                            isActive
                                ? "sidebar__link--active"
                                : ""
                        }`
                    }
                >

                    <MdDashboard className="sidebar__icon" />

                    <span>Overview</span>

                </NavLink>


                <NavLink
                    to="/weather"
                    className={({ isActive }) =>
                        `sidebar__link ${
                            isActive
                                ? "sidebar__link--active"
                                : ""
                        }`
                    }
                >

                    <MdCloud className="sidebar__icon" />

                    <span>Weather Analysis</span>

                </NavLink>

                <NavLink
                    to="/hourly-weather"
                    className={({ isActive }) =>
                        `sidebar__link ${
                            isActive
                                ? "sidebar__link--active"
                                : ""
                        }`
                    }
                >
                    <MdAccessTime className="sidebar__icon" />
                    <span>Hourly Weather</span>
                </NavLink>



                <NavLink
    to="/news"
    className={({ isActive }) =>
        `sidebar__link ${
            isActive
                ? "sidebar__link--active"
                : ""
        }`
    }
>

    <MdArticle className="sidebar__icon" />

    <span>Weather News</span>

</NavLink>

                <NavLink
                    to="/query"
                    className={({ isActive }) =>
                        `sidebar__link ${
                            isActive
                                ? "sidebar__link--active"
                                : ""
                        }`
                    }
                >

                    <MdSearch className="sidebar__icon" />

                    <span>Query Tool</span>

                </NavLink>

                <NavLink
                    to="/etl-page"
                    className={({ isActive }) =>
                        `sidebar__link ${
                            isActive
                                ? "sidebar__link--active"
                                : ""
                        }`
                    }
                >

                    <MdAir className="sidebar__icon" />
                    <span>Air Quality</span>

                </NavLink>



                <NavLink
                    to="/batch-logs"
                    className={({ isActive }) =>
                        `sidebar__link ${
                            isActive
                                ? "sidebar__link--active"
                                : ""
                        }`
                    }
                >

                    <MdListAlt className="sidebar__icon" />

                    <span>Batch Logs</span>

                </NavLink>

            </nav>


            {/* Footer */}

            {/* <div className="sidebar__footer">

                <div className="pipeline-status">

                    <span className="status-dot"></span>

                    <div>

                        <strong>ETL Pipeline</strong>

                        <small>
                            Operational
                        </small>

                    </div>

                </div>

            </div> */}

        </aside>

    );
}

export default Sidebar;