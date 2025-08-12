import graphene
from graphene_django import DjangoObjectType
from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Customer, Product, Order


# GraphQL Types
class CustomerType(DjangoObjectType):
    """
    Represents a customer in the system.
    """
    class Meta:
        model = Customer
        fields = ("id", "name", "email", "phone", "created_at")


class ProductType(DjangoObjectType):
    """
    Represents a product in the system.
    """
    class Meta:
        model = Product
        fields = ("id", "name", "price", "stock", "created_at")


class OrderType(DjangoObjectType):
    """
    Represents an order in the system.
    """
    class Meta:
        model = Order
        fields = ("id", "customer", "products", "total_amount", "order_date")


# Input Types for Mutations
class CustomerInput(graphene.InputObjectType):
    """
    Represents the input fields for creating or updating a customer.
    """
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()


class ProductInput(graphene.InputObjectType):
    """
    Represents the input fields for creating or updating a product.
    """
    name = graphene.String(required=True)
    price = graphene.Decimal(required=True)
    stock = graphene.Int()


class OrderInput(graphene.InputObjectType):
    """
    Represents the input fields for creating or updating an order.
    """
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)
    order_date = graphene.DateTime()


# Mutation Classes
class CreateCustomer(graphene.Mutation):
    """
    Creates a new customer.
    """
    class Arguments:
        input = CustomerInput(required=True)
    
    customer = graphene.Field(CustomerType)
    message = graphene.String()
    
    def mutate(self, info, input):
        try:
            customer = Customer(
                name=input.name,
                email=input.email,
                phone=input.phone
            )
            customer.full_clean()
            customer.save()
            return CreateCustomer(
                customer=customer, 
                message="Customer created successfully"
            )
        except ValidationError as e:
            raise Exception(f"Validation error: {e.message_dict}")

class BulkCreateCustomers(graphene.Mutation):
    """
    Creates multiple new customers.
    """
    class Arguments:
        input = graphene.List(CustomerInput, required=True)
    
    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)
    
    def mutate(self, info, input):
        customers = []
        errors = []
        
        with transaction.atomic():
            for customer_data in input:
                try:
                    customer = Customer(
                        name=customer_data.name,
                        email=customer_data.email,
                        phone=customer_data.phone
                    )
                    customer.full_clean()
                    customer.save()
                    customers.append(customer)
                except Exception as e:
                    errors.append(f"Error creating customer {customer_data.name}: {str(e)}")
        
        return BulkCreateCustomers(customers=customers, errors=errors)

class CreateProduct(graphene.Mutation):
    """
    Create a new product.
    """
    class Arguments:
        input = ProductInput(required=True)
    
    product = graphene.Field(ProductType)
    
    def mutate(self, info, input):
        try:
            if input.price <= 0:
                raise ValidationError("Price must be positive")
            
            product = Product(
                name=input.name,
                price=input.price,
                stock=input.stock or 0
            )
            product.full_clean()
            product.save()
            return CreateProduct(product=product)
        except ValidationError as e:
            raise Exception(f"Validation error: {str(e)}")

class CreateOrder(graphene.Mutation):
    """
    Create an order.
    """
    class Arguments:
        input = OrderInput(required=True)
    
    order = graphene.Field(OrderType)
    
    def mutate(self, info, input):
        try:
            # Validate customer exists
            customer = Customer.objects.get(id=input.customer_id)
            
            # Validate products exist
            products = Product.objects.filter(id__in=input.product_ids)
            if len(products) != len(input.product_ids):
                raise Exception("Some product IDs are invalid")
            
            # Calculate total amount
            total_amount = sum(product.price for product in products)
            
            # Create order
            order = Order.objects.create(
                customer=customer,
                total_amount=total_amount
            )
            order.products.set(products)
            
            return CreateOrder(order=order)
        except Customer.DoesNotExist:
            raise Exception("Customer not found")
        except Exception as e:
            raise Exception(str(e))

# Define Query and Mutation classes
class Query(graphene.ObjectType):
    customers = graphene.List(CustomerType)
    products = graphene.List(ProductType)
    orders = graphene.List(OrderType)
    
    def resolve_customers(self, info):
        return Customer.objects.all()
    
    def resolve_products(self, info):
        return Product.objects.all()
    
    def resolve_orders(self, info):
        return Order.objects.all()

class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()



