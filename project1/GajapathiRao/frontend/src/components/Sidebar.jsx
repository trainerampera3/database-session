import React from "react";

import {
    MdDashboard,
    MdCloud,
    MdSearch,
    MdListAlt,
} from "react-icons/md";

import { WiDaySunny } from "react-icons/wi";
function Sidebar() {
    return (
        <aside className="sidebar">

            {/* Brand */}
            <div className="sidebar__brand">

                <div className="sidebar__logo">
                    <WiDaySunny/>
                </div>

                <div>
                    <h2>Weather ETL</h2>
                    <span>Analytics Platform</span>
                </div>

            </div>


            {/* Navigation */}
            <nav className="sidebar__nav">

                <a
                    href="#overview"
                    className="sidebar__link sidebar__link--active"
                >
                    <MdDashboard className="sidebar__icon" />
                    <span>Overview</span>
                </a>


                <a
                    href="#weather"
                    className="sidebar__link"
                >
                    <MdCloud className="sidebar__icon" />
                    <span>Weather Analysis</span>
                </a>


                <a
                    href="#query"
                    className="sidebar__link"
                >
                    <MdSearch className="sidebar__icon" />
                    <span>Query Tool</span>
                </a>


                <a
                    href="#etl-logs"
                    className="sidebar__link"
                >
                    <MdListAlt className="sidebar__icon" />
                    <span>Batch Logs</span>
                </a>

            </nav>


            {/* Footer */}
            <div className="sidebar__footer">

                <div className="pipeline-status">

                    <span className="status-dot"></span>

                    <div>
                        <strong>ETL Pipeline</strong>
                        <small>Operational</small>
                    </div>

                </div>

            </div>

        </aside>
    );
}

export default Sidebar;