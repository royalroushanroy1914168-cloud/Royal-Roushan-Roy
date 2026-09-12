const API =
    localStorage.getItem("API_URL") ||
    "http://localhost:5000/api";


const token =
    localStorage.getItem("citizenToken");


/*
   Citizen must login
*/

if (!token) {

    window.location.href =
        "login.html";

}


/* =========================
   CURRENT LOCATION
========================= */

const locateButton =
    document.getElementById("locate");


if (locateButton) {

    locateButton.addEventListener(
        "click",
        function () {

            if (!navigator.geolocation) {

                alert(
                    "Geolocation is not supported."
                );

                return;

            }


            navigator.geolocation.getCurrentPosition(

                function (position) {

                    document.getElementById(
                        "latitude"
                    ).value =
                        position.coords.latitude;


                    document.getElementById(
                        "longitude"
                    ).value =
                        position.coords.longitude;


                    const locationField =
                        document.getElementById(
                            "location"
                        );


                    if (!locationField.value) {

                        locationField.value =
                            "Current location captured";

                    }

                },


                function () {

                    alert(
                        "Unable to get location. " +
                        "Please allow location access."
                    );

                }

            );

        }
    );

}


/* =========================
   REPORT FORM
========================= */

const reportForm =
    document.getElementById(
        "reportForm"
    );


if (reportForm) {

    reportForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const formData =
                new FormData();


            formData.append(
                "problem_type",
                document.getElementById(
                    "problem_type"
                ).value
            );


            formData.append(
                "description",
                document.getElementById(
                    "description"
                ).value
            );


            formData.append(
                "location",
                document.getElementById(
                    "location"
                ).value
            );


            formData.append(
                "latitude",
                document.getElementById(
                    "latitude"
                ).value
            );


            formData.append(
                "longitude",
                document.getElementById(
                    "longitude"
                ).value
            );


            formData.append(
                "contact",
                document.getElementById(
                    "contact"
                ).value
            );


            const image =
                document.getElementById(
                    "image"
                ).files[0];


            if (image) {

                formData.append(
                    "image",
                    image
                );

            }


            try {

                const response =
                    await fetch(
                        API + "/reports",
                        {

                            method: "POST",

                            headers: {

                                Authorization:
                                    "Bearer " +
                                    token

                            },

                            body: formData

                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    document.getElementById(
                        "message"
                    ).textContent =
                        data.error ||
                        "Complaint submission failed.";

                    return;

                }


                /*
                   Save acknowledgement
                */

                localStorage.setItem(
                    "lastComplaint",
                    JSON.stringify({

                        ...data,

                        problem_type:
                            document.getElementById(
                                "problem_type"
                            ).value

                    })
                );


                /*
                   Go to acknowledgement slip
                */

                window.location.href =
                    "acknowledgement.html";

            }

            catch (error) {

                document.getElementById(
                    "message"
                ).textContent =
                    "Unable to connect to server.";

            }

        }
    );

}
