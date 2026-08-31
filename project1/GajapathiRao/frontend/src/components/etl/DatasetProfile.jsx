import "../../styles/etlpage.scss";

function DatasetProfile({ profile }) {

    if (!profile) {
        return null;
    }


    return (
        <div className="profile-section">

            <h2>Dataset Profile</h2>


            <div className="profile-cards">

                <div className="profile-card">
                    <span>Rows</span>
                    <strong>
                        {profile.rows}
                    </strong>
                </div>


                <div className="profile-card">
                    <span>Columns</span>
                    <strong>
                        {profile.columns}
                    </strong>
                </div>


                <div className="profile-card">
                    <span>Null Values</span>
                    <strong>
                        {profile.null_values}
                    </strong>
                </div>


                <div className="profile-card">
                    <span>Duplicate Rows</span>
                    <strong>
                        {profile.duplicate_rows}
                    </strong>
                </div>

            </div>


            <h3>Column Details</h3>


            <div className="table-wrapper">

                <table>

                    <thead>

                        <tr>
                            <th>Column</th>
                            <th>Data Type</th>
                            <th>Nulls</th>
                            <th>Null %</th>
                            <th>Unique</th>
                        </tr>

                    </thead>


                    <tbody>

                        {profile.column_details.map(
                            (column) => (

                                <tr key={column.name}>

                                    <td>
                                        {column.name}
                                    </td>

                                    <td>
                                        {column.dtype}
                                    </td>

                                    <td>
                                        {column.null_count}
                                    </td>

                                    <td>
                                        {column.null_percentage}%
                                    </td>

                                    <td>
                                        {column.unique_count}
                                    </td>

                                </tr>

                            )
                        )}

                    </tbody>

                </table>

            </div>

        </div>
    );
}


export default DatasetProfile;