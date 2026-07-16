package dev.careerfeed.lab.config

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import org.springframework.boot.context.properties.EnableConfigurationProperties
import org.springframework.boot.test.context.TestConfiguration
import org.springframework.boot.test.context.runner.ApplicationContextRunner
import org.springframework.boot.test.util.TestPropertyValues
import java.time.Duration

class LabExternalPropertiesTest {
    private val contextRunner = ApplicationContextRunner()
        .withUserConfiguration(PropertiesTestConfiguration::class.java)

    @Test
    @DisplayName("LAB-CONFIG-001 active profile and environment-style overrides bind immutable configuration")
    fun activeProfileAndEnvironmentOverridesBindTypedValues() {
        contextRunner
            .withEnvironment(
                "SPRING_PROFILES_ACTIVE=verification",
                "LAB_EXTERNAL_API_TOKEN=runtime-provided-value",
                "LAB_EXTERNAL_RESPONSE_TIMEOUT=750ms",
                "LAB_EXTERNAL_MAX_ATTEMPTS=2",
            )
            .run { context ->
                assertThat(context.startupFailure).isNull()
                assertThat(context.environment.activeProfiles).containsExactly("verification")

                val properties = context.getBean(LabExternalProperties::class.java)
                assertThat(properties.apiToken).isEqualTo("runtime-provided-value")
                assertThat(properties.responseTimeout).isEqualTo(Duration.ofMillis(750))
                assertThat(properties.maxAttempts).isEqualTo(2)
            }
    }

    @Test
    @DisplayName("LAB-CONFIG-002 a blank environment secret fails closed during context startup")
    fun blankEnvironmentSecretStopsContextStartup() {
        contextRunner
            .withEnvironment("LAB_EXTERNAL_API_TOKEN=")
            .run { context ->
                val failure = checkNotNull(context.startupFailure)
                val failureChain = generateSequence(failure) { it.cause }
                    .map { it.message.orEmpty() }
                    .joinToString("\n")

                assertThat(failureChain).contains("apiToken")
            }
    }

    private fun ApplicationContextRunner.withEnvironment(vararg values: String): ApplicationContextRunner =
        withInitializer { context ->
            TestPropertyValues.of(*values)
                .applyTo(context.environment, TestPropertyValues.Type.SYSTEM_ENVIRONMENT)
        }

    @TestConfiguration(proxyBeanMethods = false)
    @EnableConfigurationProperties(LabExternalProperties::class)
    private class PropertiesTestConfiguration
}
