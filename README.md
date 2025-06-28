gRPC Microservices Example
This example demonstrates two microservices communicating via gRPC:

User Service (Port 50051): Manages user data
Order Service (Port 50052): Manages orders and calls User Service for user details

Architecture Overview
Client
  ├── calls User Service (port 50051)
  └── calls Order Service (port 50052)
              └── internally calls User Service
Quick Start with Docker
1. Setup
bash# Clone or create the project directory
mkdir grpc-microservices && cd grpc-microservices

# Create all the files from the artifacts above
# Make sure you have all .proto files, .py files, Dockerfile, etc.

# Install dependencies locally (for development)
pip install grpcio grpcio-tools
2. Generate Proto Files
bash# Generate Python gRPC code from proto definitions
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. user_service.proto
python -m grpc_tools.protoc --proto_path=. --python_out=. --grpc_python_out=. order_service.proto

# Or use the Makefile
make proto
3. Run with Docker
bash# Build and start all services
docker-compose up --build

# Or step by step
make build
make up

# View logs
make logs

# Test the services
make test
4. Run Locally (Development)
bash# Terminal 1: Start User Service
python user_service.py

# Terminal 2: Start Order Service  
python order_service.py

# Terminal 3: Test the services
python client.py
API Endpoints
User Service (localhost:50051)

GetUser(user_id) - Get user by ID
CreateUser(name, email, phone) - Create new user
GetMultipleUsers(user_ids) - Get multiple users

Order Service (localhost:50052)

CreateOrder(user_id, items) - Create order (validates user exists)
GetOrder(order_id) - Get order with user details
GetUserOrders(user_id) - Get all orders for a user

Testing Examples
Manual Testing with grpcurl
bash# Install grpcurl
go install github.com/fullstorydev/grpcurl/cmd/grpcurl@latest

# Test User Service
grpcurl -plaintext -d '{"user_id": 1}' localhost:50051 user.UserService/GetUser

# Test Order Service
grpcurl -plaintext -d '{"user_id": 1, "items": [{"product_name": "Laptop", "quantity": 1, "price": 999.99}]}' localhost:50052 order.OrderService/CreateOrder
Python Client Testing
The client.py file demonstrates:

Creating and retrieving users
Creating orders that validate user existence
Inter-service communication (Order Service → User Service)
Error handling for non-existent users

Key Features Demonstrated
Inter-Service Communication
The Order Service calls the User Service to:

Validate user existence before creating orders
Fetch user details for order responses
Handle service unavailability gracefully

Error Handling

Proper gRPC error responses
Service validation (user must exist to create order)
Network error handling between services

Microservices Patterns

Service Discovery: Services communicate via Docker network names
Data Consistency: Orders validate users exist
Separation of Concerns: Each service manages its own domain
Health Checks: Docker health checks for service readiness

Production Considerations
Security
python# Use TLS in production
credentials = grpc.ssl_channel_credentials()
channel = grpc.secure_channel('service:443', credentials)
Service Discovery
python# Use service discovery instead of hardcoded addresses
# Examples: Consul, etcd, Kubernetes DNS
import consul
consul_client = consul.Consul()
services = consul_client.health.service('user-service')[1]
Database Integration
python# Replace in-memory storage with real databases
import psycopg2
import redis

# PostgreSQL for persistent data
# Redis for caching user lookups
Monitoring & Logging
python# Add metrics and tracing
from prometheus_client import Counter, Histogram
import jaeger_client

# Metrics
request_count = Counter('grpc_requests_total', 'gRPC requests')
request_duration = Histogram('grpc_request_duration_seconds', 'gRPC request duration')
Scaling
Load Balancing
yaml# docker-compose.yml
user-service:
  deploy:
    replicas: 3
  # Add load balancer like HAProxy or nginx
Circuit Breaker
python# Add circuit breaker for service calls
import pybreaker

db = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)

@db
def get_user_from_service(user_id):
    # Your gRPC call here
    pass
This example provides a solid foundation for building production gRPC microservices with proper error handling, service communication, and scalability patterns.
