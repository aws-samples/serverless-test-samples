package com.amazon.aws.sample;

import com.amazon.aws.sample.sqs.SqsService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.ConfigurableApplicationContext;
import org.springframework.context.annotation.ComponentScan;

@SpringBootApplication
@ComponentScan("com.*")
public class SpringDynamodbApplication {
  private static final Logger logger = LoggerFactory.getLogger(SpringDynamodbApplication.class);
	public static void main(String[] args) {
		ConfigurableApplicationContext context = SpringApplication.run(SpringDynamodbApplication.class, args);
		if(context.isActive()) {
			logger.info("Application started successfully");
			context.getBean(SqsService.class).sendMessage();
		}
	}

}
