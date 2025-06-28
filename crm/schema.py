import graphene
from graphene_django import DjangoObjectType
from .models import Customer, Product, Order
from django.core.exceptions import ValidationError
from django.utils import timezone

from decimal import Decimal, ROUND_HALF_UP

# TYPES
class CustomerType(DjangoObjectType):
    class Meta:
        model = Customer
        fields = '__all__'

class ProductType(DjangoObjectType):
    class Meta:
        model = Product
        fields = '__all__'

class OrderType(DjangoObjectType):
    class Meta:
        model = Order
        fields = '__all__'

# INPUTS
class CustomerInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    email = graphene.String(required=True)
    phone = graphene.String()

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int()

class OrderInput(graphene.InputObjectType):
    customer_id = graphene.ID(required=True)
    product_ids = graphene.List(graphene.ID, required=True)

# MUTATIONS
class CreateCustomer(graphene.Mutation):
    class Arguments:
        input = CustomerInput(required=True)

    customer = graphene.Field(CustomerType)
    message = graphene.String()

    def mutate(self, info, input):
        if Customer.objects.filter(email=input.email).exists():
            raise Exception("Email already exists")

        customer = Customer(name=input.name, email=input.email, phone=input.phone or "")
        customer.full_clean()
        customer.save()
        return CreateCustomer(customer=customer, message="Customer created successfully.")

class BulkCreateCustomers(graphene.Mutation):
    class Arguments:
        input = graphene.List(CustomerInput, required=True)

    customers = graphene.List(CustomerType)
    errors = graphene.List(graphene.String)

    def mutate(self, info, input):
        valid_customers = []
        errors = []

        for index, data in enumerate(input):
            try:
                if Customer.objects.filter(email=data.email).exists():
                    raise Exception(f"Duplicate email: {data.email}")
                cust = Customer(name=data.name, email=data.email, phone=data.phone or "")
                cust.full_clean()
                valid_customers.append(cust)
            except Exception as e:
                errors.append(f"Entry {index + 1}: {str(e)}")

        created = Customer.objects.bulk_create(valid_customers)
        return BulkCreateCustomers(customers=created, errors=errors)
    

class CreateProduct(graphene.Mutation):
    class Arguments:
        input = ProductInput(required=True)

    product = graphene.Field(ProductType)

    def mutate(self, info, input):
        try:
            price = float(input.price)
        except (ValueError, TypeError):
            raise Exception("Price must be a number or a numeric string.")

        if price <= 0:
            raise Exception("Price must be positive.")

        if input.stock is not None and input.stock < 0:
            raise Exception("Stock cannot be negative.")

        # Convert float to Decimal with 2 decimal places for accuracy
        price = Decimal(str(price)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        product = Product(name=input.name, price=price, stock=input.stock or 0)
        product.full_clean()
        product.save()
        return CreateProduct(product=product)




class CreateOrder(graphene.Mutation):
    class Arguments:
        input = OrderInput(required=True)

    order = graphene.Field(OrderType)

    def mutate(self, info, input):
        try:
            customer = Customer.objects.get(pk=input.customer_id)
        except Customer.DoesNotExist:
            raise Exception("Invalid customer ID")

        if not input.product_ids:
            raise Exception("At least one product must be selected")

        products = []
        total = 0
        for pid in input.product_ids:
            try:
                product = Product.objects.get(pk=pid)
                products.append(product)
                total += float(product.price)
            except Product.DoesNotExist:
                raise Exception(f"Invalid product ID: {pid}")

        order = Order(customer=customer, total_amount=total, order_date=timezone.now())
        order.save()
        order.products.set(products)
        return CreateOrder(order=order)

# ------------------ EXPORT MUTATIONS ------------------
class Mutation(graphene.ObjectType):
    create_customer = CreateCustomer.Field()
    bulk_create_customers = BulkCreateCustomers.Field()
    create_product = CreateProduct.Field()
    create_order = CreateOrder.Field()

class Query(graphene.ObjectType):
    hello = graphene.String(default_value="Hello from CRM schema!")

