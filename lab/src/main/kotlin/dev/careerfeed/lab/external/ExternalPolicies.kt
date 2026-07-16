package dev.careerfeed.lab.external

import org.springframework.http.client.JdkClientHttpRequestFactory
import org.springframework.web.client.RestClient
import java.net.URI
import java.net.http.HttpClient
import java.time.Duration

class ExternalResponseClient(responseTimeout: Duration) {
    private val client: RestClient

    init {
        val factory = JdkClientHttpRequestFactory(HttpClient.newHttpClient())
        factory.setReadTimeout(responseTimeout)
        client = RestClient.builder().requestFactory(factory).build()
    }

    fun get(uri: URI): String =
        requireNotNull(client.get().uri(uri).retrieve().body(String::class.java))
}

fun interface Sleeper {
    fun sleep(duration: Duration)
}

class RetryableExternalException : RuntimeException()

class RetryPolicy(
    private val maxAttempts: Int,
    private val attemptTimeout: Duration,
    private val backoffs: List<Duration>,
    private val sleeper: Sleeper,
) {
    init {
        require(maxAttempts >= 1)
        require(backoffs.size >= maxAttempts - 1)
    }

    fun <T> execute(operation: () -> T): T {
        repeat(maxAttempts) { attempt ->
            try {
                return operation()
            } catch (exception: RetryableExternalException) {
                if (attempt == maxAttempts - 1) throw exception
                sleeper.sleep(backoffs[attempt])
            }
        }
        error("unreachable")
    }

    fun worstCaseBudget(): Duration =
        attemptTimeout.multipliedBy(maxAttempts.toLong())
            .plus(backoffs.take(maxAttempts - 1).fold(Duration.ZERO, Duration::plus))
}
