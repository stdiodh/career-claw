package dev.careerfeed.lab.order

import dev.careerfeed.lab.web.ApiExceptionHandler
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test
import org.springframework.beans.factory.annotation.Autowired
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest
import org.springframework.context.annotation.Import
import org.springframework.http.MediaType
import org.springframework.security.test.context.support.WithMockUser
import org.springframework.security.test.web.servlet.request.SecurityMockMvcRequestPostProcessors.csrf
import org.springframework.test.context.bean.override.mockito.MockitoBean
import org.springframework.test.web.servlet.MockMvc
import org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.content
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath
import org.springframework.test.web.servlet.result.MockMvcResultMatchers.status

@WebMvcTest(OrderController::class)
@Import(ApiExceptionHandler::class)
class OrderControllerWebMvcTest(@Autowired private val mockMvc: MockMvc) {
    @MockitoBean
    private lateinit var orderService: OrderService

    @Test
    @WithMockUser(username = "alice")
    @DisplayName("LAB-WEB-001 invalid DTO fields return application/problem+json with field evidence")
    fun invalidRequestReturnsProblemDetail() {
        mockMvc.perform(
            post("/api/orders")
                .with(csrf())
                .header("Idempotency-Key", "web-validation")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"productId":null,"quantity":0}"""),
        )
            .andExpect(status().isBadRequest)
            .andExpect(content().contentTypeCompatibleWith(MediaType.APPLICATION_PROBLEM_JSON))
            .andExpect(jsonPath("$.title").value("Invalid request"))
            .andExpect(jsonPath("$.errors.productId").exists())
            .andExpect(jsonPath("$.errors.quantity").exists())
    }

    @Test
    @WithMockUser(username = "alice")
    @DisplayName("LAB-TEST-002 MVC slice rejects a missing idempotency header before service invocation")
    fun mvcSliceChecksHeaderContract() {
        mockMvc.perform(
            post("/api/orders")
                .with(csrf())
                .contentType(MediaType.APPLICATION_JSON)
                .content("""{"productId":1,"quantity":1}"""),
        ).andExpect(status().isBadRequest)
    }
}
