[![Review Assignment Due Date](https://classroom.github.com/assets/deadline-readme-button-22041afd0340ce965d47ae6ef1cefeee28c7c493a6346c4f15d667ab976d596c.svg)](https://classroom.github.com/a/QUdQy4ix)
# CS3219 Project (PeerPrep) - AY2526S1
## Group: G12

## Services:

### Frontend

Folder: `PeerPrep`

Contains the project files for our frontend service built with Vite

#### Development:

Copy the `.env.template` to `.env` and update variables.

```
npm install
npm run dev
```

### API Gateway

Folder: `api-gateway`

#### Functionality:

 * Routes API traffic from users to the corresponding internal services
 * Handles the checking of access token cookies to enforce authentication and authorisation

#### Development:

Copy the `.env.template` to `.env` and update variables.

```
uv sync
uv run fastapi dev main.py
```

### Collaboration Service

Folder: `collaboration-svc`

#### Functionality:

  * Facilitate room/session creation
  * Coordinating users

#### Development:

Copy the `.env.template` to `.env` and update variables.

```
uv sync
uv run fastapi dev routes.py
```

### Expire Observer Service

Folder: `expire-observer-svc`

#### Functionality:

  * Handles TTL Matching Expire event from redis

#### Development:

Copy the `.env.template` to `.env` and update variables.

```
uv sync
uv run fastapi dev main.py
```

### Matching Service

Folder: `matching-svc`

#### Functionality:

  * Handles user matching requests
  * Corrdinating user acknowledgement for requests

#### Development:

Copy the `.env.template` to `.env` and update variables.

```
uv sync
uv run fastapi dev routes.py
```

### Question History Service

Folder: `qns-hist-svc`

#### Functionality:

  * Handles retrieval of users past attempts
  * Generate AI Summary Review on users past attempts

#### Development:

Copy the `.env.template` to `.env` and update variables.

```
uv sync
uv run fastapi dev routes.py
```

### Question Service

Folder: `qns-svc`

#### Functionality:

  * Handles retrieval of questions for users
  * Create, Update and Deletion of Question for admins

#### Development:

Copy the `.env.template` to `.env` and update variables.

```
uv sync
uv run fastapi dev routes.py
```

#### Support:

Question Service has a supplimentary files for importing questions located under `support\qns-svc-import`

### Signaling Service

Folder: `signaling-svc`

#### Functionality:

  * Coordinate WebRTC traffic between users

#### Development:

```
npm install
node server.js
```

### User Service

Folder: `user-svc`

#### Functionality:

  * Handles authentication of users
  * Retrieve profile information for users

#### Development:

Copy the `.env.template` to `.env` and update variables.

```
uv sync
uv run fastapi dev main.py
```

### Note: 
- You are required to develop individual microservices within separate folders within this repository.
- The teaching team should be given access to the repositories as we may require viewing the history of the repository in case of any disputes or disagreements. 

### Acknowledgements:

* `qns-svc/tests/conftest.py` and `qns-hist-svc/tests/conftest.py`:

  * Credits to `gxpd-jjh`. Re-used from: https://github.com/tortoise/tortoise-orm/issues/1110#issuecomment-1881967845
* Gavin has adapted `server.js` inside `signaling-svc` from `node_modules/y-webrtc/bin/server.js` and modified it to support audio stream
* Gavin has used ChatGPT to generate debugging logs to VoiceConnectionManager and signaling server
