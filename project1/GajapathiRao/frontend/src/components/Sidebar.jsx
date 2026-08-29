import React from "react";

import {
    MdDashboard,
    MdCloud,
    MdSearch,
    MdListAlt,
} from "react-icons/md";

import { WiDaySunny } from "react-icons/wi";

import { NavLink } from "react-router-dom";


function Sidebar() {

    return (

        <aside className="sidebar">

            {/* Brand */}

            <div className="sidebar__brand">

                <div className="sidebar__logo">
                    <WiDaySunny />
                </div>

                <div>
                    <h2>Weather ETL</h2>
                    <span>Analytics Platform</span>
                </div>

            </div>


            {/* Navigation */}

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

            <div className="sidebar__footer">

                <div className="pipeline-status">

                    <span className="status-dot"></span>

                    <div>

                        <strong>ETL Pipeline</strong>

                        <small>
                            Operational
                        </small>

                    </div>

                </div>

            </div>

        </aside>

    );
}

export default Sidebar;