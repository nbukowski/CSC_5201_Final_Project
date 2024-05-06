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
- **Step 1:** Clone repository in WSL ( WSL installation: https://learn.microsoft.com/en-us/windows/wsl/install) 
- **Step 2:** Download Docker Desktop ( Docker Desktop installation: https://www.docker.com/products/docker-desktop/) 
- **Step 3:** run ```docker-compose up```
      - The ```docker-compose.yml``` file will build three image containers
          - mysql
          - prom/prometheus
          - final_project-python
---
## Use case
Once each container is up and running you can go to your Chrome search bar and type ```localhost:5000/login```.

This will lead you to a login page. 
Currently, there are three users included for demo purposes, additional ones can only be added manually by going to ```/app/populate.db.py``` and adding a user in function ```populate_user_table()```. 
For demo purposes, you can use any of the three default users by using user<number> as username, and password<number> as password. User 1 has already books added to their catalog.
The user can go between two pages, a public catalog that includes 20 books for the user to select and add to their own library, as well as their personal library of their current books where they can select and drop any book of their choice. 

To see current metrics go to your Chrome search bar and type ```localhost:9090/graph```. This will open up the monitoring page which uses Prometheus. To see latency response times you will need to create a new panel and in the Expression engine type in ``` rate(request_latency_ms_sum{endpoint=~"/my_catalog"}[1d])```, change the endpoint to any of the available services to monitor their latency and execute. Ensure you are on the graph tab and not table. To check that it's working you can spam the refresh button a few times and see how the response is. 
