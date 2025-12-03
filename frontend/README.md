# Rehearsal Reservation System (Native Mini Program)

This is the frontend for the Rehearsal Reservation System, implemented as a native WeChat Mini Program.

## Project Structure

- `pages/`: Application pages
  - `index/`: Home page (Weekly Schedule)
  - `login/`: Login & Registration
  - `equipment/`: Equipment Management
  - `profile/`: User Profile
  - `my-reservations/`: User Reservations
  - `admin/`: Admin Dashboard & Subpages
- `images/`: Static assets (TabBar icons need to be placed in `images/tabbar/`)
- `app.js`: Global logic & Cloud initialization
- `app.json`: Global configuration
- `app.wxss`: Global styles

## Theme

The application uses a minimalist Black/White/Gray theme:
- Primary: Black (`#333`)
- Background: Light Gray (`#f5f5f5`)
- Cards: White (`#fff`)
- Functional Colors (Time Blocks):
  - Blue: Reserved
  - Green: Key Picked Up
  - Gray: Key Returned
  - Red/Striped: Unavailable

## Setup

1. **Open in WeChat DevTools**
   - Import the `frontend` directory.
   - Ensure your AppID is configured in `project.config.json`.

2. **Cloud Development**
   - Ensure your `cloudfunction` folder is deployed to your WeChat Cloud environment.
   - Update the environment ID in `app.js` if necessary.

3. **Icons**
   - Place your tabbar icons in `frontend/images/tabbar/`:
     - `home.png`, `home-active.png`
     - `equipment.png`, `equipment-active.png`
     - `profile.png`, `profile-active.png`
