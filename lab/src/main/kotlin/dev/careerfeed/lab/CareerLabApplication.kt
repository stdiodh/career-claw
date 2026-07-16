package dev.careerfeed.lab

import org.springframework.boot.autoconfigure.SpringBootApplication
import org.springframework.boot.context.properties.ConfigurationPropertiesScan
import org.springframework.boot.runApplication
import org.springframework.security.config.annotation.method.configuration.EnableMethodSecurity

@SpringBootApplication
@ConfigurationPropertiesScan
@EnableMethodSecurity
class CareerLabApplication

fun main(args: Array<String>) {
    runApplication<CareerLabApplication>(*args)
}
