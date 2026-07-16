package dev.careerfeed.lab.payment

data class PaymentApproval(val requestId: String, val approvalId: String)

fun interface PaymentGateway {
    fun approve(requestId: String): PaymentApproval
}

interface PaymentStateStore {
    fun markPaidIfAbsent(orderId: Long, approval: PaymentApproval): Boolean
}

class PaymentCoordinator(
    private val gateway: PaymentGateway,
    private val store: PaymentStateStore,
) {
    fun approveThenPersist(orderId: Long, requestId: String): PaymentApproval {
        val approval = gateway.approve(requestId)
        store.markPaidIfAbsent(orderId, approval)
        return approval
    }

    fun reconcile(orderId: Long, approval: PaymentApproval): Boolean =
        store.markPaidIfAbsent(orderId, approval)
}
