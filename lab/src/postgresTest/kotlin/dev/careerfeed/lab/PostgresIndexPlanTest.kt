package dev.careerfeed.lab

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.TestReporter
import org.testcontainers.junit.jupiter.Container
import org.testcontainers.junit.jupiter.Testcontainers
import org.testcontainers.postgresql.PostgreSQLContainer
import java.sql.DriverManager
import java.sql.Statement

@Testcontainers
class PostgresIndexPlanTest {
    @Test
    @DisplayName("LAB-PG-001 pinned PostgreSQL captures before and after plans and uses the target composite index")
    fun targetCompositeIndexAppearsInPlan(testReporter: TestReporter) {
        assertThat(postgres.dockerImageName).isEqualTo(POSTGRES_IMAGE)
        DriverManager.getConnection(postgres.jdbcUrl, postgres.username, postgres.password).use { connection ->
            connection.createStatement().use { statement ->
                statement.execute(
                    """
                    CREATE TABLE orders (
                        id BIGSERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        status VARCHAR(20) NOT NULL,
                        created_at TIMESTAMPTZ NOT NULL,
                        total_amount NUMERIC(12, 2) NOT NULL
                    )
                    """.trimIndent(),
                )
                statement.execute(
                    """
                    INSERT INTO orders(user_id, status, created_at, total_amount)
                    SELECT value % 1000,
                           CASE WHEN value % 3 = 0 THEN 'PAID' ELSE 'PENDING' END,
                           TIMESTAMPTZ '2026-01-01 00:00:00+00' + value * INTERVAL '1 second',
                           1000
                      FROM generate_series(1, 100000) AS value
                    """.trimIndent(),
                )
                statement.execute("ANALYZE orders")
                warmUp(statement)
                val beforeIndexPlan = explain(statement)

                statement.execute("CREATE INDEX $INDEX_NAME ON orders(user_id, status, created_at DESC)")
                statement.execute("ANALYZE orders")
                warmUp(statement)
                val afterIndexPlan = explain(statement)

                testReporter.publishEntry("warm_up_count_per_plan", WARM_UP_COUNT.toString())
                testReporter.publishEntry("before_index_plan", beforeIndexPlan)
                testReporter.publishEntry("after_index_plan", afterIndexPlan)

                assertThat(beforeIndexPlan)
                    .contains("Buffers:", "Execution Time:")
                    .doesNotContain(INDEX_NAME)
                assertThat(afterIndexPlan)
                    .contains("Buffers:", "Execution Time:", INDEX_NAME)
            }
        }
    }

    private fun warmUp(statement: Statement) {
        repeat(WARM_UP_COUNT) {
            statement.executeQuery(TARGET_QUERY).use { rows ->
                while (rows.next()) {
                    rows.getLong(1)
                    rows.getBigDecimal(2)
                }
            }
        }
    }

    private fun explain(statement: Statement): String =
        statement.executeQuery("EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) $TARGET_QUERY").use { rows ->
            buildString {
                while (rows.next()) appendLine(rows.getString(1))
            }
        }

    companion object {
        private const val INDEX_NAME = "idx_orders_user_status_created"
        private const val WARM_UP_COUNT = 3
        private const val POSTGRES_IMAGE =
            "postgres@sha256:4f736ae292687621d4dbe0d499ffd024a36bd2ee7d8ca6f2ccd4c800f047b394"
        private val TARGET_QUERY =
            """
            SELECT id, total_amount
              FROM orders
             WHERE user_id = 42 AND status = 'PAID'
             ORDER BY created_at DESC
             LIMIT 20
            """.trimIndent()

        @Container
        @JvmStatic
        val postgres = PostgreSQLContainer(POSTGRES_IMAGE)
    }
}
