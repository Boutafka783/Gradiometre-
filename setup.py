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

## التبويبات الثلاثة
1. **الجراديومتر — بحث حي**: الاتصال بالـ ESP32 + قراءة الحساس 1 والحساس 2 والفرق بينهما لحظياً مع مخططات.
2. **الجراديومتر — تجميع البيانات**: مسح شبكي بالحساسين (الحساس 1 / الحساس 2 / الفرق) مع خريطة 2D/3D وتحليل الذروة والمركز.
3. **الماغنومتر — تجميع البيانات**: نفس المسح الشبكي لكن بالحساس السفلي فقط (يُختار من أعلى الشاشة).

## التشغيل
1. افتح المجلد في Android Studio ثم انتظر Gradle Sync.
2. اقرن الـ ESP32 من إعدادات البلوتوث في الهاتف.
3. شغّل التطبيق: في التبويب الأول افحص الأجهزة ثم اتصل.
4. في تبويبي التجميع: ابدأ الجلسة وسجّل الخطوط واحداً تلو الآخر.

## البنية
- `bluetooth/BluetoothService.kt` — الاتصال وقراءة الأسطر (تدفق `readings`)
- `bluetooth/BluetoothControlViewModel.kt` — حالة الاتصال والبيانات الحيّة (يعرّض `readings`)
- `bluetooth/BluetoothControlScreen.kt` — مكوّنات الاتصال المشتركة (حالة، أجهزة، شريط علوي، مخطط)
- `bluetooth/LiveSearchScreen.kt` — تبويب البحث الحي
- `bluetooth/GridScanViewModel.kt` / `GridScanScreen.kt` — محرك المسح الشبكي والتحليل
- `bluetooth/HeatmapColors.kt` — لوحات الألوان ونطاق الألوان الديناميكي/المخصص
- `bluetooth/DepthEstimation.kt` — تقدير عمق الهدف (نصف العرض + الميل الأقصى)
- `bluetooth/SurveyStore.kt` / `SurveyArchive.kt` — حفظ المسوحات على بطاقة SD/الذاكرة (JSON) وعرضها لاحقاً وتصدير CSV
- `bluetooth/Interactive3D.kt` — مجسّم 3D قابل للتدوير والتكبير وعزل الهدف (سطح/أعمدة)
- `bluetooth/FinalInspectionScreen.kt` — التبويب الرابع: فحص نهائي بملء الشاشة (تدرج لوني + عمق، S1−S2)
- `bluetooth/LiveDiff3D.kt` — إشارة S1−S2 ثلاثية الأبعاد بتدرج لوني في تبويب البحث الحي
- `bluetooth/GradiometerDataScreen.kt` / `MagnetometerDataScreen.kt` — تبويبا التجميع (جلسة مستقلة لكل منهما)
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
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.gradiometer.bluetooth.BluetoothControlViewModel
import com.example.gradiometer.bluetooth.ConnectionStrip
import com.example.gradiometer.bluetooth.FinalInspectionScreen
import com.example.gradiometer.bluetooth.GradiometerDataScreen
import com.example.gradiometer.bluetooth.LiveSearchScreen
import com.example.gradiometer.bluetooth.MagnetometerDataScreen

private val TAB_TITLES = listOf(
    "الجراديومتر\nبحث حي",
    "الجراديومتر\nتجميع البيانات",
    "الماغنومتر\nتجميع البيانات",
    "فحص نهائي\nجراديومتر"
)

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            MaterialTheme {
                Surface(Modifier.fillMaxSize()) {
                    // نسخة واحدة من الاتصال مشتركة بين التبويبات الثلاثة (مرتبطة بالـ Activity)
                    val btVm: BluetoothControlViewModel = viewModel()
                    val ui by btVm.ui.collectAsStateWithLifecycle()
                    var tab by rememberSaveable { mutableIntStateOf(0) }

                    Column(Modifier.fillMaxSize().statusBarsPadding()) {
                        // التبويب الرابع (الفحص النهائي) بملء الشاشة: نخفي الشريط العلوي
                        if (tab != 3) {
                        TabRow(selectedTabIndex = tab) {
                            TAB_TITLES.forEachIndexed { i, title ->
                                Tab(
                                    selected = tab == i,
                                    onClick = { tab = i },
                                    text = {
                                        Text(
                                            title,
                                            fontSize = 12.sp,
                                            maxLines = 2,
                                            textAlign = TextAlign.Center
                                        )
                                    }
                                )
                            }
                        }

                        ConnectionStrip(ui.connection, ui.samplesPerSecond)
                        }

                        when (tab) {
                            0 -> LiveSearchScreen(modifier = Modifier.weight(1f), vm = btVm)
                            1 -> GradiometerDataScreen(
                                readings = btVm.readings,
                                modifier = Modifier.weight(1f)
                            )
                            2 -> MagnetometerDataScreen(
                                readings = btVm.readings,
                                modifier = Modifier.weight(1f)
                            )
                            else -> FinalInspectionScreen(
                                onClose = { tab = 1 },
                                modifier = Modifier.weight(1f)
                            )
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
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.selection.selectable
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.semantics.Role
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp

/*
 * مكوّنات الاتصال المشتركة (تُستخدم في تبويب «بحث حي» وفي شريط الحالة العلوي).
 * بقي اسم الملف كما هو حتى لا يتعارض مع نسخة قديمة إن كانت مرفوعة على GitHub.
 */

// ============================================================ مسار الأذونات

/** أذونات -> تشغيل البلوتوث -> عرض الأجهزة المقترنة والاتصال. */
@Composable
internal fun BluetoothDevicesPanel(vm: BluetoothControlViewModel, ui: BluetoothUiState) {
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

    DevicesCard(
        ui = ui,
        onScan = ::onScanClick,
        onSelect = vm::selectDevice,
        onConnect = vm::connect,
        onDisconnect = vm::disconnect
    )
}

// ============================================================ حالة الاتصال

internal class StatusStyle(val label: String, val detail: String?, val color: Color)

internal fun styleOf(s: BtState): StatusStyle = when (s) {
    BtState.Disconnected -> StatusStyle("غير متصل", null, Color(0xFF757575))
    BtState.Connecting -> StatusStyle("جارٍ الاتصال…", null, Color(0xFFF9A825))
    is BtState.Connected -> StatusStyle("متصل", s.deviceName, Color(0xFF2E7D32))
    is BtState.Error -> StatusStyle("خطأ", s.message, Color(0xFFC62828))
}

@Composable
internal fun ConnectionStatusCard(state: BtState) {
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

/** شريط رفيع يظهر فوق كل التبويبات ليبقى الاتصال مرئياً أثناء العمل الميداني. */
@Composable
internal fun ConnectionStrip(state: BtState, samplesPerSecond: Int) {
    val st = styleOf(state)
    val extra = st.detail?.let { " • $it" } ?: ""
    val rate = if (state is BtState.Connected) "  •  $samplesPerSecond عينة/ث" else ""
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .background(st.color.copy(alpha = 0.14f))
            .padding(horizontal = 12.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Box(Modifier.size(8.dp).clip(CircleShape).background(st.color))
        Text(st.label + extra + rate, style = MaterialTheme.typography.labelMedium, color = st.color)
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

// ================================================================ أدوات مشتركة

@Composable
internal fun Hint(text: String) {
    Text(text, style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant)
}

/**
 * مخطط خطي مصغّر.
 * sharedScale = true : كل الخطوط على مقياس واحد (للمقارنة المباشرة بين الحساسين).
 * sharedScale = false: لكل خط مقياسه المستقل.
 */
@Composable
internal fun Sparkline(
    series: List<List<Float>>,
    colors: List<Color>,
    modifier: Modifier = Modifier,
    sharedScale: Boolean = false
) {
    Canvas(modifier) {
        val all = series.flatten()
        val gMin = all.minOrNull() ?: return@Canvas
        val gMax = all.maxOrNull() ?: return@Canvas

        series.forEachIndexed { idx, data ->
            if (data.size < 2) return@forEachIndexed
            val lo = if (sharedScale) gMin else data.min()
            val hi = if (sharedScale) gMax else data.max()
            val range = (hi - lo).takeIf { it > 1e-6f } ?: 1f
            val stepX = size.width / (data.size - 1)
            val pad = 6.dp.toPx()
            val h = size.height - 2 * pad

            val path = Path()
            data.forEachIndexed { i, v ->
                val p = Offset(i * stepX, pad + h * (1f - (v - lo) / range))
                if (i == 0) path.moveTo(p.x, p.y) else path.lineTo(p.x, p.y)
            }
            drawPath(path, colors[idx % colors.size], style = Stroke(width = 2.dp.toPx()))
        }
    }
}
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/LiveDiff3D.kt'] = r'''package com.example.gradiometer.bluetooth

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Card
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
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
import androidx.compose.ui.graphics.luminance
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import java.util.Locale
import kotlin.math.abs
import kotlin.math.exp
import kotlin.math.max
import kotlin.math.min

/** عدد العينات الأخيرة المعروضة في المنظر ثلاثي الأبعاد */
private const val WINDOW = 60

/** إشارة تجريبية (قمة موجبة + فص سالب) لمعاينة التدرج اللوني قبل وصول بيانات حقيقية */
private val DemoSeries: List<Float> = List(WINDOW) { i ->
    val a = (i - 26) / 6f
    val b = (i - 40) / 5f
    150f * exp(-a * a) - 80f * exp(-b * b)
}

private fun fmt(v: Float, digits: Int = 1): String = String.format(Locale.US, "%.${digits}f", v)

/**
 * بطاقة تبويب «بحث حي»: إشارة الجراديومتر (الفرق S1 − S2) كأعمدة ثلاثية الأبعاد ملوّنة بتدرج حسب القيمة.
 * - الأحدث إلى اليمين (مؤطَّر بالأبيض)، الارتفاع = الفرق (موجب لأعلى، سالب لأسفل).
 * - اللون: بارد (أزرق) للقيم السالبة ← الأخضر حول الصفر ← ساخن (أصفر/أحمر) للقيم الموجبة (لوحة حرارية افتراضياً).
 * - «طرح الإزاحة» يزيل متوسط النافذة ليظهر الشذوذ بدل فرق الحساسين الثابت.
 * - «حساسية الألوان» تضيّق مدى الألوان فتتشبّع الإشارات الضعيفة بسرعة وتُرى بوضوح.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun DiffSignal3DCard(recent: List<GradiometerReading>, modifier: Modifier = Modifier) {
    var palette by rememberSaveable { mutableStateOf(Palette.Thermal) }
    var gain by rememberSaveable { mutableFloatStateOf(1f) }
    var removeOffset by rememberSaveable { mutableStateOf(true) }

    val raw = remember(recent) {
        recent.takeLast(WINDOW).mapNotNull { r ->
            val a = r.values.getOrNull(0)
            val b = r.values.getOrNull(1)
            if (a != null && b != null) (a - b).toFloat() else null
        }
    }
    val live = raw.size >= 2
    val series = if (live) raw else DemoSeries
    val diff = if (removeOffset) {
        val mu = series.average().toFloat()
        series.map { it - mu }
    } else series
    val maxAbs = max(diff.maxOf { abs(it) }, 1e-3f)
    val lim = maxAbs / gain
    val colorScale = ColorScale(-lim, lim, palette)
    val current = diff.last()
    val tileColor = colorScale.color(current)

    Card(modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Text("الإشارة ثلاثية الأبعاد (S1 − S2)", style = MaterialTheme.typography.titleMedium)
            if (!live) {
                Text(
                    "معاينة تجريبية للتدرج اللوني — تظهر القراءات الحقيقية عند الاتصال بالجهاز وإرسال قناتين.",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }

            // لون اللحظة الحالية
            Box(
                Modifier
                    .fillMaxWidth()
                    .height(56.dp)
                    .clip(RoundedCornerShape(10.dp))
                    .background(tileColor),
                contentAlignment = Alignment.Center
            ) {
                Text(
                    (if (current > 0f) "+" else "") + fmt(current, 1),
                    fontSize = 26.sp,
                    fontFamily = FontFamily.Monospace,
                    fontWeight = FontWeight.Bold,
                    color = if (tileColor.luminance() > 0.5f) Color.Black else Color.White
                )
            }

            Canvas(
                Modifier
                    .fillMaxWidth()
                    .height(210.dp)
                    .clip(RoundedCornerShape(8.dp))
                    .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f))
            ) { drawDiffBars3D(diff, maxAbs, colorScale) }

            SignalColorBar(colorScale, current)

            Text("لوحة الألوان", style = MaterialTheme.typography.labelLarge)
            FlowRow(
                horizontalArrangement = Arrangement.spacedBy(8.dp),
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                Palette.values().forEach { p ->
                    FilterChip(selected = palette == p, onClick = { palette = p }, label = { Text(p.label) })
                }
                FilterChip(
                    selected = removeOffset,
                    onClick = { removeOffset = !removeOffset },
                    label = { Text("طرح الإزاحة") }
                )
            }

            Text(
                "حساسية الألوان ×${fmt(gain, 1)}  (تشبّع عند ±${fmt(lim, 0)})",
                style = MaterialTheme.typography.bodySmall
            )
            Slider(value = gain, onValueChange = { gain = it }, valueRange = 1f..10f)
        }
    }
}

/** شريط التدرج مع مؤشر القيمة الحالية */
@Composable
private fun SignalColorBar(cs: ColorScale, current: Float) {
    Column {
        Canvas(
            Modifier
                .fillMaxWidth()
                .height(16.dp)
                .clip(RoundedCornerShape(6.dp))
        ) {
            drawRect(Brush.horizontalGradient(cs.palette.stops))
            val t = ((current - cs.lo) / (cs.hi - cs.lo)).coerceIn(0f, 1f)
            val x = t * size.width
            drawLine(Color.Black, Offset(x, 0f), Offset(x, size.height), 5f)
            drawLine(Color.White, Offset(x, 0f), Offset(x, size.height), 2.5f)
        }
        CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Ltr) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(fmt(cs.lo, 0), fontSize = 11.sp, fontFamily = FontFamily.Monospace)
                Text("0", fontSize = 11.sp, fontFamily = FontFamily.Monospace)
                Text(fmt(cs.hi, 0), fontSize = 11.sp, fontFamily = FontFamily.Monospace)
            }
        }
    }
}

/** أعمدة بإسقاط مائل: الوجه الأمامي + العلوي (أفتح) + الأيمن (أغمق) */
private fun DrawScope.drawDiffBars3D(diff: List<Float>, maxAbs: Float, cs: ColorScale) {
    val n = diff.size
    val depthX = size.width * 0.04f
    val depthY = depthX * 0.8f
    val plotW = size.width - depthX
    val pitch = plotW / n
    val barW = pitch * 0.72f
    val zeroY = depthY + (size.height - depthY) / 2f
    val halfH = (size.height - depthY) / 2f * 0.92f

    fun quad(color: Color, a: Offset, b: Offset, c: Offset, d: Offset) {
        val path = Path().apply {
            moveTo(a.x, a.y); lineTo(b.x, b.y); lineTo(c.x, c.y); lineTo(d.x, d.y); close()
        }
        drawPath(path, color)
    }

    // خط الصفر (أمامي وخلفي)
    val grid = Color.Gray.copy(alpha = 0.6f)
    drawLine(grid, Offset(0f, zeroY), Offset(plotW, zeroY), 1.5f)
    drawLine(grid, Offset(depthX, zeroY - depthY), Offset(size.width, zeroY - depthY), 1.5f)

    var lastX = 0f
    var lastTop = 0f
    var lastH = 0f
    for (i in 0 until n) {
        val v = diff[i]
        val h = v / maxAbs * halfH
        val x0 = i * pitch + (pitch - barW) / 2f
        val x1 = x0 + barW
        val yTop = min(zeroY - h, zeroY)
        val yBot = max(zeroY - h, zeroY)
        val base = cs.color(v)
        val topColor = lerp(base, Color.White, 0.25f)
        val sideColor = lerp(base, Color.Black, 0.3f)

        drawRect(base, Offset(x0, yTop), Size(barW, max(yBot - yTop, 1f)))
        quad(sideColor, Offset(x1, yTop), Offset(x1 + depthX, yTop - depthY),
            Offset(x1 + depthX, yBot - depthY), Offset(x1, yBot))
        quad(topColor, Offset(x0, yTop), Offset(x1, yTop),
            Offset(x1 + depthX, yTop - depthY), Offset(x0 + depthX, yTop - depthY))

        lastX = x0; lastTop = yTop; lastH = max(yBot - yTop, 1f)
    }

    // إبراز أحدث عينة
    drawRect(Color.White, Offset(lastX, lastTop), Size(barW, lastH), style = Stroke(2.5f))
}
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/LiveSearchScreen.kt'] = r'''package com.example.gradiometer.bluetooth

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
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Card
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import java.text.SimpleDateFormat
import java.util.Locale
import kotlin.math.abs

private val Sensor1Color = Color(0xFF1E88E5)
private val Sensor2Color = Color(0xFFE53935)
private val DiffColor = Color(0xFF8E24AA)

/**
 * تبويب 1: الجراديومتر — بحث حي.
 * يعرض لحظياً قراءة الحساس 1 والحساس 2 والفرق بينهما، مع الاتصال بالجهاز.
 * المنطق (الاستقبال والتجميع الدوري للعينات) موجود في BluetoothControlViewModel
 * الذي يجمع تدفق readings القادم من BluetoothService.
 */
@Composable
fun LiveSearchScreen(
    modifier: Modifier = Modifier,
    vm: BluetoothControlViewModel = viewModel()
) {
    val ui by vm.ui.collectAsStateWithLifecycle()

    Column(
        modifier = modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        ConnectionStatusCard(ui.connection)
        LiveSensorsCard(ui)
        DiffSignal3DCard(ui.recent)
        BluetoothDevicesPanel(vm, ui)
    }
}

@Composable
private fun LiveSensorsCard(ui: BluetoothUiState) {
    val timeFmt = remember { SimpleDateFormat("HH:mm:ss.SSS", Locale.US) }
    val last = ui.lastReading

    val s1Series = remember(ui.recent) {
        ui.recent.mapNotNull { it.values.getOrNull(0)?.toFloat() }
    }
    val s2Series = remember(ui.recent) {
        ui.recent.mapNotNull { it.values.getOrNull(1)?.toFloat() }
    }
    val diffSeries = remember(ui.recent) {
        ui.recent.mapNotNull { r ->
            val a = r.values.getOrNull(0)
            val b = r.values.getOrNull(1)
            if (a != null && b != null) (a - b).toFloat() else null
        }
    }

    Card(Modifier.fillMaxWidth()) {
        Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(10.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text("القراءات الحيّة", style = MaterialTheme.typography.titleMedium)
                Text(
                    "${ui.samplesPerSecond} عينة/ث  •  ${ui.totalSamples}",
                    style = MaterialTheme.typography.labelMedium
                )
            }

            if (last == null) {
                Hint("لا توجد بيانات بعد… اتصل بالجهاز من الأسفل وتأكد أن الـ ESP32 يرسل أسطراً مثل: 1234,1198")
                return@Column
            }

            val s1 = last.values.getOrNull(0)
            val s2 = last.values.getOrNull(1)

            SensorRow("الحساس 1", s1, Sensor1Color)
            SensorRow("الحساس 2", s2, Sensor2Color)
            if (s1 != null && s2 != null) {
                HorizontalDivider()
                SensorRow("الفرق  S1 − S2", s1 - s2, DiffColor)
            } else if (s2 == null) {
                Hint("الجهاز يرسل قناة واحدة فقط؛ الحساس 2 والفرق غير متاحين.")
            }

            Hint("الفولت يفترض قيماً خاماً من ADS1115 بمدى ±4.096V.")

            // الحساسان على مقياس واحد ليظهر الفرق بينهما بصرياً
            Text("الحساس 1 (أزرق) والحساس 2 (أحمر)", style = MaterialTheme.typography.labelMedium)
            Sparkline(
                series = listOf(s1Series, s2Series),
                colors = listOf(Sensor1Color, Sensor2Color),
                modifier = Modifier
                    .fillMaxWidth()
                    .height(90.dp)
                    .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f)),
                sharedScale = true
            )

            if (diffSeries.size >= 2) {
                Text("الفرق S1 − S2", style = MaterialTheme.typography.labelMedium)
                Sparkline(
                    series = listOf(diffSeries),
                    colors = listOf(DiffColor),
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(70.dp)
                        .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.4f))
                )
                val peak = diffSeries.maxOfOrNull { abs(it) } ?: 0f
                Text(
                    "أكبر |S1−S2| في آخر ${diffSeries.size} عينة: " +
                            String.format(Locale.US, "%.1f", peak),
                    style = MaterialTheme.typography.bodySmall
                )
            }

            HorizontalDivider()

            // سجل آخر العينات (الأحدث أولاً)
            ui.recent.takeLast(6).asReversed().forEach { r ->
                Text(
                    timeFmt.format(r.timestampMs) + "  " +
                            r.values.take(2).joinToString(",  ") { String.format(Locale.US, "%.1f", it) },
                    fontFamily = FontFamily.Monospace,
                    style = MaterialTheme.typography.bodySmall
                )
            }
        }
    }
}

@Composable
private fun SensorRow(label: String, value: Double?, color: Color) {
    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
        Box(Modifier.size(12.dp).clip(CircleShape).background(color))
        Spacer(Modifier.size(8.dp))
        Column(Modifier.weight(1f)) {
            Text(label, style = MaterialTheme.typography.bodyMedium, fontWeight = FontWeight.Bold)
            Text(
                if (value == null) "—"
                else String.format(Locale.US, "≈ %.4f V", BluetoothService.adsRawToVolts(value)),
                style = MaterialTheme.typography.bodySmall,
                fontFamily = FontFamily.Monospace
            )
        }
        Text(
            if (value == null) "—" else String.format(Locale.US, "%.1f", value),
            fontSize = 28.sp,
            fontFamily = FontFamily.Monospace,
            fontWeight = FontWeight.Bold
        )
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

    fun setLines(v: Int) = editConfig { copy(lines = v.coerceIn(1, 200)) }
    fun setPoints(v: Int) = editConfig { copy(pointsPerLine = v.coerceIn(2, 300)) }
    fun setLineLength(v: Float) = editConfig { copy(lineLengthM = v.coerceIn(0.5f, 500f)) }
    fun setLineSpacing(v: Float) = editConfig { copy(lineSpacingM = v.coerceIn(0.1f, 50f)) }
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

    /** يحمّل مسحاً محفوظاً مكان الجلسة الحالية (يُعرض كجلسة منتهية) */
    fun loadSaved(cfg: GridConfig, s1: List<FloatArray>, s2: List<FloatArray>) {
        recording = false
        b1.clear(); b2.clear()
        _ui.value = GridScanUiState(
            config = cfg, phase = ScanPhase.Finished, currentLine = 0,
            completedLines = s1.count { row -> row.any { it.isFinite() } },
            lineSamples = 0, s1 = s1, s2 = s2, message = "تم تحميل مسح محفوظ"
        )
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
    val centroidRow: Float, val centroidCol: Float,
    val ref: Float                            // مرجع الخلفية (0 بعد الطرح، وإلا المتوسط)
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
        peakRow = pr, peakCol = pc, peakValue = m[pr][pc], ref = ref,
        centroidRow = if (wSum > 0) (rSum / wSum).toFloat() else pr.toFloat(),
        centroidCol = if (wSum > 0) (cSum / wSum).toFloat() else pc.toFloat()
    )
}
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/HeatmapColors.kt'] = r'''package com.example.gradiometer.bluetooth

import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.lerp
import kotlin.math.abs
import kotlin.math.max

/** لوحات الألوان: من القيم المنخفضة (أول لون) إلى الذروة (آخر لون) */
enum class Palette(val label: String, val stops: List<Color>) {
    /** أزرق (بارد) ← سماوي ← أخضر ← أصفر ← برتقالي ← أحمر (ساخن) */
    Thermal(
        "حراري", listOf(
            Color(0xFF0B1E8F), Color(0xFF1F3BFF), Color(0xFF00C8FF), Color(0xFF2ECC40),
            Color(0xFFFFE600), Color(0xFFFF7A00), Color(0xFFE5161B), Color(0xFF7A0010)
        )
    ),

    /** أزرق ← أبيض (الصفر) ← أحمر: الأفضل للشذوذ الموجب والسالب مع النطاق «المتماثل» */
    Diverging(
        "ثنائي", listOf(
            Color(0xFF08306B), Color(0xFF2171B5), Color(0xFF9ECAE1), Color(0xFFF7F7F7),
            Color(0xFFFCA082), Color(0xFFDE2D26), Color(0xFF67000D)
        )
    ),

    /** أسود ← بنفسجي ← برتقالي ← أصفر فاتح: يُبرز الذروات الضعيفة */
    Magma(
        "ماجما", listOf(
            Color(0xFF000004), Color(0xFF3B0F70), Color(0xFF8C2981),
            Color(0xFFDE4968), Color(0xFFFE9F6D), Color(0xFFFCFDBF)
        )
    )
}

enum class ScaleMode(val label: String) {
    Auto("تلقائي (2%–98%)"),
    MinMax("كامل المدى"),
    Symmetric("متماثل حول الخلفية"),
    Custom("مخصص")
}

/** نطاق ألوان نهائي: القيمة lo -> أول لون، hi -> آخر لون */
class ColorScale(val lo: Float, val hi: Float, val palette: Palette) {
    fun norm(v: Float): Float = ((v - lo) / (hi - lo)).coerceIn(0f, 1f)
    fun color(v: Float): Color = paletteColor(palette, norm(v))
}

fun paletteColor(p: Palette, t: Float): Color {
    val s = p.stops
    val x = t.coerceIn(0f, 1f) * (s.size - 1)
    val i = x.toInt().coerceAtMost(s.size - 2)
    return lerp(s[i], s[i + 1], x - i)
}

/**
 * يحدّد lo/hi حسب الوضع:
 *  Auto: النسبتان 2% و98% (تتجاهل القيم الشاذة المتطرفة) - Symmetric إذا طُرحت الخلفية.
 *  MinMax: من أصغر إلى أكبر قيمة.
 *  Symmetric: ±أكبر انحراف عن الخلفية (الصفر في منتصف اللوحة).
 *  Custom: القيمتان اللتان يحددهما المستخدم.
 */
fun resolveScale(
    a: FieldAnalysis, mode: ScaleMode,
    customLo: Float, customHi: Float, palette: Palette
): ColorScale {
    var lo: Float
    var hi: Float
    when (mode) {
        ScaleMode.Auto -> { lo = a.lo; hi = a.hi }
        ScaleMode.MinMax -> { lo = a.min; hi = a.max }
        ScaleMode.Symmetric -> {
            val lim = max(abs(a.min - a.ref), abs(a.max - a.ref))
            lo = a.ref - lim; hi = a.ref + lim
        }
        ScaleMode.Custom -> {
            lo = if (customLo.isFinite()) customLo else a.lo
            hi = if (customHi.isFinite()) customHi else a.hi
        }
    }
    if (hi - lo < 1e-6f) hi = lo + 1f
    return ColorScale(lo, hi, palette)
}
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/DepthEstimation.kt'] = r'''package com.example.gradiometer.bluetooth

import kotlin.math.abs
import kotlin.math.pow
import kotlin.math.sqrt

/**
 * تقدير عمق الهدف من شكل منحنى الشذوذ.
 *
 * النموذج: سعة الشذوذ بدلالة المسافة الأفقية x عن الهدف
 *     A(x) = A0 · (1 + (x/z)²)^(−N/2)
 * حيث z = المسافة الرأسية بين الحساس ومركز الهدف، و N أُسّ تناقص الحقل:
 *     جسم نقطي/كروي (ثنائي قطب): N = 3 للحقل، N = 4 للتدرّج (الجراديومتر)
 *     جسم خطي/أسطواني:           N = 2 للحقل، N = 3 للتدرّج
 *
 * الطريقتان (تُطبَّقان على المقطع على الخط وعبر الخطوط عبر الذروة):
 *  1) نصف العرض: x½ = العرض عند نصف الذروة  ->  z = x½ / √(2^(2/N) − 1)
 *     (كرة/حقل: z ≈ 1.31·x½ ، تدرّج: z ≈ x½)
 *  2) الميل الأقصى: z = N·f·A0 / |dA/dx|max ،  f = (N+1)^−½ · ((N+2)/(N+1))^−(N+2)/2
 *     (مبدأ Peters / half-slope على الفص الرئيسي)
 *
 * النتيجة = متوسط التقديرات الصالحة، والمدى = أصغر/أكبر تقدير. العمق تحت السطح = z − ارتفاع الحساس.
 * تقدير تقريبي (عادة ±30%): يفترض هدفاً معزولاً وخلفية مطروحة جيداً.
 */
enum class SourceShape(val label: String) {
    Point("نقطي / كروي"),
    Linear("خطي / أسطواني")
}

class DepthPart(val label: String, val distanceM: Float)

class DepthEstimate(
    val distanceM: Float,      // المسافة حساس ← مركز الهدف (z)
    val depthM: Float,         // العمق تحت السطح = z − ارتفاع الحساس
    val minDepthM: Float,
    val maxDepthM: Float,
    val exponent: Float,       // N
    val parts: List<DepthPart>,
    val warnings: List<String>
)

fun estimateDepth(
    a: FieldAnalysis, cfg: GridConfig,
    source: FieldSource, shape: SourceShape, sensorHeightM: Float
): DepthEstimate {
    val rows = a.matrix.size
    val cols = if (rows > 0) a.matrix[0].size else 0
    val n = (if (source == FieldSource.Gradient) 4f else 3f) - (if (shape == SourceShape.Linear) 1f else 0f)
    val parts = ArrayList<DepthPart>()
    val warn = ArrayList<String>()

    fun failed(msg: String) = DepthEstimate(Float.NaN, Float.NaN, Float.NaN, Float.NaN, n, parts, warn + msg)
    if (rows == 0 || cols < 3) return failed("الشبكة صغيرة جداً لتقدير العمق")

    // نجعل الذروة موجبة دائماً: d = (القيمة − الخلفية) × الإشارة
    val sign = if (a.peakValue - a.ref >= 0f) 1f else -1f

    val alongDx = cfg.lineLengthM / (cols - 1).coerceAtLeast(1)
    val along = FloatArray(cols) { (a.matrix[a.peakRow][it] - a.ref) * sign }
    profileEstimates("على الخط", along, a.peakCol, alongDx, n, parts, warn)

    if (rows >= 5) {
        val cross = FloatArray(rows) { (a.matrix[it][a.peakCol] - a.ref) * sign }
        profileEstimates("عبر الخطوط", cross, a.peakRow, cfg.lineSpacingM, n, parts, warn)
    }

    if (a.peakCol == 0 || a.peakCol == cols - 1 || a.peakRow == 0 || a.peakRow == rows - 1) {
        warn.add("الذروة عند حافة الشبكة؛ وسّع المسح حولها لتقدير أدق")
    }
    if (parts.isEmpty()) return failed("تعذّر تقدير العمق (الشذوذ غير مكتمل أو ضيق جداً)")

    val zs = parts.map { it.distanceM }
    val z = zs.average().toFloat()
    val zMin = zs.minOrNull() ?: z
    val zMax = zs.maxOrNull() ?: z
    if (zMax - zMin > 0.6f * z) warn.add("تباين كبير بين الطرق؛ اعتبر النتيجة تقريبية جداً")

    val depth = z - sensorHeightM
    if (depth <= 0f) warn.add("العمق ≤ 0: راجع ارتفاع الحساس، أو الهدف قريب جداً من السطح")
    return DepthEstimate(z, depth, zMin - sensorHeightM, zMax - sensorHeightM, n, parts, warn)
}

private fun profileEstimates(
    label: String, raw: FloatArray, pk: Int, dx: Float, n: Float,
    parts: MutableList<DepthPart>, warn: MutableList<String>
) {
    val p = fillGaps(raw) ?: return
    if (dx <= 0f || pk !in p.indices) return
    val amp = p[pk]
    if (!(amp > 0f)) return
    val nn = n.toDouble()

    // ---- 1) نصف العرض ----
    val half = amp / 2f
    var xl = Float.NaN
    for (i in pk - 1 downTo 0) if (p[i] <= half) {
        xl = i + (half - p[i]) / (p[i + 1] - p[i]); break
    }
    var xr = Float.NaN
    for (i in pk + 1 until p.size) if (p[i] <= half) {
        xr = (i - 1) + (p[i - 1] - half) / (p[i - 1] - p[i]); break
    }
    val hwCells: Float? = when {
        !xl.isNaN() && !xr.isNaN() -> (xr - xl) / 2f
        !xl.isNaN() -> pk - xl
        !xr.isNaN() -> xr - pk
        else -> null
    }
    if (hwCells == null) {
        warn.add("لم ينخفض المنحنى إلى نصف الذروة ($label)")
    } else {
        if (xl.isNaN() || xr.isNaN()) warn.add("نصف العرض ($label) مقاس من جانب واحد فقط")
        val hw = hwCells * dx
        if (hw >= 0.75f * dx) {
            val k = sqrt(2.0.pow(2.0 / nn) - 1.0).toFloat()
            parts.add(DepthPart("نصف العرض ($label)", hw / k))
        } else {
            warn.add("القمة أضيق من تباعد العينات ($label): زِد كثافة النقاط/الخطوط")
        }
    }

    // ---- 2) الميل الأقصى على الفص الرئيسي ----
    var l = pk
    while (l > 0 && p[l - 1] > 0f) l--
    var r = pk
    while (r < p.size - 1 && p[r + 1] > 0f) r++
    if (r - l >= 2) {
        val s = FloatArray(p.size) { i ->
            (p[(i - 1).coerceAtLeast(0)] + p[i] + p[(i + 1).coerceAtMost(p.size - 1)]) / 3f
        }
        var maxSlope = 0f
        for (i in l until r) maxSlope = maxOf(maxSlope, abs(s[i + 1] - s[i]) / dx)
        val aS = s[pk]
        if (maxSlope > 0f && aS > 0f) {
            val f = (nn + 1).pow(-0.5) * ((nn + 2) / (nn + 1)).pow(-(nn + 2) / 2)
            parts.add(DepthPart("الميل الأقصى ($label)", (nn * f * aS / maxSlope).toFloat()))
        }
    }
}

/** يملأ القيم غير المقاسة (NaN) بالاستيفاء الخطي؛ null إن لم توجد أي قيمة */
private fun fillGaps(src: FloatArray): FloatArray? {
    val out = src.copyOf()
    val idx = out.indices.filter { out[it].isFinite() }
    if (idx.isEmpty()) return null
    for (i in out.indices) if (!out[i].isFinite()) {
        val prev = idx.lastOrNull { it < i }
        val next = idx.firstOrNull { it > i }
        out[i] = when {
            prev != null && next != null ->
                out[prev] + (out[next] - out[prev]) * (i - prev) / (next - prev).toFloat()
            prev != null -> out[prev]
            else -> out[next ?: 0]
        }
    }
    return out
}
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/Interactive3D.kt'] = r'''package com.example.gradiometer.bluetooth

import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.lerp
import kotlin.math.abs
import kotlin.math.cos
import kotlin.math.max
import kotlin.math.min
import kotlin.math.sign
import kotlin.math.sin
import kotlin.math.sqrt

/** سطح: شبكة مثلثة/رباعية متصلة تُظهر شكل الشذوذ، أعمدة: كل خلية عمود */
enum class View3DMode(val label: String) {
    Surface("سطح"),
    Bars("أعمدة")
}

private const val DEG2RAD = 0.017453292f

/**
 * مشهد ثلاثي الأبعاد حقيقي قابل للتدوير (إسقاط متعامد) بأبعاد فيزيائية بالمتر:
 *  - yawDeg: الدوران حول المحور الرأسي، pitchDeg: ارتفاع الكاميرا (0 = جانبي، 90 = علوي)، zoom: التكبير.
 *  - isolate (0..0.95): يُخفي ما دون هذه النسبة من أقصى انحراف عن الخلفية فيبقى «جسم الهدف» فقط.
 *    في وضع السطح يُطرح مستوى القطع فيبدأ الجسم من الصفر.
 * الرسم بترتيب الرسام (الأبعد أولاً) مع إخفاء الأوجه الخلفية وإضاءة بسيطة.
 */
fun DrawScope.drawScene3D(
    a: FieldAnalysis, cs: ColorScale, cfg: GridConfig,
    mode: View3DMode, isolate: Float,
    yawDeg: Float, pitchDeg: Float, zoom: Float
) {
    val rows = a.matrix.size
    val cols = if (rows > 0) a.matrix[0].size else 0
    if (rows < 1 || cols < 1) return

    val cellX = cfg.lineLengthM / (cols - 1).coerceAtLeast(1)
    val cellY = cfg.lineSpacingM
    val extX = cellX * cols
    val extY = cellY * rows
    var maxAbs = 1e-6f
    for (row in a.matrix) for (v in row) if (v.isFinite()) maxAbs = max(maxAbs, abs(v - a.ref))
    val hMax = 0.35f * max(extX, extY)
    val thr = isolate.coerceIn(0f, 0.95f)

    val yaw = yawDeg * DEG2RAD
    val pitch = pitchDeg.coerceIn(0f, 90f) * DEG2RAD
    val cy = cos(yaw)
    val sy = sin(yaw)
    val cp = cos(pitch)
    val sp = sin(pitch)
    val radius = 0.5f * sqrt(extX * extX + extY * extY + 4f * hMax * hMax)
    val s = min(size.width, size.height) / (2f * radius * 1.05f) * zoom
    val ox = size.width / 2f
    val oy = size.height / 2f

    fun scr(x: Float, y: Float, z: Float): Offset {
        val y1 = x * sy + y * cy
        return Offset(ox + (x * cy - y * sy) * s, oy - (y1 * sp + z * cp) * s)
    }
    fun depth(x: Float, y: Float, z: Float): Float = (x * sy + y * cy) * cp - z * sp
    fun facing(nx: Float, ny: Float, nz: Float): Boolean {
        val n1y = nx * sy + ny * cy
        return n1y * cp - nz * sp < 0f
    }
    fun shade(base: Color, nx: Float, ny: Float, nz: Float): Color {
        val n1x = nx * cy - ny * sy
        val n1y = nx * sy + ny * cy
        val n2y = n1y * cp - nz * sp
        val n2z = n1y * sp + nz * cp
        val lit = (-0.3f * n1x - 0.5f * n2y + 0.8f * n2z).coerceIn(0f, 1f)
        return lerp(Color.Black, base, 0.55f + 0.45f * lit)
    }
    fun quad(color: Color, p0: Offset, p1: Offset, p2: Offset, p3: Offset) {
        val path = Path().apply {
            moveTo(p0.x, p0.y); lineTo(p1.x, p1.y); lineTo(p2.x, p2.y); lineTo(p3.x, p3.y); close()
        }
        drawPath(path, color)
        drawPath(path, color, style = Stroke(1f)) // يخفي الشقوق بين الأوجه
    }

    // ---- الأرضية ----
    val fx0 = -extX / 2f
    val fx1 = extX / 2f
    val fy0 = -extY / 2f
    val fy1 = extY / 2f
    val floor = Path().apply {
        val q0 = scr(fx0, fy0, 0f); val q1 = scr(fx1, fy0, 0f)
        val q2 = scr(fx1, fy1, 0f); val q3 = scr(fx0, fy1, 0f)
        moveTo(q0.x, q0.y); lineTo(q1.x, q1.y); lineTo(q2.x, q2.y); lineTo(q3.x, q3.y); close()
    }
    drawPath(floor, Color.Gray.copy(alpha = 0.12f))
    drawPath(floor, Color.Gray.copy(alpha = 0.6f), style = Stroke(1.5f))

    if (mode == View3DMode.Bars) {
        val dep = FloatArray(rows * cols)
        val idx = ArrayList<Int>()
        for (r in 0 until rows) for (c in 0 until cols) {
            val v = a.matrix[r][c]
            if (!v.isFinite()) continue
            val d = v - a.ref
            if (abs(d) / maxAbs < thr) continue
            val h = d / maxAbs * hMax
            dep[r * cols + c] = depth(c * cellX + cellX / 2f - extX / 2f, r * cellY + cellY / 2f - extY / 2f, h / 2f)
            idx.add(r * cols + c)
        }
        idx.sortByDescending { dep[it] }
        for (k in idx) {
            val r = k / cols
            val c = k % cols
            val v = a.matrix[r][c]
            val h = (v - a.ref) / maxAbs * hMax
            val zLo = min(0f, h)
            val zHi = max(0f, h).coerceAtLeast(zLo + 0.004f * hMax)
            val x0 = c * cellX - extX / 2f
            val x1 = x0 + cellX
            val y0 = r * cellY - extY / 2f
            val y1 = y0 + cellY
            val base = cs.color(v)
            if (facing(0f, 0f, 1f)) quad(shade(base, 0f, 0f, 1f), scr(x0, y0, zHi), scr(x1, y0, zHi), scr(x1, y1, zHi), scr(x0, y1, zHi))
            if (facing(0f, 0f, -1f)) quad(shade(base, 0f, 0f, -1f), scr(x0, y0, zLo), scr(x1, y0, zLo), scr(x1, y1, zLo), scr(x0, y1, zLo))
            if (facing(1f, 0f, 0f)) quad(shade(base, 1f, 0f, 0f), scr(x1, y0, zLo), scr(x1, y1, zLo), scr(x1, y1, zHi), scr(x1, y0, zHi))
            if (facing(-1f, 0f, 0f)) quad(shade(base, -1f, 0f, 0f), scr(x0, y0, zLo), scr(x0, y1, zLo), scr(x0, y1, zHi), scr(x0, y0, zHi))
            if (facing(0f, 1f, 0f)) quad(shade(base, 0f, 1f, 0f), scr(x0, y1, zLo), scr(x1, y1, zLo), scr(x1, y1, zHi), scr(x0, y1, zHi))
            if (facing(0f, -1f, 0f)) quad(shade(base, 0f, -1f, 0f), scr(x0, y0, zLo), scr(x1, y0, zLo), scr(x1, y0, zHi), scr(x0, y0, zHi))
        }
    } else if (rows >= 2 && cols >= 2) {
        // ارتفاع كل رأس (عند مركز الخلية)؛ ما دون مستوى القطع = 0 والباقي يبدأ من الصفر بعد طرح المستوى
        val zz = Array(rows) { r ->
            FloatArray(cols) { c ->
                val v = a.matrix[r][c]
                if (!v.isFinite()) Float.NaN
                else {
                    val d = v - a.ref
                    val u = abs(d) / maxAbs
                    if (u < thr) 0f else sign(d) * (u - thr) / (1f - thr) * hMax
                }
            }
        }
        val nq = (rows - 1) * (cols - 1)
        val dep = FloatArray(nq)
        val idx = ArrayList<Int>()
        for (r in 0 until rows - 1) for (c in 0 until cols - 1) {
            val z00 = zz[r][c]; val z01 = zz[r][c + 1]; val z11 = zz[r + 1][c + 1]; val z10 = zz[r + 1][c]
            if (z00.isNaN() || z01.isNaN() || z11.isNaN() || z10.isNaN()) continue
            if (thr > 0f && z00 == 0f && z01 == 0f && z11 == 0f && z10 == 0f) continue
            val k = r * (cols - 1) + c
            val xm = (c + 1) * cellX - extX / 2f
            val ym = (r + 1) * cellY - extY / 2f
            dep[k] = depth(xm, ym, (z00 + z01 + z11 + z10) / 4f)
            idx.add(k)
        }
        idx.sortByDescending { dep[it] }
        for (k in idx) {
            val r = k / (cols - 1)
            val c = k % (cols - 1)
            val z00 = zz[r][c]; val z01 = zz[r][c + 1]; val z11 = zz[r + 1][c + 1]; val z10 = zz[r + 1][c]
            val xA = c * cellX + cellX / 2f - extX / 2f
            val xB = xA + cellX
            val yA = r * cellY + cellY / 2f - extY / 2f
            val yB = yA + cellY
            val avg = (a.matrix[r][c] + a.matrix[r][c + 1] + a.matrix[r + 1][c + 1] + a.matrix[r + 1][c]) / 4f
            var nx = -(z01 - z00) * cellY
            var ny = -cellX * (z10 - z00)
            var nz = cellX * cellY
            val len = sqrt(nx * nx + ny * ny + nz * nz).coerceAtLeast(1e-6f)
            nx /= len; ny /= len; nz /= len
            if (!facing(nx, ny, nz)) { nx = -nx; ny = -ny; nz = -nz }
            quad(shade(cs.color(avg), nx, ny, nz), scr(xA, yA, z00), scr(xB, yA, z01), scr(xB, yB, z11), scr(xA, yB, z10))
        }
    }

    // ---- علامة الذروة: عمود أبيض فوق موضعها ----
    val px = a.peakCol * cellX + cellX / 2f - extX / 2f
    val py = a.peakRow * cellY + cellY / 2f - extY / 2f
    val top = scr(px, py, hMax * 1.2f)
    val bottom = scr(px, py, 0f)
    drawLine(Color.Black, bottom, top, 6f)
    drawLine(Color.White, bottom, top, 3f)
    drawCircle(Color.Black, 9f, top)
    drawCircle(Color.White, 6f, top)
}
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/FinalInspectionScreen.kt'] = r'''package com.example.gradiometer.bluetooth

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.background
import androidx.compose.foundation.gestures.detectTransformGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.input.pointer.pointerInput
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.TextUnit
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import java.util.Locale
import kotlin.math.pow
import kotlin.math.roundToInt
import kotlin.math.sin

/**
 * تبويب 4: الفحص النهائي (جراديومتر) — بملء الشاشة.
 * يقرأ نتائج المسح الشبكي المجمَّعة في تبويب «الجراديومتر – تجميع البيانات» (نفس الـ ViewModel بالمفتاح gradiometer)
 * ويعتمد دائماً على الحساسين معاً: الفرق S1 − S2.
 * يعرض: خريطة/أعمدة ملوّنة بتدرج لوني + شريط الألوان + العمق المقدَّر + إحداثيات الذروة والمركز.
 * قبل وجود بيانات يعرض معاينة تجريبية (مُعلَّمة بوضوح).
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
fun FinalInspectionScreen(
    onClose: () -> Unit,
    modifier: Modifier = Modifier,
    vm: GridScanViewModel = viewModel<GridScanViewModel>(key = "gradiometer")
) {
    val ui by vm.ui.collectAsStateWithLifecycle()

    var palette by rememberSaveable { mutableStateOf(Palette.Thermal) }
    var scaleMode by rememberSaveable { mutableStateOf(ScaleMode.Auto) }
    var bg by rememberSaveable { mutableStateOf(Background.GlobalMean) }
    var view3d by rememberSaveable { mutableStateOf(false) }
    var shape by rememberSaveable { mutableStateOf(SourceShape.Point) }
    var sensorH by rememberSaveable { mutableFloatStateOf(0.3f) }
    var showSettings by rememberSaveable { mutableStateOf(false) }
    // عرض 3D قابل للتدوير
    var mode3d by rememberSaveable { mutableStateOf(View3DMode.Surface) }
    var yaw by rememberSaveable { mutableFloatStateOf(35f) }
    var pitch by rememberSaveable { mutableFloatStateOf(40f) }
    var zoom by rememberSaveable { mutableFloatStateOf(1f) }
    var isolate by rememberSaveable { mutableFloatStateOf(0f) }   // % من أقصى انحراف

    val isDemo = ui.s1.isEmpty() || ui.s2.isEmpty()
    val demo = remember { fiDemoData() }
    val s1 = if (isDemo) demo.s1 else ui.s1
    val s2 = if (isDemo) demo.s2 else ui.s2
    val cfg = if (isDemo) demo.config else ui.config
    val drawUi = if (isDemo) GridScanUiState() else ui

    val analysis = remember(s1, s2, bg) { analyze(s1, s2, FieldSource.Gradient, bg) }
    val colorScale = remember(analysis, scaleMode, palette) {
        analysis?.let { resolveScale(it, scaleMode, Float.NaN, Float.NaN, palette) }
    }
    val depth = remember(analysis, cfg, shape, sensorH) {
        analysis?.let { estimateDepth(it, cfg, FieldSource.Gradient, shape, sensorH) }
    }
    val bitmap = remember(analysis, colorScale, view3d) {
        if (analysis != null && colorScale != null && !view3d) buildHeatBitmap(analysis, colorScale) else null
    }

    Column(
        modifier
            .fillMaxSize()
            .padding(horizontal = 12.dp, vertical = 8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
            Text(
                "الفحص النهائي — جراديومتر (S1 − S2)",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.weight(1f)
            )
            TextButton(onClick = onClose) { Text("رجوع") }
        }
        SurveyArchiveBar(vm, "gradiometer")
        if (isDemo) {
            Text(
                "معاينة تجريبية — أنجز مسحاً في تبويب «الجراديومتر – تجميع البيانات» لتظهر نتائجك هنا.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }

        // ---- المنظر الرئيسي (يملأ المساحة المتاحة) ----
        Box(
            Modifier
                .weight(1f)
                .fillMaxWidth()
                .clip(RoundedCornerShape(12.dp))
                .background(MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f)),
            contentAlignment = Alignment.Center
        ) {
            if (analysis == null || colorScale == null) {
                Text(
                    "بانتظار اكتمال أول خط مسح…",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            } else {
                val rows = analysis.matrix.size
                val cols = analysis.matrix[0].size
                if (view3d) {
                    Canvas(
                        Modifier
                            .fillMaxSize()
                            .pointerInput(Unit) {
                                detectTransformGestures { _, pan, zoomChange, _ ->
                                    yaw += pan.x * 0.4f
                                    pitch = (pitch - pan.y * 0.3f).coerceIn(0f, 90f)
                                    zoom = (zoom * zoomChange).coerceIn(0.5f, 6f)
                                }
                            }
                    ) {
                        drawScene3D(analysis, colorScale, cfg, mode3d, isolate / 100f, yaw, pitch, zoom)
                    }
                    Text(
                        "اسحب للتدوير • بإصبعين للتكبير",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant,
                        modifier = Modifier
                            .align(Alignment.BottomCenter)
                            .padding(4.dp)
                    )
                } else {
                    val ratio = (cfg.lineLengthM / (rows * cfg.lineSpacingM)).coerceIn(0.5f, 2.5f)
                    Canvas(Modifier.aspectRatio(ratio)) {
                        drawHeatmap2D(analysis, colorScale, bitmap, rows, cols, drawUi, null)
                    }
                }
            }
        }

        if (colorScale != null) ColorBar(colorScale)

        if (analysis != null) FiSummary(analysis, cfg, depth)

        if (view3d && analysis != null) {
            Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                Text("عزل الهدف ${isolate.roundToInt()}%", style = MaterialTheme.typography.bodySmall)
                Slider(
                    value = isolate,
                    onValueChange = { isolate = it },
                    valueRange = 0f..90f,
                    modifier = Modifier
                        .weight(1f)
                        .padding(start = 8.dp)
                )
            }
        }

        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            FilterChip(selected = !view3d, onClick = { view3d = false }, label = { Text("خريطة 2D") })
            FilterChip(selected = view3d, onClick = { view3d = true }, label = { Text("مجسّم 3D") })
            FilterChip(selected = showSettings, onClick = { showSettings = !showSettings }, label = { Text("الإعدادات") })
            if (view3d) {
                View3DMode.values().forEach { m ->
                    FilterChip(selected = mode3d == m, onClick = { mode3d = m }, label = { Text(m.label) })
                }
                FilterChip(selected = false, onClick = { pitch = 90f; yaw = 0f }, label = { Text("علوي") })
                FilterChip(selected = false, onClick = { pitch = 8f; yaw = 0f }, label = { Text("جانبي") })
                FilterChip(selected = false, onClick = { yaw = 35f; pitch = 40f; zoom = 1f; isolate = 0f }, label = { Text("إعادة") })
            }
        }

        if (showSettings) {
            Column(
                Modifier
                    .heightIn(max = 240.dp)
                    .verticalScroll(rememberScrollState()),
                verticalArrangement = Arrangement.spacedBy(6.dp)
            ) {
                Text("لوحة الألوان", style = MaterialTheme.typography.labelLarge)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Palette.values().forEach { pl ->
                        FilterChip(selected = palette == pl, onClick = { palette = pl }, label = { Text(pl.label) })
                    }
                }
                Text("نطاق الألوان", style = MaterialTheme.typography.labelLarge)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    ScaleMode.values().filter { it != ScaleMode.Custom }.forEach { m ->
                        FilterChip(selected = scaleMode == m, onClick = { scaleMode = m }, label = { Text(m.label) })
                    }
                }
                Text("طرح الخلفية", style = MaterialTheme.typography.labelLarge)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Background.values().forEach { b ->
                        FilterChip(selected = bg == b, onClick = { bg = b }, label = { Text(fiBgLabel(b)) })
                    }
                }
                Text("شكل الهدف (للعمق)", style = MaterialTheme.typography.labelLarge)
                FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    SourceShape.values().forEach { s ->
                        FilterChip(selected = shape == s, onClick = { shape = s }, label = { Text(s.label) })
                    }
                }
                Text("ارتفاع الحساس السفلي عن الأرض: ${sensorH.fx(2)} م", style = MaterialTheme.typography.bodySmall)
                Slider(
                    value = sensorH,
                    onValueChange = { sensorH = (it * 20f).roundToInt() / 20f },
                    valueRange = 0f..2f
                )
                depth?.warnings.orEmpty().forEach {
                    Text("⚠ $it", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
    }
}

@Composable
private fun FiSummary(a: FieldAnalysis, cfg: GridConfig, d: DepthEstimate?) {
    val cols = a.matrix[0].size
    val rows = a.matrix.size
    // الإحداثيات بالمتر: x على طول الخط، y = رقم الخط × التباعد (كما في بطاقة التحليل)
    fun xM(col: Float) = col / (cols - 1).coerceAtLeast(1) * cfg.lineLengthM
    fun yM(row: Float) = row * cfg.lineSpacingM
    val ok = d?.takeIf { it.depthM.isFinite() }
    Card(
        Modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
    ) {
        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                FiTile(
                    "العمق المقدَّر",
                    if (ok != null) "${ok.depthM.fx(2)} م" else "—",
                    if (ok != null) "${ok.minDepthM.fx(1)} … ${ok.maxDepthM.fx(1)} م" else "",
                    28.sp, Modifier.weight(1.3f)
                )
                FiTile(
                    "الذروة",
                    "x ${xM(a.peakCol.toFloat()).fx(2)}\ny ${yM(a.peakRow.toFloat()).fx(2)}",
                    "خط ${a.peakRow + 1} • نقطة ${a.peakCol + 1}",
                    15.sp, Modifier.weight(1f)
                )
                FiTile(
                    "المركز",
                    "x ${xM(a.centroidCol).fx(2)}\ny ${yM(a.centroidRow).fx(2)}",
                    "خط ${(a.centroidRow + 1).fx(1)} • نقطة ${(a.centroidCol + 1).fx(1)}",
                    15.sp, Modifier.weight(1f)
                )
            }
            Text(
                "الشبكة: $rows خط × $cols نقطة • الإحداثيات بالمتر (x على الخط، y بين الخطوط)",
                style = MaterialTheme.typography.bodySmall
            )
        }
    }
}

@Composable
private fun FiTile(label: String, value: String, sub: String, valueSize: TextUnit, modifier: Modifier) {
    Column(modifier, horizontalAlignment = Alignment.CenterHorizontally) {
        Text(label, style = MaterialTheme.typography.labelMedium)
        Text(
            value,
            fontSize = valueSize,
            fontWeight = FontWeight.Bold,
            fontFamily = FontFamily.Monospace,
            textAlign = TextAlign.Center
        )
        if (sub.isNotEmpty()) Text(sub, style = MaterialTheme.typography.bodySmall, textAlign = TextAlign.Center)
    }
}

private fun fiBgLabel(b: Background): String = when (b) {
    Background.None -> "بدون"
    Background.GlobalMean -> "متوسط عام"
    Background.LineMean -> "متوسط الخط"
}

private fun Float.fx(digits: Int = 2): String = String.format(Locale.US, "%.${digits}f", this)

// ------------------------------------------------------------- بيانات تجريبية

private class FiDemo(val s1: List<FloatArray>, val s2: List<FloatArray>, val config: GridConfig)

/** هدف وهمي عند x≈6.5 م و y≈5.5 م: الحساس السفلي S1 أقرب فيرى شذوذاً أقوى من S2 */
private fun fiDemoData(): FiDemo {
    val cfg = GridConfig(lines = 12, pointsPerLine = 24, lineLengthM = 12f, lineSpacingM = 1f, zigzag = true)
    val rows = cfg.lines
    val cols = cfg.pointsPerLine
    fun field(x: Float, y: Float, z: Float, amp: Float): Float {
        val dx = x - 6.5f
        val dy = y - 5.5f
        return amp * (1f + (dx * dx + dy * dy) / (z * z)).pow(-1.5f)
    }
    val s1 = List(rows) { r ->
        FloatArray(cols) { c ->
            val x = c / (cols - 1f) * cfg.lineLengthM
            20000f + field(x, r * cfg.lineSpacingM, 1.6f, 900f) + 6f * sin(r * 12.9f + c * 7.7f)
        }
    }
    val s2 = List(rows) { r ->
        FloatArray(cols) { c ->
            val x = c / (cols - 1f) * cfg.lineLengthM
            20000f + field(x, r * cfg.lineSpacingM, 2.2f, 500f) + 6f * sin(r * 5.3f + c * 3.1f)
        }
    }
    return FiDemo(s1, s2, cfg)
}
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/SurveyStore.kt'] = r'''package com.example.gradiometer.bluetooth

import android.content.Context
import android.os.Environment
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.io.OutputStream
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/** وصف مختصر لمسح محفوظ (للعرض في القائمة) */
class SurveyMeta(
    val file: File,
    val name: String,
    val kind: String,        // "gradiometer" أو "magnetometer"
    val timeMs: Long,
    val lines: Int,
    val points: Int
)

class SavedSurvey(
    val meta: SurveyMeta,
    val config: GridConfig,
    val s1: List<FloatArray>,
    val s2: List<FloatArray>
)

/**
 * حفظ/قراءة المسوحات كملفات JSON في مجلد التطبيق على التخزين الخارجي.
 * - إن وُجدت بطاقة SD قابلة للإزالة تُحفظ عليها، وإلا في ذاكرة الجهاز.
 * - لا يحتاج أذونات. المسار: Android/data/<الحزمة>/files/surveys
 * - ملاحظة: مجلد التطبيق يُحذف عند إلغاء تثبيت التطبيق، فاستخدم «تصدير CSV» لنسخة دائمة.
 * القيم غير المقاسة (NaN) تُحفظ null.
 */
object SurveyStore {

    private fun allDirs(ctx: Context): List<File> {
        val ext = ctx.getExternalFilesDirs("surveys").filterNotNull()
        return (ext + File(ctx.filesDir, "surveys")).distinct()
    }

    private fun sdDir(ctx: Context): File? =
        ctx.getExternalFilesDirs("surveys").filterNotNull().firstOrNull {
            try { Environment.isExternalStorageRemovable(it) } catch (e: Exception) { false }
        }

    fun saveDir(ctx: Context): File {
        val dir = sdDir(ctx)
            ?: ctx.getExternalFilesDirs("surveys").filterNotNull().firstOrNull()
            ?: File(ctx.filesDir, "surveys")
        dir.mkdirs()
        return dir
    }

    /** اسم موقع الحفظ الحالي للعرض */
    fun storageLabel(ctx: Context): String =
        if (sdDir(ctx) != null) "بطاقة الذاكرة SD" else "ذاكرة الجهاز"

    fun save(
        ctx: Context, kind: String, name: String,
        cfg: GridConfig, s1: List<FloatArray>, s2: List<FloatArray>
    ): File {
        val t = System.currentTimeMillis()
        val obj = JSONObject()
        obj.put("v", 1)
        obj.put("kind", kind)
        obj.put("name", name)
        obj.put("time", t)
        obj.put(
            "config", JSONObject()
                .put("lines", cfg.lines)
                .put("pointsPerLine", cfg.pointsPerLine)
                .put("lineLengthM", cfg.lineLengthM.toString().toDouble())
                .put("lineSpacingM", cfg.lineSpacingM.toString().toDouble())
                .put("zigzag", cfg.zigzag)
        )
        obj.put("s1", toJson(s1))
        obj.put("s2", toJson(s2))
        val stamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date(t))
        val f = File(saveDir(ctx), "survey_${kind}_$stamp.json")
        f.writeText(obj.toString(), Charsets.UTF_8)
        return f
    }

    fun load(file: File): SavedSurvey? = try {
        val o = JSONObject(file.readText(Charsets.UTF_8))
        val c = o.getJSONObject("config")
        val cfg = GridConfig(
            c.getInt("lines"), c.getInt("pointsPerLine"),
            c.getDouble("lineLengthM").toFloat(), c.getDouble("lineSpacingM").toFloat(),
            c.optBoolean("zigzag", true)
        )
        val s1 = fromJson(o.getJSONArray("s1"))
        val s2 = fromJson(o.getJSONArray("s2"))
        val meta = SurveyMeta(
            file, o.optString("name", file.nameWithoutExtension),
            o.optString("kind", "gradiometer"), o.optLong("time", file.lastModified()),
            s1.size, if (s1.isNotEmpty()) s1[0].size else 0
        )
        SavedSurvey(meta, cfg, s1, s2)
    } catch (e: Exception) {
        null
    }

    /** قائمة المسوحات (الأحدث أولاً) من كل مواقع الحفظ، مع تصفية النوع اختيارياً */
    fun list(ctx: Context, kind: String?): List<SurveyMeta> =
        allDirs(ctx)
            .flatMap { d -> d.listFiles { f -> f.name.startsWith("survey_") && f.name.endsWith(".json") }?.toList() ?: emptyList() }
            .mapNotNull { load(it)?.meta }
            .filter { kind == null || it.kind == kind }
            .sortedByDescending { it.timeMs }

    /** CSV: line,point,x_m,y_m,s1,s2,diff (مع BOM ليقرأه Excel بترميز UTF-8) */
    fun writeCsv(out: OutputStream, s: SavedSurvey) {
        val w = out.bufferedWriter(Charsets.UTF_8)
        w.write("\uFEFF")
        w.write("line,point,x_m,y_m,s1,s2,diff_s1_minus_s2\n")
        val cols = if (s.s1.isNotEmpty()) s.s1[0].size else 0
        fun num(v: Float): String = if (v.isFinite()) String.format(Locale.US, "%.4f", v) else ""
        for (r in s.s1.indices) for (c in 0 until cols) {
            val v1 = s.s1[r][c]
            val v2 = s.s2.getOrNull(r)?.getOrNull(c) ?: Float.NaN
            val x = c / (cols - 1).coerceAtLeast(1).toFloat() * s.config.lineLengthM
            val y = r * s.config.lineSpacingM
            w.write("${r + 1},${c + 1},${num(x)},${num(y)},${num(v1)},${num(v2)},${num(v1 - v2)}\n")
        }
        w.flush()
    }

    private fun toJson(m: List<FloatArray>): JSONArray {
        val a = JSONArray()
        for (row in m) {
            val r = JSONArray()
            for (v in row) {
                if (v.isFinite()) r.put(v.toString().toDouble()) else r.put(JSONObject.NULL)
            }
            a.put(r)
        }
        return a
    }

    private fun fromJson(a: JSONArray): List<FloatArray> = List(a.length()) { r ->
        val row = a.getJSONArray(r)
        FloatArray(row.length()) { c -> if (row.isNull(c)) Float.NaN else row.getDouble(c).toFloat() }
    }
}
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/SurveyArchive.kt'] = r'''package com.example.gradiometer.bluetooth

import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.FilledTonalButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog
import androidx.compose.ui.window.DialogProperties
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

private fun defaultSurveyName(): String =
    "مسح " + SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.US).format(Date())

private fun fmtSurveyDate(ms: Long): String =
    SimpleDateFormat("yyyy-MM-dd HH:mm", Locale.US).format(Date(ms))

/**
 * شريط «حفظ النتائج / المحفوظات» لأي جلسة مسح (vm).
 * - حفظ: اسم + حفظ على بطاقة SD إن وُجدت وإلا ذاكرة الجهاز.
 * - المحفوظات: قائمة بملء الشاشة: فتح (يحمّل المسح في الواجهة ليعرض الخريطة والعمق)، تصدير CSV، حذف.
 * kind: "gradiometer" أو "magnetometer" (لا تُعرض إلا مسوحات النوع نفسه).
 */
@Composable
fun SurveyArchiveBar(vm: GridScanViewModel, kind: String, modifier: Modifier = Modifier) {
    val ui by vm.ui.collectAsStateWithLifecycle()
    val ctx = LocalContext.current
    val scope = rememberCoroutineScope()

    var showSave by remember { mutableStateOf(false) }
    var showArchive by remember { mutableStateOf(false) }
    var status by remember { mutableStateOf<String?>(null) }
    var items by remember { mutableStateOf<List<SurveyMeta>>(emptyList()) }
    var refresh by remember { mutableIntStateOf(0) }
    var pendingLoad by remember { mutableStateOf<SavedSurvey?>(null) }
    var pendingDelete by remember { mutableStateOf<SurveyMeta?>(null) }
    var pendingExport by remember { mutableStateOf<SavedSurvey?>(null) }

    val hasData = ui.s1.any { row -> row.any { it.isFinite() } }

    val exportLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.CreateDocument("text/csv")
    ) { uri ->
        val sv = pendingExport
        pendingExport = null
        if (uri != null && sv != null) {
            scope.launch {
                val ok = withContext(Dispatchers.IO) {
                    try {
                        ctx.contentResolver.openOutputStream(uri)?.use { SurveyStore.writeCsv(it, sv) } != null
                    } catch (e: Exception) {
                        false
                    }
                }
                status = if (ok) "تم تصدير CSV" else "تعذّر التصدير"
            }
        }
    }

    LaunchedEffect(showArchive, refresh) {
        if (showArchive) items = withContext(Dispatchers.IO) { SurveyStore.list(ctx, kind) }
    }

    Column(modifier.fillMaxWidth(), verticalArrangement = Arrangement.spacedBy(4.dp)) {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            FilledTonalButton(
                onClick = { showSave = true },
                enabled = hasData,
                modifier = Modifier.weight(1f)
            ) { Text("حفظ النتائج") }
            OutlinedButton(
                onClick = { showArchive = true },
                modifier = Modifier.weight(1f)
            ) { Text("المحفوظات") }
        }
        status?.let { Text(it, style = MaterialTheme.typography.bodySmall) }
    }

    // ---- حوار الحفظ ----
    if (showSave) {
        var name by remember { mutableStateOf(defaultSurveyName()) }
        AlertDialog(
            onDismissRequest = { showSave = false },
            title = { Text("حفظ نتائج المسح") },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    OutlinedTextField(
                        value = name, onValueChange = { name = it },
                        singleLine = true, label = { Text("اسم المسح") }
                    )
                    Text("مكان الحفظ: ${SurveyStore.storageLabel(ctx)}", style = MaterialTheme.typography.bodySmall)
                }
            },
            confirmButton = {
                TextButton(onClick = {
                    val s1 = ui.s1
                    val s2 = ui.s2
                    val cfg = ui.config
                    val nm = name.trim().ifEmpty { defaultSurveyName() }
                    showSave = false
                    scope.launch {
                        val res = withContext(Dispatchers.IO) {
                            try { SurveyStore.save(ctx, kind, nm, cfg, s1, s2) } catch (e: Exception) { null }
                        }
                        status = if (res != null) "تم الحفظ (${SurveyStore.storageLabel(ctx)}): ${res.name}" else "تعذّر الحفظ"
                        refresh++
                    }
                }) { Text("حفظ") }
            },
            dismissButton = { TextButton(onClick = { showSave = false }) { Text("إلغاء") } }
        )
    }

    // ---- قائمة المحفوظات (ملء الشاشة) ----
    if (showArchive) {
        Dialog(
            onDismissRequest = { showArchive = false },
            properties = DialogProperties(usePlatformDefaultWidth = false)
        ) {
            Surface(Modifier.fillMaxSize(), color = MaterialTheme.colorScheme.background) {
                Column(Modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Row(Modifier.fillMaxWidth(), verticalAlignment = Alignment.CenterVertically) {
                        Text(
                            "المسوحات المحفوظة",
                            style = MaterialTheme.typography.titleMedium,
                            fontWeight = FontWeight.Bold,
                            modifier = Modifier.weight(1f)
                        )
                        TextButton(onClick = { showArchive = false }) { Text("إغلاق") }
                    }
                    Text(
                        "مكان الحفظ الحالي: ${SurveyStore.storageLabel(ctx)} • ${items.size} عنصر",
                        style = MaterialTheme.typography.bodySmall
                    )
                    if (items.isEmpty()) {
                        Text("لا توجد مسوحات محفوظة بعد.", style = MaterialTheme.typography.bodyMedium)
                    } else {
                        LazyColumn(
                            Modifier.weight(1f),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            items(items, key = { it.file.absolutePath }) { m ->
                                Card(Modifier.fillMaxWidth()) {
                                    Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                                        Text(m.name, style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold)
                                        Text(
                                            "${fmtSurveyDate(m.timeMs)} • ${m.lines} خط × ${m.points} نقطة",
                                            style = MaterialTheme.typography.bodySmall
                                        )
                                        Row(horizontalArrangement = Arrangement.spacedBy(4.dp)) {
                                            Button(onClick = {
                                                scope.launch {
                                                    val sv = withContext(Dispatchers.IO) { SurveyStore.load(m.file) }
                                                    if (sv == null) {
                                                        status = "الملف تالف أو غير مقروء"
                                                    } else if (ui.phase == ScanPhase.Recording || ui.phase == ScanPhase.ReadyForLine) {
                                                        pendingLoad = sv
                                                    } else {
                                                        vm.loadSaved(sv.config, sv.s1, sv.s2)
                                                        showArchive = false
                                                        status = "تم فتح: ${m.name}"
                                                    }
                                                }
                                            }) { Text("فتح") }
                                            OutlinedButton(onClick = {
                                                scope.launch {
                                                    val sv = withContext(Dispatchers.IO) { SurveyStore.load(m.file) }
                                                    if (sv != null) {
                                                        pendingExport = sv
                                                        exportLauncher.launch(m.file.nameWithoutExtension + ".csv")
                                                    }
                                                }
                                            }) { Text("تصدير CSV") }
                                            TextButton(onClick = { pendingDelete = m }) { Text("حذف") }
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // ---- تأكيد الاستبدال أثناء جلسة جارية ----
    pendingLoad?.let { sv ->
        AlertDialog(
            onDismissRequest = { pendingLoad = null },
            title = { Text("استبدال الجلسة الحالية؟") },
            text = { Text("هناك جلسة مسح جارية، وفتح المسح المحفوظ سيستبدلها.") },
            confirmButton = {
                TextButton(onClick = {
                    vm.loadSaved(sv.config, sv.s1, sv.s2)
                    pendingLoad = null
                    showArchive = false
                    status = "تم فتح: ${sv.meta.name}"
                }) { Text("استبدال") }
            },
            dismissButton = { TextButton(onClick = { pendingLoad = null }) { Text("إلغاء") } }
        )
    }

    // ---- تأكيد الحذف ----
    pendingDelete?.let { m ->
        AlertDialog(
            onDismissRequest = { pendingDelete = null },
            title = { Text("حذف المسح؟") },
            text = { Text("سيُحذف «${m.name}» نهائياً من الذاكرة.") },
            confirmButton = {
                TextButton(onClick = {
                    pendingDelete = null
                    scope.launch {
                        withContext(Dispatchers.IO) { m.file.delete() }
                        refresh++
                    }
                }) { Text("حذف") }
            },
            dismissButton = { TextButton(onClick = { pendingDelete = null }) { Text("إلغاء") } }
        )
    }
}
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/GridScanScreen.kt'] = r'''package com.example.gradiometer.bluetooth

import android.graphics.Bitmap
import androidx.activity.compose.BackHandler
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
import androidx.compose.material3.Slider
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.ui.graphics.FilterQuality
import androidx.compose.ui.graphics.ImageBitmap
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.unit.IntOffset
import androidx.compose.ui.unit.IntSize
import androidx.compose.ui.unit.LayoutDirection
import kotlin.math.roundToInt
import androidx.compose.foundation.gestures.detectTapGestures
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
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
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
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
@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun GridScanScreen(
    readings: Flow<GradiometerReading>,
    modifier: Modifier = Modifier,
    vm: GridScanViewModel = viewModel(),
    /** إن لم يكن null يُثبَّت مصدر البيانات (مثلاً الماغنومتر = حساس واحد) وتختفي أزرار اختيار المصدر */
    fixedSource: FieldSource? = null,
    /** عنوان اختياري يظهر أعلى الشاشة */
    title: String? = null
) {
    val ui by vm.ui.collectAsStateWithLifecycle()
    LaunchedEffect(readings) { vm.bind(readings) }

    // ---- صفحة الإعدادات (بملء الشاشة) ----
    var showSettings by rememberSaveable { mutableStateOf(false) }

    // ---- متغيرات الواجهة (تبقى هنا لتُحفظ عند التنقل بين الصفحتين) ----
    var sourceChoice by rememberSaveable { mutableStateOf(FieldSource.Gradient) }
    val source = fixedSource ?: sourceChoice
    var bg by rememberSaveable { mutableStateOf(Background.GlobalMean) }
    var view3d by rememberSaveable { mutableStateOf(false) }
    var selected by remember(ui.s1) { mutableStateOf<Pair<Int, Int>?>(null) }

    // ---- ألوان الخريطة + العمق ----
    var palette by rememberSaveable { mutableStateOf(Palette.Thermal) }
    var scaleMode by rememberSaveable { mutableStateOf(ScaleMode.Auto) }
    var customLo by rememberSaveable { mutableFloatStateOf(Float.NaN) }
    var customHi by rememberSaveable { mutableFloatStateOf(Float.NaN) }
    var smooth by rememberSaveable { mutableStateOf(true) }
    var shape by rememberSaveable { mutableStateOf(SourceShape.Point) }
    var sensorH by rememberSaveable { mutableFloatStateOf(0.3f) }

    // يُعاد الحساب فقط عند اكتمال خط/بدء جلسة أو تغيير خيارات التحليل
    val analysis = remember(ui.s1, ui.s2, source, bg) { analyze(ui.s1, ui.s2, source, bg) }
    val scale = remember(analysis, scaleMode, customLo, customHi, palette) {
        analysis?.let { resolveScale(it, scaleMode, customLo, customHi, palette) }
    }
    val depth = remember(analysis, ui.config, source, shape, sensorH) {
        analysis?.let { estimateDepth(it, ui.config, source, shape, sensorH) }
    }
    val heatBitmap = remember(analysis, scale, smooth, view3d) {
        if (analysis != null && scale != null && smooth && !view3d) buildHeatBitmap(analysis, scale) else null
    }

    // زر الرجوع في النظام يغلق صفحة الإعدادات بدل الخروج من الشاشة
    BackHandler(enabled = showSettings) { showSettings = false }

    if (showSettings) {
        ScanSettingsPage(
            modifier = modifier,
            ui = ui,
            analysis = analysis,
            fixedSource = fixedSource,
            source = source,
            onSource = { sourceChoice = it },
            bg = bg,
            onBg = { bg = it },
            view3d = view3d,
            onView3d = { view3d = it },
            smooth = smooth,
            onSmooth = { smooth = it },
            palette = palette,
            onPalette = { palette = it },
            scaleMode = scaleMode,
            onScaleMode = { scaleMode = it },
            customLo = customLo,
            customHi = customHi,
            onCustomRange = { lo, hi -> customLo = lo; customHi = hi },
            onLines = vm::setLines,
            onPoints = vm::setPoints,
            onLineLength = vm::setLineLength,
            onLineSpacing = vm::setLineSpacing,
            onBack = { showSettings = false }
        )
        return
    }

    Column(
        modifier = modifier
            .verticalScroll(rememberScrollState())
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // ---- العنوان + زر الإعدادات ----
        Row(
            Modifier.fillMaxWidth(),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                title.orEmpty(),
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                modifier = Modifier.weight(1f)
            )
            FilledTonalButton(onClick = { showSettings = true }) { Text("⚙️ الإعدادات") }
        }

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

        SurveyArchiveBar(vm, if (fixedSource != null) "magnetometer" else "gradiometer")

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
                    Canvas(canvasMod) { drawBars3D(analysis, scale, rows, cols) }
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
                        drawHeatmap2D(analysis, scale, heatBitmap, rows, cols, ui, selected)
                    }
                }

                if (scale != null) ColorBar(scale)
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
        if (analysis != null) {
            AnalysisCard(
                a = analysis, cfg = ui.config, depth = depth,
                shape = shape, onShape = { shape = it },
                sensorH = sensorH, onSensorH = { sensorH = it }
            )
        }
    }
}

// ============================================================ صفحة الإعدادات

/**
 * صفحة إعدادات بملء الشاشة. لا تحتفظ بأي حالة خاصة بها:
 * كل القيم تأتي من [GridScanScreen] (rememberSaveable) وتعود إليه عبر الـ callbacks.
 */
@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun ScanSettingsPage(
    ui: GridScanUiState,
    analysis: FieldAnalysis?,
    fixedSource: FieldSource?,
    source: FieldSource,
    onSource: (FieldSource) -> Unit,
    bg: Background,
    onBg: (Background) -> Unit,
    view3d: Boolean,
    onView3d: (Boolean) -> Unit,
    smooth: Boolean,
    onSmooth: (Boolean) -> Unit,
    palette: Palette,
    onPalette: (Palette) -> Unit,
    scaleMode: ScaleMode,
    onScaleMode: (ScaleMode) -> Unit,
    customLo: Float,
    customHi: Float,
    onCustomRange: (Float, Float) -> Unit,
    onLines: (Int) -> Unit,
    onPoints: (Int) -> Unit,
    onLineLength: (Float) -> Unit,
    onLineSpacing: (Float) -> Unit,
    onBack: () -> Unit,
    modifier: Modifier = Modifier
) {
    val cfg = ui.config
    val locked = ui.phase != ScanPhase.Idle

    Column(modifier.fillMaxSize()) {
        // ---- الشريط العلوي ----
        Surface(tonalElevation = 3.dp, modifier = Modifier.fillMaxWidth()) {
            Row(
                Modifier
                    .fillMaxWidth()
                    .padding(horizontal = 8.dp, vertical = 6.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                TextButton(onClick = onBack) { Text("← رجوع للمسح") }
                Spacer(Modifier.weight(1f))
                Text(
                    "الإعدادات",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    modifier = Modifier.padding(end = 8.dp)
                )
            }
        }

        Column(
            Modifier
                .weight(1f)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            // ================= 1) أبعاد مساحة المسح =================
            Card(Modifier.fillMaxWidth()) {
                Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
                    Text("أبعاد مساحة المسح", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
                    if (locked) {
                        Text(
                            "الجلسة بدأت — اضغط «إعادة الضبط» في الشاشة الرئيسية لتعديل الأبعاد.",
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.error
                        )
                    }

                    Text("عدد الخطوط: ${cfg.lines}", style = MaterialTheme.typography.bodyMedium)
                    Slider(
                        value = cfg.lines.toFloat(),
                        onValueChange = { onLines(it.roundToInt()) },
                        valueRange = 1f..200f,
                        steps = 198,
                        enabled = !locked
                    )

                    Text("النقاط لكل خط: ${cfg.pointsPerLine}", style = MaterialTheme.typography.bodyMedium)
                    Slider(
                        value = cfg.pointsPerLine.toFloat(),
                        onValueChange = { onPoints(it.roundToInt()) },
                        valueRange = 2f..300f,
                        steps = 297,
                        enabled = !locked
                    )

                    Text("طول الخط: ${cfg.lineLengthM.f(1)} م", style = MaterialTheme.typography.bodyMedium)
                    Slider(
                        value = cfg.lineLengthM,
                        onValueChange = { onLineLength((it * 2f).roundToInt() / 2f) },
                        valueRange = 0.5f..500f,
                        enabled = !locked
                    )

                    Text("المسافة بين الخطوط: ${cfg.lineSpacingM.f(1)} م", style = MaterialTheme.typography.bodyMedium)
                    Slider(
                        value = cfg.lineSpacingM,
                        onValueChange = { onLineSpacing((it * 10f).roundToInt() / 10f) },
                        valueRange = 0.1f..50f,
                        enabled = !locked
                    )

                    HorizontalDivider()
                    val area = cfg.lineLengthM * cfg.lines * cfg.lineSpacingM
                    StatRow("إجمالي المساحة", "${area.f(1)} م²")
                }
            }

            // ================= 2) البيانات والتحليل =================
            Card(Modifier.fillMaxWidth()) {
                Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("البيانات والتحليل", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)

                    Text("مصدر البيانات", style = MaterialTheme.typography.labelLarge)
                    if (fixedSource == null) {
                        FlowRow(
                            horizontalArrangement = Arrangement.spacedBy(8.dp),
                            verticalArrangement = Arrangement.spacedBy(4.dp)
                        ) {
                            listOf(
                                FieldSource.S1 to "الحساس 1",
                                FieldSource.S2 to "الحساس 2",
                                FieldSource.Gradient to "الفرق S1−S2"
                            ).forEach { (v, label) ->
                                FilterChip(selected = source == v, onClick = { onSource(v) }, label = { Text(label) })
                            }
                        }
                    } else {
                        Text(
                            sourceLabel(fixedSource),
                            style = MaterialTheme.typography.bodyMedium,
                            fontWeight = FontWeight.Medium
                        )
                    }

                    Text("طرح الخلفية", style = MaterialTheme.typography.labelLarge)
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        listOf(
                            Background.None to "بدون",
                            Background.GlobalMean to "متوسط عام",
                            Background.LineMean to "متوسط الخط"
                        ).forEach { (v, label) ->
                            FilterChip(selected = bg == v, onClick = { onBg(v) }, label = { Text(label) })
                        }
                    }
                }
            }

            // ================= 3) الخريطة والألوان =================
            Card(Modifier.fillMaxWidth()) {
                Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                    Text("الخريطة والألوان", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)

                    Text("نمط العرض", style = MaterialTheme.typography.labelLarge)
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        FilterChip(selected = !view3d, onClick = { onView3d(false) }, label = { Text("خريطة حرارية 2D") })
                        FilterChip(selected = view3d, onClick = { onView3d(true) }, label = { Text("أعمدة 3D") })
                    }
                    if (!view3d) {
                        FilterChip(
                            selected = smooth,
                            onClick = { onSmooth(!smooth) },
                            label = { Text("تنعيم الألوان (استيفاء)") }
                        )
                    }

                    Text("لوحة الألوان", style = MaterialTheme.typography.labelLarge)
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Palette.values().forEach { p ->
                            FilterChip(selected = palette == p, onClick = { onPalette(p) }, label = { Text(p.label) })
                        }
                    }
                    Canvas(
                        Modifier
                            .fillMaxWidth()
                            .height(10.dp)
                            .clip(RoundedCornerShape(5.dp))
                    ) { drawRect(Brush.horizontalGradient(palette.stops)) }

                    Text("نطاق الألوان", style = MaterialTheme.typography.labelLarge)
                    FlowRow(
                        horizontalArrangement = Arrangement.spacedBy(8.dp),
                        verticalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        ScaleMode.values().forEach { m ->
                            FilterChip(
                                selected = scaleMode == m,
                                onClick = {
                                    onScaleMode(m)
                                    if (m == ScaleMode.Custom && analysis != null && customLo.isNaN()) {
                                        onCustomRange(analysis.lo, analysis.hi)
                                    }
                                },
                                label = { Text(m.label) }
                            )
                        }
                    }
                    if (scaleMode == ScaleMode.Custom && analysis != null && analysis.max - analysis.min > 1e-6f) {
                        val lo0 = analysis.min
                        val hi0 = analysis.max
                        val gap = (hi0 - lo0) * 0.01f
                        val curLo = (if (customLo.isFinite()) customLo else analysis.lo).coerceIn(lo0, hi0)
                        val curHi = (if (customHi.isFinite()) customHi else analysis.hi).coerceIn(lo0, hi0)
                        Text("أدنى لون (بارد): ${curLo.f(2)} $UNIT_LABEL", style = MaterialTheme.typography.bodySmall)
                        Slider(
                            value = curLo,
                            onValueChange = { onCustomRange(minOf(it, curHi - gap), curHi) },
                            valueRange = lo0..hi0
                        )
                        Text("أعلى لون (ساخن): ${curHi.f(2)} $UNIT_LABEL", style = MaterialTheme.typography.bodySmall)
                        Slider(
                            value = curHi,
                            onValueChange = { onCustomRange(curLo, maxOf(it, curLo + gap)) },
                            valueRange = lo0..hi0
                        )
                        TextButton(onClick = {
                            onCustomRange(Float.NaN, Float.NaN); onScaleMode(ScaleMode.Auto)
                        }) { Text("إعادة إلى التلقائي") }
                    }
                }
            }

            Spacer(Modifier.height(16.dp))
        }
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

@OptIn(ExperimentalLayoutApi::class)
@Composable
private fun AnalysisCard(
    a: FieldAnalysis,
    cfg: GridConfig,
    depth: DepthEstimate?,
    shape: SourceShape,
    onShape: (SourceShape) -> Unit,
    sensorH: Float,
    onSensorH: (Float) -> Unit
) {
    // موضع النقطة بالمتر: العمود يمتد على طول الخط، والصف = رقم الخط × التباعد
    fun xM(col: Float) = col / (cfg.pointsPerLine - 1).coerceAtLeast(1) * cfg.lineLengthM
    fun yM(row: Float) = row * cfg.lineSpacingM
    val d = depth?.takeIf { it.depthM.isFinite() }

    Card(Modifier.fillMaxWidth()) {
        Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(6.dp)) {
            Text("تفاصيل التحليل", style = MaterialTheme.typography.titleMedium, fontWeight = FontWeight.SemiBold)
            HorizontalDivider()

            // ---- ملخص الهدف: الإحداثيات + العمق ----
            Card(
                Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(containerColor = MaterialTheme.colorScheme.primaryContainer)
            ) {
                Column(Modifier.padding(10.dp), verticalArrangement = Arrangement.spacedBy(4.dp)) {
                    Text("الهدف المقدَّر", style = MaterialTheme.typography.labelLarge, fontWeight = FontWeight.Bold)
                    StatRow("الذروة (x , y)", "${xM(a.peakCol.toFloat()).f(2)} ، ${yM(a.peakRow.toFloat()).f(2)} م")
                    StatRow("المركز (x , y)", "${xM(a.centroidCol).f(2)} ، ${yM(a.centroidRow).f(2)} م")
                    StatRow("العمق المقدَّر", if (d != null) "${d.depthM.f(2)} م" else "—")
                }
            }

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
            Text("تقدير العمق (Depth)", style = MaterialTheme.typography.labelLarge, color = MaterialTheme.colorScheme.primary)
            Text("شكل الهدف", style = MaterialTheme.typography.bodySmall)
            FlowRow(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                SourceShape.values().forEach { s ->
                    FilterChip(selected = shape == s, onClick = { onShape(s) }, label = { Text(s.label) })
                }
            }
            Text("ارتفاع الحساس السفلي عن الأرض: ${sensorH.f(2)} م", style = MaterialTheme.typography.bodySmall)
            Slider(
                value = sensorH,
                onValueChange = { onSensorH((it * 20f).roundToInt() / 20f) },
                valueRange = 0f..2f
            )
            if (d != null) {
                d.parts.forEach { StatRow(it.label, "${it.distanceM.f(2)} م") }
                StatRow("المسافة حساس ← مركز الهدف", "${d.distanceM.f(2)} م")
                StatRow("العمق تحت السطح", "${d.depthM.f(2)} م")
                StatRow("المدى", "${d.minDepthM.f(2)} … ${d.maxDepthM.f(2)} م")
                StatRow("أُسّ التناقص N", d.exponent.f(0))
            }
            depth?.warnings.orEmpty().forEach {
                Text("⚠ $it", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
            Text(
                "تقدير تقريبي (عادة ±30%): يفترض هدفاً معزولاً وخلفية مطروحة جيداً.",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )

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
internal fun ColorBar(sc: ColorScale) {
    Column {
        Canvas(
            Modifier
                .fillMaxWidth()
                .height(14.dp)
                .clip(RoundedCornerShape(6.dp))
        ) {
            drawRect(Brush.horizontalGradient(sc.palette.stops))
            if (sc.lo < 0f && sc.hi > 0f) { // علامة الصفر
                val x = (-sc.lo / (sc.hi - sc.lo)) * size.width
                drawLine(Color.Black, Offset(x, 0f), Offset(x, size.height), 4f)
                drawLine(Color.White, Offset(x, 0f), Offset(x, size.height), 2f)
            }
        }
        Spacer(Modifier.height(2.dp))
        // التدرج يُرسم يسار←يمين دائماً، لذا نثبّت اتجاه الأرقام حتى في واجهة RTL
        CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Ltr) {
            Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
                Text(sc.lo.f(1), fontSize = 11.sp, fontFamily = FontFamily.Monospace)
                Text(UNIT_LABEL, fontSize = 11.sp, color = MaterialTheme.colorScheme.onSurfaceVariant)
                Text(sc.hi.f(1), fontSize = 11.sp, fontFamily = FontFamily.Monospace)
            }
        }
    }
}

// ============================================================== الرسم (2D)

internal fun DrawScope.drawHeatmap2D(
    a: FieldAnalysis?,
    sc: ColorScale?, bmp: ImageBitmap?,
    rows: Int, cols: Int,
    ui: GridScanUiState,
    selected: Pair<Int, Int>?
) {
    val cw = size.width / cols
    val ch = size.height / rows
    val empty = Color(0xFF2B2B2B)

    if (bmp != null) { // وضع التنعيم: صورة صغيرة (cols×rows) تُكبَّر باستيفاء ثنائي الخطية
        drawImage(
            image = bmp,
            srcOffset = IntOffset.Zero,
            srcSize = IntSize(bmp.width, bmp.height),
            dstOffset = IntOffset.Zero,
            dstSize = IntSize(size.width.toInt(), size.height.toInt()),
            filterQuality = FilterQuality.High
        )
    } else for (r in 0 until rows) for (c in 0 until cols) {
        val v = a?.matrix?.getOrNull(r)?.getOrNull(c)
        val color = if (sc != null && v != null && v.isFinite()) sc.color(v) else empty
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
internal fun DrawScope.drawBars3D(a: FieldAnalysis?, cs: ColorScale?, rows: Int, cols: Int) {
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
            val valid = a != null && cs != null && v != null && v.isFinite()
            val t = if (valid) cs!!.norm(v!!) else 0f
            val z = t * hMax
            val top = if (valid) paletteColor(cs!!.palette, t) else Color(0xFF3A3A3A)
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

// ===================================================================== ألوان (الصورة المنعّمة)

/** صورة بحجم الشبكة (عمود = بكسل) تُلوَّن وفق النطاق الحالي؛ الخلايا غير المقاسة رمادية */
internal fun buildHeatBitmap(a: FieldAnalysis, sc: ColorScale): ImageBitmap? {
    val rows = a.matrix.size
    val cols = if (rows > 0) a.matrix[0].size else 0
    if (rows < 1 || cols < 1) return null
    val empty = Color(0xFF2B2B2B).toArgb()
    val px = IntArray(rows * cols)
    for (r in 0 until rows) for (c in 0 until cols) {
        val v = a.matrix[r][c]
        px[r * cols + c] = if (v.isFinite()) sc.color(v).toArgb() else empty
    }
    val bmp = Bitmap.createBitmap(cols, rows, Bitmap.Config.ARGB_8888)
    bmp.setPixels(px, 0, cols, 0, 0, cols, rows)
    return bmp.asImageBitmap()
}

private fun sourceLabel(s: FieldSource): String = when (s) {
    FieldSource.S1 -> "الحساس 1"
    FieldSource.S2 -> "الحساس 2"
    FieldSource.Gradient -> "الفرق S1−S2"
}

private fun Float.f(digits: Int = 2): String = String.format(Locale.US, "%.${digits}f", this)
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/GradiometerDataScreen.kt'] = r'''package com.example.gradiometer.bluetooth

import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.flow.Flow

/**
 * تبويب 2: الجراديومتر — تجميع البيانات.
 * مسح شبكي بالحساسين معاً: الحساس 1 / الحساس 2 / الفرق S1−S2، مع الخريطة والتحليل.
 * له ViewModel مستقل (key = "gradiometer") فلا تختلط جلسته بجلسة الماغنومتر.
 */
@Composable
fun GradiometerDataScreen(
    readings: Flow<GradiometerReading>,
    modifier: Modifier = Modifier,
    vm: GridScanViewModel = viewModel<GridScanViewModel>(key = "gradiometer")
) {
    GridScanScreen(
        readings = readings,
        modifier = modifier,
        vm = vm,
        fixedSource = null,
        title = "الجراديومتر — تجميع البيانات (الحساس 1 + الحساس 2)"
    )
}
'''

FILES['app/src/main/java/com/example/gradiometer/bluetooth/MagnetometerDataScreen.kt'] = r'''package com.example.gradiometer.bluetooth

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.lifecycle.viewmodel.compose.viewModel
import kotlinx.coroutines.flow.Flow

/**
 * تبويب 3: الماغنومتر — تجميع البيانات.
 * نفس محرك المسح الشبكي لكن بمصدر واحد ثابت: الحساس السفلي فقط (بلا فرق ولا حساس ثانٍ).
 * له ViewModel مستقل (key = "magnetometer").
 *
 * أي القناتين هي «السفلية»؟ يحدده المستخدم هنا (الافتراضي: الحساس 1 = أول رقم في السطر).
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun MagnetometerDataScreen(
    readings: Flow<GradiometerReading>,
    modifier: Modifier = Modifier,
    vm: GridScanViewModel = viewModel<GridScanViewModel>(key = "magnetometer")
) {
    // 1 = الحساس 1 (أول قيمة)، 2 = الحساس 2 (ثاني قيمة)
    var lower by rememberSaveable { mutableIntStateOf(1) }

    Column(modifier.fillMaxSize()) {
        Card(Modifier.fillMaxWidth().padding(start = 16.dp, end = 16.dp, top = 12.dp)) {
            Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text("الحساس السفلي (مصدر الماغنومتر)", style = MaterialTheme.typography.labelLarge)
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    FilterChip(
                        selected = lower == 1,
                        onClick = { lower = 1 },
                        label = { Text("الحساس 1") }
                    )
                    FilterChip(
                        selected = lower == 2,
                        onClick = { lower = 2 },
                        label = { Text("الحساس 2") }
                    )
                }
            }
        }

        GridScanScreen(
            readings = readings,
            modifier = Modifier.weight(1f),
            vm = vm,
            fixedSource = if (lower == 1) FieldSource.S1 else FieldSource.S2,
            title = "الماغنومتر — تجميع البيانات (الحساس السفلي فقط)"
        )
    }
}
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
