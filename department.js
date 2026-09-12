const API =
    localStorage.getItem("API_URL") ||
    "http://localhost:5000/api";


const departmentToken =
    localStorage.getItem(
        "departmentToken"
    );


/*
   Protect dashboard
*/

if (!departmentToken) {

    window.location.href =
        "department-login.html";

}


/* =========================
   LOAD COMPLAINTS
========================= */

async function loadReports() {

    try {

        const response =
            await fetch(
                API + "/department/reports",
                {

                    headers: {

                        Authorization:
                            "Bearer " +
                            departmentToken

                    }

                }
            );


        /*
           Unauthorized
        */

        if (response.status === 401) {

            localStorage.removeItem(
                "departmentToken"
            );

            window.location.href =
                "department-login.html";

            return;

        }


        const reports =
            await response.json();


        /*
           Count statuses
        */

        const counts = {

            Pending: 0,

            Assigned: 0,

            "In Progress": 0,

            Resolved: 0

        };


        reports.forEach(
            report => {

                if (
                    counts[
                        report.status
                    ] !== undefined
                ) {

                    counts[
                        report.status
                    ]++;

                }

            }
        );


        /*
           Statistics
        */

        document.getElementById(
            "stats"
        ).innerHTML =

            Object.entries(
                counts
            )

            .map(

                ([status, count]) => `

                    <div class="stat">

                        <b>
                            ${status}
                        </b>

                        <br>

                        ${count}

                    </div>

                `

            )

            .join("");


        /*
           Complaint table
        */

        document.getElementById(
            "reports"
        ).innerHTML =

            reports

            .map(

                report => `

                    <tr>

                        <td>
                            ${report.tracking_id}
                        </td>

                        <td>
                            ${report.citizen_name}
                        </td>

                        <td>
                            ${report.problem_type}
                        </td>

                        <td>
                            ${report.location || "-"}
                        </td>

                        <td class="priority-high">
                            ${report.priority_score}
                        </td>

                        <td>

                            <select
                                class="status-select"
                                data-id="${report.id}"
                            >

                                <option
                                    ${
                                        report.status ===
                                        "Pending"
                                        ? "selected"
                                        : ""
                                    }
                                >
                                    Pending
                                </option>

                                <option
                                    ${
                                        report.status ===
                                        "Assigned"
                                        ? "selected"
                                        : ""
                                    }
                                >
                                    Assigned
                                </option>

                                <option
                                    ${
                                        report.status ===
                                        "In Progress"
                                        ? "selected"
                                        : ""
                                    }
                                >
                                    In Progress
                                </option>

                                <option
                                    ${
                                        report.status ===
                                        "Resolved"
                                        ? "selected"
                                        : ""
                                    }
                                >
                                    Resolved
                                </option>

                            </select>

                        </td>

                        <td>

                            <button
                                class="btn"
                                onclick="
                                    updateReport(
                                        ${report.id}
                                    )
                                "
                            >
                                Update
                            </button>

                        </td>

                    </tr>

                `

            )

            .join("");

    }

    catch (error) {

        console.error(error);

    }

}


/* =========================
   UPDATE COMPLAINT
========================= */

async function updateReport(
    reportId
) {

    const select =
        document.querySelector(
            `select[data-id="${reportId}"]`
        );


    const status =
        select.value;


    try {

        const response =
            await fetch(

                API +
                "/department/reports/" +
                reportId,

                {

                    method: "PATCH",

                    headers: {

                        "Content-Type":
                            "application/json",

                        Authorization:
                            "Bearer " +
                            departmentToken

                    },

                    body: JSON.stringify({

                        status:

                            status,

                        assigned_department:
                            "Civic Department"

                    })

                }

            );


        const data =
            await response.json();


        alert(
            data.message ||
            data.error
        );


        if (response.ok) {

            loadReports();

        }

    }

    catch (error) {

        alert(
            "Unable to update complaint."
        );

    }

}


/* =========================
   LOGOUT
========================= */

const logout =
    document.getElementById(
        "logout"
    );


if (logout) {

    logout.addEventListener(
        "click",
        function () {

            localStorage.removeItem(
                "departmentToken"
            );

            window.location.href =
                "department-login.html";

        }
    );

}


/*
   Initial load
*/

loadReports();
