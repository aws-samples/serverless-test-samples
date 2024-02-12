# Springboot-with-dynamoDB
Simple Dynamo DB & SQS integration with Spring Boot application

![customer_crud_app.png](doc%2Fcustomer_crud_app.png)

### Application
Java17 maven application with Springboot 2.2.6 and AWS Java SDK 1.11.614 dependencies.

### How to run?
1) Update application.properties with your AWS sqs queue name. If not already created, code will auto create it.
2) Run these commands in the terminal
   1) mvn clean install
   2) mvn spring-boot:run

### Pre-requisites
1) SQS Queue
2) DynamoDB tables
3) Table Attributes
   1) customer_details ref: src/test/resources/customer_details.json

### Steps for deploying the docker images on ECS with Fargate
1) Create a Docker Image ensuring that you have a 'Dockerfile' in your application code.
2) Push Docker Image to Amazon ECR
3) Create ECS Task Definition through the AWS Management Console or use the AWS CLI. 

![ecs_task_definition.png](src%2Fmain%2Fresources%2Fimages%2Fecs_task_definition.png)
4) Create ECS Cluster and configure ECS Service specifying the task definition and other configurations.

![ecs_cluster.png](src%2Fmain%2Fresources%2Fimages%2Fecs_cluster.png)
5) Set the launch type to Fargate, which means ECS manages the underlying infrastructure.
6) Deploy ECS Service through the AWS Management Console or using the AWS CLI.


### APIs 
1) Add customer details (curl --location 'http://<HOST>/customer/new' \
   --header 'Content-Type: application/json' \
   --data-raw '{
   "customerId": "1",
   "name": "customer-1",
   "email": "customer1@gmail.com"
   }')

2) Get all customers (curl --location 'http://<HOST>/customers/all')

3) Delete customer details based on customer-id (curl --location --request DELETE 'http://<HOST>/customer/delete?customerId=<customerId>')

4) Retrieve customer details based on customer-id (curl --location 'http://<HOST>/customers?customerId=<customerId>')

### Note
Once the application starts, we will trigger a message {"application_status":"ready"} will be dropped to the SQS