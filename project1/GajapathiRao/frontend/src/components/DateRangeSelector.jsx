function DateRangeSelector({
    startDate,
    endDate,
    onStartDateChange,
    onEndDateChange,
}) {
    return (
        <div className="date-range">
            <div className="filter">
                <label className="filter__label">
                    Start Date
                </label>

                <input
                    className="filter__input"
                    type="date"
                    value={startDate}
                    onChange={(event) =>
                        onStartDateChange(event.target.value)
                    }
                />
            </div>

            <div className="filter">
                <label className="filter__label">
                    End Date
                </label>

                <input
                    className="filter__input"
                    type="date"
                    value={endDate}
                    onChange={(event) =>
                        onEndDateChange(event.target.value)
                    }
                />
            </div>
        </div>
    );
}

export default DateRangeSelector;