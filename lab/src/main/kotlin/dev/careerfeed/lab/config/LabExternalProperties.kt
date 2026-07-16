package dev.careerfeed.lab.config

import jakarta.validation.constraints.Max
import jakarta.validation.constraints.Min
import jakarta.validation.constraints.NotBlank
import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.validation.annotation.Validated
import java.time.Duration

@Validated
@ConfigurationProperties("lab.external")
data class LabExternalProperties(
    @field:NotBlank
    val apiToken: String = "",
    val responseTimeout: Duration = Duration.ofMillis(500),
    @field:Min(1)
    @field:Max(3)
    val maxAttempts: Int = 3,
)
