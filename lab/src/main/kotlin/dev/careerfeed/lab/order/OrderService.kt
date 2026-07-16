package dev.careerfeed.lab.order

import io.micrometer.core.instrument.MeterRegistry
import org.springframework.security.access.prepost.PreAuthorize
import org.springframework.security.core.Authentication
import org.springframework.stereotype.Component
import org.springframework.stereotype.Service
import org.springframework.transaction.annotation.Propagation
import org.springframework.transaction.annotation.Transactional
import java.nio.charset.StandardCharsets
import java.security.MessageDigest
import java.time.Instant

data class CreateOrderCommand(
    val productId: Long,
    val quantity: Int,
    val note: String?,
)

data class CreateOrderResult(
    val orderId: Long,
    val replayed: Boolean,
)

class ResourceNotFoundException(message: String) : RuntimeException(message)
class IdempotencyConflictException(message: String) : RuntimeException(message)
class OutOfStockException(message: String) : RuntimeException(message)

@Service
class OrderService(
    private val customers: CustomerRepository,
    private val products: ProductRepository,
    private val orders: PurchaseOrderRepository,
    private val idempotencyRecords: IdempotencyRecordRepository,
    private val idempotencyLocks: IdempotencyLockRepository,
    private val meterRegistry: MeterRegistry,
) {
    @Transactional
    fun create(username: String, idempotencyKey: String, command: CreateOrderCommand): CreateOrderResult {
        val bucketId = Math.floorMod(idempotencyKey.hashCode(), IDEMPOTENCY_LOCK_BUCKETS)
        checkNotNull(idempotencyLocks.findForUpdate(bucketId)) { "Idempotency lock bucket is missing: $bucketId" }
        val fingerprint = fingerprint(command)
        idempotencyRecords.findById(idempotencyKey).orElse(null)?.let { existing ->
            if (existing.fingerprint != fingerprint) {
                throw IdempotencyConflictException("같은 Idempotency-Key에 다른 요청 본문을 사용할 수 없습니다.")
            }
            meterRegistry.counter(METRIC, "outcome", "replayed").increment()
            return CreateOrderResult(existing.orderId, replayed = true)
        }

        val customer = customers.findByUsername(username)
            ?: throw ResourceNotFoundException("등록되지 않은 사용자입니다.")
        val product = products.findById(command.productId).orElseThrow {
            ResourceNotFoundException("상품을 찾을 수 없습니다.")
        }
        if (products.decrementIfAvailable(product.id, command.quantity) != 1) {
            throw OutOfStockException("재고가 부족합니다.")
        }

        val order = orders.saveAndFlush(
            PurchaseOrderEntity(
                customer = customer,
                product = product,
                quantity = command.quantity,
                note = command.note,
                createdAt = Instant.now(),
            ),
        )
        val orderId = requireNotNull(order.id)
        idempotencyRecords.save(IdempotencyRecordEntity(idempotencyKey, fingerprint, orderId))
        meterRegistry.counter(METRIC, "outcome", "created").increment()
        return CreateOrderResult(orderId, replayed = false)
    }

    @Transactional(readOnly = true)
    @PreAuthorize("@orderAuthorization.canRead(#orderId, authentication)")
    fun get(orderId: Long): OrderSummary =
        orders.findById(orderId).orElseThrow {
            ResourceNotFoundException("주문을 찾을 수 없습니다.")
        }.let { OrderSummary(requireNotNull(it.id), it.customer.username, it.quantity) }

    private fun fingerprint(command: CreateOrderCommand): String {
        val canonical = "${command.productId}:${command.quantity}:${command.note.orEmpty()}"
        return MessageDigest.getInstance("SHA-256")
            .digest(canonical.toByteArray(StandardCharsets.UTF_8))
            .joinToString("") { "%02x".format(it) }
    }

    companion object {
        const val METRIC = "lab.orders.requests"
        private const val IDEMPOTENCY_LOCK_BUCKETS = 64
    }
}

@Service
class StockService(private val products: ProductRepository) {
    @Transactional(propagation = Propagation.REQUIRES_NEW)
    fun reserve(productId: Long, quantity: Int): Boolean =
        products.decrementIfAvailable(productId, quantity) == 1
}

@Component("orderAuthorization")
class OrderAuthorization(private val orders: PurchaseOrderRepository) {
    fun canRead(orderId: Long, authentication: Authentication): Boolean =
        authentication.authorities.any { it.authority == "ROLE_ADMIN" } ||
            orders.findOwnerUsername(orderId) == authentication.name
}
