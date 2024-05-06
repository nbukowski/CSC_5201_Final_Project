# Library Catalog Application 
----

## About this repository
----
This repository contains the necessary files to build a library catalog application. Contains three specific services:
- **Flask Application:** Application that allows users to login, view their personal library catalog or public, and logout. 
- **MySQL Database:** Database consisting of three tables: users, books, and user book link.
    - **Users table**: Includes the user's name, username, and password.
    - **Book table:** Includes book title, author, ISBN, and cover image location for displaying purposes in the application.
    - **User book link table:** Includes user ID, and book ID and intended to query which books users currently have saved in their personal library or have added/dropped to and from their personal library.
- **Monitoring Service:** Using Prometheus to record and display each endpoint's latency response. 

----
## Installation instructions 
- **Step 1:** Clone the repository in WSL and ensure you have Docker Desktop connected and accessible to WSL. 
- **Step 2:** run ```docker-compose up``` - this will create the necessary containers and allow users to view each service via Docker Desktop and/or accessing localhost:5000 for actual library catalog application and/or localhost:9090 to access monitoring metrics recording each page/endpoints latency for viewing/monitoring purposes.
