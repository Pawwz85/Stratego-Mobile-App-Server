# Simple Stratego Server

A simple Stratego (https://en.wikipedia.org/wiki/Stratego) server that I wrote as a part of my mobile app for passing a college class.

After passing the class, I decided not to dump the project but to overhaul it. The new version of this server was designed to:
- be scalable horizontally
- allow serving both websocket and browser clients (browser support still in development)
- have sophisticated  test environment for business logic

## Infrastructure

According to point 1 on our list, our server needs to be scalable. This can be a bit tricky since we are also going to support websocket clients. To achieve these goals, the application was designed as microservices:
1. Microservice that processes and manages all rooms/chats and business logic
2. Microservice that accepts connections and serves as a proxy between the user and nodes that manage business logic

To synchronize these two microservices, the application uses a Redis Queue and Redis publish/subscribe mechanism. User authentication is backed by a PostgreSQL database.

Thanks to this design, one could easily place this app behind a load balancer.

## Websocket Protocol

Check the \`protocol.odt\` file. Note: The registration mechanism has not yet been implemented.

## Running the App Locally

If you wish to run this app locally:
1. Run a local Redis server or get the URL to a remote Redis server.
2. Create and configure a PostgreSQL server. You can then create the necessary \`t_users\` table with the following SQL script:

   ```sql
   CREATE TABLE IF NOT EXISTS public.t_users
   (
       username text COLLATE pg_catalog."default" NOT NULL,
       password text COLLATE pg_catalog."default" NOT NULL,
       id integer NOT NULL,
       CONSTRAINT t_users_pkey PRIMARY KEY (id),
       CONSTRAINT t_users_username_key UNIQUE (username)
   )
   ```

3. Configure your secret configurations. The application expects to find a file named \`secret_config.properties\` in a \`Config/\` folder. This file must be written in JSON format.

   ```json
   {
     "redis_url": "redis://127.0.0.1:6379",
     "backend_api_channel_name": "request_channel",
     "request_queue_name": "request_queue",
     "frontend_api_channel_name": "frontend_channel",
     "db_name": "stratego_app_server",
     "db_host": "localhost",
     "db_user": "YOUR_USERNAME",
     "db_password": "YOUR_PASSWORD",
     "db_port": 5432,
     "secret_key": "YOUR_SECRET_KEY"
   }
   ```

   - **redis_url**: URL for the Redis server, including the protocol \(redis\), IP address, and port number.
   - **backend_api_channel_name**: Name of the backend API channel used that is being read by the business logic microservice.
   - **request_queue_name**: Similar to \`backend_api_channel\` but used only if a single business node should receive a request.
   - **frontend_api_channel_name**: Name of the frontend microservice, where business logic service output events/requests.
   - **db_name**: Name of the database used by the application.
   - **db_host**: Hostname or IP address of the database server.
   - **db_user**: Username for accessing the database.
   - **db_password**: Password for accessing the database.
   - **db_port**: Port number on which the database server is listening \(default for PostgreSQL\).
   - **secret_key**: Secret key used for application security \(e.g., encryption, sessions\).

4. Run \`src/BackendSystem.py\` to start the business logic process.
5. Run \`src/Frontend/Frontend.py\` to start the frontend system.

6. To connect to the server, open in a browser \`localhost:5000/\` to connect to the browser version, or \`localhost:5001/\` for the websocket version.

---
