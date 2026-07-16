package dev.careerfeed.lab.runtime

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.DisplayName
import org.junit.jupiter.api.Test

class JvmRuntimeProbeTest {
    @Test
    @DisplayName("LAB-JVM-001 Java 21 captures heap evidence on a named virtual thread")
    fun javaRuntimeEvidenceComesFromVirtualThread() {
        val snapshot = JvmRuntimeProbe.captureOnVirtualThread()

        assertThat(snapshot.javaVersion()).isEqualTo("21")
        assertThat(snapshot.threadName()).isEqualTo("career-lab-probe")
        assertThat(snapshot.virtual()).isTrue()
        assertThat(snapshot.usedHeapBytes()).isPositive()
    }
}
