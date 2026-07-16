package dev.careerfeed.lab.payment

import org.assertj.core.api.Assertions.assertThat
import org.assertj.core.api.Assertions.assertThatThrownBy
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test

class PaymentRecoveryTest {
    @Test
    @DisplayName("LAB-TX-001 approval survives a DB failure and idempotent reconciliation completes exactly once")
    fun approvalIsRetainedAndReconciliationIsIdempotent() {
        var gatewayCalls = 0
        var retainedApproval: PaymentApproval? = null
        val gateway = PaymentGateway { requestId ->
            gatewayCalls++
            PaymentApproval(requestId, "approval-42").also { retainedApproval = it }
        }
        val store = FailsOncePaymentStore()
        val coordinator = PaymentCoordinator(gateway, store)

        assertThatThrownBy { coordinator.approveThenPersist(42, "payment-request-42") }
            .isInstanceOf(IllegalStateException::class.java)

        assertThat(retainedApproval).isNotNull
        assertThat(coordinator.reconcile(42, requireNotNull(retainedApproval))).isTrue()
        assertThat(coordinator.reconcile(42, requireNotNull(retainedApproval))).isFalse()
        assertThat(store.persistedApproval).isEqualTo(retainedApproval)
        assertThat(gatewayCalls).isEqualTo(1)
    }

    private class FailsOncePaymentStore : PaymentStateStore {
        var persistedApproval: PaymentApproval? = null
        private var failNext = true

        override fun markPaidIfAbsent(orderId: Long, approval: PaymentApproval): Boolean {
            if (failNext) {
                failNext = false
                throw IllegalStateException("simulated DB failure")
            }
            if (persistedApproval != null) return false
            persistedApproval = approval
            return true
        }
    }
}
