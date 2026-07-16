package dev.careerfeed.lab.order

import jakarta.validation.Valid
import jakarta.validation.constraints.Max
import jakarta.validation.constraints.Min
import jakarta.validation.constraints.NotBlank
import jakarta.validation.constraints.NotNull
import jakarta.validation.constraints.Positive
import jakarta.validation.constraints.Size
import org.springframework.http.HttpStatus
import org.springframework.http.ResponseEntity
import org.springframework.security.core.Authentication
import org.springframework.validation.annotation.Validated
import org.springframework.web.bind.annotation.GetMapping
import org.springframework.web.bind.annotation.PathVariable
import org.springframework.web.bind.annotation.PostMapping
import org.springframework.web.bind.annotation.RequestBody
import org.springframework.web.bind.annotation.RequestHeader
import org.springframework.web.bind.annotation.RequestMapping
import org.springframework.web.bind.annotation.RestController

data class CreateOrderRequest(
    @field:NotNull
    @field:Positive
    val productId: Long?,
    @field:NotNull
    @field:Min(1)
    @field:Max(10)
    val quantity: Int?,
    @field:Size(max = 200)
    val note: String? = null,
)

data class CreateOrderResponse(
    val orderId: Long,
    val replayed: Boolean,
)

@RestController
@Validated
@RequestMapping("/api/orders")
class OrderController(private val orderService: OrderService) {
    @PostMapping
    fun create(
        authentication: Authentication,
        @RequestHeader("Idempotency-Key") @NotBlank @Size(max = 120) idempotencyKey: String,
        @Valid @RequestBody request: CreateOrderRequest,
    ): ResponseEntity<CreateOrderResponse> {
        val result = orderService.create(
            authentication.name,
            idempotencyKey,
            CreateOrderCommand(
                productId = requireNotNull(request.productId),
                quantity = requireNotNull(request.quantity),
                note = request.note,
            ),
        )
        val status = if (result.replayed) HttpStatus.OK else HttpStatus.CREATED
        return ResponseEntity.status(status).body(CreateOrderResponse(result.orderId, result.replayed))
    }

    @GetMapping("/{orderId}")
    fun get(@PathVariable orderId: Long): OrderSummary = orderService.get(orderId)
}
