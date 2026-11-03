// SPDX-License-Identifier: Apache-2.0
package com.android.internal.telephony.metrics;

/** Legacy telemetry API used by the prebuilt MediaTek IMS package. */
public final class TelephonyMetrics {
    private static final TelephonyMetrics INSTANCE = new TelephonyMetrics();
    private TelephonyMetrics() {}
    public static TelephonyMetrics getInstance() { return INSTANCE; }
    public void writeOnRilSolicitedResponse(int phone, int serial, int error,
            int request, Object result) {}
    public void writeOnRilTimeoutResponse(int phone, int serial, int request) {}
    public void writeRilSendSms(int phone, int serial, int technology, int format,
            long messageId) {}
    public void writeRilAnswer(int phone, int serial) {}
}
