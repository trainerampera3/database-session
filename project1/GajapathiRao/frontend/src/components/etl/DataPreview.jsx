function DataPreview({
    data,
    title = "Data Preview",
}) {

    if (!data || data.length === 0) {
        return null;
    }


    const columns = Object.keys(data[0]);


    return (
        <div className="preview-section">

            <h2>{title}</h2>


            <div className="table-wrapper">

                <table>

                    <thead>

                        <tr>

                            {columns.map(
                                (column) => (
                                    <th key={column}>
                                        {column}
                                    </th>
                                )
                            )}

                        </tr>

                    </thead>


                    <tbody>

                        {data.map(
                            (row, rowIndex) => (

                                <tr key={rowIndex}>

                                    {columns.map(
                                        (column) => (

                                            <td
                                                key={column}
                                            >
                                                {row[column] === null
                                                    ? "NULL"
                                                    : String(row[column])
                                                }
                                            </td>

                                        )
                                    )}

                                </tr>

                            )
                        )}

                    </tbody>

                </table>

            </div>

        </div>
    );
}


export default DataPreview;