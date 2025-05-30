# TopTunes Project

Welcome to the TopTunes Project! This project is a Django-based web application that integrates with various APIs to provide a rich user experience. Below you'll find detailed information about the project, how to set it up, and how to contribute.

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Project Overview

The TopTunes Project is a web application built with Django. It integrates with the Spotify API to fetch artist data, including top tracks and albums. The application also allows users to vote for their favorite artists and view the results.

## Features

- Fetch artist data from Spotify
- Display artist details, including top tracks and albums
- Allow users to vote for their favorite artists
- Display voting results
- Responsive design with a clean UI

## Installation

To get started with the TopTunes Project, follow these steps:

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/TopTunes.git
    cd TopTunes
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
```

## Usage

Once the development server is running, you can access the application at `http://127.0.0.1:8000/`. Use the admin interface at `http://127.0.0.1:8000/admin/` to manage the application data.

## Contributing

We welcome contributions to the TopTunes Project! To contribute, follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes and commit them with a descriptive message.
4. Push your changes to your fork.
5. Create a pull request to the main repository.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more details.

## Acknowledgements

- [Django](https://www.djangoproject.com/)
- [Spotify API](https://developer.spotify.com/documentation/web-api/)
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/)
- [Python Decouple](https://github.com/henriquebastos/python-decouple)
- [Gspread](https://github.com/burnash/gspread)
- [More Itertools](https://github.com/more-itertools/more-itertools)
- [OAuth2Client](https://github.com/google/oauth2client)
- [NumPy](https://numpy.org/)
- [Requests](https://docs.python-requests.org/en/latest/)
- [Scikit-Learn](https://scikit-learn.org/stable/)
- [Spotipy](https://spotipy.readthedocs.io/en/2.16.1/)
- [PyMySQL](https://github.com/PyMySQL/PyMySQL)
- [Gunicorn](https://gunicorn.org/)
- [Uvicorn](https://www.uvicorn.org/)
- [DJ-Database-URL](https://github.com/jacobian/dj-database-url)
- [Psycopg2](https://www.psycopg.org/)
- [Whitenoise](http://whitenoise.evans.io/en/stable/)
