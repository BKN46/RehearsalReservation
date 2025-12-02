# Cloud Function Backend

This directory contains the WeChat Mini Program Cloud Function adapted from the original Python backend.

## Deployment

1.  Open WeChat Developer Tools.
2.  Right-click on the `cloudfunction` folder and select "Sync Cloud Function List".
3.  Right-click on `api` and select "Upload and Deploy: Cloud Installation (Install dependencies)".

## Database Setup

You need to create the following collections in the Cloud Database:

-   `reservations`
-   `campuses`
-   `unavailable_times`
-   `key_managers`
-   `equipment`
-   `equipment_borrows`
-   `users`

### Initial Data

You should manually add the campuses to the `campuses` collection:

```json
[
  { "id": 1, "name": "学院路校区" },
  { "id": 2, "name": "沙河校区" }
]
```

## Configuration

It is recommended to set the timezone to `Asia/Shanghai` in the Cloud Function configuration to ensure correct date handling.

## API Structure

The `api` cloud function uses `tcb-router`. You can call it from the Mini Program like this:

```javascript
wx.cloud.callFunction({
  name: 'api',
  data: {
    $url: 'reservation/create', // The route path
    campus_id: 1,
    date: '2023-10-27',
    start_hour: 18,
    end_hour: 20,
    student_id: '2137xxxx',
    name: 'Zhang San'
  }
})
```

## Routes

### Reservation
-   `reservation/campuses` (GET)
-   `reservation/create` (POST)
-   `reservation/my-reservations` (GET)
-   `reservation/weekly` (GET)
-   `reservation/cancel` (POST)

### Admin
-   `admin/unavailable-times` (GET, POST, DELETE) - Pass `httpMethod: 'POST'/'DELETE'` in data for write operations.
-   `admin/key-managers` (GET, POST, DELETE) - Pass `httpMethod: 'POST'/'DELETE'` in data for write operations.
-   `admin/reservations` (GET)

### Key Management
-   `key/pickup` (POST)
-   `key/return` (POST)
-   `key/pickups` (GET)

### Equipment
-   `equipment/borrow` (POST)
-   `equipment/return` (POST)
-   `equipment/list` (GET)
-   `equipment/register` (POST)
