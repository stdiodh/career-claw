package com.stdiodh.career_claw

import java.net.URI
import java.net.http.HttpClient
import java.net.http.HttpRequest
import java.net.http.HttpResponse
import kotlin.test.assertEquals
import org.junit.jupiter.api.Test
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.context.SpringBootTest.WebEnvironment
import org.springframework.boot.test.web.server.LocalServerPort

@SpringBootTest(webEnvironment = WebEnvironment.RANDOM_PORT)
class CareerClawApplicationTests {

	@LocalServerPort
	var port: Int = 0

	@Test
	fun contextLoads() {
	}

	@Test
	fun healthEndpointReturnsOk() {
		val client = HttpClient.newHttpClient()
		val request = HttpRequest.newBuilder()
			.uri(URI.create("http://127.0.0.1:$port/health"))
			.GET()
			.build()

		val response = client.send(request, HttpResponse.BodyHandlers.ofString())

		assertEquals(200, response.statusCode())
		assertEquals("""{"status":"ok"}""", response.body())
	}
}
