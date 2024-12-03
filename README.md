# Pokemon Tournament

## Technical Stack

- **Frontend**: Vues.js
- **Backend**: Python Flask
- **Database**: MongoDB
- **Containerization**: Docker, Docker Compose

## Quickstart
### Prerequisites
- Docker
- Docker Compose

### How to Spin Up the Environment

1. Clone the repository: 

```
git clone <repo-link>
cd pokemon-tournament
```

2. Start up containers: 

```
docker-compose up --build
```

3. Access the application: 

- **Frontend**:  Accessible at `http://localhost:3001`.
- **Backend**: Accessible at `http://localhost:6035`.

## Note! This application runs best on chrome

## Login Information:
#### User role can play game, view public logs and create new Pokemon. 
- **Username**: operator
- **Password**: password2

#### Admin role has enhanced capabilities like viewing internal battle logs.
- **Username**: admin
- **Password**: password1


## Available Backend Routes
1. `GET /pokemon` Retrieve all available pokemon and details.
2. `GET /battle/<battle_id>` Retrieve details for the requested battle.
3. `GET /tournament/<tournament_id>` Retrieve details for the requested tournament.
4. `GET /adminLogs` Retrieve list of battle logs, meant for the admin.
5. `POST /pokemon` Send with Json body including pokemon details. Pokemon created and stored in database. 
6. `POST /battle` Send with Json body including battle details. Battle is executed and results stored in database.
7. `POST /tournament` Send with Json body including tournament details. Tournament created and stored in database.
8. `POST /login` Send with Json body including username and password. User authentication verified.

## Clean up
To stop the containers and clean up resources:

```
docker-compose down
```
