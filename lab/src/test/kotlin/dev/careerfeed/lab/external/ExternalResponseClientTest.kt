package dev.careerfeed.lab.external

import com.sun.net.httpserver.HttpServer
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import org.springframework.web.client.ResourceAccessException
import java.net.InetSocketAddress
import java.net.URI
import java.net.http.HttpTimeoutException
import java.time.Duration

class ExternalResponseClientTest {
    @Test
    @DisplayName("LAB-TIMEOUT-001 JDK-backed RestClient stops waiting at its response timeout")
    fun responseTimeoutIsEnforcedByUnderlyingClient() {
        val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        server.createContext("/slow") { exchange ->
            Thread.sleep(250)
            val body = "late".toByteArray()
            runCatching {
                exchange.sendResponseHeaders(200, body.size.toLong())
                exchange.responseBody.use { it.write(body) }
            }
        }
        server.start()

        try {
            val client = ExternalResponseClient(Duration.ofMillis(50))
            val uri = URI("http://127.0.0.1:${server.address.port}/slow")

            assertThatThrownBy { client.get(uri) }
                .isInstanceOf(ResourceAccessException::class.java)
                .hasRootCauseInstanceOf(HttpTimeoutException::class.java)
        } finally {
            server.stop(0)
        }
    }
}
