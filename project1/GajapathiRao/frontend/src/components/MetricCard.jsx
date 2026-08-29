import React from "react";


function MetricCard({
    title,
    value,
    unit,
    icon,
    description
}) {

    return (

        <div className="metric-card">

            <div className="metric-card__top">

                <div className="metric-card__title">
                    {title}
                </div>

                <div className="metric-card__icon">
                    {icon}
                </div>

            </div>


            <div className="metric-card__value">

                {value}

                {unit && (
                    <span>
                        {unit}
                    </span>
                )}

            </div>


            {description && (

                <div className="metric-card__description">

                    {description}

                </div>

            )}

        </div>

    );
}

export default MetricCard;