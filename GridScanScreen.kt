package com.example.gradiometer.bluetooth

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
