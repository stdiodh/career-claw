package dev.careerfeed.lab.runtime;

import java.util.concurrent.atomic.AtomicReference;

public final class JvmRuntimeProbe {

    private JvmRuntimeProbe() {
    }

    public record Snapshot(String javaVersion, String threadName, boolean virtual, long usedHeapBytes) {
    }

    public static Snapshot captureOnVirtualThread() throws InterruptedException {
        var snapshot = new AtomicReference<Snapshot>();
        Thread thread = Thread.ofVirtual().name("career-lab-probe").start(() -> {
            Runtime runtime = Runtime.getRuntime();
            snapshot.set(new Snapshot(
                    Runtime.version().feature() + "",
                    Thread.currentThread().getName(),
                    Thread.currentThread().isVirtual(),
                    runtime.totalMemory() - runtime.freeMemory()
            ));
        });
        thread.join();
        return snapshot.get();
    }
}
