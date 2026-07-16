package dev.careerfeed.lab.order

import jakarta.persistence.Column
import jakarta.persistence.Entity
import jakarta.persistence.FetchType
import jakarta.persistence.GeneratedValue
import jakarta.persistence.GenerationType
import jakarta.persistence.Id
import jakarta.persistence.JoinColumn
import jakarta.persistence.ManyToOne
import jakarta.persistence.Table
import java.time.Instant

@Entity
@Table(name = "customers")
class CustomerEntity(
    @Id
    val id: Long = 0,
    @Column(nullable = false, unique = true)
    val username: String = "",
)

@Entity
@Table(name = "products")
class ProductEntity(
    @Id
    val id: Long = 0,
    @Column(nullable = false)
    val name: String = "",
    @Column(nullable = false)
    var stock: Int = 0,
)

@Entity
@Table(name = "purchase_orders")
class PurchaseOrderEntity(
    @Id
    @GeneratedValue(strategy = GenerationType.IDENTITY)
    var id: Long? = null,
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "customer_id", nullable = false)
    val customer: CustomerEntity = CustomerEntity(),
    @ManyToOne(fetch = FetchType.LAZY, optional = false)
    @JoinColumn(name = "product_id", nullable = false)
    val product: ProductEntity = ProductEntity(),
    @Column(nullable = false)
    val quantity: Int = 0,
    val note: String? = null,
    @Column(nullable = false)
    val status: String = "CREATED",
    @Column(name = "created_at", nullable = false)
    val createdAt: Instant = Instant.now(),
)

@Entity
@Table(name = "idempotency_records")
class IdempotencyRecordEntity(
    @Id
    @Column(name = "idempotency_key", nullable = false, length = 120)
    val key: String = "",
    @Column(name = "request_fingerprint", nullable = false, length = 64)
    val fingerprint: String = "",
    @Column(name = "order_id", nullable = false, unique = true)
    val orderId: Long = 0,
)

@Entity
@Table(name = "idempotency_lock_buckets")
class IdempotencyLockEntity(
    @Id
    @Column(name = "bucket_id")
    val bucketId: Int = 0,
)

data class OrderSummary(
    val id: Long,
    val customerUsername: String,
    val quantity: Int,
)
