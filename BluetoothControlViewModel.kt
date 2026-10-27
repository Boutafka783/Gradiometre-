package com.example.gradiometer.bluetooth

import android.annotation.SuppressLint
import android.app.Application
import android.os.SystemClock
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

/** جهاز مقترن مبسّط للعرض في الواجهة (بدون الاعتماد على BluetoothDevice). */
data class PairedDevice(val name: String, val address: String) {
    /** يطابق الأسماء المتوقعة لجهازك */
    val isLikelyTarget: Boolean
        get() = name.contains("ESP32", ignoreCase = true) ||
                name.contains("Gradiometer", ignoreCase = true)
}

data class BluetoothUiState(
    val hasPermission: Boolean = false,
    val bluetoothOn: Boolean = false,
    val scanned: Boolean = false,
    val devices: List<PairedDevice> = emptyList(),
    val selectedAddress: String? = null,
    val connection: BtState = BtState.Disconnected,
    val lastReading: GradiometerReading? = null,
    /** آخر N عينة (الأقدم أولاً) لرسم المخطط */
    val recent: List<GradiometerReading> = emptyList(),
    val totalSamples: Long = 0,
    val samplesPerSecond: Int = 0
)

class BluetoothControlViewModel(app: Application) : AndroidViewModel(app) {

    private val bt = BluetoothService(app)

    private val _ui = MutableStateFlow(BluetoothUiState())
    val ui: StateFlow<BluetoothUiState> = _ui.asStateFlow()

    // تُعدَّل كلها على الـ Main thread فقط (viewModelScope) فلا حاجة لمزامنة
    private val buffer = ArrayDeque<GradiometerReading>()
    private var total = 0L
    private var dirty = false

    init {
        refreshStatus()
        viewModelScope.launch { bt.state.collect { s -> _ui.update { it.copy(connection = s) } } }
        viewModelScope.launch { bt.readings.collect(::onReading) }
        startUiTicker()
    }

    // ------------------------------------------------------------ الأذونات والفحص

    fun refreshStatus() {
        _ui.update { it.copy(hasPermission = bt.hasPermission(), bluetoothOn = bt.isBluetoothOn) }
    }

    @SuppressLint("MissingPermission")
    fun scanPaired() {
        refreshStatus()
        if (!bt.hasPermission() || !bt.isBluetoothOn) return

        val list = bt.getPairedDevices().map { PairedDevice(it.name ?: "بدون اسم", it.address) }
        _ui.update { s ->
            val keep = s.selectedAddress?.takeIf { sel -> list.any { it.address == sel } }
            s.copy(
                scanned = true,
                devices = list,
                selectedAddress = keep ?: list.firstOrNull { it.isLikelyTarget }?.address
            )
        }
    }

    fun selectDevice(address: String) {
        _ui.update { it.copy(selectedAddress = address) }
    }

    // ------------------------------------------------------------------- الاتصال

    fun connect() {
        val s = _ui.value
        val address = s.selectedAddress ?: return
        if (s.connection is BtState.Connecting || s.connection is BtState.Connected) return
        val device = bt.getPairedDevices().firstOrNull { it.address == address } ?: return

        resetStats()
        viewModelScope.launch { bt.connect(device) } // الحالة تصل عبر bt.state
    }

    fun disconnect() = bt.disconnect()

    private fun resetStats() {
        buffer.clear()
        total = 0
        dirty = false
        _ui.update {
            it.copy(lastReading = null, recent = emptyList(), totalSamples = 0, samplesPerSecond = 0)
        }
    }

    // ------------------------------------------------------------ البيانات الحيّة

    private fun onReading(r: GradiometerReading) {
        buffer.addLast(r)
        if (buffer.size > MAX_BUFFER) buffer.removeFirst()
        total++
        dirty = true
    }

    /**
     * قد تصل مئات العينات في الثانية؛ تحديث الواجهة مع كل عينة يرهق الـ Compose.
     * لذلك نجمّع العينات وننشر الحالة 10 مرات في الثانية فقط.
     */
    private fun startUiTicker() = viewModelScope.launch {
        var lastTotal = 0L
        var lastTime = SystemClock.elapsedRealtime()
        while (true) {
            delay(UI_REFRESH_MS)
            val now = SystemClock.elapsedRealtime()
            var rate = _ui.value.samplesPerSecond
            if (now - lastTime >= 1000) {
                rate = ((total - lastTotal) * 1000 / (now - lastTime)).toInt()
                lastTotal = total
                lastTime = now
            }
            if (dirty || rate != _ui.value.samplesPerSecond) {
                dirty = false
                _ui.update {
                    it.copy(
                        lastReading = buffer.lastOrNull(),
                        recent = buffer.toList(),
                        totalSamples = total,
                        samplesPerSecond = rate
                    )
                }
            }
        }
    }

    override fun onCleared() {
        bt.release()
    }

    private companion object {
        const val MAX_BUFFER = 120
        const val UI_REFRESH_MS = 100L
    }
}
