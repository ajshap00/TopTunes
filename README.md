# Goat Project

Welcome to the Goat Project! This project is a Django-based web application that integrates with various APIs to provide a rich user experience. Below you'll find detailed information about the project, how to set it up, and how to contribute.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The Goat Project is a web application built with Django. It integrates with the Spotify API to fetch artist data, including top tracks and albums. The application also allows users to vote for their favorite artists and view the results.

## Features

- Fetch artist data from Spotify
- Display artist details, including top tracks and albums
- Allow users to vote for their favorite artists
- Display voting results
- Responsive design with a clean UI

## Installation

To get started with the Goat Project, follow these steps:

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/goat.git
    cd goat
    ```

2. **Create a virtual environment and activate it:**

    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required packages:**

    ```sh
    pip install -r requirements.txt
    ```

4. **Set up the database:**

    ```sh
    python manage.py migrate
    ```

5. **Create a superuser:**

    ```sh
    python manage.py createsuperuser
    ```

6. **Run the development server:**

    ```sh
    python manage.py runserver
    ```

## Configuration

Create a `.env` file in the root directory of your project and add the following environment variables:

```properties
SECRET_KEY=your_secret_key
SPOTIFY_CLIENT_ID=your_spotify_client_id
SPOTIFY_CLIENT_SECRET=your_spotify_client_secret
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgresql://user:password@hostname:port/database
