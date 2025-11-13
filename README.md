# Profile Management Microservice

## API Endpoints

- `GET /health` - Health check
- `POST /users/create` - Create new user
- `POST /users/login` - User authentication
- `GET /users/{user_id}` - Get user by ID
- `GET /users/username/{username}` - Get user by username

## Usage Examples

### POST Data (Create User)

```bash
curl -X POST http://localhost:8000/users/create \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secret123", "timezone": "UTC"}'
```

### POST Data (Login)

```bash
curl -X POST http://localhost:8000/users/login \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "password": "secret123"}'
```

### GET Data (Get user by username)

```bash
curl http://localhost:8000/users/username/john
```

### POST Data (Delete User)

```bash
curl -X POST http://localhost:8000/users/delete \
  -H "Content-Type: application/json" \
  -d '{"username": "john", "user_id": "<INSERT_YOUR_USER_ID_HERE>"}'
```