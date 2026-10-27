package com.example.gradiometer.bluetooth

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
        b1.add(r.values[0] * VALUE_SCALE)
        b2.add(if (r.values.size > 1) r.values[1] * VALUE_SCALE else Float.NaN)

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
