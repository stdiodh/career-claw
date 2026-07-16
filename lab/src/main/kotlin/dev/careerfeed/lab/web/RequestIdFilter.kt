package dev.careerfeed.lab.web

import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.slf4j.LoggerFactory
import org.slf4j.MDC
import org.springframework.stereotype.Component
import org.springframework.web.filter.OncePerRequestFilter
import java.util.UUID

@Component
class RequestIdFilter : OncePerRequestFilter() {
    private val log = LoggerFactory.getLogger(javaClass)

    override fun doFilterInternal(
        request: HttpServletRequest,
        response: HttpServletResponse,
        filterChain: FilterChain,
    ) {
        val requestId = request.getHeader(HEADER)?.takeIf(VALID::matches) ?: UUID.randomUUID().toString()
        response.setHeader(HEADER, requestId)
        MDC.put(MDC_KEY, requestId)
        try {
            filterChain.doFilter(request, response)
        } finally {
            log.atInfo()
                .addKeyValue("method", request.method)
                .addKeyValue("path", request.requestURI)
                .addKeyValue("status", response.status)
                .log("http_request")
            MDC.remove(MDC_KEY)
        }
    }

    companion object {
        const val HEADER = "X-Request-Id"
        private const val MDC_KEY = "request_id"
        private val VALID = Regex("[A-Za-z0-9._-]{1,64}")
    }
}
