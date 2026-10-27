#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup.py - ينشئ مشروع Gradiometer (Android / Jetpack Compose) كاملاً من ملف واحد.

الاستخدام:
    python setup.py            # ينشئ المجلد ./Gradiometer
    python setup.py MyFolder   # ينشئ المجلد المحدد

بعد التنفيذ: افتح المجلد في Android Studio (File > Open) وانتظر Gradle Sync.
"""
import os
import sys

FILES = {}

FILES['build.gradle.kts'] = r'''plugins {
    id("com.android.application") version "8.5.2" apply false
    id("org.jetbrains.kotlin.android") version "2.0.20" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.20" apply false
}
'''

FILES['.gitignore'] = r'''# Gradle
.gradle/
build/
!gradle/wrapper/gradle-wrapper.jar

# Android Studio / IntelliJ
.idea/
*.iml
local.properties
captures/
.externalNativeBuild/
.cxx/

# OS
.DS_Store
Thumbs.db

# Signing / secrets
*.jks
*.keystore
keystore.properties
'''

FILES['.gitattributes'] = r'''* text=auto
*.bat text eol=crlf
gradlew text eol=lf
*.jar binary
'''

FILES['README.md'] = r'''# Gradiometer

تطبيق Android (Kotlin + Jetpack Compose) لقراءة بيانات مقياس التدرج المغناطيسي من ESP32 عبر Bluetooth Classic (SPP)
وإنشاء خريطة مسح شبكية (2D / 3D) مع تحليل الذروة والمركز المقدَّر.

## المتطلبات
- Android Studio (إصدار حديث) و JDK 17
- minSdk 26 / targetSdk 34
- ESP32 يرسل سطراً نصياً لكل عينة، مثل: `1234,1198` (قيم مفصولة بفاصلة وينتهي بـ `\n`)

## التشغيل
1. افتح المجلد في Android Studio ثم انتظر Gradle Sync.
2. اقرن الـ ESP32 من إعدادات البلوتوث في الهاتف.
3. شغّل التطبيق، تبويب «الاتصال»: افحص الأجهزة ثم اتصل.
4. تبويب «المسح الشبكي»: ابدأ الجلسة وسجّل الخطوط واحداً تلو الآخر.

## البنية
- `bluetooth/BluetoothService.kt` — الاتصال وقراءة الأسطر
- `bluetooth/BluetoothControlViewModel.kt` / `BluetoothControlScreen.kt` — شاشة الاتصال والبيانات الحيّة
- `bluetooth/GridScanViewModel.kt` / `GridScanScreen.kt` — المسح الشبكي والتحليل
'''

FILES['gradle/wrapper/gradle-wrapper.properties'] = r'''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.7-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
'''

FILES['settings.gradle.kts'] = r'''pluginManagement {
    repositories {
        google()
        mavenCentral()
        gradlePluginPortal()
    }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        google()
        mavenCentral()
    }
}
rootProject.name = "Gradiometer"
include(":app")
'''

FILES['gradle.properties'] = r'''org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
android.useAndroidX=true
kotlin.code.style=official
android.nonTransitiveRClass=true
'''

FILES['app/build.gradle.kts'] = r'''plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

android {
    namespace = "com.example.gradiometer"
    compileSdk = 34

    defaultConfig {
        applicationId = "com.example.gradiometer"
        minSdk = 26
        targetSdk = 34
        versionCode = 1
        versionName = "1.0"
    }

    buildTypes {
        release {
            isMinifyEnabled = false
        }
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }
    kotlinOptions {
        jvmTarget = "17"
    }
    buildFeatures {
        compose = true
    }
}

dependencies {
    implementation(platform("androidx.compose:compose-bom:2024.09.03"))
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.foundation:foundation")
    implementation("androidx.compose.material3:material3")

    implementation("androidx.core:core-ktx:1.13.1")
    implementation("androidx.activity:activity-compose:1.9.2")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.6")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.6")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.6")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.8.1")
}
'''

FILES['app/src/main/AndroidManifest.xml'] = r'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.BLUETOOTH" android:maxSdkVersion="30" />
    <uses-permission android:name="android.permission.BLUETOOTH_ADMIN" android:maxSdkVersion="30" />
    <uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />

    <uses-feature android:name="android.hardware.bluetooth" android:required="false" />

    <application
        android:allowBackup="true"
        android:label="Gradiometer"
        android:supportsRtl="true"
        android:theme="@android:style/Theme.Material.Light.NoActionBar">
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>

</manifest>
'''

FILES['app/src/main/java/com/example/gradiometer/MainActivity.kt'] = r'''package com.example.gradiometer

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.Text
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.gradiometer.bluetooth.BluetoothControlScreen
import com.example.gradiometer.bluetooth.BluetoothControlViewModel
import com.example.gradiometer.bluetooth.GridScanScreen

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(Modifier.fillMaxSize()) {
                    // نسخة واحدة مشتركة بين التبويبين (مرتبطة بالـ Activity)
                    val btVm: BluetoothControlViewModel = viewModel()
                    var tab by rememberSaveable { mutableIntStateOf(0) }

                    Column(Modifier.fillMaxSize().statusBarsPadding()) {
                        TabRow(selectedTabIndex = tab) {
                            Tab(selected = tab == 0, onClick = { tab = 0 }, text = { Text("الاتصال") })
                            Tab(selected = tab == 1, onClick = { tab = 1 }, text = { Text("المسح الشبكي") })
                        }
                        when (tab) {
                            0 -> BluetoothControlScreen(vm = btVm)
                            else -> GridScanScreen(readings = btVm.readings)
                        }
                    }
                }
            }
        }
    }
}
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/BluetoothService.kt'] = r'''package com.example.gradiometer.bluetooth

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
import kotlinx.coroutines.channels.BufferOverflow
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
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/BluetoothControlViewModel.kt'] = r'''package com.example.gradiometer.bluetooth

import android.annotation.SuppressLint
import android.app.Application
import android.os.SystemClock
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
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

    /** تدفق العينات الحيّة (يستهلكه GridScanScreen) */
    val readings: SharedFlow<GradiometerReading> get() = bt.readings

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
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/BluetoothControlScreen.kt'] = r'''package com.example.gradiometer.bluetooth

import android.Manifest
import android.bluetooth.BluetoothAdapter
import android.content.Intent
import android.os.Build
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.draw.clip
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import java.text.SimpleDateFormat
import java.util.Locale

@Composable
fun BluetoothControlScreen(
    modifier: Modifier = Modifier,
    vm: BluetoothControlViewModel = viewModel()
) {
    val ui by vm.ui.collectAsStateWithLifecycle()

    // ---- مسار الأذونات: إذن -> تشغيل البلوتوث -> بحث ----
    val enableBtLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { vm.scanPaired() }

    fun proceed() {
        vm.refreshStatus()
        if (!vm.ui.value.bluetoothOn) {
            enableBtLauncher.launch(Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE))
        } else {
            vm.scanPaired()
        }
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        vm.refreshStatus()
        if (granted) proceed()
    }

    fun onScanClick() {
        vm.refreshStatus()
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S && !vm.ui.value.hasPermission) {
            permissionLauncher.launch(Manifest.permission.BLUETOOTH_CONNECT)
        } else {
            proceed()
        }
    }

    LazyColumn(
        modifier = modifier.fillMaxSize().padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        item { StatusCard(ui.connection) }
        item {
            DevicesCard(
                ui = ui,
                onScan = ::onScanClick,
                onSelect = vm::selectDevice,
                onConnect = vm::connect,
                onDisconnect = vm::disconnect
            )
        }
        item { LiveDataCard(ui) }
    }
}

// ============================================================ حالة الاتصال

private class StatusStyle(val label: String, val detail: String?, val color: Color)

private fun styleOf(s: BtState): StatusStyle = when (s) {
    BtState.Disconnected -> StatusStyle("غير متصل", null, Color(0xFF757575))
    BtState.Connecting -> StatusStyle("جارٍ الاتصال…", null, Color(0xFFF9A825))
    is BtState.Connected -> StatusStyle("متصل", s.deviceName, Color(0xFF2E7D32))
    is BtState.Error -> StatusStyle("خطأ", s.message, Color(0xFFC62828))
}

@Composable
private fun StatusCard(state: BtState) {
    val st = styleOf(state)
    Card(
        modifier = Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = st.color.copy(alpha = 0.14f))
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            if (state is BtState.Connecting) {
                CircularProgressIndicator(
                    modifier = Modifier.size(18.dp), strokeWidth = 2.dp, color = st.color
                )
            } else {
                Box(Modifier.size(18.dp).clip(CircleShape).background(st.color))
            }
            Column {
                Text(st.label, style = MaterialTheme.typography.titleMedium, color = st.color,
                    fontWeight = FontWeight.Bold)
                st.detail?.let { Text(it, style = MaterialTheme.typography.bodyMedium) }
            }
        }
    }
}

// ================================================================== الأجهزة

@Composable
private fun DevicesCard(
    ui: BluetoothUiState,
    onScan: () -> Unit,
    onSelect: (String) -> Unit,
    onConnect: () -> Unit,
    onDisconnect: () -> Unit
) {
    val connected = ui.connection is BtState.Connected
    val connecting = ui.connection is BtState.Connecting

    Card(Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("الأجهزة المقترنة", style = MaterialTheme.typography.titleMedium)

            Button(onClick = onScan, enabled = !connecting && !connected, modifier = Modifier.fillMaxWidth()) {
                Text("فحص الأذونات والبحث عن الأجهزة")
            }

            // رسائل تشخيصية
            if (!ui.hasPermission) {
                Hint("إذن البلوتوث غير ممنوح بعد.")
            } else if (!ui.bluetoothOn) {
                Hint("البلوتوث مُطفأ، سيُطلب تشغيله عند الفحص.")
            } else if (ui.scanned && ui.devices.isEmpty()) {
                Hint("لا توجد أجهزة مقترنة. اقترن بالـ ESP32 من إعدادات البلوتوث في الهاتف أولاً.")
            }

            ui.devices.forEach { d ->
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .selectable(
                            selected = d.address == ui.selectedAddress,
                            enabled = !connected && !connecting,
                            role = Role.RadioButton,
                            onClick = { onSelect(d.address) }
                        )
                        .padding(vertical = 6.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    RadioButton(selected = d.address == ui.selectedAddress, onClick = null)
                    Spacer(Modifier.size(12.dp))
                    Column(Modifier.weight(1f)) {
                        Text(d.name, style = MaterialTheme.typography.bodyLarge)
                        Text(d.address, style = MaterialTheme.typography.bodySmall,
                            fontFamily = FontFamily.Monospace)
                    }
                    if (d.isLikelyTarget) {
                        Text("مقترح", style = MaterialTheme.typography.labelMedium,
                            color = MaterialTheme.colorScheme.primary)
                    }
                }
            }

            if (connected) {
                OutlinedButton(onClick = onDisconnect, modifier = Modifier.fillMaxWidth()) {
                    Text("قطع الاتصال")
                }
            } else {
                Button(
                    onClick = onConnect,
                    enabled = ui.selectedAddress != null && !connecting,
                    modifier = Modifier.fillMaxWidth()
                ) { Text(if (connecting) "جارٍ الاتصال…" else "اتصال بالجهاز المختار") }
            }
        }
    }
}

@Composable
private fun Hint(text: String) {
    Text(text, style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant)
}

// ============================================================= البيانات الحيّة

private val channelColors = listOf(Color(0xFF1E88E5), Color(0xFFE53935), Color(0xFF43A047))

@Composable
private fun LiveDataCard(ui: BluetoothUiState) {
    val timeFmt = remember { SimpleDateFormat("HH:mm:ss.SSS", Locale.US) }
    val last = ui.lastReading

    Card(Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("البيانات الحيّة", style = MaterialTheme.typography.titleMedium)
                Text("${ui.samplesPerSecond} عينة/ث  •  ${ui.totalSamples}",
                    style = MaterialTheme.typography.labelMedium)
            }

            if (last == null) {
                Hint("لا توجد بيانات بعد… اتصل بالجهاز وتأكد أن الـ ESP32 يرسل أسطراً مثل: 1234,1198")
                return@Column
            }

            // القيم الحالية لكل قناة
            last.values.forEachIndexed { i, v ->
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Box(Modifier.size(10.dp).clip(CircleShape)
                        .background(channelColors[i % channelColors.size]))
                    Spacer(Modifier.size(8.dp))
                    Text("CH${i + 1}", Modifier.weight(0.25f), fontWeight = FontWeight.Bold)
                    Text(String.format(Locale.US, "%.2f", v), Modifier.weight(0.4f),
                        fontFamily = FontFamily.Monospace, fontSize = 20.sp)
                    Text(
                        String.format(Locale.US, "≈ %.4f V", BluetoothService.adsRawToVolts(v)),
                        Modifier.weight(0.35f),
                        style = MaterialTheme.typography.bodySmall,
                        fontFamily = FontFamily.Monospace
                    )
                }
            }
            Hint("الفولت يفترض قيماً خاماً من ADS1115 بمدى ±4.096V.")

            // مخطط مصغّر (مقياس مستقل لكل قناة)
            val channels = minOf(last.values.size, channelColors.size)
            val series = remember(ui.recent, channels) {
                List(channels) { c -> ui.recent.map { it.values.getOrNull(c)?.toFloat() ?: 0f } }
            }
            Sparkline(series, channelColors,
                Modifier.fillMaxWidth().height(100.dp)
                    .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f)))

            HorizontalDivider()

            // سجل آخر العينات (الأحدث أولاً)
            ui.recent.takeLast(6).asReversed().forEach { r ->
                Text(
                    timeFmt.format(r.timestampMs) + "  " +
                            r.values.joinToString(", ") { String.format(Locale.US, "%.1f", it) },
                    fontFamily = FontFamily.Monospace,
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

@Composable
private fun Sparkline(series: List<List<Float>>, colors: List<Color>, modifier: Modifier = Modifier) {
    Canvas(modifier) {
        series.forEachIndexed { idx, data ->
            if (data.size < 2) return@forEachIndexed
            val min = data.min()
            val range = (data.max() - min).takeIf { it > 1e-6f } ?: 1f
            val stepX = size.width / (data.size - 1)
            val pad = 6.dp.toPx()
            val h = size.height - 2 * pad

            val path = Path()
            data.forEachIndexed { i, v ->
                val p = Offset(i * stepX, pad + h * (1f - (v - min) / range))
                if (i == 0) path.moveTo(p.x, p.y) else path.lineTo(p.x, p.y)
            }
            drawPath(path, colors[idx % colors.size], style = Stroke(width = 2.dp.toPx()))
        }
    }
}
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/GridScanViewModel.kt'] = r'''package com.example.gradiometer.bluetooth

import android.os.SystemClock
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import kotlinx.coroutines.Job
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.sqrt

/** عدّل هذين الثابتين بعد معايرة الحساس (مثلاً لتحويل القيم الخام إلى nT) */
const val VALUE_SCALE = 1f
const val UNIT_LABEL = "raw"

// ============================================================== النماذج

data class GridConfig(
    val lines: Int = 10,            // عدد الخطوط (صفوف)
    val pointsPerLine: Int = 20,    // عدد النقاط على كل خط (أعمدة)
    val lineLengthM: Float = 10f,   // طول الخط بالمتر
    val lineSpacingM: Float = 1f,   // المسافة بين الخطوط بالمتر
    val zigzag: Boolean = true      // الخطوط الفردية تُمسح بالاتجاه المعاكس
)

enum class ScanPhase { Idle, ReadyForLine, Recording, Finished }

data class GridScanUiState(
    val config: GridConfig = GridConfig(),
    val phase: ScanPhase = ScanPhase.Idle,
    val currentLine: Int = 0,
    val completedLines: Int = 0,
    val lineSamples: Int = 0,
    /** مصفوفة الحساس الأول [الخط][النقطة] (NaN = لم تُقَس بعد) */
    val s1: List<FloatArray> = emptyList(),
    /** مصفوفة الحساس الثاني */
    val s2: List<FloatArray> = emptyList(),
    val message: String? = null
)

// ============================================================== ViewModel

class GridScanViewModel : ViewModel() {

    private val _ui = MutableStateFlow(GridScanUiState())
    val ui: StateFlow<GridScanUiState> = _ui.asStateFlow()

    private var boundSource: Any? = null
    private var collectJob: Job? = null

    private val b1 = FloatBuf()
    private val b2 = FloatBuf()
    private var recording = false
    private var lastPublish = 0L

    /** يربط تدفق العينات (آمن للاستدعاء المتكرر بنفس المصدر). يستمر الجمع حتى لو غادرت الشاشة. */
    fun bind(source: Flow<GradiometerReading>) {
        if (boundSource === source) return
        boundSource = source
        collectJob?.cancel()
        collectJob = viewModelScope.launch { source.collect(::onReading) }
    }

    private fun onReading(r: GradiometerReading) {
        if (!recording || r.values.isEmpty()) return
        b1.add((r.values[0] * VALUE_SCALE).toFloat())
        b2.add(if (r.values.size > 1) (r.values[1] * VALUE_SCALE).toFloat() else Float.NaN)

        // لا ننشر الحالة مع كل عينة (قد تصل مئات العينات في الثانية)
        val now = SystemClock.elapsedRealtime()
        if (now - lastPublish >= 150) {
            lastPublish = now
            _ui.update { it.copy(lineSamples = b1.n) }
        }
    }

    // ------------------------------------------------------------ الإعدادات

    fun setLines(v: Int) = editConfig { copy(lines = v.coerceIn(1, 60)) }
    fun setPoints(v: Int) = editConfig { copy(pointsPerLine = v.coerceIn(2, 100)) }
    fun setLineLength(v: Float) = editConfig { copy(lineLengthM = v.coerceIn(0.5f, 1000f)) }
    fun setLineSpacing(v: Float) = editConfig { copy(lineSpacingM = v.coerceIn(0.1f, 100f)) }
    fun setZigzag(v: Boolean) = editConfig { copy(zigzag = v) }

    private fun editConfig(block: GridConfig.() -> GridConfig) {
        if (_ui.value.phase == ScanPhase.Idle) _ui.update { it.copy(config = it.config.block()) }
    }

    // ---------------------------------------------------------- دورة الجلسة

    fun startSession() {
        val c = _ui.value.config
        recording = false
        b1.clear(); b2.clear()
        fun empty() = List(c.lines) { FloatArray(c.pointsPerLine) { Float.NaN } }
        _ui.update {
            it.copy(
                phase = ScanPhase.ReadyForLine, currentLine = 0, completedLines = 0,
                lineSamples = 0, s1 = empty(), s2 = empty(), message = null
            )
        }
    }

    fun startLine() {
        if (_ui.value.phase != ScanPhase.ReadyForLine) return
        b1.clear(); b2.clear()
        recording = true
        _ui.update { it.copy(phase = ScanPhase.Recording, lineSamples = 0, message = null) }
    }

    /** ينهي الخط: يعيد توزيع العينات المسجّلة بالتساوي على عدد النقاط ويخزّنها في صفّها */
    fun finishLine() {
        val s = _ui.value
        if (s.phase != ScanPhase.Recording) return
        recording = false

        if (b1.n < MIN_SAMPLES) {
            _ui.update {
                it.copy(phase = ScanPhase.ReadyForLine, lineSamples = 0,
                    message = "عدد العينات قليل جداً (${b1.n}). أعد تسجيل الخط.")
            }
            return
        }

        val c = s.config
        val row1 = resample(b1.toArray(), c.pointsPerLine)
        val row2 = resample(b2.toArray(), c.pointsPerLine)
        if (c.zigzag && s.currentLine % 2 == 1) { // الاتجاه المعاكس -> اقلب ليتطابق مع الموضع الفعلي
            row1.reverse(); row2.reverse()
        }

        val n1 = s.s1.toMutableList().also { it[s.currentLine] = row1 }
        val n2 = s.s2.toMutableList().also { it[s.currentLine] = row2 }
        val next = s.currentLine + 1
        val done = next >= c.lines

        _ui.update {
            it.copy(
                s1 = n1, s2 = n2,
                completedLines = it.completedLines + 1,
                currentLine = if (done) it.currentLine else next,
                phase = if (done) ScanPhase.Finished else ScanPhase.ReadyForLine,
                lineSamples = 0, message = null
            )
        }
    }

    fun discardLine() {
        recording = false
        _ui.update { it.copy(phase = ScanPhase.ReadyForLine, lineSamples = 0, message = null) }
    }

    /** إيقاف الجلسة مع الاحتفاظ بالخطوط المكتملة (الخط الجاري يُهمَل) */
    fun stopSession() {
        recording = false
        _ui.update { it.copy(phase = ScanPhase.Finished, lineSamples = 0, message = null) }
    }

    fun resetSession() {
        recording = false
        b1.clear(); b2.clear()
        _ui.update {
            it.copy(phase = ScanPhase.Idle, currentLine = 0, completedLines = 0, lineSamples = 0,
                s1 = emptyList(), s2 = emptyList(), message = null)
        }
    }

    private companion object { const val MIN_SAMPLES = 3 }
}

// ===================================================== أدوات مساعدة (رياضيات)

private class FloatBuf {
    private var a = FloatArray(1024)
    var n = 0; private set
    fun add(v: Float) { if (n == a.size) a = a.copyOf(n * 2); a[n++] = v }
    fun clear() { n = 0 }
    fun toArray(): FloatArray = a.copyOf(n)
}

/**
 * يحوّل عدداً غير محدد من العينات إلى [n] نقطة متساوية التباعد على الخط
 * (افتراض: سرعة مشي ثابتة ومعدل عينات ثابت).
 * - عينات أكثر من النقاط: متوسط كل مجموعة. - أقل: استيفاء خطي.
 */
internal fun resample(src: FloatArray, n: Int): FloatArray {
    if (src.isEmpty()) return FloatArray(n) { Float.NaN }
    if (src.size == 1) return FloatArray(n) { src[0] }
    val out = FloatArray(n)
    if (src.size >= n) {
        for (i in 0 until n) {
            val a = (i.toLong() * src.size / n).toInt()
            val b = max(a + 1, ((i + 1).toLong() * src.size / n).toInt()).coerceAtMost(src.size)
            var sum = 0f
            for (k in a until b) sum += src[k]
            out[i] = sum / (b - a)
        }
    } else {
        for (i in 0 until n) {
            val pos = i * (src.size - 1).toFloat() / (n - 1)
            val i0 = pos.toInt().coerceAtMost(src.size - 2)
            val f = pos - i0
            out[i] = src[i0] * (1 - f) + src[i0 + 1] * f
        }
    }
    return out
}

// ============================================================== التحليل

enum class FieldSource { S1, S2, Gradient }
enum class Background { None, GlobalMean, LineMean }

class FieldAnalysis(
    val matrix: List<FloatArray>,
    val lo: Float, val hi: Float,            // مدى الألوان
    val min: Float, val max: Float, val mean: Float, val std: Float,
    val peakRow: Int, val peakCol: Int, val peakValue: Float,
    val centroidRow: Float, val centroidCol: Float
)

private fun finiteMean(rows: List<FloatArray>): Float {
    var s = 0.0; var n = 0
    for (r in rows) for (v in r) if (v.isFinite()) { s += v; n++ }
    return if (n == 0) Float.NaN else (s / n).toFloat()
}

/**
 * يبني المصفوفة المعروضة (حساس 1 / حساس 2 / الفرق S1−S2)، يطرح الخلفية اختيارياً،
 * ثم يحسب الإحصاءات وذروة الشذوذ ومركز الهدف المقدّر (متوسط موزون للخلايا > 50% من الذروة).
 */
fun analyze(
    s1: List<FloatArray>, s2: List<FloatArray>,
    source: FieldSource, bg: Background
): FieldAnalysis? {
    val rows = s1.size
    if (rows == 0) return null
    val cols = s1[0].size

    val m = List(rows) { r ->
        FloatArray(cols) { c ->
            when (source) {
                FieldSource.S1 -> s1[r][c]
                FieldSource.S2 -> s2[r][c]
                FieldSource.Gradient -> s1[r][c] - s2[r][c]
            }
        }
    }

    when (bg) {
        Background.None -> Unit
        Background.GlobalMean -> {
            val mu = finiteMean(m)
            if (mu.isFinite()) m.forEach { row -> for (i in row.indices) row[i] -= mu }
        }
        Background.LineMean -> m.forEach { row ->
            val mu = finiteMean(listOf(row))
            if (mu.isFinite()) for (i in row.indices) row[i] -= mu
        }
    }

    var n = 0; var sum = 0.0
    var mn = Float.MAX_VALUE; var mx = -Float.MAX_VALUE
    for (row in m) for (v in row) if (v.isFinite()) {
        n++; sum += v
        if (v < mn) mn = v
        if (v > mx) mx = v
    }
    if (n == 0) return null
    val mean = (sum / n).toFloat()

    var sq = 0.0
    val vals = FloatArray(n)
    var k = 0
    for (row in m) for (v in row) if (v.isFinite()) { sq += (v - mean) * (v - mean); vals[k++] = v }
    val std = sqrt(sq / n).toFloat()
    vals.sort()
    val p2 = vals[((n - 1) * 0.02f).toInt()]
    val p98 = vals[((n - 1) * 0.98f).toInt()]

    // الذروة = أكبر انحراف مطلق عن الخلفية (الصفر بعد الطرح، وإلا المتوسط)
    val ref = if (bg == Background.None) mean else 0f
    var pr = 0; var pc = 0; var pd = 0f
    for (r in 0 until rows) for (c in 0 until cols) {
        val v = m[r][c]
        if (v.isFinite() && abs(v - ref) > abs(pd)) { pd = v - ref; pr = r; pc = c }
    }

    val thr = 0.5f * abs(pd)
    var wSum = 0.0; var rSum = 0.0; var cSum = 0.0
    for (r in 0 until rows) for (c in 0 until cols) {
        val v = m[r][c]
        if (!v.isFinite()) continue
        val d = v - ref
        if (d * pd > 0f && abs(d) >= thr) {
            val w = abs(d).toDouble()
            wSum += w; rSum += w * r; cSum += w * c
        }
    }

    var lo = p2; var hi = p98
    if (bg != Background.None) { // مقياس متماثل حول الصفر
        val lim = max(abs(p2), abs(p98)); lo = -lim; hi = lim
    }
    if (hi - lo < 1e-6f) hi = lo + 1f

    return FieldAnalysis(
        matrix = m, lo = lo, hi = hi, min = mn, max = mx, mean = mean, std = std,
        peakRow = pr, peakCol = pc, peakValue = m[pr][pc],
        centroidRow = if (wSum > 0) (rSum / wSum).toFloat() else pr.toFloat(),
        centroidCol = if (wSum > 0) (cSum / wSum).toFloat() else pc.toFloat()
    )
}
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/GridScanScreen.kt'] = r'''package com.example.gradiometer.bluetooth

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.FilterChip
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.lerp
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.flow.Flow
import java.util.Locale

// ===================================================================== الشاشة

/**
 * @param readings تدفق العينات الحيّة (مثلاً BluetoothControlViewModel.readings).
 *                 يُربط مرة واحدة بالـ ViewModel ويستمر الجمع حتى لو غادرت الشاشة.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun GridScanScreen(
    readings: Flow<GradiometerReading>,
    modifier: Modifier = Modifier,
    vm: GridScanViewModel = viewModel()
) {
    val ui by vm.ui.collectAsStateWithLifecycle()
    LaunchedEffect(readings) { vm.bind(readings) }

    var source by rememberSaveable { mutableStateOf(FieldSource.Gradient) }
    var bg by rememberSaveable { mutableStateOf(Background.GlobalMean) }
    var view3d by rememberSaveable { mutableStateOf(false) }
    var selected by remember(ui.s1) { mutableStateOf<Pair<Int, Int>?>(null) }

    // يُعاد الحساب فقط عند اكتمال خط/بدء جلسة أو تغيير خيارات التحليل
    val analysis = remember(ui.s1, ui.s2, source, bg) { analyze(ui.s1, ui.s2, source, bg) }

    Column(
        modifier = modifier
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        StatusCard(ui)

        ControlButtons(
            ui = ui,
            onStartSession = vm::startSession,
            onStartLine = vm::startLine,
            onFinishLine = vm::finishLine,
            onReset = vm::resetSession,
            onDiscardLine = vm::discardLine,
            onStopSession = vm::stopSession
        )

        // ---- خيارات العرض ----
        Card(Modifier.fillMaxWidth()) {
            Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("مصدر البيانات", style = MaterialTheme.typography.labelLarge)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    listOf(
                        FieldSource.S1 to "الحساس 1",
                        FieldSource.S2 to "الحساس 2",
                        FieldSource.Gradient to "الفرق S1−S2"
                    ).forEach { (v, label) ->
                        FilterChip(selected = source == v, onClick = { source = v }, label = { Text(label) })
                    }
                }
                Text("طرح الخلفية", style = MaterialTheme.typography.labelLarge)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    listOf(
                        Background.None to "بدون",
                        Background.GlobalMean to "متوسط عام",
                        Background.LineMean to "متوسط الخط"
                    ).forEach { (v, label) ->
                        FilterChip(selected = bg == v, onClick = { bg = v }, label = { Text(label) })
                    }
                }
                Text("نمط العرض", style = MaterialTheme.typography.labelLarge)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    FilterChip(selected = !view3d, onClick = { view3d = false }, label = { Text("خريطة حرارية 2D") })
                    FilterChip(selected = view3d, onClick = { view3d = true }, label = { Text("أعمدة 3D") })
                }
            }
        }

        // ---- الخريطة ----
        Card(Modifier.fillMaxWidth()) {
            Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                val cfg = ui.config
                val rows = if (ui.s1.isNotEmpty()) ui.s1.size else cfg.lines
                val cols = if (ui.s1.isNotEmpty()) ui.s1[0].size else cfg.pointsPerLine
                val ratio = if (view3d) 1.2f
                else (cfg.lineLengthM / (cfg.lines * cfg.lineSpacingM)).coerceIn(0.6f, 2.2f)

                val canvasMod = Modifier
                    .fillMaxWidth()
                    .aspectRatio(ratio)
                    .clip(RoundedCornerShape(8.dp))

                if (view3d) {
                    Canvas(canvasMod) { drawBars3D(analysis, rows, cols) }
                } else {
                    Canvas(
                        canvasMod.pointerInput(rows, cols) {
                            detectTapGestures { p ->
                                val c = (p.x / size.width * cols).toInt().coerceIn(0, cols - 1)
                                val r = (p.y / size.height * rows).toInt().coerceIn(0, rows - 1)
                                selected = r to c
                            }
                        }
                    ) {
                        drawHeatmap2D(analysis, rows, cols, ui, selected)
                    }
                }

                if (analysis != null) ColorBar(analysis.lo, analysis.hi)
                else Text(
                    if (ui.phase == ScanPhase.Idle) "ابدأ جلسة لعرض الخريطة" else "لا توجد بيانات مكتملة بعد",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )

                selected?.let { (r, c) ->
                    val v = analysis?.matrix?.getOrNull(r)?.getOrNull(c)
                    Text(
                        "الخط ${r + 1} • النقطة ${c + 1}: " +
                                if (v != null && v.isFinite()) "${v.f(2)} $UNIT_LABEL" else "لم تُقَس",
                        style = MaterialTheme.typography.bodyMedium,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        }

        // ---- التفاصيل ----
        if (analysis != null) AnalysisCard(analysis, ui.config)
    }
}

// ================================================================= أزرار التحكم

@Composable
private fun ControlButtons(
    ui: GridScanUiState,
    onStartSession: () -> Unit,
    onStartLine: () -> Unit,
    onFinishLine: () -> Unit,
    onReset: () -> Unit,
    onDiscardLine: () -> Unit,
    onStopSession: () -> Unit
) {
    val phase = ui.phase
    Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            Button(
                onClick = onStartSession,
                enabled = phase == ScanPhase.Idle || phase == ScanPhase.Finished,
                modifier = Modifier.weight(1f)
            ) { Text("بدء الجلسة") }

            FilledTonalButton(
                onClick = onStartLine,
                enabled = phase == ScanPhase.ReadyForLine,
                modifier = Modifier.weight(1f)
            ) { Text("بدء تسجيل خط") }
        }
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            FilledTonalButton(
                onClick = onFinishLine,
                enabled = phase == ScanPhase.Recording,
                modifier = Modifier.weight(1f)
            ) { Text("إنهاء الخط") }

            OutlinedButton(
                onClick = onReset,
                enabled = phase != ScanPhase.Idle,
                modifier = Modifier.weight(1f)
            ) { Text("إعادة الضبط") }
        }
        if (phase == ScanPhase.Recording) {
            TextButton(onClick = onDiscardLine, modifier = Modifier.fillMaxWidth()) {
                Text("تجاهل الخط الحالي")
            }
        } else if (phase == ScanPhase.ReadyForLine && ui.completedLines > 0) {
            TextButton(onClick = onStopSession, modifier = Modifier.fillMaxWidth()) {
                Text("إيقاف الجلسة بالخطوط المكتملة")
            }
        }
    }
}

@Composable
private fun StatusCard(ui: GridScanUiState) {
    val c = ui.config
    Card(
        Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.surfaceVariant)
    ) {
        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text(
                when (ui.phase) {
                    ScanPhase.Idle -> "جاهز — اضغط «بدء الجلسة»"
                    ScanPhase.ReadyForLine -> "جاهز للخط ${ui.currentLine + 1} من ${c.lines}"
                    ScanPhase.Recording -> "يسجّل الخط ${ui.currentLine + 1} • ${ui.lineSamples} عينة"
                    ScanPhase.Finished -> "اكتمل المسح (${ui.completedLines} خط)"
                },
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )

            if (ui.phase == ScanPhase.ReadyForLine || ui.phase == ScanPhase.Recording) {
                val toRight = !c.zigzag || ui.currentLine % 2 == 0
                Text(
                    "اتجاه المشي: " + if (toRight) "من اليسار إلى اليمين ➜" else "من اليمين إلى اليسار ⬅",
                    style = MaterialTheme.typography.bodyMedium
                )
            }
            if (ui.phase != ScanPhase.Idle) {
                LinearProgressIndicator(
                    progress = { if (c.lines > 0) ui.completedLines / c.lines.toFloat() else 0f },
                    modifier = Modifier.fillMaxWidth()
                )
            }
            ui.message?.let {
                Text(it, color = MaterialTheme.colorScheme.error, style = MaterialTheme.typography.bodyMedium)
            }
        }
    }
}

// ============================================================== بطاقة التحليل

@Composable
private fun AnalysisCard(a: FieldAnalysis, cfg: GridConfig) {
    // موضع النقطة بالمتر: العمود يمتد على طول الخط، والصف = رقم الخط × التباعد
    fun xM(col: Float) = col / (cfg.pointsPerLine - 1).coerceAtLeast(1) * cfg.lineLengthM
    fun yM(row: Float) = row * cfg.lineSpacingM

    Card(Modifier.fillMaxWidth()) {
        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text("تفاصيل التحليل", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
            HorizontalDivider()

            Text("الذروة (Peak)", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
            StatRow("القيمة", "${a.peakValue.f(2)} $UNIT_LABEL")
            StatRow("الموضع", "خط ${a.peakRow + 1} • نقطة ${a.peakCol + 1}")
            StatRow("الإحداثي", "x=${xM(a.peakCol.toFloat()).f(2)} م ، y=${yM(a.peakRow.toFloat()).f(2)} م")

            HorizontalDivider()
            Text("المركز المقدَّر (Centroid)", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
            StatRow("الموضع", "خط ${(a.centroidRow + 1).f(2)} • نقطة ${(a.centroidCol + 1).f(2)}")
            StatRow("الإحداثي", "x=${xM(a.centroidCol).f(2)} م ، y=${yM(a.centroidRow).f(2)} م")

            HorizontalDivider()
            Text("الإحصاءات", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
            StatRow("الأدنى / الأعلى", "${a.min.f(2)} / ${a.max.f(2)}")
            StatRow("المتوسط", a.mean.f(2))
            StatRow("الانحراف المعياري", a.std.f(2))
            StatRow("مدى الألوان (lo…hi)", "${a.lo.f(2)} … ${a.hi.f(2)} $UNIT_LABEL")
        }
    }
}

@Composable
private fun StatRow(label: String, value: String) {
    Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
        Text(label, style = MaterialTheme.typography.bodyMedium, color = MaterialTheme.colorScheme.onSurfaceVariant)
        Text(value, style = MaterialTheme.typography.bodyMedium, fontFamily = FontFamily.Monospace, fontWeight = FontWeight.Medium)
    }
}

@Composable
private fun ColorBar(lo: Float, hi: Float) {
    Column {
        Canvas(
            Modifier
                .fillMaxWidth()
                .height(12.dp)
                .clip(RoundedCornerShape(6.dp))
        ) {
            drawRect(Brush.horizontalGradient(HeatStops))
        }
        Spacer(Modifier.height(2.dp))
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            Text(lo.f(1), fontSize = 11.sp, fontFamily = FontFamily.Monospace)
            Text(UNIT_LABEL, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
            Text(hi.f(1), fontSize = 11.sp, fontFamily = FontFamily.Monospace)
        }
    }
}

// ============================================================== الرسم (2D)

private fun DrawScope.drawHeatmap2D(
    a: FieldAnalysis?,
    rows: Int, cols: Int,
    ui: GridScanUiState,
    selected: Pair<Int, Int>?
) {
    val cw = size.width / cols
    val ch = size.height / rows
    val empty = Color(0xFF2B2B2B)

    for (r in 0 until rows) for (c in 0 until cols) {
        val v = a?.matrix?.getOrNull(r)?.getOrNull(c)
        val color = if (a != null && v != null && v.isFinite()) heatColor(a.norm(v)) else empty
        // +0.5 لتفادي خطوط شعرية بين المربعات
        drawRect(color, Offset(c * cw, r * ch), Size(cw + 0.5f, ch + 0.5f))
    }

    // إبراز الخط الحالي
    if (ui.phase == ScanPhase.ReadyForLine || ui.phase == ScanPhase.Recording) {
        drawRect(
            color = if (ui.phase == ScanPhase.Recording) Color.White else Color.White.copy(alpha = 0.6f),
            topLeft = Offset(0f, ui.currentLine * ch),
            size = Size(size.width, ch),
            style = Stroke(width = 3f)
        )
    }

    // المربع المحدد
    selected?.let { (r, c) ->
        drawRect(Color.Black, Offset(c * cw, r * ch), Size(cw, ch), style = Stroke(5f))
        drawRect(Color.White, Offset(c * cw, r * ch), Size(cw, ch), style = Stroke(2.5f))
    }

    if (a != null) {
        // الذروة: حلقة
        val pc = Offset((a.peakCol + 0.5f) * cw, (a.peakRow + 0.5f) * ch)
        val rad = minOf(cw, ch) * 0.8f
        drawCircle(Color.Black, rad, pc, style = Stroke(5f))
        drawCircle(Color.White, rad, pc, style = Stroke(2.5f))

        // المركز: علامة +
        val cc = Offset((a.centroidCol + 0.5f) * cw, (a.centroidRow + 0.5f) * ch)
        val arm = minOf(cw, ch) * 1.2f
        for ((col, w) in listOf(Color.Black to 6f, Color.White to 3f)) {
            drawLine(col, Offset(cc.x - arm, cc.y), Offset(cc.x + arm, cc.y), w)
            drawLine(col, Offset(cc.x, cc.y - arm), Offset(cc.x, cc.y + arm), w)
        }
    }
}

// ============================================================== الرسم (3D)

private const val COS30 = 0.866f

/** عرض أيزومتري: كل خلية عمود ارتفاعه يتناسب مع القيمة المُطبَّعة (الرسم من الخلف للأمام). */
private fun DrawScope.drawBars3D(a: FieldAnalysis?, rows: Int, cols: Int) {
    val hMax = maxOf(rows, cols) * 0.35f

    val minX = -rows * COS30
    val maxX = cols * COS30
    val minY = -hMax
    val maxY = (rows + cols) * 0.5f
    val sc = minOf(size.width / (maxX - minX), size.height / (maxY - minY)) * 0.95f
    val ox = -minX * sc + (size.width - (maxX - minX) * sc) / 2f
    val oy = -minY * sc + (size.height - (maxY - minY) * sc) / 2f

    fun pt(x: Float, y: Float, z: Float) =
        Offset(ox + (x - y) * COS30 * sc, oy + ((x + y) * 0.5f - z) * sc)

    fun poly(color: Color, p0: Offset, p1: Offset, p2: Offset, p3: Offset) {
        val path = Path().apply {
            moveTo(p0.x, p0.y); lineTo(p1.x, p1.y); lineTo(p2.x, p2.y); lineTo(p3.x, p3.y); close()
        }
        drawPath(path, color)
    }

    for (d in 0..(rows + cols - 2)) {
        for (r in maxOf(0, d - cols + 1)..minOf(rows - 1, d)) {
            val c = d - r
            val v = a?.matrix?.getOrNull(r)?.getOrNull(c)
            val valid = a != null && v != null && v.isFinite()
            val t = if (valid) a!!.norm(v!!) else 0f
            val z = t * hMax
            val top = if (valid) heatColor(t) else Color(0xFF3A3A3A)
            val side = lerp(top, Color.Black, 0.35f)
            val side2 = lerp(top, Color.Black, 0.2f)
            val x0 = c.toFloat(); val x1 = x0 + 1f
            val y0 = r.toFloat(); val y1 = y0 + 1f

            if (z > 0.01f) {
                poly(side, pt(x1, y0, z), pt(x1, y1, z), pt(x1, y1, 0f), pt(x1, y0, 0f)) // الوجه الأيمن
                poly(side2, pt(x0, y1, z), pt(x1, y1, z), pt(x1, y1, 0f), pt(x0, y1, 0f)) // الوجه الأمامي
            }
            poly(top, pt(x0, y0, z), pt(x1, y0, z), pt(x1, y1, z), pt(x0, y1, z))
        }
    }
}

// ===================================================================== ألوان

private val HeatStops = listOf(
    Color(0xFF1F3BFF), // أزرق (lo)
    Color(0xFF00C8FF),
    Color(0xFF2ECC40),
    Color(0xFFFFE600),
    Color(0xFFE5161B)  // أحمر (hi)
)

private fun heatColor(t: Float): Color {
    val x = t.coerceIn(0f, 1f) * (HeatStops.size - 1)
    val i = x.toInt().coerceAtMost(HeatStops.size - 2)
    return lerp(HeatStops[i], HeatStops[i + 1], x - i)
}

/** تطبيع القيمة إلى [0..1] وفق lo/hi من FieldAnalysis */
private fun FieldAnalysis.norm(v: Float): Float = ((v - lo) / (hi - lo)).coerceIn(0f, 1f)

private fun Float.f(digits: Int = 2): String = String.format(Locale.US, "%.${digits}f", this)
'''


def main():
    root = sys.argv[1] if len(sys.argv) > 1 else "Gradiometer"
    for rel, content in FILES.items():
        path = os.path.join(root, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)
        print("created:", path)
    print("\nتم. افتح المجلد '%s' في Android Studio." % root)


if __name__ == "__main__":
    main()
