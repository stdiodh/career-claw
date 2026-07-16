package dev.careerfeed.lab.order

import jakarta.persistence.EntityManager
import jakarta.persistence.EntityManagerFactory
import org.assertj.core.api.Assertions.assertThat
import org.hibernate.Hibernate
import org.hibernate.SessionFactory
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.data.jpa.test.autoconfigure.DataJpaTest
import org.springframework.data.domain.PageRequest
import org.springframework.jdbc.core.JdbcTemplate
import java.time.Instant

@DataJpaTest(showSql = false, properties = ["spring.jpa.properties.hibernate.generate_statistics=true"])
class OrderRepositoryTest @Autowired constructor(
    private val customers: CustomerRepository,
    private val products: ProductRepository,
    private val orders: PurchaseOrderRepository,
    private val entityManager: EntityManager,
    private val entityManagerFactory: EntityManagerFactory,
    private val jdbcTemplate: JdbcTemplate,
) {
    @Test
    @DisplayName("LAB-JPA-001 a lazy association loads only when accessed inside the persistence context")
    fun lazyAssociationBoundaryIsVisible() {
        val saved = saveOrder(quantity = 1, createdAt = Instant.parse("2026-01-01T00:00:00Z"))
        entityManager.flush()
        entityManager.clear()

        val reloaded = orders.findById(requireNotNull(saved.id)).orElseThrow()

        assertThat(Hibernate.isInitialized(reloaded.customer)).isFalse()
        assertThat(reloaded.customer.username).isEqualTo("alice")
        assertThat(Hibernate.isInitialized(reloaded.customer)).isTrue()
    }

    @Test
    @DisplayName("LAB-JPA-002 projection pagination returns the requested page without exposing entities")
    fun projectionPaginationHasStableBoundaries() {
        repeat(3) { index ->
            saveOrder(quantity = index + 1, createdAt = Instant.parse("2026-01-01T00:00:0${index}Z"))
        }
        entityManager.flush()

        val page = orders.findSummaries(PageRequest.of(0, 2))

        assertThat(page.content).hasSize(2)
        assertThat(page.totalElements).isEqualTo(3)
        assertThat(page.totalPages).isEqualTo(2)
        assertThat(page.content).allMatch { it.customerUsername == "alice" }
    }

    @Test
    @DisplayName("LAB-JPA-003 lazy traversal reproduces N+1 and join fetch reduces it to one query")
    fun queryShapeRemovesNPlusOneWithDeterministicQueryCounts() {
        val testCustomers = (10L..12L).map { id -> CustomerEntity(id, "n-plus-one-$id") }
        customers.saveAll(testCustomers)
        testCustomers.forEachIndexed { index, customer ->
            orders.save(
                PurchaseOrderEntity(
                    customer = customer,
                    product = products.getReferenceById(1),
                    quantity = index + 1,
                    createdAt = Instant.parse("2026-01-01T00:00:0${index}Z"),
                ),
            )
        }
        entityManager.flush()
        entityManager.clear()
        val statistics = entityManagerFactory.unwrap(SessionFactory::class.java).statistics

        statistics.clear()
        val lazyOrders = orders.findAll()
        assertThat(lazyOrders.map { it.customer.username }).hasSize(3)
        val nPlusOneQueryCount = statistics.prepareStatementCount

        entityManager.clear()
        statistics.clear()
        val shapedOrders = orders.findAllWithCustomer()
        assertThat(shapedOrders.map { it.customer.username }).hasSize(3)
        val joinFetchQueryCount = statistics.prepareStatementCount

        assertThat(nPlusOneQueryCount).isEqualTo(4)
        assertThat(joinFetchQueryCount).isEqualTo(1)
    }

    @Test
    @DisplayName("LAB-MIG-001 Flyway creates the tracked schema before Hibernate validation")
    fun flywayMigrationIsApplied() {
        val successfulMigrations = jdbcTemplate.queryForObject(
            "select count(*) from \"flyway_schema_history\" where \"version\" = '1' and \"success\" = true",
            Int::class.java,
        )
        val orderTable = jdbcTemplate.queryForObject(
            "select count(*) from information_schema.tables where lower(table_name) = 'purchase_orders'",
            Int::class.java,
        )

        assertThat(successfulMigrations).isEqualTo(1)
        assertThat(orderTable).isEqualTo(1)
    }

    @Test
    @DisplayName("LAB-TEST-003 JPA slice persists and queries without loading the full web application")
    fun jpaSlicePersistsEntity() {
        val saved = saveOrder(quantity = 2, createdAt = Instant.parse("2026-01-01T00:00:00Z"))

        assertThat(orders.existsById(requireNotNull(saved.id))).isTrue()
    }

    private fun saveOrder(quantity: Int, createdAt: Instant): PurchaseOrderEntity =
        orders.save(
            PurchaseOrderEntity(
                customer = customers.getReferenceById(1),
                product = products.getReferenceById(1),
                quantity = quantity,
                createdAt = createdAt,
            ),
        )
}
