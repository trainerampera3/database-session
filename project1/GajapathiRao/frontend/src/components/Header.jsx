import React from "react";

import { MdStorage } from "react-icons/md";


function Header() {

    return (

        <header className="header">

            <div className="header__left">
{/* 
                <div className="header__icon">
                    <MdStorage />
                </div> */}

                <div>

                    <h1 className="header__title">
                        Weather Data Platform
                    </h1>

                    <p className="header__subtitle">
                        Real-time weather monitoring & ETL analytics
                    </p>

                </div>

            </div>


            <div className="header__status">

                <span className="status-dot"></span>

                System Operational

            </div>

        </header>

    );
}

export default Header;