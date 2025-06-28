import grpc
import time
import logging
from concurrent import futures
import UserService_pb2
import UserService_pb2_grpc

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class UserServicer(UserService_pb2_grpc.UserServiceServicer):
    """User Service implementation"""
    
    def __init__(self):
        # In-memory user database (in production, use a real database)
        self.users = {
            1: {
                'id': 1,
                'name': 'John Doe',
                'email': 'john@example.com',
                'phone': '+1234567890',
                'created_at': int(time.time())
            },
            2: {
                'id': 2,
                'name': 'Jane Smith',
                'email': 'jane@example.com',
                'phone': '+1987654321',
                'created_at': int(time.time())
            }
        }
        self.next_user_id = 3
    
    def GetUser(self, request, context):
        """Get a single user by ID"""
        logger.info(f"Getting user with ID: {request.user_id}")
        
        user_data = self.users.get(request.user_id)
        
        if user_data:
            user = UserService_pb2.User(
                id=user_data['id'],
                name=user_data['name'],
                email=user_data['email'],
                phone=user_data['phone'],
                created_at=user_data['created_at']
            )
            
            return UserService_pb2.GetUserResponse(
                success=True,
                message="User found successfully",
                user=user
            )
        else:
            return UserService_pb2.GetUserResponse(
                success=False,
                message=f"User with ID {request.user_id} not found"
            )
    
    def CreateUser(self, request, context):
        """Create a new user"""
        logger.info(f"Creating user: {request.name}")
        
        # Validate input
        if not request.name or not request.email:
            return UserService_pb2.CreateUserResponse(
                success=False,
                message="Name and email are required"
            )
        
        # Check if email already exists
        for user in self.users.values():
            if user['email'] == request.email:
                return UserService_pb2.CreateUserResponse(
                    success=False,
                    message="Email already exists"
                )
        
        # Create new user
        user_id = self.next_user_id
        self.next_user_id += 1
        
        user_data = {
            'id': user_id,
            'name': request.name,
            'email': request.email,
            'phone': request.phone,
            'created_at': int(time.time())
        }
        
        self.users[user_id] = user_data
        
        user = UserService_pb2.User(
            id=user_data['id'],
            name=user_data['name'],
            email=user_data['email'],
            phone=user_data['phone'],
            created_at=user_data['created_at']
        )
        
        return UserService_pb2.CreateUserResponse(
            success=True,
            message="User created successfully",
            user=user
        )
    
    def GetMultipleUsers(self, request, context):
        """Get multiple users by their IDs"""
        logger.info(f"Getting multiple users: {list(request.user_ids)}")
        
        users = []
        not_found_ids = []
        
        for user_id in request.user_ids:
            user_data = self.users.get(user_id)
            if user_data:
                user = UserService_pb2.User(
                    id=user_data['id'],
                    name=user_data['name'],
                    email=user_data['email'],
                    phone=user_data['phone'],
                    created_at=user_data['created_at']
                )
                users.append(user)
            else:
                not_found_ids.append(user_id)
        
        if not_found_ids:
            message = f"Users found: {len(users)}, Not found IDs: {not_found_ids}"
        else:
            message = f"All {len(users)} users found successfully"
        
        return UserService_pb2.GetMultipleUsersResponse(
            success=True,
            message=message,
            users=users
        )

def serve():
    """Start the User Service server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add the servicer to the server
    UserService_pb2_grpc.add_UserServiceServicer_to_server(UserServicer(), server)
    
    # Listen on port 50051
    listen_addr = '[::]:50051'
    server.add_insecure_port(listen_addr)
    
    logger.info(f"User Service starting on {listen_addr}")
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down User Service...")
        server.stop(grace=5)

if __name__ == '__main__':
    serve()