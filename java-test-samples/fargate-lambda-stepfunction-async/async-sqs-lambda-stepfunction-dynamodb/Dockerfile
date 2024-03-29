FROM openjdk:17-alpine

# Refer to Maven build -> finalName
ARG JAR_FILE=target/async-sqs-lambda-stepfunction-dynamodb-0.0.1-SNAPSHOT.jar

# cd /opt/app
WORKDIR /opt/app

# cp target/spring-boot-web.jar /opt/app/app.jar
COPY ${JAR_FILE} app.jar

EXPOSE 8080
# java -jar /opt/app/app.jar
ENTRYPOINT ["java","-jar","app.jar"]

