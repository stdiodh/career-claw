package dev.careerfeed.lab.order

import ch.qos.logback.classic.Logger
import ch.qos.logback.classic.spi.ILoggingEvent
import ch.qos.logback.core.read.ListAppender
import io.micrometer.core.instrument.MeterRegistry
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import org.springframework.aop.support.AopUtils
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.test.context.SpringBootTest
import org.springframework.boot.test.context.TestConfiguration
import org.springframework.boot.webmvc.test.autoconfigure.AutoConfigureMockMvc
import org.springframework.context.annotation.Bean
import org.springframework.context.annotation.Import
import org.springframework.http.MediaType
import org.springframework.jdbc.core.JdbcTemplate
import org.springframework.security.core.userdetails.User
import org.springframework.security.provisioning.InMemoryUserDetailsManager
import org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.httpBasic
import org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.user
import org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.MvcResult
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.header
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.status
import org.slf4j.LoggerFactory
import dev.careerfeed.lab.web.RequestIdFilter
import tools.jackson.databind.json.JsonMapper
import java.util.concurrent.CyclicBarrier
import java.util.concurrent.Executors
import java.util.concurrent.TimeUnit
import java.util.UUID

@SpringBootTest(properties = ["lab.external.api-token=runtime-provided-test-value"])
@AutoConfigureMockMvc
@Import(CredentialAuthenticationTestConfig::class)
class OrderWorkflowIntegrationTest @Autowired constructor(
    private val mockMvc: MockMvc,
    private val jsonMapper: JsonMapper,
    private val jdbcTemplate: JdbcTemplate,
    private val orderService: OrderService,
    private val stockService: StockService,
    private val meterRegistry: MeterRegistry,
    private val testCredentials: RuntimeTestCredentials,
) {
    @BeforeEach
    fun resetDatabase() {
        jdbcTemplate.update("delete from idempotency_records")
        jdbcTemplate.update("delete from purchase_orders")
        jdbcTemplate.update("update products set stock = 10 where id = 1")
    }

    @Test
    @DisplayName("LAB-IDEMP-001 the same key and body replay the original order without another stock change")
    fun sameRequestReplaysOriginalResult() {
        val first = createOrder("idem-001", 1)
        val second = createOrder("idem-001", 1, expectedStatus = 200)

        assertThat(orderId(first)).isEqualTo(orderId(second))
        assertThat(jsonMapper.readTree(second.response.contentAsString)["replayed"].booleanValue()).isTrue()
        assertThat(jdbcTemplate.queryForObject("select count(*) from purchase_orders", Int::class.java)).isEqualTo(1)
        assertThat(stock()).isEqualTo(9)
    }

    @Test
    @DisplayName("LAB-IDEMP-002 the same key with a different fingerprint is rejected with 409")
    fun changedFingerprintIsRejected() {
        createOrder("idem-002", 1)

        mockMvc.perform(
            post("/api/orders")
                .with(user("alice"))
                .with(csrf())
                .header("Idempotency-Key", "idem-002")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"productId":1,"quantity":2}"""),
        )
            .andExpect(status().isConflict)
            .andExpect(jsonPath("$.title").value("Idempotency conflict"))

        assertThat(stock()).isEqualTo(9)
    }

    @Test
    @DisplayName("LAB-IDEMP-003 concurrent requests with the same key persist one order and one stock change")
    fun concurrentSameKeyHasNoRaceLeak() {
        val barrier = CyclicBarrier(2)
        val executor = Executors.newFixedThreadPool(2)
        try {
            val futures = List(2) {
                executor.submit<CreateOrderResult> {
                    barrier.await(5, TimeUnit.SECONDS)
                    orderService.create(
                        "alice",
                        "idem-003",
                        CreateOrderCommand(productId = 1, quantity = 1, note = null),
                    )
                }
            }
            val results = futures.map { it.get(10, TimeUnit.SECONDS) }

            assertThat(results.map { it.orderId }.distinct()).hasSize(1)
            assertThat(results.count { it.replayed }).isEqualTo(1)
            assertThat(results.count { !it.replayed }).isEqualTo(1)
            assertThat(jdbcTemplate.queryForObject("select count(*) from purchase_orders", Int::class.java)).isEqualTo(1)
            assertThat(stock()).isEqualTo(9)
        } finally {
            executor.shutdownNow()
        }
    }

    @Test
    @DisplayName("LAB-AUTHN-001 actual HTTP Basic authentication rejects anonymous and wrong credentials")
    fun credentialAuthenticationSuccessAndFailureAreSeparated() {
        fun request() = post("/api/orders")
            .with(csrf())
            .header("Idempotency-Key", "authn-001")
            .contentType(MediaType.APPLICATION_JSON)
            .content("""{"productId":1,"quantity":1}""")

        mockMvc.perform(request())
            .andExpect(status().isUnauthorized)
        mockMvc.perform(
            request().with(httpBasic(testCredentials.username, "${testCredentials.password}-wrong")),
        ).andExpect(status().isUnauthorized)
        mockMvc.perform(
            request().with(httpBasic(testCredentials.username, testCredentials.password)),
        ).andExpect(status().isCreated)

        assertThat(jdbcTemplate.queryForObject("select count(*) from purchase_orders", Int::class.java)).isEqualTo(1)
    }

    @Test
    @DisplayName("LAB-AUTHZ-001 an owner can read an order and another authenticated user receives 403")
    fun ownerAuthorizationPreventsBola() {
        val created = createOrder("authz-001", 1)
        val id = orderId(created)

        mockMvc.perform(get("/api/orders/{id}", id).with(user("alice")))
            .andExpect(status().isOk)
            .andExpect(jsonPath("$.customerUsername").value("alice"))
        mockMvc.perform(get("/api/orders/{id}", id).with(user("bob")))
            .andExpect(status().isForbidden)
    }

    @Test
    @DisplayName("LAB-OBS-001 request ID is preserved in the response and structured request log")
    fun requestIdIsPreserved() {
        val logger = LoggerFactory.getLogger(RequestIdFilter::class.java) as Logger
        val appender = ListAppender<ILoggingEvent>().also {
            it.start()
            logger.addAppender(it)
        }
        try {
            mockMvc.perform(get("/actuator/health").header("X-Request-Id", "request-42"))
                .andExpect(status().isOk)
                .andExpect(header().string("X-Request-Id", "request-42"))

            val requestLog = appender.list.single { it.formattedMessage == "http_request" }
            val structuredFields = requestLog.keyValuePairs.associate { it.key to it.value }
            assertThat(requestLog.mdcPropertyMap).containsEntry("request_id", "request-42")
            assertThat(structuredFields)
                .containsEntry("method", "GET")
                .containsEntry("path", "/actuator/health")
                .containsEntry("status", 200)
        } finally {
            logger.detachAppender(appender)
            appender.stop()
        }
    }

    @Test
    @DisplayName("LAB-OBS-002 an order outcome metric and health signal are both queryable")
    fun metricAndHealthAreAvailable() {
        val before = meterRegistry.find(OrderService.METRIC).tag("outcome", "created").counter()?.count() ?: 0.0

        createOrder("obs-001", 1)

        val after = meterRegistry.get(OrderService.METRIC).tag("outcome", "created").counter().count()
        assertThat(after - before).isEqualTo(1.0)
        mockMvc.perform(get("/actuator/health"))
            .andExpect(status().isOk)
            .andExpect(jsonPath("$.status").value("UP"))
    }

    @Test
    @DisplayName("LAB-CONC-001 two concurrent decrements yield one success, one failure, and stock zero")
    fun conditionalUpdatePreventsOversell() {
        jdbcTemplate.update("update products set stock = 1 where id = 1")
        val barrier = CyclicBarrier(2)
        val executor = Executors.newFixedThreadPool(2)
        try {
            val futures = List(2) {
                executor.submit<Boolean> {
                    barrier.await(5, TimeUnit.SECONDS)
                    stockService.reserve(1, 1)
                }
            }
            val results = futures.map { it.get(10, TimeUnit.SECONDS) }

            assertThat(results.count { it }).isEqualTo(1)
            assertThat(results.count { !it }).isEqualTo(1)
            assertThat(stock()).isZero()
        } finally {
            executor.shutdownNow()
        }
    }

    @Test
    @DisplayName("LAB-KOTLIN-001 Jackson applies Kotlin default nullability when an optional field is absent")
    fun jacksonUsesKotlinDefaultForMissingOptionalField() {
        val request = jsonMapper.readValue(
            """{"productId":1,"quantity":1}""",
            CreateOrderRequest::class.java,
        )

        assertThat(request.note).isNull()
        assertThat(request.productId).isEqualTo(1)
    }

    @Test
    @DisplayName("LAB-KOTLIN-002 kotlin-spring opens the transactional service for an AOP proxy")
    fun transactionalKotlinServiceIsProxied() {
        assertThat(AopUtils.isAopProxy(orderService)).isTrue()
    }

    private fun createOrder(key: String, quantity: Int, expectedStatus: Int = 201): MvcResult =
        mockMvc.perform(
            post("/api/orders")
                .with(user("alice"))
                .with(csrf())
                .header("Idempotency-Key", key)
                .header("X-Request-Id", "test-$key")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"productId":1,"quantity":$quantity}"""),
        ).andExpect(status().`is`(expectedStatus)).andReturn()

    private fun orderId(result: MvcResult): Long =
        jsonMapper.readTree(result.response.contentAsString)["orderId"].longValue()

    private fun stock(): Int =
        requireNotNull(jdbcTemplate.queryForObject("select stock from products where id = 1", Int::class.java))
}

data class RuntimeTestCredentials(val username: String, val password: String)

@TestConfiguration(proxyBeanMethods = false)
class CredentialAuthenticationTestConfig {
    @Bean
    fun runtimeTestCredentials(): RuntimeTestCredentials =
        RuntimeTestCredentials(username = "alice", password = UUID.randomUUID().toString())

    @Bean
    fun testUsers(credentials: RuntimeTestCredentials): InMemoryUserDetailsManager =
        InMemoryUserDetailsManager(
            User.withUsername(credentials.username)
                .password("{noop}${credentials.password}")
                .roles("USER")
                .build(),
        )
}
