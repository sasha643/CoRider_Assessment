# User Management API

![License](https://img.shields.io/badge/license-MIT-brightgreen) ![Python Version](https://img.shields.io/badge/python-3.9-blue) ![Flask Version](https://img.shields.io/badge/flask-2.0.3-orange)

RESTful API for managing users, built with Flask and MongoDB. This API supports user creation, retrieval, updating, and deletion, along with JWT authentication and Redis caching for enhanced performance.

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Caching](#caching)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## Features

- **User Management**: Create, read, update, and delete user records.
- **JWT Authentication**: Secure endpoints with JSON Web Tokens.
- **Redis Caching**: Improve performance for frequently accessed data.
- **RESTful Design**: Follow REST principles for easy integration.

## Technologies

- **Python 3.9**: Programming language
- **Flask**: Web framework for building the API
- **MongoDB**: NoSQL database for data storage
- **Redis**: In-memory data structure store used for caching
- **Docker**: Containerization for easy deployment

## Installation

To set up the project locally, follow these steps:

1. **Clone the repository**:

   ```bash
   git clone https://github.com/yourusername/user-management-api.git
   cd user-management-api
