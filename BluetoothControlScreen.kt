package com.example.gradiometer.bluetooth

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
