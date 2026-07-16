package dev.careerfeed.lab.observability

import io.micrometer.core.instrument.MeterRegistry
import io.micrometer.core.instrument.Timer
import java.time.Duration
import kotlin.math.ceil

data class PerformanceSummary(
    val averageMs: Double,
    val p95Ms: Long,
    val p99Ms: Long,
    val totalThroughputPerSecond: Double,
    val successThroughputPerSecond: Double,
    val errorRate: Double,
)

class PerformanceMetrics(private val registry: MeterRegistry) {
    fun summarize(successLatenciesMs: List<Long>, failures: Int, window: Duration): PerformanceSummary {
        require(successLatenciesMs.isNotEmpty())
        require(failures >= 0)
        require(!window.isZero && !window.isNegative)

        val sorted = successLatenciesMs.sorted()
        val timer = Timer.builder("lab.http.latency").register(registry)
        sorted.forEach { timer.record(Duration.ofMillis(it)) }
        registry.counter("lab.http.errors").increment(failures.toDouble())

        val total = sorted.size + failures
        return PerformanceSummary(
            averageMs = sorted.average(),
            p95Ms = nearestRank(sorted, 0.95),
            p99Ms = nearestRank(sorted, 0.99),
            totalThroughputPerSecond = total / window.toMillis().times(0.001),
            successThroughputPerSecond = sorted.size / window.toMillis().times(0.001),
            errorRate = failures.toDouble() / total,
        )
    }

    private fun nearestRank(sorted: List<Long>, percentile: Double): Long {
        val index = ceil(percentile * sorted.size).toInt() - 1
        return sorted[index]
    }
}
