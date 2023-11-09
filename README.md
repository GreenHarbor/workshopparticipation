# Workshop Participation Service

## Introduction

This repository hosts the Workshop Participation Service, a Flask application designed to facilitate the registration and withdrawal processes for workshops. It integrates with RabbitMQ to ensure that once a request is handled, a message is sent to the notification service for email dispatch and to the logging service for record-keeping.

## Features

- **Workshop Registration**: Allows users to register for a workshop.
- **Workshop Withdrawal**: Enables users to withdraw from a workshop.
- **RabbitMQ Integration**: Communicates with RabbitMQ to send messages to other services.
- **Email Notifications**: Works with a notification service to send emails upon registration or withdrawal.
- **Logging**: Interacts with a logging service to log user actions.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Prerequisites

- Python 3.6+
- Flask
- Access to a RabbitMQ instance

### Installation

1. Clone the repository:
   ```
   git clone https://github.com/GreenHarbor/workshopparticipation.git
   ```
2. Navigate to the project directory:
   ```
   cd workshopparticipation
   ```
3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

### Configuration

- Configure your environment variables to include the necessary RabbitMQ settings.
- Ensure that the RabbitMQ instance is running and accessible.

### Running the Application

1. Start the Flask application:
   ```
   flask run
   ```
2. The application will now be running and can handle workshop registration and withdrawal requests.

## Usage

- **Register for a Workshop**: Send a POST request to `/register` with the user and workshop details.
- **Withdraw from a Workshop**: Send a POST request to `/withdraw` with the user and workshop details.
