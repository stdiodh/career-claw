package dev.careerfeed.lab.external

import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import java.time.Duration

class RetryPolicyTest {
    @Test
    @DisplayName("LAB-RETRY-001 three attempts request only 100ms and 200ms sleeps within an 1800ms budget")
    fun retryBudgetAndSleepsAreDeterministic() {
        val requestedSleeps = mutableListOf<Duration>()
        val policy = RetryPolicy(
            maxAttempts = 3,
            attemptTimeout = Duration.ofMillis(500),
            backoffs = listOf(Duration.ofMillis(100), Duration.ofMillis(200), Duration.ofMillis(400)),
            sleeper = Sleeper(requestedSleeps::add),
        )
        var attempts = 0

        assertThatThrownBy {
            policy.execute {
                attempts++
                throw RetryableExternalException()
            }
        }.isInstanceOf(RetryableExternalException::class.java)

        assertThat(attempts).isEqualTo(3)
        assertThat(requestedSleeps).containsExactly(Duration.ofMillis(100), Duration.ofMillis(200))
        assertThat(policy.worstCaseBudget()).isEqualTo(Duration.ofMillis(1800))
    }
}
