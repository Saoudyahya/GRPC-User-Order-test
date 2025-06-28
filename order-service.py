import grpc
import time
import logging
from concurrent import futures
import order_service_pb2
import order_service_pb2_grpc
import UserService_pb2
import UserService_pb2_grpc


# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderServicer(order_service_pb2_grpc.OrderServiceServicer):
    """Order Service implementation"""
    
    def __init__(self, user_service_host='localhost:50051'):
        # In-memory order database (in production, use a real database)
        self.orders = {}
        self.next_order_id = 1
        self.user_service_host = user_service_host
        
        # Create gRPC channel to User Service
        self.user_channel = grpc.insecure_channel(user_service_host)
        self.user_stub = UserService_pb2_grpc.UserServiceStub(self.user_channel)
    
    def _get_user_from_service(self, user_id):
        """Helper method to get user from User Service"""
        try:
            request = UserService_pb2.GetUserRequest(user_id=user_id)
            response = self.user_stub.GetUser(request)
            
            if response.success:
                return response.user
            else:
                logger.warning(f"User not found: {response.message}")
                return None
                
        except grpc.RpcError as e:
            logger.error(f"Failed to get user from User Service: {e}")
            return None
    
    def CreateOrder(self, request, context):
        """Create a new order"""
        logger.info(f"Creating order for user ID: {request.user_id}")
        
        # Validate that user exists by calling User Service
        user = self._get_user_from_service(request.user_id)
        if not user:
            return order_service_pb2.CreateOrderResponse(
                success=False,
                message=f"User with ID {request.user_id} not found"
            )
        
        # Validate order items
        if not request.items:
            return order_service_pb2.CreateOrderResponse(
                success=False,
                message="Order must contain at least one item"
            )
        
        # Calculate total amount
        total_amount = sum(item.price * item.quantity for item in request.items)
        
        # Create order
        order_id = self.next_order_id
        self.next_order_id += 1
        
        order_data = {
            'id': order_id,
            'user_id': request.user_id,
            'items': [
                {
                    'product_name': item.product_name,
                    'quantity': item.quantity,
                    'price': item.price
                }
                for item in request.items
            ],
            'total_amount': total_amount,
            'status': 'pending',
            'created_at': int(time.time())
        }
        
        self.orders[order_id] = order_data
        
        # Create response with order and user info
        order = order_service_pb2.Order(
            id=order_data['id'],
            user_id=order_data['user_id'],
            items=[
                order_service_pb2.OrderItem(
                    product_name=item['product_name'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                for item in order_data['items']
            ],
            total_amount=order_data['total_amount'],
            status=order_data['status'],
            created_at=order_data['created_at']
        )
        
        order_with_user = order_service_pb2.OrderWithUser(
            order=order,
            user=user
        )
        
        return order_service_pb2.CreateOrderResponse(
            success=True,
            message="Order created successfully",
            order=order_with_user
        )
    
    def GetOrder(self, request, context):
        """Get an order by ID"""
        logger.info(f"Getting order with ID: {request.order_id}")
        
        order_data = self.orders.get(request.order_id)
        
        if not order_data:
            return order_service_pb2.GetOrderResponse(
                success=False,
                message=f"Order with ID {request.order_id} not found"
            )
        
        # Get user info from User Service
        user = self._get_user_from_service(order_data['user_id'])
        if not user:
            return order_service_pb2.GetOrderResponse(
                success=False,
                message=f"User associated with order not found"
            )
        
        # Create order object
        order = order_service_pb2.Order(
            id=order_data['id'],
            user_id=order_data['user_id'],
            items=[
                order_service_pb2.OrderItem(
                    product_name=item['product_name'],
                    quantity=item['quantity'],
                    price=item['price']
                )
                for item in order_data['items']
            ],
            total_amount=order_data['total_amount'],
            status=order_data['status'],
            created_at=order_data['created_at']
        )
        
        order_with_user = order_service_pb2.OrderWithUser(
            order=order,
            user=user
        )
        
        return order_service_pb2.GetOrderResponse(
            success=True,
            message="Order found successfully",
            order=order_with_user
        )
    
    def GetUserOrders(self, request, context):
        """Get all orders for a specific user"""
        logger.info(f"Getting orders for user ID: {request.user_id}")
        
        # Validate that user exists
        user = self._get_user_from_service(request.user_id)
        if not user:
            return order_service_pb2.GetUserOrdersResponse(
                success=False,
                message=f"User with ID {request.user_id} not found"
            )
        
        # Find all orders for this user
        user_orders = []
        for order_data in self.orders.values():
            if order_data['user_id'] == request.user_id:
                order = order_service_pb2.Order(
                    id=order_data['id'],
                    user_id=order_data['user_id'],
                    items=[
                        order_service_pb2.OrderItem(
                            product_name=item['product_name'],
                            quantity=item['quantity'],
                            price=item['price']
                        )
                        for item in order_data['items']
                    ],
                    total_amount=order_data['total_amount'],
                    status=order_data['status'],
                    created_at=order_data['created_at']
                )
                
                order_with_user = order_service_pb2.OrderWithUser(
                    order=order,
                    user=user
                )
                user_orders.append(order_with_user)
        
        return order_service_pb2.GetUserOrdersResponse(
            success=True,
            message=f"Found {len(user_orders)} orders for user",
            orders=user_orders
        )

def serve():
    """Start the Order Service server"""
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    
    # Add the servicer to the server
    order_service_pb2_grpc.add_OrderServiceServicer_to_server(
        OrderServicer(), server
    )
    
    # Listen on port 50052
    listen_addr = '[::]:50052'
    server.add_insecure_port(listen_addr)
    
    logger.info(f"Order Service starting on {listen_addr}")
    logger.info("Connecting to User Service at localhost:50051")
    
    server.start()
    
    try:
        server.wait_for_termination()
    except KeyboardInterrupt:
        logger.info("Shutting down Order Service...")
        server.stop(grace=5)

if __name__ == '__main__':
    serve()