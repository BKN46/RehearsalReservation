# Rehearsal Reservation Mini Program

This is the WeChat Mini Program frontend for the Rehearsal Reservation system.

## Setup

1.  Open **WeChat Developer Tools**.
2.  Import this project (select the `frontend` folder).
3.  Set the **AppID** (use your own or a test ID).
4.  Ensure the **Cloud Development** environment is set up and the `api` cloud function is deployed (see `../cloudfunction/README.md`).

## Features

-   **Login**: WeChat Login + Student ID Binding.
-   **Reservation**: Select campus, date, and time slot.
-   **My Reservations**: View and cancel reservations.
-   **Equipment**: Browse, borrow, and register equipment.
-   **Admin**: Manage unavailable times and key managers.

## Project Structure

-   `pages/`: Page files.
    -   `login/`: Login and registration.
    -   `index/`: Home page (Reservation).
    -   `my-reservations/`: User's reservations.
    -   `equipment/`: Equipment management.
    -   `profile/`: User profile.
    -   `admin/`: Admin dashboard.
-   `images/`: Assets.
-   `app.js`: Global logic (Cloud init).
-   `app.json`: Global configuration.
