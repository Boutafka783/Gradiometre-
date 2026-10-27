package com.example.gradiometer.bluetooth

import android.Manifest
import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.bluetooth.BluetoothSocket
import android.content.Context
import android.content.pm.PackageManager
import android.os.Build
import androidx.core.content.ContextCompat
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.flow.BufferOverflow
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.io.BufferedReader
import java.io.IOException
import java.io.InputStreamReader
import java.io.OutputStream
import java.util.UUID

/** قراءة واحدة: وقت الاستلام + مصفوفة القنوات (مثلاً: [حساس1, حساس2]) */
class GradiometerReading(
    val timestampMs: Long,
    val values: DoubleArray
)

sealed interface BtState {
    data object Disconnected : BtState
    data object Connecting : BtState
    data class Connected(val deviceName: String) : BtState
    data class Error(val message: String) : BtState
}

/**
 * خدمة البلوتوث (Bluetooth Classic - SPP) للاتصال مع ESP32.
 *
 * البروتوكول المتوقع من ESP32: سطر نصي لكل عينة، القيم مفصولة بفاصلة وينتهي بـ \n
 * مثال:  "1234,1198\n"  أو  "12.5,11.9,0.3\n"
 */
class BluetoothService(context: Context) {

    private val appContext = context.applicationContext
    private val adapter: BluetoothAdapter? =
        (appContext.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager)?.adapter

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)
    private var readJob: Job? = null
    private var socket: BluetoothSocket? = null
    private var output: OutputStream? = null

    private val _state = MutableStateFlow<BtState>(BtState.Disconnected)
    val state: StateFlow<BtState> = _state.asStateFlow()

    // DROP_OLDEST حتى لا يتوقف القارئ إذا كانت الواجهة أبطأ من البيانات
    private val _readings = MutableSharedFlow<GradiometerReading>(
        extraBufferCapacity = 512,
        onBufferOverflow = BufferOverflow.DROP_OLDEST
    )
    val readings: SharedFlow<GradiometerReading> = _readings.asSharedFlow()

    // ---------------------------------------------------------------- الأذونات

    fun hasPermission(): Boolean =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            ContextCompat.checkSelfPermission(
                appContext, Manifest.permission.BLUETOOTH_CONNECT
            ) == PackageManager.PERMISSION_GRANTED
        } else true

    val isBluetoothOn: Boolean get() = adapter?.isEnabled == true

    // ---------------------------------------------------- 1) الأجهزة المقترنة

    @SuppressLint("MissingPermission")
    fun getPairedDevices(): List<BluetoothDevice> {
        if (!hasPermission()) return emptyList()
        return adapter?.bondedDevices?.toList().orEmpty()
    }

    /** يبحث بالاسم بين الأجهزة المقترنة (مثلاً "Gradiometer" أو "ESP32") */
    @SuppressLint("MissingPermission")
    fun findPairedByName(namePart: String): BluetoothDevice? =
        getPairedDevices().firstOrNull {
            it.name?.contains(namePart, ignoreCase = true) == true
        }

    // ------------------------------------------------------------- الاتصال

    @SuppressLint("MissingPermission")
    suspend fun connect(device: BluetoothDevice): Result<Unit> = withContext(Dispatchers.IO) {
        if (!hasPermission()) {
            _state.value = BtState.Error("إذن BLUETOOTH_CONNECT غير ممنوح")
            return@withContext Result.failure(SecurityException("No BT permission"))
        }
        disconnect()
        _state.value = BtState.Connecting
        try {
            adapter?.cancelDiscovery() // البحث الجاري يبطئ/يفشل الاتصال
            val s = device.createRfcommSocketToServiceRecord(SPP_UUID)
            s.connect() // blocking
            socket = s
            output = s.outputStream
            _state.value = BtState.Connected(device.name ?: device.address)
            startReading(s)
            Result.success(Unit)
        } catch (e: IOException) {
            closeQuietly()
            _state.value = BtState.Error(e.message ?: "فشل الاتصال")
            Result.failure(e)
        }
    }

    fun disconnect() {
        readJob?.cancel()
        readJob = null
        closeQuietly()
        if (_state.value !is BtState.Error) _state.value = BtState.Disconnected
    }

    /** إرسال أمر إلى ESP32 (مثلاً "START\n" أو "CAL\n") */
    suspend fun send(command: String): Result<Unit> = withContext(Dispatchers.IO) {
        try {
            output?.apply { write(command.toByteArray()); flush() }
                ?: return@withContext Result.failure(IOException("غير متصل"))
            Result.success(Unit)
        } catch (e: IOException) {
            Result.failure(e)
        }
    }

    /** يجب استدعاؤها عند التخلص من الخدمة (onCleared في الـ ViewModel) */
    fun release() {
        disconnect()
        scope.cancel()
    }

    // ------------------------------------------- 2) حلقة القراءة في الخلفية

    private fun startReading(s: BluetoothSocket) {
        readJob = scope.launch {
            try {
                val reader = BufferedReader(InputStreamReader(s.inputStream, Charsets.US_ASCII))
                while (isActive) {
                    // readLine تحجب الخيط؛ إغلاق الـ socket ينهيها بـ IOException
                    val line = reader.readLine() ?: break
                    val values = parseLine(line) ?: continue
                    _readings.tryEmit(GradiometerReading(System.currentTimeMillis(), values))
                }
            } catch (e: IOException) {
                if (isActive) _state.value = BtState.Error("انقطع الاتصال: ${e.message}")
            } finally {
                closeQuietly()
                if (_state.value is BtState.Connected) _state.value = BtState.Disconnected
            }
        }
    }

    private fun closeQuietly() {
        try { output?.close() } catch (_: IOException) {}
        try { socket?.close() } catch (_: IOException) {}
        output = null
        socket = null
    }

    companion object {
        /** UUID القياسي لـ Serial Port Profile (يستخدمه BluetoothSerial في ESP32) */
        val SPP_UUID: UUID = UUID.fromString("00001101-0000-1000-8000-00805F9B34FB")

        // ---------------------------------------- 3) فك تحويل البيانات

        /**
         * يحوّل سطراً نصياً إلى مصفوفة أرقام.
         * يقبل الفواصل "," أو ";" أو المسافات، ويتجاهل بادئة مثل "D:".
         * يرجع null إذا كان السطر فارغاً أو تالفاً (قيمة غير رقمية).
         */
        fun parseLine(raw: String): DoubleArray? {
            var line = raw.trim()
            if (line.isEmpty()) return null
            val colon = line.indexOf(':')
            if (colon in 0..3) line = line.substring(colon + 1).trim() // "D:1,2" -> "1,2"

            val parts = line.split(',', ';', ' ', '\t').filter { it.isNotBlank() }
            if (parts.isEmpty()) return null

            val out = DoubleArray(parts.size)
            for (i in parts.indices) {
                out[i] = parts[i].toDoubleOrNull() ?: return null // سطر تالف -> تجاهله كاملاً
            }
            return out
        }

        /**
         * تحويل قراءة ADS1115 الخام (16-bit signed) إلى فولت.
         * fullScaleVolts حسب الـ gain: ±6.144 / ±4.096 / ±2.048 / ±1.024 / ±0.512 / ±0.256
         */
        fun adsRawToVolts(raw: Double, fullScaleVolts: Double = 4.096): Double =
            raw * fullScaleVolts / 32768.0
    }
}
