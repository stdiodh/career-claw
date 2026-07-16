package dev.careerfeed.lab.observability

import io.micrometer.core.instrument.simple.SimpleMeterRegistry
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import java.time.Duration

class PerformanceMetricsTest {
    @Test
    @DisplayName("LAB-OBS-003 fixed latency data produces reproducible throughput, error rate, p95, and p99")
    fun fixedDataProducesReproducibleSummary() {
        val registry = SimpleMeterRegistry()
        val metrics = PerformanceMetrics(registry)
        val latencies = listOf(45L, 48, 50, 51, 52, 53, 55, 57, 60, 62, 65, 68, 70, 74, 80, 90, 110, 180, 420, 900)

        val summary = metrics.summarize(latencies, failures = 2, window = Duration.ofSeconds(10))

        assertThat(summary.averageMs).isEqualTo(129.5)
        assertThat(summary.p95Ms).isEqualTo(420)
        assertThat(summary.p99Ms).isEqualTo(900)
        assertThat(summary.totalThroughputPerSecond).isEqualTo(2.2)
        assertThat(summary.successThroughputPerSecond).isEqualTo(2.0)
        assertThat(summary.errorRate).isCloseTo(0.0909, org.assertj.core.data.Offset.offset(0.0001))
        assertThat(registry.get("lab.http.latency").timer().count()).isEqualTo(20)
        assertThat(registry.get("lab.http.latency").timer().max(java.util.concurrent.TimeUnit.MILLISECONDS))
            .isEqualTo(900.0)
    }
}
