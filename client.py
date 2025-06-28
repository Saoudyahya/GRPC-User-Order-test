import grpc
import UserService_pb2
import UserService_pb2_grpc
import order_service_pb2
import order_service_pb2_grpc

def test_user_service():
    """Test User Service operations"""
    print("=== Testing User Service ===")
    
    # Connect to User Service
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = UserService_pb2_grpc.UserServiceStub(channel)
        
        # Test 1: Get existing user
        print("\n1. Getting existing user (ID: 1)")
        try:
            request = UserService_pb2.GetUserRequest(user_id=1)
            response = stub.GetUser(request)
            print(f"Success: {response.success}")
            print(f"Message: {response.message}")
            if response.success:
                user = response.user
                print(f"User: {user.name} ({user.email})")
        except grpc.RpcError as e:
            print(f"Error: {e}")
        
        # Test 2: Create new user
        print("\n2. Creating new user")
        try:
            request = UserService_pb2.CreateUserRequest(
                name="Alice Johnson",
                email="alice@example.com",
                phone="+1555123456"
            )
            response = stub.CreateUser(request)
            print(f"Success: {response.success}")
            print(f"Message: {response.message}")
            if response.success:
                user = response.user
                print(f"Created User ID: {user.id}")
                new_user_id = user.id
        except grpc.RpcError as e:
            print(f"Error: {e}")
            new_user_id = None
        
        # Test 3: Get multiple users
        print("\n3. Getting multiple users")
        try:
            user_ids = [1, 2]
            if new_user_id:
                user_ids.append(new_user_id)
            
            request = UserService_pb2.GetMultipleUsersRequest(user_ids=user_ids)
            response = stub.GetMultipleUsers(request)
            print(f"Success: {response.success}")
            print(f"Message: {response.message}")
            print(f"Found {len(response.users)} users")
        except grpc.RpcError as e:
            print(f"Error: {e}")

def test_order_service():
    """Test Order Service operations"""
    print("\n\n=== Testing Order Service ===")
    
    # Connect to Order Service
    with grpc.insecure_channel('localhost:50052') as channel:
        stub = order_service_pb2_grpc.OrderServiceStub(channel)
        
        # Test 1: Create order for existing user
        print("\n1. Creating order for user ID: 1")
        try:
            items = [
                order_service_pb2.OrderItem(
                    product_name="Laptop",
                    quantity=1,
                    price=999.99
                ),
                order_service_pb2.OrderItem(
                    product_name="Mouse",
                    quantity=2,
                    price=25.50
                )
            ]
            
            request = order_service_pb2.CreateOrderRequest(
                user_id=1,
                items=items
            )
            response = stub.CreateOrder(request)
            print(f"Success: {response.success}")
            print(f"Message: {response.message}")
            if response.success:
                order = response.order.order
                user = response.order.user
                print(f"Order ID: {order.id}")
                print(f"Total: ${order.total_amount:.2f}")
                print(f"Customer: {user.name} ({user.email})")
                created_order_id = order.id
        except grpc.RpcError as e:
            print(f"Error: {e}")
            created_order_id = None
        
        # Test 2: Get specific order
        if created_order_id:
            print(f"\n2. Getting order ID: {created_order_id}")
            try:
                request = order_service_pb2.GetOrderRequest(order_id=created_order_id)
                response = stub.GetOrder(request)
                print(f"Success: {response.success}")
                print(f"Message: {response.message}")
                if response.success:
                    order = response.order.order
                    user = response.order.user
                    print(f"Order Status: {order.status}")
                    print(f"Items: {len(order.items)}")
                    for item in order.items:
                        print(f"  - {item.product_name}: {item.quantity} x ${item.price}")
            except grpc.RpcError as e:
                print(f"Error: {e}")
        
        # Test 3: Get user orders
        print("\n3. Getting all orders for user ID: 1")
        try:
            request = order_service_pb2.GetUserOrdersRequest(user_id=1)
            response = stub.GetUserOrders(request)
            print(f"Success: {response.success}")
            print(f"Message: {response.message}")
            print(f"Total orders: {len(response.orders)}")
            
            for order_with_user in response.orders:
                order = order_with_user.order
                print(f"  Order {order.id}: ${order.total_amount:.2f} - {order.status}")
        except grpc.RpcError as e:
            print(f"Error: {e}")
        
        # Test 4: Try to create order for non-existent user
        print("\n4. Creating order for non-existent user (ID: 999)")
        try:
            items = [
                order_service_pb2.OrderItem(
                    product_name="Test Product",
                    quantity=1,
                    price=10.00
                )
            ]
            
            request = order_service_pb2.CreateOrderRequest(
                user_id=999,
                items=items
            )
            response = stub.CreateOrder(request)
            print(f"Success: {response.success}")
            print(f"Message: {response.message}")
        except grpc.RpcError as e:
            print(f"Error: {e}")

def main():
    """Main function to run all tests"""
    print("Testing Microservices Communication")
    print("=" * 50)
    
    try:
        test_user_service()
        test_order_service()
        
        print("\n" + "=" * 50)
        print("All tests completed!")
        
    except Exception as e:
        print(f"Test failed: {e}")

if __name__ == '__main__':
    main()