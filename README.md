# Simple Stratego Server

A simple Stratego (https://en.wikipedia.org/wiki/Stratego) server,

which was designed to:
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

Check the \`protocol.odt\` file. 

## Running the App Locally

If you wish to run this app locally:
1. Make sure you have docker and docker-compose installed on you machine
2. Open project's root directory in the terminal
3. Enter the following command:
   ```CMD
   docker-compose up
   ```
4. Visit localhost:8123, to see the app running
5. You can login on one of two predefined accounts "tester" and "tester2" via password "123"
---
