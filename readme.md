Getting Started
===============

The easiest way to test out BudgetApp is to use Docker Compose to setup an environment for you. [Installation instructions.](https://docs.docker.com/compose/install/)

- `git clone https://github.com/DanWright91/budgetapp.git`
- `cd budgetapp`
- `docker-compose up`
- Run `docker ps` to find the container id of the budgetapp-django container
- `docker exec -it <container-id> bash`
- Inside the container:
  - `cd /code/budgetapp`
  - `python manage.py makemigrations && python manage.py migrate`
- BudgetApp will be available at localhost on port 80
