const API =
    localStorage.getItem("API_URL") ||
    "https://royal-roushan-roy.onrender.com";


function showMessage(message) {

    const element =
        document.getElementById("message");

    if (element) {

        element.textContent = message;

    }

}


/* =========================
   CITIZEN REGISTRATION
========================= */

const registerForm =
    document.getElementById("registerForm");


if (registerForm) {

    registerForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const name =
                document.getElementById("name").value.trim();

            const email =
                document.getElementById("email").value.trim();

            const password =
                document.getElementById("password").value;

            const confirm =
                document.getElementById("confirm").value;


            if (password !== confirm) {

                showMessage(
                    "Passwords do not match."
                );

                return;

            }


            try {

                const response =
                    await fetch(
                        API + "/register",
                        {

                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                name,
                                email,
                                password
                            })

                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    showMessage(
                        data.error ||
                        "Registration failed."
                    );

                    return;

                }


                showMessage(
                    "Registration successful!"
                );


                setTimeout(
                    () => {
                        window.location.href =
                            "login.html";
                    },
                    800
                );

            }

            catch (error) {

                showMessage(
                    "Unable to connect to server."
                );

            }

        }
    );

}


/* =========================
   CITIZEN LOGIN
========================= */

const loginForm =
    document.getElementById("loginForm");


if (loginForm) {

    loginForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const email =
                document.getElementById("email").value.trim();

            const password =
                document.getElementById("password").value;


            try {

                const response =
                    await fetch(
                        API + "/login",
                        {

                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                email,
                                password
                            })

                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    showMessage(
                        data.error ||
                        "Invalid login."
                    );

                    return;

                }


                localStorage.setItem(
                    "citizenToken",
                    data.token
                );


                localStorage.setItem(
                    "citizen",
                    JSON.stringify(data.user)
                );


                window.location.href =
                    "report.html";

            }

            catch (error) {

                showMessage(
                    "Unable to connect to server."
                );

            }

        }
    );

}


/* =========================
   DEPARTMENT LOGIN
========================= */

const departmentLoginForm =
    document.getElementById(
        "departmentLoginForm"
    );


if (departmentLoginForm) {

    departmentLoginForm.addEventListener(
        "submit",
        async function (event) {

            event.preventDefault();


            const email =
                document.getElementById("email").value.trim();

            const password =
                document.getElementById("password").value;


            try {

                const response =
                    await fetch(
                        API + "/department/login",
                        {

                            method: "POST",

                            headers: {
                                "Content-Type":
                                    "application/json"
                            },

                            body: JSON.stringify({
                                email,
                                password
                            })

                        }
                    );


                const data =
                    await response.json();


                if (!response.ok) {

                    showMessage(
                        data.error ||
                        "Invalid department credentials."
                    );

                    return;

                }


                localStorage.setItem(
                    "departmentToken",
                    data.token
                );


                window.location.href =
                    "department-dashboard.html";

            }

            catch (error) {

                showMessage(
                    "Unable to connect to server."
                );

            }

        }
    );

}
