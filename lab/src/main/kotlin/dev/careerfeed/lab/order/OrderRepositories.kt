package dev.careerfeed.lab.order

import org.springframework.data.domain.Page
import org.springframework.data.domain.Pageable
import org.springframework.data.jpa.repository.JpaRepository
import org.springframework.data.jpa.repository.Lock
import org.springframework.data.jpa.repository.Modifying
import org.springframework.data.jpa.repository.Query
import org.springframework.data.repository.query.Param
import jakarta.persistence.LockModeType

interface CustomerRepository : JpaRepository<CustomerEntity, Long> {
    fun findByUsername(username: String): CustomerEntity?
}

interface ProductRepository : JpaRepository<ProductEntity, Long> {
    @Modifying(clearAutomatically = true, flushAutomatically = true)
    @Query(
        """
        update ProductEntity p
           set p.stock = p.stock - :quantity
         where p.id = :productId
           and p.stock >= :quantity
        """,
    )
    fun decrementIfAvailable(
        @Param("productId") productId: Long,
        @Param("quantity") quantity: Int,
    ): Int
}

interface PurchaseOrderRepository : JpaRepository<PurchaseOrderEntity, Long> {
    @Query(
        "select purchaseOrder from PurchaseOrderEntity purchaseOrder " +
            "join fetch purchaseOrder.customer order by purchaseOrder.id",
    )
    fun findAllWithCustomer(): List<PurchaseOrderEntity>

    @Query(
        """
        select new dev.careerfeed.lab.order.OrderSummary(o.id, c.username, o.quantity)
          from PurchaseOrderEntity o
          join o.customer c
         order by o.createdAt desc
        """,
    )
    fun findSummaries(pageable: Pageable): Page<OrderSummary>

    @Query("select o.customer.username from PurchaseOrderEntity o where o.id = :orderId")
    fun findOwnerUsername(@Param("orderId") orderId: Long): String?
}

interface IdempotencyRecordRepository : JpaRepository<IdempotencyRecordEntity, String>

interface IdempotencyLockRepository : JpaRepository<IdempotencyLockEntity, Int> {
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("select bucket from IdempotencyLockEntity bucket where bucket.bucketId = :bucketId")
    fun findForUpdate(@Param("bucketId") bucketId: Int): IdempotencyLockEntity?
}
