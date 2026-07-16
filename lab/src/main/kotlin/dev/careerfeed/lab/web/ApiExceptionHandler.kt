package dev.careerfeed.lab.web

import dev.careerfeed.lab.order.IdempotencyConflictException
import dev.careerfeed.lab.order.OutOfStockException
import dev.careerfeed.lab.order.ResourceNotFoundException
import jakarta.validation.ConstraintViolationException
import org.springframework.http.HttpStatus
import org.springframework.http.ProblemDetail
import org.springframework.web.bind.MethodArgumentNotValidException
import org.springframework.web.bind.annotation.ExceptionHandler
import org.springframework.web.bind.annotation.RestControllerAdvice

@RestControllerAdvice
class ApiExceptionHandler {
    @ExceptionHandler(MethodArgumentNotValidException::class)
    fun invalidBody(exception: MethodArgumentNotValidException): ProblemDetail {
        val problem = ProblemDetail.forStatusAndDetail(HttpStatus.BAD_REQUEST, "요청 본문 검증에 실패했습니다.")
        problem.title = "Invalid request"
        problem.setProperty(
            "errors",
            exception.bindingResult.fieldErrors.associate { it.field to (it.defaultMessage ?: "invalid") },
        )
        return problem
    }

    @ExceptionHandler(ConstraintViolationException::class)
    fun invalidParameter(exception: ConstraintViolationException): ProblemDetail =
        problem(HttpStatus.BAD_REQUEST, "Invalid request", exception.message ?: "요청 값이 올바르지 않습니다.")

    @ExceptionHandler(IdempotencyConflictException::class)
    fun conflict(exception: IdempotencyConflictException): ProblemDetail =
        problem(HttpStatus.CONFLICT, "Idempotency conflict", requireNotNull(exception.message))

    @ExceptionHandler(OutOfStockException::class)
    fun outOfStock(exception: OutOfStockException): ProblemDetail =
        problem(HttpStatus.CONFLICT, "Out of stock", requireNotNull(exception.message))

    @ExceptionHandler(ResourceNotFoundException::class)
    fun notFound(exception: ResourceNotFoundException): ProblemDetail =
        problem(HttpStatus.NOT_FOUND, "Not found", requireNotNull(exception.message))

    private fun problem(status: HttpStatus, title: String, detail: String): ProblemDetail =
        ProblemDetail.forStatusAndDetail(status, detail).also { it.title = title }
}
