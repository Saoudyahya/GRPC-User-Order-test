# gRPC Microservices Example

A complete example of two microservices communicating via gRPC:

- **User Service** (Port 50051): Manages user CRUD operations
- **Order Service** (Port 50052): Manages orders and communicates with User Service

## Architecture

```
Client
  ├── calls User Service (localhost:50051)
  └── calls Order Service (localhost:50052)
              └── internally calls User Service for validation
```

The Order Service demonstrates inter-service communication by calling the User Service to validate users before creating orders.

## Prerequisites

- **Python 3.7+** (tested with Python 3.13)
- **pip** (Python package manager)

## Installation & Setup

### 1. Clone/Download the Project

```bash
# Create project directory
mkdir grpc-microservices
cd grpc-microservices

# Copy all the .proto and .py files from the examples
```

### 2. Install Dependencies

```bash
# Install gRPC and tools
pip install grpcio grpcio-tools

# Or if you have multiple Python versions:
python -m pip install grpcio grpcio-tools
```

### 3. Project Structure

Ensure your project has this structure:

```
grpc-microservices/
├── user_service.proto           # User service interface definition
├── order_service.proto          # Order service interface definition
├── user_service.py              # User service implementation
├── order_service.py             # Order service implementation
├── client.py                    # Test client
├── user_service_pb2.py          # Generated (after step 4)
├── user_service_pb2_grpc.py     # Generated (after step 4)
├── order_service_pb2.py         # Generated (after step 4)
├── order_service_pb2_grpc.py    # Generated (after step 4)
└── README.md                    # This file
```

### 4. Generate gRPC Code

**Important**: You must generate the Python gRPC code from the `.proto` files before running the services.

```bash
# Generate code for User Service
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. user_service.proto

# Generate code for Order Service
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. order_service.proto
```

This creates the `*_pb2.py` and `*_pb2_grpc.py` files that contain the generated Python classes.

## Running the Services

### Step 1: Start User Service

```bash
# Terminal 1
python user_service.py
```

You should see:
```
INFO:__main__:User Service starting on [::]:50051
```

### Step 2: Start Order Service

```bash
# Terminal 2 (new terminal window)
python order_service.py
```

You should see:
```
INFO:__main__:Order Service starting on [::]:50052
INFO:__main__:Connecting to User Service at localhost:50051
```

### Step 3: Test the Services

```bash
# Terminal 3 (new terminal window)
python client.py
```

## API Documentation

### User Service (Port 50051)

#### GetUser
- **Input**: `user_id` (integer)
- **Output**: User object with id, name, email, phone, created_at
- **Example**:
```python
request = GetUserRequest(user_id=1)
response = user_stub.GetUser(request)
```

#### CreateUser
- **Input**: `name`, `email`, `phone` (strings)
- **Output**: Created user object
- **Example**:
```python
request = CreateUserRequest(
    name="John Doe", 
    email="john@example.com", 
    phone="+1234567890"
)
response = user_stub.CreateUser(request)
```

#### GetMultipleUsers
- **Input**: `user_ids` (list of integers)
- **Output**: List of user objects
- **Example**:
```python
request = GetMultipleUsersRequest(user_ids=[1, 2, 3])
response = user_stub.GetMultipleUsers(request)
```

### Order Service (Port 50052)

#### CreateOrder
- **Input**: `user_id` (integer), `items` (list of OrderItem objects)
- **Output**: Order object with user details
- **Validation**: Checks if user exists via User Service
- **Example**:
```python
items = [OrderItem(product_name="Laptop", quantity=1, price=999.99)]
request = CreateOrderRequest(user_id=1, items=items)
response = order_stub.CreateOrder(request)
```

#### GetOrder
- **Input**: `order_id` (integer)
- **Output**: Order object with user details
- **Example**:
```python
request = GetOrderRequest(order_id=1)
response = order_stub.GetOrder(request)
```

#### GetUserOrders
- **Input**: `user_id` (integer)
- **Output**: List of orders for the user
- **Example**:
```python
request = GetUserOrdersRequest(user_id=1)
response = order_stub.GetUserOrders(request)
```

## Testing Examples

### Manual Testing with Python

Create a simple test script:

```python
import grpc
import user_service_pb2
import user_service_pb2_grpc

# Test User Service
with grpc.insecure_channel('localhost:50051') as channel:
    stub = user_service_pb2_grpc.UserServiceStub(channel)
    
    # Get existing user
    request = user_service_pb2.GetUserRequest(user_id=1)
    response = stub.GetUser(request)
    print(f"User: {response.user.name}")
    
    # Create new user
    request = user_service_pb2.CreateUserRequest(
        name="Test User",
        email="test@example.com",
        phone="+1234567890"
    )
    response = stub.CreateUser(request)
    print(f"Created user with ID: {response.user.id}")
```

### Testing with grpcurl (Optional)

If you have grpcurl installed:

```bash
# Install grpcurl (optional)
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# Test User Service
grpcurl -plaintext -d '{"user_id": 1}' localhost:50051 user.UserService/GetUser

# Test Order Service
grpcurl -plaintext -d '{"user_id": 1, "items": [{"product_name": "Laptop", "quantity": 1, "price": 999.99}]}' localhost:50052 order.OrderService/CreateOrder
```

## Expected Output

When you run the client, you should see output like:

```
Testing Microservices Communication
==================================================
=== Testing User Service ===

1. Getting existing user (ID: 1)
Success: True
Message: User found successfully
User: John Doe (john@example.com)

2. Creating new user
Success: True
Message: User created successfully
Created User ID: 3

=== Testing Order Service ===

1. Creating order for user ID: 1
Success: True
Message: Order created successfully
Order ID: 1
Total: $1050.99
Customer: John Doe (john@example.com)

2. Getting order ID: 1
Success: True
Message: Order found successfully
Order Status: pending
Items: 2
  - Laptop: 1 x $999.99
  - Mouse: 2 x $25.5
```

## How Inter-Service Communication Works

1. **Client calls Order Service** to create an order
2. **Order Service validates** the user exists by calling User Service
3. **User Service responds** with user details or error
4. **Order Service creates** the order only if user is valid
5. **Order Service returns** the order with complete user information

This demonstrates a common microservices pattern where services need to communicate with each other.

## Troubleshooting

### Common Issues

#### "ModuleNotFoundError: No module named 'grpc'"
```bash
# Install gRPC
pip install grpcio grpcio-tools

# If you have multiple Python versions, be specific:
C:/path/to/your/python.exe -m pip install grpcio grpcio-tools
```

#### "ModuleNotFoundError: No module named 'user_service_pb2'"
```bash
# Generate the proto files first
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. user_service.proto
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. order_service.proto
```

#### "Connection refused" when testing
- Make sure User Service is running on port 50051
- Make sure Order Service is running on port 50052
- Check if ports are already in use: `netstat -an | grep 5005`

#### "User Service not responding"
- Start User Service before Order Service
- Check User Service logs for errors
- Verify User Service is listening on the correct port

### Stopping the Services

To stop the services:
- Press `Ctrl+C` in each terminal window
- Or close the terminal windows

### Port Conflicts

If ports 50051 or 50052 are already in use:

1. **Find what's using the port:**
```bash
# Windows
netstat -ano | grep 50051

# Linux/Mac
lsof -i :50051
```

2. **Change the port in the code:**
```python
# In user_service.py, change:
listen_addr = '[::]:50052'  # Use different port

# In order_service.py, update the connection:
self.user_service_host = 'localhost:50052'  # Match new port
```

## Development Tips

### Adding New Services

1. Create a new `.proto` file
2. Generate Python code: `python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. your_service.proto`
3. Implement your service class
4. Add client calls in other services if needed

### Debugging

Add more logging to see what's happening:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Performance

For production use:
- Use connection pooling
- Add retry logic
- Implement health checks
- Use TLS for security
- Add monitoring and metrics

## Next Steps

- Add database integration (replace in-memory storage)
- Implement authentication and authorization
- Add error handling and retry logic
- Set up monitoring and logging
- Deploy to production environment

## Resources

- [gRPC Python Documentation](https://grpc.io/docs/languages/python/)
- [Protocol Buffers Documentation](https://developers.google.com/protocol-buffers)
- [gRPC Best Practices](https://grpc.io/docs/guides/best-practices/)
