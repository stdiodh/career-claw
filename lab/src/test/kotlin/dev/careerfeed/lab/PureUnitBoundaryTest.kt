package dev.careerfeed.lab

import dev.careerfeed.lab.external.RetryPolicy
import dev.careerfeed.lab.external.Sleeper
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import java.time.Duration

class PureUnitBoundaryTest {
    @Test
    @DisplayName("LAB-TEST-001 a pure unit test runs without Spring or infrastructure")
    fun pureUnitHasNoSpringContext() {
        val policy = RetryPolicy(1, Duration.ofMillis(10), emptyList(), Sleeper { })

        assertThat(policy.execute { "ok" }).isEqualTo("ok")
    }
}
