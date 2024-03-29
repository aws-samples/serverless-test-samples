package com.amazon.aws.sample;


import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.context.annotation.ComponentScan;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@SpringBootApplication
@RequestMapping("/")
@ComponentScan("com.amazon.*")
public class Main {

    @GetMapping
    public String applicationStatus(){
        return "Application is running";
    }

    public static void main(String[] args) {
        SpringApplication.run(Main.class, args);

    }

}

