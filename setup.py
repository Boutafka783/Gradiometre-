#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
setup.py
ينشئ مشروع أندرويد كامل باسم VoiceAssistant (com.example.voiceassistant).

الميزات المضافة في هذا الإصدار:
  1. المساعد الافتراضي (ASSIST + VoiceInteractionService) مع الاستماع التلقائي.
  2. المحادثة المستمرة (إعادة تشغيل الميكروفون بعد ثانية من انتهاء الرد الصوتي).
  3. المحادثة مع الذكاء الاصطناعي (Gemini) عبر OkHttp عندما لا يُفهم الأمر.
  4. التحكم بمفاتيح الإعدادات (Wi-Fi / Bluetooth ...) عبر خدمة الوصول.
  5. كتابة الأكواد والملفات (HTML / CSS / Java / setup وغيرها) مع نسخ وحفظ (موسّعة).
  6. توليد الصور بالذكاء الاصطناعي (مثال: «ارسم لي قطة») مع حفظ الصورة.
  7. قراءة ملفات الأكواد والتعديل عليها بالصوت أو الكتابة، ثم كتابة التعديل فوق الملف الأصلي.
  8. واجهة محسّنة: الأفاتار ظاهر دائماً، الميكروفون داخل شريط الكتابة،
     والرد على النص المكتوب صامت (الرد الصوتي فقط عند التحدث).
  9. تذكيرات صوتية («ذكرني بشرب الماء بعد 10 دقائق») عبر AlarmManager + ReminderReceiver +
     SpeakingService (خدمة أمامية + TTS) وتعمل حتى لو كان التطبيق مغلقاً.
 10. تفاعل استباقي: ترحيب صوتي عند فتح التطبيق، وسؤال عن الأحوال كل 6 ساعات في الخلفية
     عبر WorkManager (ProactiveWorker) مع إشعار ونطق (TTS).
 11. ذاكرة طويلة المدى محلية (حقائق المستخدم + المشاريع) تُحقن في system prompt بدون أي طلب شبكة إضافي.
 12. الحماية من السرقة: موقع عبر SMS عند إرسال كلمة السر من الرقم الموثوق، تنبيه عند تغيير الشريحة بعد
     الإقلاع، وتنبيه عند محاولة إلغاء مدير الجهاز (Device Admin).
 13. توليد الصور عبر نماذج Imagen (نقطة النهاية predict) مع احتياط نماذج Gemini للصور.
 14. شاشة إعدادات النماذج (القائمة الجانبية): التبديل بين Gemini و ChatGPT و Claude (claude-3-haiku-20240307)
     وإدخال مفتاح API لكل نموذج وحفظه مشفّراً على الجهاز. مفاتيح GitHub تأتي من GitHub Secrets عبر BuildConfig فقط.
 16. البحث المباشر في الويب (Google Search Grounding) مع Gemini: أداة google_search تُرسل مع كل سؤال عادي،
     ويمكن إيقافها من شاشة «نماذج الذكاء الاصطناعي».
 15. زر Enter العادي (سطر جديد) في لوحة المفاتيح بدل زر الإرسال؛ الإرسال بزر السهم بجانب الحقل.
 17. تحليل الكاميرا: زر كاميرا في شريط الإدخال يفتح تطبيق الكاميرا (TakePicture + FileProvider)،
     تُحفظ الصورة في الكاش وتُرسل عبر askWithFile مع «حلل هذه الصورة واشرح ما فيها».
 18. لقطة الشاشة: زر في شريط الإدخال يطلب إذن MediaProjection ثم ScreenCaptureService (خدمة أمامية)
     تأخذ لقطة واحدة وتتوقف، وتُرسل عبر askWithFile مع «اقرأ ما في هذه الشاشة واشرحه لي».
 19. أصوات بشرية حقيقية (ذكور وإناث) عبر Gemini TTS: زر «الصوت» في قائمة الإعدادات يفتح شاشة اختيار الصوت مع تجربة
     لكل صوت، ومفتاح للرجوع إلى صوت الهاتف. احتياط تلقائي بصوت الهاتف عند غياب الإنترنت أو المفتاح.
20. الربط الخارجي: زر «البلوتوث والواي فاي» في قائمة الإعدادات يفتح شاشة لالتقاط أجهزة البلوتوث وشبكات الواي فاي القريبة،
    والاقتران بجهاز بلوتوث، والاتصال بشبكة واي فاي (بكلمة مرور)، وجعل الهاتف مرئياً للأجهزة الأخرى.

الاستخدام:
    python setup.py            # ينشئ المشروع في المجلد الحالي
    python setup.py MyDir      # ينشئ المشروع في المجلد MyDir
    python setup.py --test     # يختبر هذا الملف قبل رفعه (بيئة اختبار مدمجة، لا تنشئ شيئاً في المجلد الحالي)

بعد ذلك:  gradle assembleDebug   (Gradle 8.10+, JDK 17, Android SDK 35)
"""
import os
import re
import sys

# ==============================================================================
# بيئة الاختبار المدمجة:  python setup.py --test
# تشغّل هذا الملف نفسه في مجلد مؤقت معزول وتفحص المشروع المولَّد قبل رفعه إلى GitHub.
# لا تؤثر إطلاقاً على التوليد العادي (python setup.py / python setup.py MyDir).
# خيارات: --keep (إبقاء المشروع)  --build (gradle assembleDebug إن توفر)  -v (تفاصيل)  [مسار ملف setup آخر]
# ==============================================================================
import argparse
import ast
import bisect
import hashlib
import os
import re
import shutil
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from collections import defaultdict

PKG = "com.example.voiceassistant"
PKG_DIR = "app/src/main/java/com/example/voiceassistant"
KEY_ENV = ("GEMINI_API_KEY", "OPENAI_API_KEY", "CLAUDE_API_KEY")

SECRET_PATTERNS = [
    ("Google API key", re.compile(r"AIza[0-9A-Za-z_\-]{35}")),
    ("Anthropic key", re.compile(r"sk-ant-[A-Za-z0-9_\-]{20,}")),
    ("OpenAI key", re.compile(r"sk-(?:proj-)?[A-Za-z0-9_\-]{32,}")),
    ("GitHub token", re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}|github_pat_[A-Za-z0-9_]{40,}")),
]

# أسماء قد تأتي من كلاس أب (nested/inherited) فلا تحتاج استيراداً: تُستثنى من فحص "استيراد ناقص".
INHERITED_NAMES = {"Callback", "Companion", "Builder", "Listener", "Result", "Key", "Entry"}

# مكتبة -> (بادئة الاستيراد، جزء من إحداثيات gradle المطلوبة)
LIB_MAP = [
    ("okhttp3.", "com.squareup.okhttp3:okhttp"),
    ("androidx.work.", "androidx.work:work-runtime"),
    ("androidx.security.crypto.", "androidx.security:security-crypto"),
    ("androidx.compose.material.icons.", "androidx.compose.material:material-icons"),
    ("androidx.compose.material3.", "androidx.compose.material3:material3"),
    ("androidx.compose.ui.", "androidx.compose.ui:ui"),
    ("androidx.activity.compose.", "androidx.activity:activity-compose"),
    ("androidx.lifecycle.compose.", "androidx.lifecycle:lifecycle-runtime-compose"),
    ("androidx.lifecycle.viewmodel.compose.", "androidx.lifecycle:lifecycle-viewmodel-compose"),
    ("androidx.core.", "androidx.core:core"),
    ("kotlinx.coroutines.", "kotlinx-coroutines"),
]
NO_LIB_PREFIXES = (
    "android.", "java.", "javax.", "kotlin.", "org.json.", "org.xmlpull.", "org.w3c.",
    "androidx.compose.runtime.", "androidx.compose.foundation.", "androidx.compose.animation.",
    "androidx.activity.", "androidx.lifecycle.", PKG + ".",
)

OK, FAIL, WARN = "PASS", "FAIL", "WARN"


# ------------------------------------------------------------------ تقرير النتائج
class Report:
    def __init__(self, verbose):
        self.verbose = verbose
        self.counts = {OK: 0, FAIL: 0, WARN: 0}

    def add(self, status, title, details=None):
        self.counts[status] += 1
        print("[{}] {}".format(status, title))
        details = details or []
        limit = len(details) if self.verbose else 12
        for line in details[:limit]:
            print("       - " + line)
        if len(details) > limit:
            print("       ... و {} أخرى (استخدم -v لعرضها كلها)".format(len(details) - limit))

    def run(self, title, fn):
        """fn() -> (errors, warnings)"""
        try:
            errors, warnings = fn()
        except Exception as exc:  # خطأ في الاختبار نفسه لا يجب أن يخفي بقية النتائج
            self.add(FAIL, title + " (تعذّر تنفيذ الفحص)", ["{}: {}".format(type(exc).__name__, exc)])
            return
        if errors:
            self.add(FAIL, title, errors + ["(تحذيرات) " + w for w in warnings])
        elif warnings:
            self.add(WARN, title, warnings)
        else:
            self.add(OK, title)


# ------------------------------------------------------------------ تشغيل setup.py في بيئة معزولة
def run_setup(setup_copy, out_dir, workdir):
    env = {k: v for k, v in os.environ.items() if k not in KEY_ENV}
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    return subprocess.run(
        [sys.executable, setup_copy, out_dir],
        cwd=workdir, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        timeout=300, universal_newlines=True, encoding="utf-8", errors="replace",
    )


def snapshot(root):
    result = {}
    for base, _dirs, files in os.walk(root):
        for name in files:
            path = os.path.join(base, name)
            with open(path, "rb") as f:
                result[os.path.relpath(path, root).replace(os.sep, "/")] = hashlib.sha256(f.read()).hexdigest()
    return result


def read(root, rel):
    with open(os.path.join(root, rel), "r", encoding="utf-8") as f:
        return f.read()


# ------------------------------------------------------------------ ماسح Kotlin (تعليقات / نصوص / قوالب ${})
class KtMasked:
    """نسخة من الكود بنفس الطول: التعليقات والنصوص تُستبدل بمسافات (الأسطر محفوظة)."""

    def __init__(self, src):
        self.src = src
        self.errors = []
        self.nl = [m.start() for m in re.finditer("\n", src)]
        self.text = self._mask()

    def line(self, pos):
        return bisect.bisect_left(self.nl, pos) + 1

    @staticmethod
    def _blank(seg):
        return re.sub(r"[^\n]", " ", seg)

    def _mask(self):
        src, n, i = self.src, len(self.src), 0
        out, frames = [], [["code", 0]]
        while i < n:
            kind, c = frames[-1][0], src[i]
            top = len(frames) == 1
            if kind in ("code", "tmpl"):
                if src.startswith("//", i):
                    j = src.find("\n", i)
                    j = n if j < 0 else j
                    out.append(" " * (j - i)); i = j; continue
                if src.startswith("/*", i):
                    depth, j = 1, i + 2
                    while j < n and depth:
                        if src.startswith("/*", j): depth += 1; j += 2
                        elif src.startswith("*/", j): depth -= 1; j += 2
                        else: j += 1
                    if depth:
                        self.errors.append((self.line(i), "تعليق /* بدون إغلاق"))
                    out.append(self._blank(src[i:j])); i = j; continue
                if src.startswith('"""', i):
                    frames.append(["raw", 0]); out.append("   "); i += 3; continue
                if c == '"':
                    frames.append(["str", 0]); out.append(" "); i += 1; continue
                if c == "'":
                    j = i + 1
                    if j < n and src[j] == "\\":
                        j += 2
                        while j < n and src[j] not in ("'", "\n"):
                            j += 1
                    else:
                        j += 1
                    if j < n and src[j] == "'":
                        out.append(" " * (j + 1 - i)); i = j + 1; continue
                    out.append(c); i += 1; continue
                if c == "`":
                    j = src.find("`", i + 1)
                    if j > 0 and "\n" not in src[i:j]:
                        out.append(" " * (j + 1 - i)); i = j + 1; continue
                if kind == "tmpl":
                    if c == "{":
                        frames[-1][1] += 1
                    elif c == "}":
                        if frames[-1][1] == 0:
                            frames.pop(); out.append(" "); i += 1; continue
                        frames[-1][1] -= 1
                out.append(c if (top or c == "\n") else " "); i += 1
            elif kind == "str":
                if c == "\\":
                    out.append(self._blank(src[i:i + 2])); i += 2
                elif c == '"':
                    frames.pop(); out.append(" "); i += 1
                elif c == "$" and src.startswith("${", i):
                    frames.append(["tmpl", 0]); out.append("  "); i += 2
                elif c == "\n":
                    self.errors.append((self.line(i), 'نص "..." بدون إغلاق في نفس السطر'))
                    frames.pop(); out.append("\n"); i += 1
                else:
                    out.append(" "); i += 1
            else:  # raw string
                if src.startswith('"""', i):
                    j = i
                    while j < n and src[j] == '"':
                        j += 1
                    frames.pop(); out.append(" " * (j - i)); i = j
                elif c == "$" and src.startswith("${", i):
                    frames.append(["tmpl", 0]); out.append("  "); i += 2
                else:
                    out.append(c if c == "\n" else " "); i += 1
        if len(frames) > 1:
            self.errors.append((self.line(n - 1), "نص أو قالب ${} مفتوح ولم يُغلق حتى نهاية الملف"))
        return "".join(out)

    def balance_errors(self):
        pairs = {")": "(", "]": "[", "}": "{"}
        stack, errs = [], []
        for idx, ch in enumerate(self.text):
            if ch in "([{":
                stack.append((ch, idx))
            elif ch in pairs:
                if not stack:
                    errs.append("السطر {}: '{}' زائد بلا فتح".format(self.line(idx), ch)); continue
                if stack[-1][0] != pairs[ch]:
                    errs.append("السطر {}: '{}' لا يطابق '{}' المفتوح في السطر {}".format(
                        self.line(idx), ch, stack[-1][0], self.line(stack[-1][1])))
                    continue
                stack.pop()
        for ch, idx in stack:
            errs.append("السطر {}: '{}' لم يُغلق".format(self.line(idx), ch))
        return errs[:6]


DECL_RE = re.compile(
    r"^[ \t]*(?:@\w+(?:\([^)\n]*\))?[ \t]*)*"
    r"(?P<mods>(?:(?:public|internal|private|protected|abstract|open|final|sealed|data|enum|annotation|"
    r"inline|value|const|lateinit|override|expect|actual|companion|suspend|tailrec|operator|infix|"
    r"external|inner|fun)[ \t]+)*)"
    r"(?P<kind>class|interface|object|fun|val|var|typealias)[ \t]+"
    r"(?:<[^\n]*?>[ \t]*)?"
    r"(?P<recv>[\w.<>?,* ]*?\.)?(?P<name>\w+)",
    re.M,
)
IMPORT_RE = re.compile(r"^[ \t]*import[ \t]+([\w.]+)(?:\.(\*))?(?:[ \t]+as[ \t]+(\w+))?[ \t]*$", re.M)
PACKAGE_RE = re.compile(r"^[ \t]*package[ \t]+([\w.]+)", re.M)


class KtFile:
    def __init__(self, rel, src):
        self.rel = rel
        self.m = KtMasked(src)
        t = self.m.text
        pk = PACKAGE_RE.search(t)
        self.package = pk.group(1) if pk else ""
        self.imports = []  # (fqn, wildcard, alias, line)
        for im in IMPORT_RE.finditer(t):
            fqn, star, alias = im.group(1), im.group(2), im.group(3)
            self.imports.append((fqn + (".*" if star else ""), bool(star), alias, self.m.line(im.start())))
        # نص بدون سطور package/import، لاستخراج المعرّفات المستخدمة
        self.body = IMPORT_RE.sub(lambda mm: " " * len(mm.group(0)), t)
        self.body = PACKAGE_RE.sub(lambda mm: " " * len(mm.group(0)), self.body)
        self.decls = self._decls()

    def _decls(self):
        """يحلّل التعريفات مع مسار الأقواس { } وعمق الأقواس ( ) عند كل تعريف."""
        t = self.m.text
        found = {m.start(): m for m in DECL_RE.finditer(t)}
        starts = sorted(found)
        result, stack, counter, paren, si = [], [], 0, 0, 0
        for pos, ch in enumerate(t):
            while si < len(starts) and starts[si] <= pos:
                m = found[starts[si]]; si += 1
                if paren == 0:
                    result.append(dict(
                        kind=m.group("kind"), name=m.group("name"), recv=(m.group("recv") or "").strip(),
                        mods=m.group("mods").split(), scope=tuple(stack), pos=m.start("kind"),
                        end=m.end(), top=not stack))
            if ch == "{":
                counter += 1; stack.append(counter)
            elif ch == "}":
                if stack: stack.pop()
            elif ch == "(":
                paren += 1
            elif ch == ")":
                paren = max(0, paren - 1)
        return result

    def params_of(self, d):
        t = self.m.text
        j = d["end"]
        while j < len(t) and t[j] in " \t":
            j += 1
        if j >= len(t) or t[j] != "(":
            return None
        depth, k = 0, j
        while k < len(t):
            if t[k] == "(": depth += 1
            elif t[k] == ")":
                depth -= 1
                if depth == 0: break
            k += 1
        inner, parts, cur, lvl = t[j + 1:k], [], "", 0
        for ch in inner:
            if ch in "(<[{": lvl += 1
            elif ch in ")>]}": lvl -= 1
            if ch == "," and lvl == 0:
                parts.append(cur); cur = ""
            else:
                cur += ch
        parts.append(cur)
        types = []
        for p in parts:
            p = re.sub(r"\s+", " ", p).strip()
            if not p: continue
            p = re.sub(r"^(?:(?:vararg|crossinline|noinline|val|var)\s+)+", "", p)
            tp = p.split(":", 1)[1] if ":" in p else p
            tp = re.split(r"(?<![<>=!\-])=(?![=>])", tp)[0].strip()
            types.append(tp)
        return tuple(types)


# ------------------------------------------------------------------ بناء فهرس المشروع
def load_kotlin(root):
    files = {}
    for base, _d, names in os.walk(os.path.join(root, "app", "src", "main", "java")):
        for name in names:
            if name.endswith(".kt"):
                full = os.path.join(base, name)
                rel = os.path.relpath(full, root).replace(os.sep, "/")
                with open(full, "r", encoding="utf-8") as f:
                    files[rel] = KtFile(rel, f.read())
    return files


def top_names(files):
    """package -> {name: kinds}  (التعريفات العلنية على مستوى الملف فقط)"""
    table = defaultdict(lambda: defaultdict(set))
    for kf in files.values():
        for d in kf.decls:
            if d["top"] and "private" not in d["mods"]:
                table[kf.package][d["name"]].add(d["kind"])
    return table


# ------------------------------------------------------------------ الفحوص
def chk_python_syntax(setup_path):
    def fn():
        src = open(setup_path, "r", encoding="utf-8").read()
        try:
            ast.parse(src, setup_path)
        except SyntaxError as e:
            return ["السطر {}: {}".format(e.lineno, e.msg)], []
        return [], []
    return fn


def chk_secrets_text(label, text):
    errs = []
    for name, rx in SECRET_PATTERNS:
        for m in rx.finditer(text):
            val = m.group(0)
            errs.append("{}: يبدو أنه {} ({}…) - لا ترفعه إلى GitHub".format(
                label, name, val[:6] + "*" * 6))
    return errs


def chk_expected_files(root):
    def fn():
        errs, warns = [], []
        required = [
            "settings.gradle.kts", "build.gradle.kts", "gradle.properties", "proguard-rules.pro",
            "app/build.gradle.kts", "app/src/main/AndroidManifest.xml", ".github/workflows/build.yml",
            ".gitignore", PKG_DIR + "/MainActivity.kt", PKG_DIR + "/VoiceAssistantApp.kt",
            "app/src/main/res/values/strings.xml", "app/src/main/res/values/themes.xml",
        ]
        for rel in required:
            if not os.path.isfile(os.path.join(root, rel)):
                errs.append("ملف أساسي مفقود: " + rel)
        for base, _d, names in os.walk(root):
            for name in names:
                path = os.path.join(base, name)
                rel = os.path.relpath(path, root).replace(os.sep, "/")
                raw = open(path, "rb").read()
                if not raw.strip():
                    errs.append("ملف فارغ: " + rel)
                    continue
                try:
                    txt = raw.decode("utf-8")
                except UnicodeDecodeError as e:
                    errs.append("{} ليس UTF-8 صالحاً ({})".format(rel, e)); continue
                if "\x00" in txt: errs.append("{} يحتوي على بايت صفري".format(rel))
                if "\r" in txt: warns.append("{} فيه نهايات أسطر Windows (CR)".format(rel))
                if txt.startswith("\ufeff"): warns.append("{} يبدأ بعلامة BOM".format(rel))
                if re.search(r"\.(orig|rej|tmp|bak)$", name): warns.append("ملف مؤقت مولَّد: " + rel)
        return errs, warns
    return fn


def chk_xml(root):
    def fn():
        errs = []
        for base, _d, names in os.walk(root):
            for name in names:
                if name.endswith(".xml"):
                    path = os.path.join(base, name)
                    try:
                        ET.parse(path)
                    except ET.ParseError as e:
                        errs.append("{}: {}".format(os.path.relpath(path, root).replace(os.sep, "/"), e))
        return errs, []
    return fn


ANDROID = "{http://schemas.android.com/apk/res/android}"


def resources(root):
    res = defaultdict(set)
    rdir = os.path.join(root, "app", "src", "main", "res")
    if not os.path.isdir(rdir):
        return res
    for folder in os.listdir(rdir):
        full = os.path.join(rdir, folder)
        if not os.path.isdir(full): continue
        kind = folder.split("-")[0]
        for name in os.listdir(full):
            path = os.path.join(full, name)
            if kind == "values" and name.endswith(".xml"):
                try:
                    for el in ET.parse(path).getroot():
                        nm = el.get("name")
                        if nm:
                            res[{"string": "string", "color": "color", "style": "style", "dimen": "dimen"}.get(el.tag, el.tag)].add(nm)
                except ET.ParseError:
                    pass
            else:
                res[kind].add(os.path.splitext(name)[0])
    return res


def chk_manifest(root, files):
    def fn():
        errs, warns = [], []
        mpath = "app/src/main/AndroidManifest.xml"
        tree = ET.parse(os.path.join(root, mpath)).getroot()
        names = top_names(files)
        res = resources(root)
        declared_perms = [e.get(ANDROID + "name") for e in tree.iter("uses-permission")]
        for p in set(declared_perms):
            if declared_perms.count(p) > 1: warns.append("إذن مكرر: " + p)
        for tag in ("application", "activity", "service", "receiver", "provider"):
            for el in tree.iter(tag):
                cls = el.get(ANDROID + "name")
                if not cls: continue
                fq = PKG + cls if cls.startswith(".") else cls
                if fq.startswith(PKG + "."):
                    pkg, _, simple = fq.rpartition(".")
                    if simple not in names.get(pkg, {}):
                        errs.append("<{}> يشير إلى كلاس غير موجود: {}".format(tag, fq))
        raw = read(root, mpath)
        for kind, name in set(re.findall(r"@(xml|string|style|color|drawable|mipmap)/([\w.]+)", raw)):
            if name not in res.get(kind, set()):
                errs.append("المانيفست يستخدم المورد @{}/{} وهو غير موجود".format(kind, name))
        fg_perm = lambda t: "android.permission.FOREGROUND_SERVICE_" + re.sub(r"(?<!^)([A-Z])", r"_\1", t).upper()
        for svc in tree.iter("service"):
            types = svc.get(ANDROID + "foregroundServiceType")
            for t in (types or "").split("|"):
                t = t.strip()
                if t and t != "shortService" and fg_perm(t) not in declared_perms:
                    errs.append("الخدمة {} نوعها {} لكن الإذن {} غير مُعلن (يتعطل على أندرويد 14+)".format(
                        svc.get(ANDROID + "name"), t, fg_perm(t).split(".")[-1]))
        # Manifest.permission.X المستخدمة في الكود يجب أن تكون مُعلنة
        used = defaultdict(list)
        for kf in files.values():
            for m in re.finditer(r"\bManifest\.permission\.(\w+)", kf.m.text):
                used[m.group(1)].append(kf.rel.split("/")[-1])
        for perm, where in sorted(used.items()):
            if "android.permission." + perm not in declared_perms:
                errs.append("الكود يطلب Manifest.permission.{} ({}) وهو غير مُعلن في المانيفست".format(
                    perm, where[0]))
        return errs, warns
    return fn


def chk_kotlin_syntax(files):
    def fn():
        errs = []
        for rel, kf in sorted(files.items()):
            short = rel.replace(PKG_DIR + "/", "")
            for line, msg in kf.m.errors:
                errs.append("{}:{} {}".format(short, line, msg))
            for e in kf.m.balance_errors():
                errs.append("{}: {}".format(short, e))
            for m in re.finditer(r"\\", kf.m.text):
                errs.append("{}:{} رمز '\\' خارج أي نص (غالباً هروب خاطئ من بايثون)".format(
                    short, kf.m.line(m.start())))
                break
            expected = PKG + "." + os.path.dirname(rel[len(PKG_DIR) + 1:]).replace("/", ".")
            expected = expected.rstrip(".")
            if kf.package != expected:
                errs.append("{}: package هو '{}' والمسار يتوقع '{}'".format(short, kf.package, expected))
        return errs, []
    return fn


def chk_kotlin_declarations(files):
    def fn():
        errs = []
        owners = defaultdict(list)
        for rel, kf in files.items():
            for d in kf.decls:
                if d["top"] and "private" not in d["mods"] and d["kind"] in ("class", "interface", "object", "typealias"):
                    owners[(kf.package, d["name"])].append(rel)
                if d["top"] and "private" not in d["mods"] and d["kind"] in ("val", "var") and not d["recv"]:
                    owners[(kf.package, "val:" + d["name"])].append(rel)
        for (pkg, name), where in sorted(owners.items()):
            if len(where) > 1:
                errs.append("تعريف مكرر {}.{} في: {}".format(pkg, name.replace("val:", ""),
                                                          ", ".join(w.split("/")[-1] for w in where)))
        for rel, kf in sorted(files.items()):
            short = rel.split("/")[-1]
            seen = {}
            for d in kf.decls:
                if d["kind"] == "fun":
                    key = (d["scope"], "fun", d["recv"], d["name"], kf.params_of(d))
                elif d["kind"] in ("val", "var") and d["scope"]:
                    key = (d["scope"], "prop", d["recv"], d["name"], None)
                elif d["kind"] in ("class", "object", "interface"):
                    key = (d["scope"], "type", "", d["name"], None)
                else:
                    continue
                if key in seen:
                    errs.append("{}:{} تعريف مكرر في نفس النطاق: {} {}".format(
                        short, kf.m.line(d["pos"]), d["kind"], d["name"]))
                seen[key] = True
        return errs, []
    return fn


def chk_kotlin_imports(files):
    def fn():
        errs, warns = [], []
        names = top_names(files)
        dictionary = defaultdict(set)  # simple name -> {fqn} من استيرادات المشروع نفسه
        for kf in files.values():
            for fqn, star, alias, _l in kf.imports:
                if not star and not alias:
                    dictionary[fqn.rsplit(".", 1)[-1]].add(fqn)
        project_names = defaultdict(set)  # name -> {package}
        for pkg, ns in names.items():
            for n in ns:
                project_names[n].add(pkg)

        for rel, kf in sorted(files.items()):
            short = rel.replace(PKG_DIR + "/", "")
            seen_simple = {}
            seen_fq = set()
            for fqn, star, alias, line in kf.imports:
                if fqn in seen_fq:
                    warns.append("{}:{} استيراد مكرر {}".format(short, line, fqn))
                seen_fq.add(fqn)
                # 1) استيرادات المشروع يجب أن تشير إلى شيء موجود
                if fqn.startswith(PKG + ".") and not star and fqn not in (PKG + ".R", PKG + ".BuildConfig"):
                    # R و BuildConfig يولّدهما Android Gradle Plugin وقت البناء، فليسا في المصدر
                    parts = fqn.split(".")
                    ok = any(parts[k] in names.get(".".join(parts[:k]), {}) for k in range(len(parts) - 1, 0, -1))
                    if not ok:
                        errs.append("{}:{} استيراد غير موجود في المشروع: {}".format(short, line, fqn))
                # 2) نفس الاسم من مكانين مختلفين بدون alias = خطأ ترجمة
                if not star:
                    simple = alias or fqn.rsplit(".", 1)[-1]
                    if simple in seen_simple and seen_simple[simple] != fqn:
                        errs.append("{}:{} الاسم {} مستورد من مكانين: {} و {}".format(
                            short, line, simple, seen_simple[simple], fqn))
                    seen_simple[simple] = fqn
            imported = set(seen_simple)
            wild_pkgs = {fqn[:-2] for fqn, star, _a, _l in kf.imports if star}
            declared_here = {d["name"] for d in kf.decls}
            declared_here |= set(re.findall(r"\b(?:class|object|interface|typealias)\s+(\w+)", kf.m.text))

            # 3) أيقونات Icons.* تحتاج استيراداً صريحاً لكل أيقونة
            for m in re.finditer(r"\bIcons\.((?:AutoMirrored\.)?(?:Filled|Outlined|Rounded|Sharp|TwoTone))\.(\w+)", kf.body):
                sub, icon = m.group(1), m.group(2)
                pkgpath = "androidx.compose.material.icons." + sub.replace("AutoMirrored.", "automirrored.").lower()
                if icon not in imported and pkgpath not in wild_pkgs:
                    errs.append("{}:{} الأيقونة Icons.{}.{} بدون import {}.{}".format(
                        short, kf.m.line(m.start()), sub, icon, pkgpath, icon))

            # 4) استيراد ناقص: معرّف يبدأ بحرف كبير مستخدم بدون استيراد
            reported = set()
            for m in re.finditer(r"(?<![\w.])([A-Z][A-Za-z0-9_]*)\b", kf.body):
                ident = m.group(1)
                if len(ident) == 1 or ident in reported or ident in imported or ident in declared_here:
                    continue
                if ident in INHERITED_NAMES or ident.isupper():
                    continue
                if ident in names.get(kf.package, {}):
                    continue
                target = None
                pk = project_names.get(ident)
                if pk and len(pk) == 1:
                    target = next(iter(pk)) + "." + ident
                elif len(dictionary.get(ident, ())) == 1:
                    target = next(iter(dictionary[ident]))
                if not target:
                    continue
                if target.rsplit(".", 1)[0] in wild_pkgs:
                    continue
                reported.add(ident)
                errs.append("{}:{} يستخدم {} بدون استيراد (المتوقع: import {})".format(
                    short, kf.m.line(m.start()), ident, target))
        return errs, warns
    return fn


def chk_resources_buildconfig(root, files):
    def fn():
        errs = []
        gradle = read(root, "app/build.gradle.kts")
        defined = set(re.findall(r'buildConfigField\(\s*"[^"]+"\s*,\s*"(\w+)"', gradle))
        defined |= {"DEBUG", "APPLICATION_ID", "BUILD_TYPE", "FLAVOR", "VERSION_CODE", "VERSION_NAME", "LIBRARY_PACKAGE_NAME"}
        res = resources(root)
        for rel, kf in sorted(files.items()):
            short = rel.split("/")[-1]
            for m in re.finditer(r"\bBuildConfig\.(\w+)", kf.m.text):
                if m.group(1) not in defined:
                    errs.append("{}:{} BuildConfig.{} غير معرّف في app/build.gradle.kts".format(
                        short, kf.m.line(m.start()), m.group(1)))
            for m in re.finditer(r"(?<![\w.])R\.(\w+)\.(\w+)", kf.m.text):
                kind, name = m.group(1), m.group(2)
                if kind == "id": continue
                if name not in res.get(kind, set()):
                    errs.append("{}:{} المورد R.{}.{} غير موجود".format(short, kf.m.line(m.start()), kind, name))
        if "buildFeatures" in gradle and "BuildConfig." in "".join(f.m.text for f in files.values()) \
                and not re.search(r"buildConfig\s*=\s*true", gradle):
            errs.append("الكود يستخدم BuildConfig لكن buildFeatures { buildConfig = true } غير مفعّل")
        return errs, []
    return fn


def chk_gradle(root, files):
    def fn():
        errs, warns = [], []
        app = read(root, "app/build.gradle.kts")
        top = read(root, "build.gradle.kts")
        for rel in ("app/build.gradle.kts", "build.gradle.kts", "settings.gradle.kts"):
            masked = KtMasked(read(root, rel))
            for line, msg in masked.errors: errs.append("{}:{} {}".format(rel, line, msg))
            for e in masked.balance_errors(): errs.append("{}: {}".format(rel, e))
        ns = re.search(r'namespace\s*=\s*"([^"]+)"', app)
        aid = re.search(r'applicationId\s*=\s*"([^"]+)"', app)
        if not ns or ns.group(1) != PKG: errs.append("namespace يجب أن يكون " + PKG)
        if not aid or aid.group(1) != PKG: errs.append("applicationId يجب أن يكون " + PKG)
        c, t, mn = (re.search(p + r"\s*=\s*(\d+)", app) for p in ("compileSdk", "targetSdk", "minSdk"))
        if not (c and t and mn):
            errs.append("compileSdk / targetSdk / minSdk غير مكتملة")
        elif int(c.group(1)) < int(t.group(1)):
            errs.append("compileSdk ({}) أقل من targetSdk ({})".format(c.group(1), t.group(1)))
        kot = re.search(r'org\.jetbrains\.kotlin\.android"\)\s*version\s*"([^"]+)"', top)
        comp = re.search(r'org\.jetbrains\.kotlin\.plugin\.compose"\)\s*version\s*"([^"]+)"', top)
        if kot and comp and kot.group(1) != comp.group(1):
            errs.append("إصدار Kotlin ({}) ≠ إصدار Compose plugin ({})".format(kot.group(1), comp.group(1)))
        if "jvmTarget" in app and "VERSION_17" in app and 'jvmTarget = "17"' not in app:
            errs.append("jvmTarget لا يطابق JavaVersion.VERSION_17")
        deps = re.findall(r'(?:implementation|api|debugImplementation|ksp|kapt)\(\s*"([^"]+)"', app)
        for d in set(deps):
            if deps.count(d) > 1: warns.append("اعتمادية مكررة: " + d)
        for d in deps:
            if d.count(":") < 1: errs.append("إحداثيات اعتمادية غير صالحة: " + d)
        # كل مكتبة مستورَدة في الكود يجب أن يقابلها سطر dependencies
        coords = " ".join(deps)
        flagged, unknown = set(), set()
        for kf in files.values():
            for fqn, _s, _a, _l in kf.imports:
                if fqn.startswith(NO_LIB_PREFIXES): continue
                hit = next(((p, c2) for p, c2 in LIB_MAP if fqn.startswith(p)), None)
                if hit:
                    if hit[1] not in coords and hit[1] not in flagged:
                        flagged.add(hit[1])
                        errs.append("الكود يستورد {}… لكن اعتمادية {} غير موجودة في app/build.gradle.kts".format(hit[0], hit[1]))
                else:
                    unknown.add(".".join(fqn.split(".")[:3]))
        for u in sorted(unknown):
            warns.append("لم أستطع التحقق من اعتمادية الاستيراد: " + u)
        return errs, warns
    return fn


def chk_workflow_and_ignore(root):
    def fn():
        errs, warns = [], []
        wf = read(root, ".github/workflows/build.yml")
        if "\t" in wf: errs.append("build.yml يحتوي على Tab (YAML لا يقبلها)")
        try:
            import yaml  # اختياري
            data = yaml.safe_load(wf)
            jobs = data.get("jobs", {}) if isinstance(data, dict) else {}
            if not jobs: errs.append("build.yml: لا يوجد jobs")
            for jname, job in jobs.items():
                if "runs-on" not in job: errs.append("job {} بدون runs-on".format(jname))
                steps = job.get("steps") or []
                if not steps: errs.append("job {} بدون steps".format(jname))
                for i, st in enumerate(steps):
                    if not ("uses" in st or "run" in st):
                        errs.append("job {} الخطوة {} بلا uses/run".format(jname, i + 1))
        except ImportError:
            warns.append("PyYAML غير مثبّت: فحص بنية YAML مبسّط فقط (pip install pyyaml)")
            for need in ("jobs:", "runs-on:", "steps:"):
                if need not in wf: errs.append("build.yml ينقصه " + need)
        except Exception as e:
            errs.append("build.yml YAML غير صالح: {}".format(str(e).splitlines()[0]))
        i_py, i_gr = wf.find("python setup.py"), wf.find("./gradlew assembleDebug")
        if i_py < 0 or i_gr < 0 or i_py > i_gr:
            errs.append("يجب أن يعمل 'python setup.py' قبل './gradlew assembleDebug' في build.yml")
        ig = read(root, ".gitignore")
        for need in ("keys.properties", "build/", ".gradle/"):
            if need not in ig: errs.append(".gitignore ينقصه: " + need)
        return errs, warns
    return fn


def chk_no_secrets_output(root):
    def fn():
        errs = []
        for base, _d, names in os.walk(root):
            for name in names:
                rel = os.path.relpath(os.path.join(base, name), root).replace(os.sep, "/")
                try:
                    txt = open(os.path.join(base, name), "r", encoding="utf-8").read()
                except UnicodeDecodeError:
                    continue
                errs += chk_secrets_text(rel, txt)
        if os.path.exists(os.path.join(root, "keys.properties")):
            errs.append("keys.properties ظهر في المخرجات رغم عدم تمرير أي مفتاح")
        return errs, []
    return fn


def try_build(root):
    gradle = shutil.which("gradle")
    sdk = os.environ.get("ANDROID_HOME") or os.environ.get("ANDROID_SDK_ROOT")
    if not gradle or not sdk:
        return None
    p = subprocess.run([gradle, "assembleDebug", "--stacktrace", "--console=plain"], cwd=root,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True,
                       encoding="utf-8", errors="replace", timeout=3600)
    return p.returncode, p.stdout


# ------------------------------------------------------------------ main
def _selftest(argv):
    ap = argparse.ArgumentParser(prog="python setup.py --test", description="اختبار setup.py قبل رفعه")
    ap.add_argument("setup", nargs="?", default=os.path.abspath(__file__))
    ap.add_argument("--keep", action="store_true", help="إبقاء المشروع المولَّد")
    ap.add_argument("--build", action="store_true", help="تشغيل gradle assembleDebug (يتطلب gradle + Android SDK)")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass
    if not os.path.isfile(args.setup):
        print("لم أجد الملف: " + args.setup); return 2

    rep = Report(args.verbose)
    setup_src = open(args.setup, "r", encoding="utf-8").read()
    print("== اختبار {} ==\n".format(args.setup))

    rep.run("صياغة بايثون في setup.py", chk_python_syntax(args.setup))
    rep.run("لا مفاتيح API مكتوبة داخل setup.py",
            lambda: (chk_secrets_text("setup.py", setup_src), []))
    if rep.counts[FAIL]:
        print("\nتوقفت: أصلح الأخطاء أعلاه أولاً."); return 1

    tmp = tempfile.mkdtemp(prefix="setup_test_")
    try:
        src_dir, out = os.path.join(tmp, "src"), os.path.join(tmp, "out")
        os.makedirs(src_dir)
        copy = os.path.join(src_dir, "setup.py")
        shutil.copyfile(args.setup, copy)  # نسخة معزولة: لا يُقرأ أي AiChatService.kt بجوار الأصل

        proc = run_setup(copy, out, src_dir)
        if proc.returncode != 0:
            tail = [l for l in proc.stdout.strip().splitlines() if l.strip()][-6:]
            rep.add(FAIL, "تشغيل setup.py (رمز الخروج {})".format(proc.returncode), tail)
            print("\nتوقفت: المشروع لم يُولَّد.")
            return 1
        made = re.search(r"Done\.\s+(\d+)\s+files created", proc.stdout)
        rep.add(OK, "تشغيل setup.py وتوليد المشروع ({} ملف)".format(made.group(1) if made else "؟"))

        first = snapshot(out)

        def idem():
            p2 = run_setup(copy, out, src_dir)
            if p2.returncode != 0:
                return ["فشل التشغيل الثاني فوق مخرجات موجودة"], []
            second = snapshot(out)
            diff = sorted(k for k in set(first) | set(second) if first.get(k) != second.get(k))
            return ["يختلف بعد إعادة التشغيل: " + k for k in diff], []
        rep.run("إعادة التشغيل تعطي نفس الملفات", idem)

        rep.run("الملفات الأساسية + UTF-8 + بلا ملفات فارغة", chk_expected_files(out))
        rep.run("كل ملفات XML سليمة", chk_xml(out))
        files = load_kotlin(out)
        rep.run("Kotlin: توازن الأقواس والنصوص + package + بلا أخطاء هروب", chk_kotlin_syntax(files))
        rep.run("Kotlin: لا تعريفات مكررة", chk_kotlin_declarations(files))
        rep.run("Kotlin: الاستيرادات (موجودة، بلا تعارض، بلا نقص)", chk_kotlin_imports(files))
        rep.run("AndroidManifest: الكلاسات والموارد والأذونات", chk_manifest(out, files))
        rep.run("BuildConfig و R.* معرّفة", chk_resources_buildconfig(out, files))
        rep.run("Gradle: الإعدادات والاعتماديات", chk_gradle(out, files))
        rep.run("GitHub Actions و .gitignore", chk_workflow_and_ignore(out))
        rep.run("لا أسرار في المشروع المولَّد", chk_no_secrets_output(out))

        if args.build:
            result = try_build(out)
            if result is None:
                rep.add(WARN, "gradle assembleDebug تم تخطيه", ["gradle أو ANDROID_HOME غير متوفرين على هذا الجهاز"])
            elif result[0] == 0:
                rep.add(OK, "gradle assembleDebug نجح")
            else:
                errs = [l for l in result[1].splitlines() if l.startswith("e: ") or "error:" in l.lower()]
                rep.add(FAIL, "gradle assembleDebug فشل", errs[:30] or result[1].splitlines()[-15:])

        if args.keep:
            keep = os.path.abspath("setup_test_output")
            shutil.rmtree(keep, ignore_errors=True)
            shutil.copytree(out, keep)
            print("\nالمشروع المولَّد محفوظ في: " + keep)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    c = rep.counts
    print("\n== النتيجة: {} ناجح، {} تحذير، {} فاشل ==".format(c[OK], c[WARN], c[FAIL]))
    if c[FAIL]:
        print("لا ترفع الملف قبل إصلاح الأخطاء أعلاه.")
        return 1
    print("الفحص الساكن سليم. (الترجمة الفعلية لـ Kotlin تتم في gradle / GitHub Actions.)")
    return 0


if len(sys.argv) > 1 and sys.argv[1] == "--test":
    sys.exit(_selftest(sys.argv[2:]))
# ==============================================================================
# نهاية بيئة الاختبار: ما بعدها هو مولّد المشروع الأصلي دون أي تغيير
# ==============================================================================


SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else "."
os.makedirs(ROOT, exist_ok=True)
os.chdir(ROOT)

print(">> Creating VoiceAssistant project in:", os.getcwd())

# ------------------------------------------------------------------------------
# المجلدات
# ------------------------------------------------------------------------------
DIRS = [
    ".github/workflows",
    "gradle/wrapper",
    "app",
    "app/src/main",
    "app/src/main/java/com/example/voiceassistant",
    "app/src/main/java/com/example/voiceassistant/commands",
    "app/src/main/java/com/example/voiceassistant/commands/commands",
    "app/src/main/java/com/example/voiceassistant/data",
    "app/src/main/java/com/example/voiceassistant/data/models",
    "app/src/main/java/com/example/voiceassistant/service",
    "app/src/main/java/com/example/voiceassistant/speech",
    "app/src/main/java/com/example/voiceassistant/ui",
    "app/src/main/java/com/example/voiceassistant/ui/components",
    "app/src/main/java/com/example/voiceassistant/ui/theme",
    "app/src/main/java/com/example/voiceassistant/viewmodel",
    "app/src/main/res/values",
    "app/src/main/res/xml",
]
for d in DIRS:
    os.makedirs(d, exist_ok=True)

FILES_CREATED = [0]


def write_file(path, content):
    """Writes one file as UTF-8 (needed for the Arabic strings)."""
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    FILES_CREATED[0] += 1


# ------------------------------------------------------------------------------
# الملفات
# ------------------------------------------------------------------------------
# 1. settings.gradle.kts
write_file("settings.gradle.kts", r'''pluginManagement {
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

rootProject.name = "VoiceAssistant"
include(":app")
''')

# 2. build.gradle.kts
write_file("build.gradle.kts", r'''// Top-level build file
plugins {
    id("com.android.application") version "8.7.3" apply false
    id("org.jetbrains.kotlin.android") version "2.0.21" apply false
    id("org.jetbrains.kotlin.plugin.compose") version "2.0.21" apply false
}
''')

# 3. gradle.properties
write_file("gradle.properties", r'''org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
org.gradle.parallel=true
org.gradle.caching=true
android.useAndroidX=true
android.nonTransitiveRClass=true
kotlin.code.style=official
''')

# 4. proguard-rules.pro
write_file("proguard-rules.pro", r'''# Add project specific ProGuard rules here.
# The accessibility service is referenced from the manifest.
-keep class com.example.voiceassistant.service.VoiceAccessibilityService { *; }
-keep class com.example.voiceassistant.service.VaInteractionService { *; }
-keep class com.example.voiceassistant.service.VaSessionService { *; }
-keep class com.example.voiceassistant.service.VaRecognitionService { *; }
-keep class com.example.voiceassistant.VoiceAssistantApp { *; }
-keep class com.example.voiceassistant.service.ReminderReceiver { *; }
-keep class com.example.voiceassistant.service.SpeakingService { *; }
-keep class com.example.voiceassistant.service.ScreenCaptureService { *; }
-keep class com.example.voiceassistant.service.ProactiveWorker { *; }
-keep class com.example.voiceassistant.antitheft.** { *; }

# Keep line numbers for readable crash reports
-keepattributes SourceFile,LineNumberTable
-renamesourcefileattribute SourceFile
''')

# 5. app/build.gradle.kts
write_file("app/build.gradle.kts", r'''import java.util.Properties

plugins {
    id("com.android.application")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
}

// API keys reach the app through BuildConfig, never through the source code.
// Order: environment variable (GitHub Secrets in CI), then keys.properties (git-ignored, local builds).
val keyProps = Properties().apply {
    val file = rootProject.file("keys.properties")
    if (file.exists()) file.inputStream().use { load(it) }
}

fun buildKey(name: String): String =
    (System.getenv(name)?.takeIf { it.isNotBlank() } ?: keyProps.getProperty(name) ?: "")
        .trim()
        .replace("\\", "\\\\")
        .replace("\"", "\\\"")

android {
    namespace = "com.example.voiceassistant"
    compileSdk = 35

    defaultConfig {
        applicationId = "com.example.voiceassistant"
        minSdk = 26
        targetSdk = 35
        versionCode = 4
        versionName = "2.2"

        // Built-in keys (GitHub Secrets). A key typed in the app (Settings) always wins over these.
        buildConfigField("String", "GEMINI_API_KEY", "\"${buildKey("GEMINI_API_KEY")}\"")
        buildConfigField("String", "OPENAI_API_KEY", "\"${buildKey("OPENAI_API_KEY")}\"")
        buildConfigField("String", "CLAUDE_API_KEY", "\"${buildKey("CLAUDE_API_KEY")}\"")
    }

    buildTypes {
        release {
            isMinifyEnabled = false
            proguardFiles(
                getDefaultProguardFile("proguard-android-optimize.txt"),
                "../proguard-rules.pro"
            )
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
        buildConfig = true
    }

    packaging {
        resources {
            excludes += "/META-INF/{AL2.0,LGPL2.1}"
        }
    }
}

dependencies {
    implementation("androidx.core:core-ktx:1.15.0")
    implementation("androidx.lifecycle:lifecycle-runtime-ktx:2.8.7")
    implementation("androidx.lifecycle:lifecycle-runtime-compose:2.8.7")
    implementation("androidx.lifecycle:lifecycle-viewmodel-compose:2.8.7")
    implementation("androidx.activity:activity-compose:1.9.3")
    implementation("org.jetbrains.kotlinx:kotlinx-coroutines-android:1.7.3")
    implementation("androidx.security:security-crypto:1.1.0-alpha06")

    // HTTP client for the conversational AI service
    implementation("com.squareup.okhttp3:okhttp:4.12.0")

    // Background scheduling for the proactive "how are you?" check-ins
    implementation("androidx.work:work-runtime-ktx:2.9.1")

    val composeBom = platform("androidx.compose:compose-bom:2024.10.01")
    implementation(composeBom)
    implementation("androidx.compose.ui:ui")
    implementation("androidx.compose.ui:ui-graphics")
    implementation("androidx.compose.ui:ui-tooling-preview")
    implementation("androidx.compose.material3:material3")
    implementation("androidx.compose.material:material-icons-extended")

    debugImplementation("androidx.compose.ui:ui-tooling")
}
''')

# 6. app/src/main/AndroidManifest.xml
write_file("app/src/main/AndroidManifest.xml", r'''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.RECORD_AUDIO" />
    <uses-permission android:name="android.permission.READ_CONTACTS" />
    <uses-permission android:name="android.permission.CALL_PHONE" />
    <uses-permission android:name="com.android.alarm.permission.SET_ALARM" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.SCHEDULE_EXACT_ALARM" />
    <uses-permission android:name="android.permission.RECEIVE_BOOT_COMPLETED" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PLAYBACK" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MICROPHONE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_MEDIA_PROJECTION" />
    <uses-permission android:name="android.permission.READ_CLIPBOARD" />
    <uses-permission android:name="android.permission.RECEIVE_SMS" />
    <uses-permission android:name="android.permission.SEND_SMS" />
    <uses-permission android:name="android.permission.READ_PHONE_STATE" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_BACKGROUND_LOCATION" />
    <uses-permission android:name="android.permission.WAKE_LOCK" />

    <uses-feature
        android:name="android.hardware.microphone"
        android:required="false" />
    <uses-feature
        android:name="android.hardware.telephony"
        android:required="false" />

    <!-- Package visibility (Android 11+) -->
    <queries>
        <intent>
            <action android:name="android.speech.RecognitionService" />
        </intent>
        <intent>
            <action android:name="android.intent.action.TTS_SERVICE" />
        </intent>
        <intent>
            <action android:name="android.intent.action.MAIN" />
            <category android:name="android.intent.category.LAUNCHER" />
        </intent>
    </queries>

    <application
        android:name=".VoiceAssistantApp"
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:label="@string/app_name"
        android:supportsRtl="true"
        android:theme="@style/Theme.VoiceAssistant">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>

            <!-- Default digital assistant entry point -->
            <intent-filter>
                <action android:name="android.intent.action.ASSIST" />
                <category android:name="android.intent.category.DEFAULT" />
            </intent-filter>
        </activity>

        <service
            android:name=".service.VoiceAccessibilityService"
            android:exported="true"
            android:label="@string/app_name"
            android:permission="android.permission.BIND_ACCESSIBILITY_SERVICE">
            <intent-filter>
                <action android:name="android.accessibilityservice.AccessibilityService" />
            </intent-filter>
            <meta-data
                android:name="android.accessibilityservice"
                android:resource="@xml/accessibility_service_config" />
        </service>

        <!-- Voice interaction (makes the app selectable as the default assistant) -->
        <service
            android:name=".service.VaInteractionService"
            android:exported="true"
            android:label="@string/app_name"
            android:permission="android.permission.BIND_VOICE_INTERACTION">
            <meta-data
                android:name="android.voice_interaction"
                android:resource="@xml/assist_interaction" />
            <intent-filter>
                <action android:name="android.service.voice.VoiceInteractionService" />
            </intent-filter>
        </service>

        <service
            android:name=".service.VaSessionService"
            android:exported="true"
            android:permission="android.permission.BIND_VOICE_INTERACTION" />

        <service
            android:name=".service.VaRecognitionService"
            android:exported="true"
            android:label="@string/app_name">
            <intent-filter>
                <action android:name="android.speech.RecognitionService" />
                <category android:name="android.intent.category.DEFAULT" />
            </intent-filter>
        </service>

        <!-- Reminders: fired by AlarmManager; also re-arms everything after a reboot -->
        <receiver
            android:name=".service.ReminderReceiver"
            android:exported="false">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
                <action android:name="android.intent.action.MY_PACKAGE_REPLACED" />
                <action android:name="android.app.action.SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED" />
            </intent-filter>
        </receiver>

        <!-- Speaks reminders / check-ins (TTS) while the app is closed -->
        <service
            android:name=".service.SpeakingService"
            android:exported="false"
            android:foregroundServiceType="mediaPlayback" />

        <!-- Security monitor: watches the clipboard for suspicious links while protection is on -->
        <service
            android:name=".service.SecurityMonitorService"
            android:exported="false"
            android:foregroundServiceType="dataSync" />

        <!-- Wake word: keeps listening for "يا مساعد" / "hey assistant" while the switch is on -->
        <service
            android:name=".service.WakeWordService"
            android:exported="false"
            android:foregroundServiceType="microphone" />

        <!-- Anti-theft: replies with the location when the PIN arrives from the trusted number -->
        <receiver
            android:name=".antitheft.LocationSmsReceiver"
            android:exported="true"
            android:permission="android.permission.BROADCAST_SMS">
            <intent-filter android:priority="999">
                <action android:name="android.provider.Telephony.SMS_RECEIVED" />
            </intent-filter>
        </receiver>

        <!-- Anti-theft: after a reboot, warns the trusted number if the SIM operator changed -->
        <receiver
            android:name=".antitheft.SimChangeReceiver"
            android:exported="false">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>

        <!-- Anti-theft: Device Admin, warns when someone tries to turn it off -->
        <receiver
            android:name=".antitheft.AntiTheftDeviceAdminReceiver"
            android:exported="true"
            android:label="@string/app_name"
            android:permission="android.permission.BIND_DEVICE_ADMIN">
            <meta-data
                android:name="android.app.device_admin"
                android:resource="@xml/device_admin" />
        </receiver>

        <!-- Anti-theft settings screen (trusted number, PIN, permissions, Device Admin) -->
        <activity
            android:name=".antitheft.SecuritySettingsActivity"
            android:exported="false"
            android:label="@string/app_name" />

        <!-- Screen capture: takes ONE screenshot (MediaProjection) and stops itself -->
        <service
            android:name=".service.ScreenCaptureService"
            android:exported="false"
            android:foregroundServiceType="mediaProjection" />

        <!-- FileProvider: gives the camera app a content:// Uri inside our cache folder (Android 7+) -->
        <provider
            android:name="androidx.core.content.FileProvider"
            android:authorities="${applicationId}.fileprovider"
            android:exported="false"
            android:grantUriPermissions="true">
            <meta-data
                android:name="android.support.FILE_PROVIDER_PATHS"
                android:resource="@xml/file_paths" />
        </provider>

    </application>

</manifest>
''')

# 7. app/src/main/res/values/strings.xml
write_file("app/src/main/res/values/strings.xml", r'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Zevorix AI</string>
    <string name="accessibility_service_description">Lets Zevorix AI perform on-screen actions such as Back, Home, Recents, Notifications, scrolling, taking a screenshot, tapping items by name and flipping switches (Wi-Fi, Bluetooth...) in Settings.</string>
    <string name="device_admin_explanation">Lets Zevorix AI warn your trusted phone number by SMS when someone tries to turn off device protection.</string>
</resources>
''')

# 8. app/src/main/res/values/colors.xml
write_file("app/src/main/res/values/colors.xml", r'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="background">#FFFBFAFF</color>
    <color name="primary">#FF4F5BD5</color>
    <color name="primary_dark">#FF3640A8</color>
    <color name="accent">#FF00B8A9</color>
    <color name="black">#FF000000</color>
    <color name="white">#FFFFFFFF</color>
</resources>
''')

# 9. app/src/main/res/values/themes.xml
write_file("app/src/main/res/values/themes.xml", r'''<?xml version="1.0" encoding="utf-8"?>
<resources>
    <style name="Theme.VoiceAssistant" parent="android:Theme.Material.Light.NoActionBar">
        <item name="android:statusBarColor">@android:color/transparent</item>
        <item name="android:navigationBarColor">@android:color/transparent</item>
        <item name="android:windowBackground">@color/background</item>
    </style>
</resources>
''')

# 10. app/src/main/res/xml/accessibility_service_config.xml
write_file("app/src/main/res/xml/accessibility_service_config.xml", r'''<?xml version="1.0" encoding="utf-8"?>
<accessibility-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:accessibilityEventTypes="typeWindowStateChanged"
    android:accessibilityFeedbackType="feedbackGeneric"
    android:accessibilityFlags="flagDefault|flagIncludeNotImportantViews"
    android:canRetrieveWindowContent="true"
    android:description="@string/accessibility_service_description"
    android:notificationTimeout="100" />
''')

# 11. app/src/main/res/xml/backup_rules.xml
write_file("app/src/main/res/xml/backup_rules.xml", r'''<?xml version="1.0" encoding="utf-8"?>
<full-backup-content>
    <exclude domain="sharedpref" path="." />
    <exclude domain="database" path="." />
</full-backup-content>
''')

# 12. app/src/main/res/xml/data_extraction_rules.xml
write_file("app/src/main/res/xml/data_extraction_rules.xml", r'''<?xml version="1.0" encoding="utf-8"?>
<data-extraction-rules>
    <cloud-backup>
        <exclude domain="sharedpref" path="." />
        <exclude domain="database" path="." />
    </cloud-backup>
    <device-transfer>
        <exclude domain="sharedpref" path="." />
        <exclude domain="database" path="." />
    </device-transfer>
</data-extraction-rules>
''')

# 12b. app/src/main/res/xml/assist_interaction.xml  (NEW)
write_file("app/src/main/res/xml/assist_interaction.xml", r'''<?xml version="1.0" encoding="utf-8"?>
<voice-interaction-service xmlns:android="http://schemas.android.com/apk/res/android"
    android:recognitionService="com.example.voiceassistant.service.VaRecognitionService"
    android:sessionService="com.example.voiceassistant.service.VaSessionService"
    android:supportsAssist="true" />
''')

# 13. .github/workflows/build.yml
write_file(".github/workflows/build.yml", r'''name: Build VoiceAssistant APK

on:
  push:
    branches: [ main, master ]
  pull_request:
  workflow_dispatch:

jobs:
  build:
    runs-on: ubuntu-latest

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up JDK 17
        uses: actions/setup-java@v4
        with:
          distribution: temurin
          java-version: '17'

      - name: Set up Android SDK
        uses: android-actions/setup-android@v3

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Generate project files from setup.py
        run: python setup.py
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}

      # gradle-wrapper.properties (written by setup.py) pins Gradle 8.10.2; gradlew and the wrapper jar
      # are generated here with the runner's Gradle in an empty folder (AGP is not involved yet).
      - name: Generate Gradle wrapper scripts
        run: |
          mkdir -p "$RUNNER_TEMP/wrapper-gen"
          cd "$RUNNER_TEMP/wrapper-gen"
          touch settings.gradle
          gradle wrapper --gradle-version 8.10.2 --distribution-type bin --no-daemon
          cd "$GITHUB_WORKSPACE"
          cp "$RUNNER_TEMP/wrapper-gen/gradlew" "$RUNNER_TEMP/wrapper-gen/gradlew.bat" .
          cp "$RUNNER_TEMP/wrapper-gen/gradle/wrapper/gradle-wrapper.jar" gradle/wrapper/
          chmod +x gradlew

      - name: Build debug APK
        run: ./gradlew assembleDebug --stacktrace
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY }}
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          CLAUDE_API_KEY: ${{ secrets.CLAUDE_API_KEY }}

      - name: Upload APK
        uses: actions/upload-artifact@v4
        with:
          name: VoiceAssistant-debug-apk
          path: app/build/outputs/apk/debug/*.apk
''')

# 13b. gradle/wrapper/gradle-wrapper.properties: pins Gradle 8.10.2 (AGP 8.7.3 needs Gradle 8.9+)
write_file("gradle/wrapper/gradle-wrapper.properties", r'''distributionBase=GRADLE_USER_HOME
distributionPath=wrapper/dists
distributionUrl=https\://services.gradle.org/distributions/gradle-8.10.2-bin.zip
zipStoreBase=GRADLE_USER_HOME
zipStorePath=wrapper/dists
''')

# 14. app/src/main/java/com/example/voiceassistant/MainActivity.kt
write_file("app/src/main/java/com/example/voiceassistant/MainActivity.kt", r'''package com.example.voiceassistant

import android.Manifest
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.view.WindowManager
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.core.view.WindowCompat
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.setValue
import com.example.voiceassistant.ui.MainScreen
import com.example.voiceassistant.ui.theme.VoiceAssistantTheme

class MainActivity : ComponentActivity() {

    companion object {
        /** Set by the voice-interaction session when the user invokes the default assistant. */
        const val EXTRA_AUTO_LISTEN = "com.example.voiceassistant.AUTO_LISTEN"
    }

    /** Android 13+: reminders and check-ins need the notification permission. */
    private val notificationPermission =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { }

    /** Incremented every time the app is opened as the assistant; the UI reacts by listening. */
    private var autoListenToken by mutableIntStateOf(0)

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // لوحة المفاتيح: أندرويد 15+ يفرض edge-to-edge (و Compose يتولى الأمر عبر imePadding).
        // في الإصدارات الأقدم لا نستعمل edge-to-edge، فيقوم النظام نفسه بتصغير النافذة فوق لوحة المفاتيح
        // (adjustResize)، وهذا يعمل على كل الأجهزة وكل لوحات المفاتيح.
        window.setSoftInputMode(WindowManager.LayoutParams.SOFT_INPUT_ADJUST_RESIZE)
        if (Build.VERSION.SDK_INT >= 35) {
            enableEdgeToEdge()
        } else {
            WindowCompat.setDecorFitsSystemWindows(window, true)
        }

        // Ask for the notification permission (not when opened as the assistant: the mic prompt comes first).
        if (savedInstanceState == null && !isAssistLaunch(intent)) {
            requestNotificationPermissionIfNeeded()
        }

        // savedInstanceState == null: don't re-trigger after rotation / recreation.
        if (savedInstanceState == null && isAssistLaunch(intent)) {
            autoListenToken++
        }

        setContent {
            VoiceAssistantTheme {
                MainScreen(autoListenToken = autoListenToken)
            }
        }
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        if (isAssistLaunch(intent)) {
            autoListenToken++
        }
    }

    private fun requestNotificationPermissionIfNeeded() {
        if (Build.VERSION.SDK_INT >= 33 &&
            ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) !=
            PackageManager.PERMISSION_GRANTED
        ) {
            notificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
        }
    }

    private fun isAssistLaunch(intent: Intent?): Boolean =
        intent?.action == Intent.ACTION_ASSIST ||
            intent?.getBooleanExtra(EXTRA_AUTO_LISTEN, false) == true
}
''')

# 15. app/src/main/java/com/example/voiceassistant/VoiceAssistantApp.kt
write_file("app/src/main/java/com/example/voiceassistant/VoiceAssistantApp.kt", r'''package com.example.voiceassistant

import android.app.Application
import com.example.voiceassistant.data.AiSettings
import com.example.voiceassistant.data.ConversationRepository
import com.example.voiceassistant.service.NotificationHelper
import com.example.voiceassistant.service.ProactiveScheduler
import com.example.voiceassistant.service.WakeWordService

class VoiceAssistantApp : Application() {
    /** Single in-memory conversation store shared by the whole process. */
    val conversationRepository: ConversationRepository by lazy { ConversationRepository() }

    override fun onCreate() {
        super.onCreate()
        // AI model + API key settings (encrypted on the device).
        AiSettings.init(this)
        // Notification channels are required on Android 8+ for any notification to show.
        NotificationHelper.createChannels(this)
        // Periodic "how are you?" check-in (KEEP: no duplicates, survives reboot).
        ProactiveScheduler.schedule(this)
        // Wake word: remember whether the app is on screen, and restart the service if the switch was left on.
        WakeWordService.trackForeground(this)
        WakeWordService.loadState(this)
        WakeWordService.startIfEnabled(this)
    }
}
''')

# 16. app/src/main/java/com/example/voiceassistant/data/models/Message.kt
write_file("app/src/main/java/com/example/voiceassistant/data/models/Message.kt", r'''package com.example.voiceassistant.data.models

import androidx.compose.runtime.Immutable

/** A block of code returned by the AI (language tag + full source). */
@Immutable
data class CodeBlock(
    val language: String,
    val content: String,
    /** True when this block is the COMPLETE edited version of the working file. */
    val isEdit: Boolean = false,
    /** Name of the file this code belongs to (null = unknown). */
    val fileName: String? = null,
    /** content:// Uri of the original file so the edit can be written back (null = not possible). */
    val sourceUri: String? = null
)

// @Immutable: lets Compose skip redrawing a chat bubble whose message did not change.
@Immutable
data class Message(
    val id: Long,
    val text: String,
    val isUser: Boolean,
    val timestamp: Long = System.currentTimeMillis(),
    val code: List<CodeBlock> = emptyList(),
    /** Path of a generated picture (null = no picture). */
    val imagePath: String? = null
)
''')

# 17. app/src/main/java/com/example/voiceassistant/data/ConversationRepository.kt
write_file("app/src/main/java/com/example/voiceassistant/data/ConversationRepository.kt", r'''package com.example.voiceassistant.data

import com.example.voiceassistant.data.models.CodeBlock
import com.example.voiceassistant.data.models.Message
import java.util.concurrent.atomic.AtomicLong
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update

class ConversationRepository {

    private val nextId = AtomicLong(1)
    private val _messages = MutableStateFlow<List<Message>>(emptyList())
    val messages: StateFlow<List<Message>> = _messages.asStateFlow()

    fun addUserMessage(text: String): Message = add(text, isUser = true)

    fun addAssistantMessage(
        text: String,
        code: List<CodeBlock> = emptyList(),
        imagePath: String? = null
    ): Message =
        add(text, isUser = false, code = code, imagePath = imagePath)

    fun clear() {
        _messages.value = emptyList()
    }

    /** Replaces the whole conversation (used to restore a saved session). */
    fun setMessages(messages: List<Message>) {
        val maxId = messages.maxOfOrNull { it.id } ?: 0L
        nextId.set(maxOf(nextId.get(), maxId + 1))
        _messages.value = messages
    }

    private fun add(
        text: String,
        isUser: Boolean,
        code: List<CodeBlock> = emptyList(),
        imagePath: String? = null
    ): Message {
        val message = Message(
            id = nextId.getAndIncrement(),
            text = text,
            isUser = isUser,
            code = code,
            imagePath = imagePath
        )
        _messages.update { it + message }
        return message
    }
}
''')

# 17a. app/src/main/java/com/example/voiceassistant/data/ChatHistoryManager.kt
write_file("app/src/main/java/com/example/voiceassistant/data/ChatHistoryManager.kt", r'''package com.example.voiceassistant.data

import android.content.Context
import com.example.voiceassistant.data.models.CodeBlock
import com.example.voiceassistant.data.models.Message
import java.io.File
import org.json.JSONArray
import org.json.JSONException
import org.json.JSONObject

/** Light entry shown in the chats list. The messages themselves are read only when a chat is opened. */
data class SavedSession(
    val id: Long,
    val title: String,
    val timestamp: Long
)

/**
 * Stores conversations on disk:
 *  - a small index (id / title / time) in SharedPreferences, newest first: all the chats list needs;
 *  - one JSON file per conversation in filesDir/chat_sessions, read only when that chat is opened.
 * Saving one chat never rewrites or parses the other chats. Data saved by the previous version
 * (one big JSON string) is moved over automatically the first time.
 * All methods are synchronized, so they are safe to call from a background thread.
 */
class ChatHistoryManager(context: Context) {

    private val prefs = context.applicationContext
        .getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    private val dir = File(context.applicationContext.filesDir, DIR_NAME).apply { mkdirs() }

    init {
        migrateLegacy()
    }

    /** A new, unused session id. */
    @Synchronized
    fun newSessionId(): Long {
        val index = readIndex()
        var id = System.currentTimeMillis()
        while (containsId(index, id)) id++
        return id
    }

    /** Saves [messages] as the session [id] (creates or updates it) and returns the id. */
    @Synchronized
    fun saveSession(title: String, messages: List<Message>, id: Long? = null): Long {
        val sessionId = id ?: newSessionId()
        writeAtomically(fileFor(sessionId), messagesToJson(messages).toString())
        val existing = readIndex()
        val result = JSONArray()
        result.put(
            JSONObject()
                .put("id", sessionId)
                .put("title", title)
                .put("timestamp", System.currentTimeMillis())
        )
        for (i in 0 until existing.length()) {
            val item = existing.optJSONObject(i) ?: continue
            if (item.optLong("id") != sessionId) result.put(item)
        }
        prefs.edit().putString(KEY_INDEX, result.toString()).apply()
        return sessionId
    }

    /** The chats list (newest first). Cheap: no messages are read. */
    @Synchronized
    fun getAllSessions(): List<SavedSession> {
        val array = readIndex()
        val list = ArrayList<SavedSession>(array.length())
        for (i in 0 until array.length()) {
            val item = array.optJSONObject(i) ?: continue
            list.add(
                SavedSession(
                    id = item.optLong("id"),
                    title = item.optString("title"),
                    timestamp = item.optLong("timestamp")
                )
            )
        }
        return list
    }

    /** Reads the messages of one conversation (empty list if it can't be read). */
    @Synchronized
    fun loadMessages(id: Long): List<Message> {
        val file = fileFor(id)
        if (!file.exists()) return emptyList()
        return try {
            parseMessages(file.readText(Charsets.UTF_8))
        } catch (e: Exception) {
            emptyList()
        }
    }

    @Synchronized
    fun deleteSession(id: Long) {
        val existing = readIndex()
        val result = JSONArray()
        for (i in 0 until existing.length()) {
            val item = existing.optJSONObject(i) ?: continue
            if (item.optLong("id") != id) result.put(item)
        }
        prefs.edit().putString(KEY_INDEX, result.toString()).apply()
        fileFor(id).delete()
    }

    private fun fileFor(id: Long) = File(dir, "$id.json")

    /** Writes to a temp file first, so a crash in the middle never leaves a half-written chat. */
    private fun writeAtomically(target: File, text: String) {
        val tmp = File(dir, target.name + ".tmp")
        tmp.writeText(text, Charsets.UTF_8)
        if (!tmp.renameTo(target)) {
            target.delete()
            tmp.renameTo(target)
        }
    }

    /** Moves the old single-string history (key "sessions") into per-chat files, once. */
    private fun migrateLegacy() {
        val legacy = prefs.getString(KEY_LEGACY, null) ?: return
        val old = try {
            JSONArray(legacy)
        } catch (e: JSONException) {
            JSONArray()
        }
        val index = JSONArray()
        var failed = false
        for (i in 0 until old.length()) {
            val item = old.optJSONObject(i) ?: continue
            val id = item.optLong("id")
            try {
                writeAtomically(fileFor(id), item.optString("messagesJson", "[]"))
                index.put(
                    JSONObject()
                        .put("id", id)
                        .put("title", item.optString("title"))
                        .put("timestamp", item.optLong("timestamp"))
                )
            } catch (e: Exception) {
                failed = true
            }
        }
        val editor = prefs.edit().putString(KEY_INDEX, index.toString())
        if (!failed) editor.remove(KEY_LEGACY)   // kept if something failed, so the next start retries
        editor.apply()
    }

    private fun containsId(array: JSONArray, id: Long): Boolean {
        for (i in 0 until array.length()) {
            if (array.optJSONObject(i)?.optLong("id") == id) return true
        }
        return false
    }

    private fun readIndex(): JSONArray = try {
        JSONArray(prefs.getString(KEY_INDEX, null) ?: "[]")
    } catch (e: JSONException) {
        JSONArray()
    }

    companion object {
        private const val PREFS_NAME = "chat_history"
        private const val KEY_INDEX = "index"
        private const val KEY_LEGACY = "sessions"
        private const val DIR_NAME = "chat_sessions"

        fun messagesToJson(messages: List<Message>): JSONArray {
            val array = JSONArray()
            for (m in messages) {
                val codeArray = JSONArray()
                for (c in m.code) {
                    val code = JSONObject()
                        .put("language", c.language)
                        .put("content", c.content)
                        .put("isEdit", c.isEdit)
                    if (c.fileName != null) code.put("fileName", c.fileName)
                    if (c.sourceUri != null) code.put("sourceUri", c.sourceUri)
                    codeArray.put(code)
                }
                val obj = JSONObject()
                    .put("id", m.id)
                    .put("text", m.text)
                    .put("isUser", m.isUser)
                    .put("timestamp", m.timestamp)
                    .put("code", codeArray)
                if (m.imagePath != null) obj.put("imagePath", m.imagePath)
                array.put(obj)
            }
            return array
        }

        fun parseMessages(json: String): List<Message> {
            val array = try {
                JSONArray(json)
            } catch (e: JSONException) {
                return emptyList()
            }
            val list = ArrayList<Message>(array.length())
            for (i in 0 until array.length()) {
                val obj = array.optJSONObject(i) ?: continue
                val codeArray = obj.optJSONArray("code") ?: JSONArray()
                val blocks = ArrayList<CodeBlock>(codeArray.length())
                for (j in 0 until codeArray.length()) {
                    val c = codeArray.optJSONObject(j) ?: continue
                    blocks.add(
                        CodeBlock(
                            language = c.optString("language"),
                            content = c.optString("content"),
                            isEdit = c.optBoolean("isEdit", false),
                            fileName = if (c.has("fileName") && !c.isNull("fileName")) c.getString("fileName") else null,
                            sourceUri = if (c.has("sourceUri") && !c.isNull("sourceUri")) c.getString("sourceUri") else null
                        )
                    )
                }
                list.add(
                    Message(
                        id = obj.optLong("id", (i + 1).toLong()),
                        text = obj.optString("text"),
                        isUser = obj.optBoolean("isUser", false),
                        timestamp = obj.optLong("timestamp", System.currentTimeMillis()),
                        code = blocks,
                        imagePath = if (obj.has("imagePath") && !obj.isNull("imagePath")) obj.getString("imagePath") else null
                    )
                )
            }
            return list
        }
    }
}
''')

# 17b. AiChatService.kt (النسخة المحسّنة مدمجة بالكامل داخل السكريبت)
#   - ترتيب النماذج: الأسرع أولاً (gemini-2.5-flash ...) مع تخطي النماذج التي ترجع 404
#   - مهلات أقصر: readTimeout 40s و callTimeout 45s لكل محاولة
# مفتاح Gemini لا يُكتب داخل السكريبت. يُؤخذ بالترتيب من:
#   1) متغير البيئة GEMINI_API_KEY
#   2) ملف AiChatService.kt قديم بجوار السكريبت (يُقرأ منه المفتاح فقط)
def _resolve_key(env_name):
    key = os.environ.get(env_name, "").strip()
    if key:
        return key
    if env_name == "GEMINI_API_KEY":
        for folder in (SCRIPT_DIR, os.getcwd()):
            candidate = os.path.join(folder, "AiChatService.kt")
            if os.path.exists(candidate):
                with open(candidate, "r", encoding="utf-8") as f:
                    found = re.search(r'const val GEMINI_API_KEY = "([^"]*)"', f.read())
                if found and found.group(1) and found.group(1) != "__GEMINI_API_KEY__":
                    return found.group(1)
    return ""


GEMINI_KEY = _resolve_key("GEMINI_API_KEY")
OPENAI_KEY = _resolve_key("OPENAI_API_KEY")
CLAUDE_KEY = _resolve_key("CLAUDE_API_KEY")
# المفاتيح لم تعد تُكتب داخل ملفات Kotlin. تصل للتطبيق عبر BuildConfig:
#   - على GitHub: GitHub Secrets -> متغيرات البيئة التي يقرؤها app/build.gradle.kts
#   - محلياً: متغيرات البيئة، أو ملف keys.properties (مُتجاهَل في git) يُنشأ هنا من AiChatService.kt قديم.
# ويمكن للمستخدم إدخال مفاتيحه من شاشة الإعدادات في التطبيق (تتغلب على مفاتيح البناء).
_legacy_keys = {
    name: key
    for name, key in (("GEMINI_API_KEY", GEMINI_KEY), ("OPENAI_API_KEY", OPENAI_KEY), ("CLAUDE_API_KEY", CLAUDE_KEY))
    if key and not os.environ.get(name, "").strip()
}
if _legacy_keys:
    with open("keys.properties", "w", encoding="utf-8", newline="\n") as _kf:
        for _name, _key in _legacy_keys.items():
            _kf.write("{}={}\n".format(_name, _key))

_existing_ignore = ""
if os.path.exists(".gitignore"):
    with open(".gitignore", "r", encoding="utf-8") as _gf:
        _existing_ignore = _gf.read()
if "keys.properties" not in _existing_ignore:
    with open(".gitignore", "a", encoding="utf-8", newline="\n") as _gf:
        if not _existing_ignore:
            _gf.write(".gradle/\nbuild/\nlocal.properties\n.idea/\n*.iml\n")
        elif not _existing_ignore.endswith("\n"):
            _gf.write("\n")
        _gf.write("# Local API keys (never commit)\nkeys.properties\n")
if not (GEMINI_KEY or OPENAI_KEY or CLAUDE_KEY):
    print(">> NOTE: no built-in API key (GitHub Secrets / env). Enter your keys in the app: menu > AI models.")

AI_SERVICE_TEMPLATE = r'''package com.example.voiceassistant.data

import android.util.Base64
import android.util.Log
import com.example.voiceassistant.data.models.CodeBlock
import com.example.voiceassistant.viewmodel.AppLanguage
import java.io.IOException
import java.util.concurrent.TimeUnit
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.delay
import kotlinx.coroutines.suspendCancellableCoroutine
import kotlinx.coroutines.withContext
import kotlinx.coroutines.withTimeoutOrNull
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.update
import kotlin.coroutines.resume
import kotlin.coroutines.resumeWithException
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.Call
import okhttp3.Callback
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject

// المفاتيح تُقرأ وقت الطلب: المفتاح المُدخل في إعدادات التطبيق أولاً، ثم مفتاح البناء (GitHub Secrets / BuildConfig).
private val GEMINI_API_KEY: String get() = AiSettings.apiKey(AiProvider.GEMINI)
private val OPENAI_API_KEY: String get() = AiSettings.apiKey(AiProvider.OPENAI)
private val CLAUDE_API_KEY: String get() = AiSettings.apiKey(AiProvider.CLAUDE)

// النماذج النصية: الأحدث والأكثر استقراراً أولاً
val GEMINI_MODELS = listOf(
    "gemini-3.8-flash",          // الأقوى في عائلة Flash
    "gemini-3.1-flash-lite",     // الأسرع والأقل تكلفة
)
// نموذج توليد الصور: استخدم الجيل الأحدث
const val IMAGE_MODEL = "gemini-3.1-flash-image" // Nano Banana 2
// أو للسرعة: "gemini-3.1-flash-lite-image"
val IMAGE_MODELS = listOf(IMAGE_MODEL)

private const val GEMINI_BASE = "https://generativelanguage.googleapis.com/v1beta/models/"
private const val OPENAI_BASE = "https://api.openai.com/v1/chat/completions"
private const val CLAUDE_BASE = "https://api.anthropic.com/v1/messages"

private val RETRY_CODES = setOf(429, 500, 502, 503, 504)
private const val MAX_HISTORY_MESSAGES = 12
private const val TAG = "AiChat"

// أقصى زمن إجمالي لسلسلة نماذج Gemini كلها: بعده تظهر رسالة خطأ بدل أن تبقى "جارٍ المعالجة" معلّقة.
private const val GEMINI_TOTAL_TIMEOUT_MS = 40_000L

// الأسئلة المدعومة بالبحث المباشر أبطأ قليلاً (بحث ثم صياغة الرد)، لذلك نمنحها وقتاً أطول.
private const val SEARCH_TOTAL_TIMEOUT_MS = 60_000L

// عند وجود ملف عمل (قراءة/تعديل كود) يتضمن الرد الملف كاملاً، لذلك نمنحه وقتاً أطول.
private const val EDIT_TOTAL_TIMEOUT_MS = 110_000L

/** عدّاد استهلاك التوكنات (مجموع الجلسة) لكل المزوّدين. يُحدَّث من حقل usage في ردود الـ API. */
object TokenCounter {
    data class Usage(val input: Long = 0, val output: Long = 0) {
        val total: Long get() = input + output
    }

    private val _usage = kotlinx.coroutines.flow.MutableStateFlow(Usage())
    val usage: kotlinx.coroutines.flow.StateFlow<Usage> = _usage.asStateFlow()

    fun add(input: Long, output: Long) {
        if (input <= 0 && output <= 0) return
        _usage.update { Usage(it.input + input.coerceAtLeast(0), it.output + output.coerceAtLeast(0)) }
        Log.i("TokenCounter", "+in=$input +out=$output | total=${_usage.value.total}")
    }

    fun reset() { _usage.value = Usage() }

    internal fun fromGemini(raw: String) {
        val u = try { JSONObject(raw).optJSONObject("usageMetadata") } catch (e: Exception) { null } ?: return
        add(u.optLong("promptTokenCount"), u.optLong("candidatesTokenCount") + u.optLong("thoughtsTokenCount"))
    }

    internal fun fromOpenAi(raw: String) {
        val u = try { JSONObject(raw).optJSONObject("usage") } catch (e: Exception) { null } ?: return
        add(u.optLong("prompt_tokens"), u.optLong("completion_tokens"))
    }

    internal fun fromClaude(raw: String) {
        val u = try { JSONObject(raw).optJSONObject("usage") } catch (e: Exception) { null } ?: return
        add(u.optLong("input_tokens"), u.optLong("output_tokens"))
    }
}

enum class AiError { NOT_CONFIGURED, BAD_KEY, RATE_LIMIT, NETWORK, EMPTY, OTHER }

sealed class AiResult {
    data class Success(val text: String, val code: List<CodeBlock> = emptyList()) : AiResult()
    data class Error(val kind: AiError, val detail: String = "") : AiResult()
}

sealed class ImageResult {
    class Success(val bytes: ByteArray) : ImageResult()
    data class Error(val kind: AiError, val detail: String = "") : ImageResult()
}

/** The code file the user is working on: read once, then explained / edited over several requests. */
data class WorkingFile(
    val name: String,
    /** Uri of the original file (null = unknown, so the edit can only be copied or saved as new). */
    val uri: String?,
    val content: String
)

class AiChatService(private val memoryManager: MemoryManager? = null) {

    private val client: OkHttpClient = OkHttpClient.Builder()
        .connectTimeout(8, TimeUnit.SECONDS)
        .writeTimeout(10, TimeUnit.SECONDS)
        .readTimeout(20, TimeUnit.SECONDS)
        .callTimeout(25, TimeUnit.SECONDS)   // حد أقصى لكل محاولة (نموذج) حتى لا يعلق الطلب
        .build()

    // للطلبات الثقيلة فقط (توليد الصور / تحليل الملفات): تحتاج وقتاً أطول من الدردشة العادية.
    private val longClient: OkHttpClient = client.newBuilder()
        .readTimeout(90, TimeUnit.SECONDS)
        .callTimeout(100, TimeUnit.SECONDS)
        .build()

    // نماذج رجعت 404 (غير موجودة/متوقفة): نتجاوزها في بقية الجلسة بدل إعادة تجربتها كل مرة.
    private val unavailableModels: MutableSet<String> = java.util.concurrent.ConcurrentHashMap.newKeySet()

    private fun activeModels(): List<String> =
        GEMINI_MODELS.filter { it !in unavailableModels }.ifEmpty { GEMINI_MODELS }

    private fun activeImageModels(): List<String> =
        IMAGE_MODELS.filter { it !in unavailableModels }.ifEmpty { IMAGE_MODELS }

    private val history = ArrayList<Pair<String, String>>()
    private val lock = Any()

    /** While set, its content is sent with every request so the AI can read and edit it. */
    @Volatile
    var workingFile: WorkingFile? = null

    /** The user's name (null = unknown). Use [setUserName] to change it. */
    @set:JvmName("assignUserName")
    var userName: String? = null

    fun setUserName(name: String) {
        userName = name.trim().ifEmpty { null }
    }

    /**
     * Providers to try, in order: the one selected in Settings first, then the others (only when
     * "use another model if the selected one fails" is on). Providers without any key are skipped.
     */
    private fun providerOrder(): List<AiProvider> {
        val selected = AiSettings.selectedProvider()
        val order = if (AiSettings.fallbackEnabled()) {
            listOf(selected) + AiProvider.values().filter { it != selected }
        } else {
            listOf(selected)
        }
        return order.filter { AiSettings.apiKey(it).isNotBlank() }
    }

    fun isConfigured(): Boolean = providerOrder().isNotEmpty()

    fun clearHistory() {
        synchronized(lock) { history.clear() }
    }

    suspend fun ask(text: String, lang: AppLanguage): AiResult = withContext(Dispatchers.IO) {
        val providers = providerOrder()
        if (providers.isEmpty()) return@withContext AiResult.Error(AiError.NOT_CONFIGURED)

        var lastError: AiResult.Error = AiResult.Error(AiError.OTHER, "No models tried")
        for (provider in providers) {
            val result = when (provider) {
                AiProvider.GEMINI -> askGemini(text, lang)
                AiProvider.OPENAI -> askChatGPT(text, lang)
                AiProvider.CLAUDE -> askClaude(text, lang)
            }
            if (result is AiResult.Success) return@withContext result
            if (result is AiResult.Error) lastError = result
        }
        return@withContext lastError
    }

    /** The whole Gemini model chain (fastest first, 404 models skipped, one overall time limit). */
    private suspend fun askGemini(text: String, lang: AppLanguage): AiResult {
        val trace = ArrayList<String>()
        var lastError: AiResult.Error = AiResult.Error(AiError.OTHER, "No models tried")
        var timedOut = true
        val editing = workingFile != null
        val searching = !editing && AiSettings.webSearchEnabled()
        val totalTimeout = when {
            editing -> EDIT_TOTAL_TIMEOUT_MS
            searching -> SEARCH_TOTAL_TIMEOUT_MS
            else -> GEMINI_TOTAL_TIMEOUT_MS
        }
        // للتعديل على الكود نفضّل النماذج الأقوى (غير lite) أولاً.
        val models = if (editing) activeModels().sortedBy { if (it.contains("lite")) 1 else 0 } else activeModels()
        val geminiResult: AiResult? = withTimeoutOrNull(totalTimeout) {
            for (modelName in models) {
                val started = System.currentTimeMillis()
                val result = askGeminiModel(modelName, text, lang)
                val took = System.currentTimeMillis() - started
                if (result is AiResult.Success) {
                    Log.i(TAG, "$modelName OK in ${took}ms")
                    timedOut = false
                    return@withTimeoutOrNull result
                }
                if (result is AiResult.Error) {
                    val line = "$modelName ${took}ms ${result.kind} ${result.detail}".take(140)
                    Log.w(TAG, line)   // Logcat: فلتر AiChat
                    trace.add(line)
                    lastError = result
                    if (result.kind == AiError.BAD_KEY || result.kind == AiError.NOT_CONFIGURED) break
                }
            }
            timedOut = false
            null
        }
        if (geminiResult is AiResult.Success) return geminiResult
        val summary = trace.joinToString(" | ").take(400)
        return if (timedOut) {
            AiResult.Error(AiError.NETWORK, "timeout ${totalTimeout / 1000}s | $summary")
        } else {
            lastError.copy(detail = summary.ifBlank { lastError.detail })
        }
    }

    private suspend fun askGeminiModel(modelName: String, text: String, lang: AppLanguage): AiResult {
        try {
            // Google Search grounding: live web results. Not used while editing a code file.
            var useSearch = workingFile == null && AiSettings.webSearchEnabled()
            fun buildRequest(): Request = Request.Builder()
                .url("$GEMINI_BASE$modelName:generateContent")
                .header("x-goog-api-key", GEMINI_API_KEY)
                .post(buildGeminiBody(text, lang, useSearch).toString().toRequestBody("application/json; charset=utf-8".toMediaType()))
                .build()

            val callClient = if (workingFile != null || useSearch) longClient else client
            val maxAttempts = 3          // المحاولة الأولى + محاولتان إضافيتان كحد أقصى
            val baseDelayMs = 1500L      // أول انتظار، ثم يتضاعف مع كل محاولة

            for (attempt in 1..maxAttempts) {
                var httpCode = 0
                val outcome: AiResult = callClient.newCall(buildRequest()).await().use { response ->
                    httpCode = response.code
                    val raw = response.body?.string().orEmpty()
                    if (!response.isSuccessful) {
                        if (response.code == 404) unavailableModels.add(modelName)
                        AiResult.Error(kindForGemini(response.code, raw), apiError(response.code, raw))
                    } else {
                        val full = extractGeminiText(raw)
                        if (full.isBlank()) {
                            AiResult.Error(AiError.EMPTY)
                        } else {
                            val (spoken, rawCode) = splitCode(full, lang)
                            val code = applyEdit(rawCode)
                            // The edited file already lives in the system prompt, so history only keeps the short summary.
                            remember(text, if (code.any { it.isEdit }) spoken else full)
                            AiResult.Success(spoken, code)
                        }
                    }
                }

                // A model that rejects the search tool (HTTP 400): retry once without it instead of failing.
                if (outcome is AiResult.Error && httpCode == 400 && useSearch && outcome.kind != AiError.BAD_KEY) {
                    useSearch = false
                    Log.w(TAG, "$modelName rejected google_search, retrying without it")
                    continue
                }

                // Exponential backoff with jitter for "High Demand" (503) and rate limits (429).
                val retryable = httpCode == 503 || httpCode == 429
                if (outcome is AiResult.Error && retryable && attempt < maxAttempts) {
                    val delayMs = baseDelayMs * (1L shl (attempt - 1)) + kotlin.random.Random.nextLong(0L, 500L)
                    Log.w(TAG, "$modelName HTTP $httpCode, retry $attempt/${maxAttempts - 1} in ${delayMs}ms")
                    delay(delayMs)
                    continue
                }
                return outcome
            }
            return AiResult.Error(AiError.OTHER, "retries exhausted")
        } catch (e: IOException) {
            return AiResult.Error(AiError.NETWORK, e.toString().take(160))
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            return AiResult.Error(AiError.OTHER, e.toString().take(160))
        }
    }

    /** Common ending for non-Gemini answers: split code, apply a file edit, keep the history. */
    private fun finishText(userText: String, full: String, lang: AppLanguage): AiResult {
        val (spoken, rawCode) = splitCode(full, lang)
        val code = applyEdit(rawCode)
        remember(userText, if (code.any { it.isEdit }) spoken else full)
        return AiResult.Success(spoken, code)
    }

    private fun kindForBearer(code: Int): AiError = when (code) {
        401, 403 -> AiError.BAD_KEY
        429, 529 -> AiError.RATE_LIMIT
        else -> AiError.OTHER
    }

    /** One ChatGPT call with the system prompt, the history and [userContent] (a String or a JSON content array). */
    private suspend fun callOpenAi(userContent: Any, lang: AppLanguage): Pair<String?, AiResult.Error?> {
        try {
            val messages = JSONArray()
            messages.put(JSONObject().put("role", "system").put("content", systemPrompt(lang)))
            synchronized(lock) {
                history.forEach { (role, t) ->
                    messages.put(JSONObject().put("role", if (role == "model") "assistant" else "user").put("content", t))
                }
            }
            messages.put(JSONObject().put("role", "user").put("content", userContent))
            val json = JSONObject()
                .put("model", AiSettings.model(AiProvider.OPENAI))
                .put("messages", messages)
                .toString()
            val request = Request.Builder()
                .url(OPENAI_BASE)
                .header("Authorization", "Bearer $OPENAI_API_KEY")
                .post(json.toRequestBody("application/json; charset=utf-8".toMediaType()))
                .build()
            val callClient = if (workingFile != null) longClient else client
            return callClient.newCall(request).await().use { response ->
                val raw = response.body?.string().orEmpty()
                val outcome: Pair<String?, AiResult.Error?> = if (!response.isSuccessful) {
                    null to AiResult.Error(kindForBearer(response.code), apiError(response.code, raw))
                } else {
                    TokenCounter.fromOpenAi(raw)
                    val full = JSONObject(raw).optJSONArray("choices")?.optJSONObject(0)
                        ?.optJSONObject("message")?.optString("content").orEmpty().trim()
                    if (full.isBlank()) null to AiResult.Error(AiError.EMPTY) else full to null
                }
                outcome
            }
        } catch (e: CancellationException) {
            throw e
        } catch (e: IOException) {
            return null to AiResult.Error(AiError.NETWORK, e.toString().take(160))
        } catch (e: Exception) {
            return null to AiResult.Error(AiError.OTHER, e.toString().take(160))
        }
    }

    /** One Claude call with the system prompt, the history and [userContent] (a String or a JSON content array). */
    private suspend fun callClaude(userContent: Any, lang: AppLanguage): Pair<String?, AiResult.Error?> {
        try {
            val messages = JSONArray()
            synchronized(lock) {
                history.forEach { (role, t) ->
                    messages.put(JSONObject().put("role", if (role == "model") "assistant" else "user").put("content", t))
                }
            }
            messages.put(JSONObject().put("role", "user").put("content", userContent))
            val json = JSONObject()
                .put("model", AiSettings.model(AiProvider.CLAUDE))
                .put("max_tokens", if (workingFile != null) 16384 else 4096)
                .put("system", systemPrompt(lang))
                .put("messages", messages)
                .toString()
            val request = Request.Builder()
                .url(CLAUDE_BASE)
                .header("x-api-key", CLAUDE_API_KEY)
                .header("anthropic-version", "2023-06-01")
                .post(json.toRequestBody("application/json; charset=utf-8".toMediaType()))
                .build()
            val callClient = if (workingFile != null) longClient else client
            return callClient.newCall(request).await().use { response ->
                val raw = response.body?.string().orEmpty()
                val outcome: Pair<String?, AiResult.Error?> = if (!response.isSuccessful) {
                    null to AiResult.Error(kindForBearer(response.code), apiError(response.code, raw))
                } else {
                    TokenCounter.fromClaude(raw)
                    val blocks = JSONObject(raw).optJSONArray("content")
                    val sb = StringBuilder()
                    if (blocks != null) {
                        for (i in 0 until blocks.length()) {
                            val block = blocks.optJSONObject(i) ?: continue
                            if (block.optString("type") == "text") sb.append(block.optString("text"))
                        }
                    }
                    val full = sb.toString().trim()
                    if (full.isBlank()) null to AiResult.Error(AiError.EMPTY) else full to null
                }
                outcome
            }
        } catch (e: CancellationException) {
            throw e
        } catch (e: IOException) {
            return null to AiResult.Error(AiError.NETWORK, e.toString().take(160))
        } catch (e: Exception) {
            return null to AiResult.Error(AiError.OTHER, e.toString().take(160))
        }
    }

    private suspend fun askChatGPT(text: String, lang: AppLanguage): AiResult {
        val (full, error) = callOpenAi(text, lang)
        if (full == null) return error ?: AiResult.Error(AiError.OTHER)
        return finishText(text, full, lang)
    }

    private suspend fun askClaude(text: String, lang: AppLanguage): AiResult {
        val (full, error) = callClaude(text, lang)
        if (full == null) return error ?: AiResult.Error(AiError.OTHER)
        return finishText(text, full, lang)
    }

    private fun isImagen(modelName: String): Boolean = modelName.startsWith("imagen-")

    /** Imagen (:predict) answer: predictions[].bytesBase64Encoded. */
    private fun extractImagenBytes(raw: String): ByteArray? {
        val predictions = JSONObject(raw).optJSONArray("predictions") ?: return null
        for (i in 0 until predictions.length()) {
            val data = predictions.optJSONObject(i)?.optString("bytesBase64Encoded").orEmpty()
            if (data.isNotBlank()) return Base64.decode(data, Base64.DEFAULT)
        }
        return null
    }

    /** Gemini image (:generateContent) answer: candidates[0].content.parts[].inlineData. */
    private fun extractGeminiImageBytes(raw: String): ByteArray? {
        val parts = JSONObject(raw).optJSONArray("candidates")?.optJSONObject(0)
            ?.optJSONObject("content")?.optJSONArray("parts") ?: return null
        for (i in 0 until parts.length()) {
            val part = parts.optJSONObject(i) ?: continue
            val inline = part.optJSONObject("inlineData") ?: part.optJSONObject("inline_data")
            val data = inline?.optString("data").orEmpty()
            if (data.isNotBlank()) return Base64.decode(data, Base64.DEFAULT)
        }
        return null
    }

    suspend fun generateImage(prompt: String): ImageResult = withContext(Dispatchers.IO) {
        if (GEMINI_API_KEY.isBlank()) return@withContext ImageResult.Error(AiError.NOT_CONFIGURED)
        var lastError: ImageResult.Error = ImageResult.Error(AiError.OTHER, "No image models tried")
        try {
            val imagenBody = JSONObject()
                .put("instances", JSONArray().put(JSONObject().put("prompt", prompt)))
                .put("parameters", JSONObject().put("sampleCount", 1))
                .toString()
            val geminiBody = JSONObject()
                .put("contents", JSONArray().put(turn("user", prompt)))
                .put("generationConfig", JSONObject().put("responseModalities", JSONArray().put("TEXT").put("IMAGE")))
                .toString()
            for (modelName in activeImageModels()) {
                val imagen = isImagen(modelName)
                val endpoint = if (imagen) "predict" else "generateContent"
                val request = Request.Builder()
                    .url("$GEMINI_BASE$modelName:$endpoint")
                    .header("x-goog-api-key", GEMINI_API_KEY)
                    .post((if (imagen) imagenBody else geminiBody).toRequestBody("application/json; charset=utf-8".toMediaType()))
                    .build()
                try {
                    val found: ByteArray? = longClient.newCall(request).await().use { response ->
                        val raw = response.body?.string().orEmpty()
                        if (!response.isSuccessful) {
                            if (response.code == 404) unavailableModels.add(modelName)
                            lastError = ImageResult.Error(
                                kindForGemini(response.code, raw),
                                "$modelName ${apiError(response.code, raw)}".take(220)
                            )
                            null
                        } else {
                            if (!imagen) TokenCounter.fromGemini(raw)
                            val bytes = if (imagen) extractImagenBytes(raw) else extractGeminiImageBytes(raw)
                            if (bytes == null) lastError = ImageResult.Error(AiError.EMPTY, modelName)
                            bytes
                        }
                    }
                    if (found != null) return@withContext ImageResult.Success(found)
                } catch (e: CancellationException) {
                    throw e
                } catch (e: Exception) {
                    lastError = ImageResult.Error(AiError.NETWORK, e.toString().take(160))
                }
            }
            return@withContext lastError
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            return@withContext ImageResult.Error(AiError.NETWORK, e.toString().take(160))
        }
    }

    /** تنفيذ الطلب بشكل قابل للإلغاء: عند انتهاء المهلة أو إلغاء الكوروتين يُقطع الاتصال فعلاً. */
    private suspend fun Call.await(): Response = suspendCancellableCoroutine { cont ->
        cont.invokeOnCancellation { cancel() }
        enqueue(object : Callback {
            override fun onFailure(call: Call, e: IOException) {
                if (cont.isActive) cont.resumeWithException(e)
            }

            override fun onResponse(call: Call, response: Response) {
                if (cont.isActive) cont.resume(response) else response.close()
            }
        })
    }

    private fun kindForGemini(code: Int, raw: String): AiError = when (code) {
        401, 403 -> AiError.BAD_KEY
        400 -> if (raw.contains("API key", ignoreCase = true)) AiError.BAD_KEY else AiError.OTHER
        429 -> AiError.RATE_LIMIT
        else -> AiError.OTHER
    }

    private fun apiError(code: Int, raw: String): String {
        val msg = try { JSONObject(raw).optJSONObject("error")?.optString("message").orEmpty() } catch (e: Exception) { "" }
        return "HTTP $code: " + msg.replace("\n", " ").take(200)
    }

    private fun turn(role: String, text: String): JSONObject =
        JSONObject().put("role", role).put("parts", JSONArray().put(JSONObject().put("text", text)))

    private fun basePrompt(lang: AppLanguage): String {
        val base = lang.tr(
            "أنت Zevorix AI، مساعد صوتي ذكي. أجب بالعربية وبإيجاز. إذا طلب المستخدم كوداً، اكتبه داخل كتلة markdown.",
            "You are Zevorix AI, a smart voice assistant. Answer briefly in English. If the user asks for code, provide it in a markdown block."
        )
        val name = userName?.takeIf { it.isNotBlank() }
        val withName = if (name == null) base else base + "\n" + lang.tr(
            "اسم المستخدم هو $name (محفوظ بشكل دائم). ناده باسمه أحياناً ليكون ودوداً، ولا تسأله عن اسمه مرة أخرى أبداً.",
            "The user's name is $name (saved permanently). Address them by their name occasionally to be friendly, and never ask for their name again."
        )
        // Long-term memory: read from RAM, no extra request. "" when nothing is stored.
        val memory = memoryManager?.renderForPrompt(lang).orEmpty()
        return if (memory.isEmpty()) withName else withName + "\n\n" + memory
    }

    private fun editingRules(): String = """
        The user is working on the code file given below. You can read it, explain it, find bugs and edit it when asked.
        Rules:
        1. When asked to change, fix, add or refactor something, return the COMPLETE updated file (never only a snippet, never "rest unchanged") in exactly ONE code block. Write the word edit after the language on the opening fence, for example ```kotlin edit. Keep all unrelated code and formatting exactly as it was.
        2. Outside the code block write 1-3 short plain sentences saying what you changed. They are read aloud, so put no code or symbols there.
        3. If the user only asks a question or wants an explanation, answer in plain text and do NOT return the whole file.
        4. If the request is unclear, ask one short question instead of guessing.
        5. If the question is unrelated to this file, ignore the file.
    """.trimIndent()

    private fun systemPrompt(lang: AppLanguage): String {
        val base = basePrompt(lang)
        val file = workingFile ?: return base
        return base + "\n\n" + editingRules() +
            "\n\n=== BEGIN FILE: ${file.name} ===\n" + file.content + "\n=== END FILE ==="
    }

    private fun buildGeminiBody(text: String, lang: AppLanguage, withSearch: Boolean = false): JSONObject {
        val contents = JSONArray()
        synchronized(lock) { history.forEach { (role, t) -> contents.put(turn(role, t)) } }
        contents.put(turn("user", text))
        return JSONObject()
            .put("system_instruction", JSONObject().put("parts", JSONArray().put(JSONObject().put("text", systemPrompt(lang)))))
            .put("contents", contents)
            .put("generationConfig", JSONObject().put("maxOutputTokens", if (workingFile != null) 32768 else 8192))
            .apply {
                // Grounding with Google Search: the model decides when a web search improves the answer.
                if (withSearch) put("tools", JSONArray().put(JSONObject().put("google_search", JSONObject())))
            }
    }

    private fun extractGeminiText(raw: String): String {
        TokenCounter.fromGemini(raw)
        val parts = JSONObject(raw).optJSONArray("candidates")?.optJSONObject(0)?.optJSONObject("content")?.optJSONArray("parts") ?: return ""
        val sb = StringBuilder()
        for (i in 0 until parts.length()) {
            parts.optJSONObject(i)?.optString("text")?.let { sb.append(it) }
        }
        return sb.toString().trim()
    }

    // group 1 = language, group 2 = extra words on the fence line (e.g. "edit"), group 3 = the code.
    private val fence = Regex("```([A-Za-z0-9+#._-]*)([^\\r\\n]*)\\r?\\n([\\s\\S]*?)```")

    private fun splitCode(full: String, lang: AppLanguage): Pair<String, List<CodeBlock>> {
        if (!full.contains("```")) return clean(full) to emptyList()
        val text = if (Regex("```").findAll(full).count() % 2 == 1) full + "\n```" else full
        val blocks = fence.findAll(text).map {
            CodeBlock(
                language = it.groupValues[1].lowercase(),
                content = it.groupValues[3].trimEnd(),
                isEdit = it.groupValues[2].contains("edit", ignoreCase = true)
            )
        }.toList()
        if (blocks.isEmpty()) return clean(full) to emptyList()
        var spoken = clean(fence.replace(text, " "))
        if (spoken.isBlank()) spoken = lang.tr("تفضل، هذا هو الكود.", "Here is the code.")
        return spoken to blocks
    }

    /**
     * If the answer holds the complete edited file, it becomes the new working file and the block is tagged
     * with the original file name / Uri so the UI can write it back. Short snippets are left untouched.
     */
    private fun applyEdit(blocks: List<CodeBlock>): List<CodeBlock> {
        val file = workingFile ?: return blocks
        val originalLines = file.content.lines().size
        val edited = blocks.firstOrNull { it.isEdit }
            ?: blocks.singleOrNull()?.takeIf { it.content.lines().size >= originalLines * 6 / 10 }
            ?: return blocks
        val trailing = if (file.content.endsWith("\n")) "\n" else ""
        workingFile = file.copy(content = edited.content + trailing)
        return blocks.map {
            if (it === edited) it.copy(isEdit = true, fileName = file.name, sourceUri = file.uri) else it
        }
    }

    private fun clean(text: String): String = text.replace("*", "").replace("#", "").replace("`", "").replace(Regex("\\n{2,}"), "\n").trim()

    private fun remember(userText: String, answer: String) {
        synchronized(lock) {
            history.add("user" to userText)
            history.add("model" to answer)
            while (history.size > MAX_HISTORY_MESSAGES) history.removeAt(0)
        }
    }
}
'''

write_file(
    "app/src/main/java/com/example/voiceassistant/data/AiChatService.kt",
    AI_SERVICE_TEMPLATE
)

# 17b. الذاكرة طويلة المدى: النموذج + المدير (تخزين محلي فقط، بدون شبكة)
write_file("app/src/main/java/com/example/voiceassistant/data/models/MemoryEntry.kt", r'''package com.example.voiceassistant.data.models

/** What a memory entry describes. PREFERENCE = likes / dislikes, FACT = anything else about the user. */
enum class MemoryType { FACT, PROJECT, PREFERENCE }

/**
 * One thing the assistant remembers, stored locally (see MemoryManager).
 *
 * For a PROJECT: [content] is the last note about the file, [createdAt] is when it was first opened,
 * [lastUsedAt] is when it was last opened / edited, and [metadata] holds "fileName" and "fileUri".
 */
data class MemoryEntry(
    val id: Long,
    val type: MemoryType,
    val content: String,
    val createdAt: Long,
    val lastUsedAt: Long,
    val metadata: Map<String, String> = emptyMap()
)
''')

write_file("app/src/main/java/com/example/voiceassistant/data/MemoryManager.kt", r'''package com.example.voiceassistant.data

import android.content.Context
import com.example.voiceassistant.commands.TextNormalizer
import com.example.voiceassistant.data.models.MemoryEntry
import com.example.voiceassistant.data.models.MemoryType
import com.example.voiceassistant.viewmodel.AppLanguage
import org.json.JSONArray
import org.json.JSONException
import org.json.JSONObject

/**
 * Long-term memory, stored only on this device (SharedPreferences, JSON like ChatHistoryManager).
 * It never talks to the network: facts come from local regex rules and explicit commands.
 *
 * The list is kept in RAM; the disk is read once and written (apply) only when something changes.
 */
class MemoryManager(context: Context) {

    private val prefs = context.applicationContext
        .getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    private val lock = Any()

    private val entries: MutableList<MemoryEntry> = load()

    /**
     * Adds a fact / preference. The text is tidied and cut to [MAX_FACT_CHARS]; a duplicate only refreshes
     * its lastUsedAt. With a [key] (e.g. "name") the new value replaces the older one with the same key.
     * Returns null when the text is blank.
     */
    fun addFact(text: String, type: MemoryType = MemoryType.FACT, key: String? = null): MemoryEntry? =
        synchronized(lock) {
            if (type == MemoryType.PROJECT) return@synchronized null
            val clean = tidy(text).take(MAX_FACT_CHARS).trim()
            if (clean.isEmpty()) return@synchronized null
            val now = System.currentTimeMillis()
            val norm = TextNormalizer.key(clean)

            if (key != null) {
                val old = entries.firstOrNull { it.metadata[META_KEY] == key }
                if (old != null) {
                    if (TextNormalizer.key(old.content) == norm) return@synchronized touch(old, now)
                    entries.remove(old)
                }
            }
            val same = entries.firstOrNull {
                it.type != MemoryType.PROJECT && TextNormalizer.key(it.content) == norm
            }
            if (same != null) return@synchronized touch(same, now)

            val entry = MemoryEntry(
                id = newId(now),
                type = type,
                content = clean,
                createdAt = now,
                lastUsedAt = now,
                metadata = if (key == null) emptyMap() else mapOf(META_KEY to key)
            )
            entries.add(entry)
            prune()
            save()
            entry
        }

    /**
     * Remembers a file the user works on. The same file (same Uri, or same name when there is no Uri)
     * is updated instead of duplicated: lastUsedAt moves forward and a non-blank [summary] becomes the last note.
     */
    fun addProject(name: String, uri: String?, summary: String = ""): MemoryEntry? =
        synchronized(lock) {
            val cleanName = tidy(name).take(MAX_NAME_CHARS)
            if (cleanName.isEmpty()) return@synchronized null
            val note = tidy(summary).take(MAX_FACT_CHARS)
            val now = System.currentTimeMillis()

            val existing = entries.firstOrNull {
                it.type == MemoryType.PROJECT && sameProject(it, cleanName, uri)
            }
            if (existing != null) {
                val meta = existing.metadata.toMutableMap()
                meta[META_FILE_NAME] = cleanName
                if (uri != null) meta[META_FILE_URI] = uri
                val updated = existing.copy(
                    content = if (note.isNotEmpty()) note else existing.content,
                    lastUsedAt = now,
                    metadata = meta
                )
                replace(updated)
                save()
                return@synchronized updated
            }

            val meta = mutableMapOf(META_FILE_NAME to cleanName, META_FIRST_OPENED to now.toString())
            if (uri != null) meta[META_FILE_URI] = uri
            val entry = MemoryEntry(newId(now), MemoryType.PROJECT, note, now, now, meta)
            entries.add(entry)
            prune()
            save()
            entry
        }

    /** Marks a project as just used (optionally with a new last note). */
    fun updateProjectLastUsed(id: Long, summary: String? = null): MemoryEntry? = synchronized(lock) {
        val project = entries.firstOrNull { it.id == id && it.type == MemoryType.PROJECT }
            ?: return@synchronized null
        val note = summary?.let { tidy(it).take(MAX_FACT_CHARS) }?.takeIf { it.isNotEmpty() }
        touch(project, System.currentTimeMillis(), note)
    }

    /** Facts and preferences, most recently used first. */
    fun getFacts(): List<MemoryEntry> = synchronized(lock) {
        entries.filter { it.type != MemoryType.PROJECT }.sortedByDescending { it.lastUsedAt }
    }

    /** Projects, most recently used first. */
    fun getProjects(): List<MemoryEntry> = synchronized(lock) {
        entries.filter { it.type == MemoryType.PROJECT }.sortedByDescending { it.lastUsedAt }
    }

    /** Removes one entry and returns it (null if the id is unknown). */
    fun remove(id: Long): MemoryEntry? = synchronized(lock) {
        val index = entries.indexOfFirst { it.id == id }
        if (index < 0) return@synchronized null
        val removed = entries.removeAt(index)
        save()
        removed
    }

    fun clearAll() {
        synchronized(lock) {
            if (entries.isEmpty()) return
            entries.clear()
            prefs.edit().remove(KEY_ENTRIES).apply()
        }
    }

    /** Fuzzy search used by "انسى ...": the entry sharing the most words with [query] (newest wins ties). */
    fun findBest(query: String): MemoryEntry? = synchronized(lock) {
        val words = TextNormalizer.key(query)
            .split(NON_WORD)
            .map { if (it.startsWith("ال") && it.length > 4) it.substring(2) else it }
            .filter { it.length >= 2 && it !in STOP_WORDS }
        if (words.isEmpty()) return@synchronized null

        var best: MemoryEntry? = null
        var bestScore = 0
        for (entry in entries.sortedByDescending { it.lastUsedAt }) {
            val haystack = TextNormalizer.key(entry.content + " " + (entry.metadata[META_FILE_NAME] ?: ""))
            val score = words.count { haystack.contains(it) }
            if (score > bestScore) {
                best = entry
                bestScore = score
            }
        }
        best
    }

    /**
     * Text appended to the system prompt. Hard caps keep the token cost small:
     * at most [MAX_PROMPT_FACTS] facts + [MAX_PROMPT_PROJECTS] projects, newest first, and
     * [MAX_PROMPT_CHARS] characters in total (the rest is cut). Projects contribute only the file name and
     * the last note, never the Uri or the file content. Returns "" (no header at all) when nothing is stored.
     */
    fun renderForPrompt(lang: AppLanguage): String = synchronized(lock) {
        if (entries.isEmpty()) return@synchronized ""

        // The name is already sent by AiChatService (userName), so it is not repeated here.
        val facts = entries
            .filter { it.type != MemoryType.PROJECT && it.metadata[META_KEY] != KEY_NAME }
            .sortedByDescending { it.lastUsedAt }
            .take(MAX_PROMPT_FACTS)
        val projects = entries
            .filter { it.type == MemoryType.PROJECT }
            .sortedByDescending { it.lastUsedAt }
            .take(MAX_PROMPT_PROJECTS)
        if (facts.isEmpty() && projects.isEmpty()) return@synchronized ""

        val sb = StringBuilder(lang.tr(HEADER_AR, HEADER_EN))
        var added = 0
        for (entry in (facts + projects).sortedByDescending { it.lastUsedAt }) {
            val line = "\n- " + lineFor(entry, lang)
            if (sb.length + line.length > MAX_PROMPT_CHARS) break
            sb.append(line)
            added++
        }
        if (added == 0) "" else sb.toString()
    }

    // ---- internals (always called while holding [lock]) ---------------------------------------

    private fun lineFor(entry: MemoryEntry, lang: AppLanguage): String {
        if (entry.type != MemoryType.PROJECT) return entry.content
        val name = entry.metadata[META_FILE_NAME] ?: entry.content
        val label = lang.tr("ملف عمل: ", "Working file: ") + name
        return if (entry.content.isNotEmpty() && entry.content != name) label + " — " + entry.content else label
    }

    private fun sameProject(project: MemoryEntry, name: String, uri: String?): Boolean =
        if (uri != null) project.metadata[META_FILE_URI] == uri
        else project.metadata[META_FILE_NAME].equals(name, ignoreCase = true)

    private fun tidy(text: String): String = text.replace(WHITESPACE, " ").trim()

    private fun newId(now: Long): Long {
        var id = now
        while (entries.any { it.id == id }) id++
        return id
    }

    private fun replace(updated: MemoryEntry) {
        val index = entries.indexOfFirst { it.id == updated.id }
        if (index >= 0) entries[index] = updated
    }

    private fun touch(entry: MemoryEntry, now: Long, content: String? = null): MemoryEntry {
        val updated = entry.copy(lastUsedAt = now, content = content ?: entry.content)
        replace(updated)
        save()
        return updated
    }

    /** Keeps the store small: oldest projects / facts beyond the limits are dropped. */
    private fun prune() {
        val projects = entries.filter { it.type == MemoryType.PROJECT }
        if (projects.size > MAX_PROJECTS) {
            projects.sortedBy { it.lastUsedAt }.take(projects.size - MAX_PROJECTS).forEach { entries.remove(it) }
        }
        val facts = entries.filter { it.type != MemoryType.PROJECT }
        if (facts.size > MAX_FACTS) {
            facts.sortedBy { it.lastUsedAt }.take(facts.size - MAX_FACTS).forEach { entries.remove(it) }
        }
    }

    private fun save() {
        val array = JSONArray()
        for (entry in entries) {
            val meta = JSONObject()
            for ((k, v) in entry.metadata) meta.put(k, v)
            array.put(
                JSONObject()
                    .put("id", entry.id)
                    .put("type", entry.type.name)
                    .put("content", entry.content)
                    .put("createdAt", entry.createdAt)
                    .put("lastUsedAt", entry.lastUsedAt)
                    .put("metadata", meta)
            )
        }
        prefs.edit().putString(KEY_ENTRIES, array.toString()).apply()
    }

    private fun load(): MutableList<MemoryEntry> {
        val list = ArrayList<MemoryEntry>()
        val array = try {
            JSONArray(prefs.getString(KEY_ENTRIES, null) ?: "[]")
        } catch (e: JSONException) {
            return list
        }
        for (i in 0 until array.length()) {
            val obj = array.optJSONObject(i) ?: continue
            val type = try {
                MemoryType.valueOf(obj.optString("type"))
            } catch (e: IllegalArgumentException) {
                continue
            }
            val content = obj.optString("content")
            if (content.isEmpty() && type != MemoryType.PROJECT) continue
            val meta = HashMap<String, String>()
            obj.optJSONObject("metadata")?.let { m ->
                val keys = m.keys()
                while (keys.hasNext()) {
                    val k = keys.next()
                    meta[k] = m.optString(k)
                }
            }
            list.add(
                MemoryEntry(
                    id = obj.optLong("id"),
                    type = type,
                    content = content,
                    createdAt = obj.optLong("createdAt"),
                    lastUsedAt = obj.optLong("lastUsedAt"),
                    metadata = meta
                )
            )
        }
        return list
    }

    companion object {
        // Metadata keys.
        const val META_KEY = "key"
        const val META_FILE_NAME = "fileName"
        const val META_FILE_URI = "fileUri"
        const val META_FIRST_OPENED = "firstOpened"

        /** [META_KEY] value of the fact that holds the user's name. */
        const val KEY_NAME = "name"

        // Limits (consumption hardening).
        const val MAX_FACT_CHARS = 200
        const val MAX_PROMPT_FACTS = 15
        const val MAX_PROMPT_PROJECTS = 3
        const val MAX_PROMPT_CHARS = 1500
        private const val MAX_NAME_CHARS = 120
        private const val MAX_FACTS = 100
        private const val MAX_PROJECTS = 10

        private const val PREFS_NAME = "assistant_memory"
        private const val KEY_ENTRIES = "entries"

        private const val HEADER_AR = "ما تعرفه عن المستخدم (استخدمه عند الحاجة فقط ولا تكرره عليه):"
        private const val HEADER_EN = "What you know about the user (use it only when relevant, don't recite it):"

        // Built once, not per message.
        private val WHITESPACE = Regex("""\s+""")
        private val NON_WORD = Regex("""[^\p{L}\p{N}]+""")
        private val STOP_WORDS = setOf(
            "اني", "انني", "انا", "ان", "ما", "عن", "في", "من", "هذا", "هذه", "ذلك", "كل", "شيء", "شي",
            "لي", "عني", "عنك", "the", "that", "my", "about", "me", "and", "is", "am", "are", "to", "of", "it"
        )
    }
}
''')

# 18. app/src/main/java/com/example/voiceassistant/speech/SpeechRecognizerManager.kt
write_file("app/src/main/java/com/example/voiceassistant/speech/SpeechRecognizerManager.kt", r'''package com.example.voiceassistant.speech

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer

/**
 * Thin wrapper around [SpeechRecognizer]. Must be used from the main thread.
 * A fresh recognizer is created for every session, which is the most robust approach.
 */
class SpeechRecognizerManager(context: Context) {

    interface Listener {
        fun onReady()
        fun onPartial(text: String)
        fun onResult(text: String)
        fun onError(code: Int)
        fun onEnd()
    }

    private val appContext = context.applicationContext
    private var recognizer: SpeechRecognizer? = null

    // After a network error, on-device recognition is preferred for a minute (then online is tried again).
    @Volatile
    private var offlineUntil = 0L
    private val mainHandler = android.os.Handler(android.os.Looper.getMainLooper())

    var listener: Listener? = null

    fun isAvailable(): Boolean = OfflineSpeech.isAvailable(appContext)

    fun start(languageTag: String) {
        destroy()
        val offline = System.currentTimeMillis() < offlineUntil || !OfflineSpeech.isOnline(appContext)
        val created = OfflineSpeech.createRecognizer(appContext, offline)
        created.setRecognitionListener(object : RecognitionListener {
            override fun onReadyForSpeech(params: Bundle?) {
                listener?.onReady()
            }

            override fun onBeginningOfSpeech() {}

            override fun onRmsChanged(rmsdB: Float) {}

            override fun onBufferReceived(buffer: ByteArray?) {}

            override fun onEndOfSpeech() {
                listener?.onEnd()
            }

            override fun onError(error: Int) {
                // Connection lost or no internet: retry right away with on-device recognition.
                if (OfflineSpeech.isNetworkError(error) && !offline) {
                    offlineUntil = System.currentTimeMillis() + 60_000L
                    mainHandler.post { start(languageTag) }
                    return
                }
                listener?.onError(error)
            }

            override fun onResults(results: Bundle?) {
                val text = results
                    ?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    ?.firstOrNull()
                    .orEmpty()
                listener?.onResult(text)
            }

            override fun onPartialResults(partialResults: Bundle?) {
                val text = partialResults
                    ?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                    ?.firstOrNull()
                    .orEmpty()
                if (text.isNotBlank()) listener?.onPartial(text)
            }

            override fun onEvent(eventType: Int, params: Bundle?) {}
        })
        recognizer = created

        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(
                RecognizerIntent.EXTRA_LANGUAGE_MODEL,
                RecognizerIntent.LANGUAGE_MODEL_FREE_FORM
            )
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, languageTag)
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, appContext.packageName)
            putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, offline)
        }
        created.startListening(intent)
    }

    /** Stops listening and lets the recognizer deliver what it heard so far. */
    fun stop() {
        recognizer?.stopListening()
    }

    /** Aborts the current session without delivering results. */
    fun cancel() {
        recognizer?.cancel()
    }

    fun destroy() {
        recognizer?.destroy()
        recognizer = null
    }
}
''')

# 18b. OfflineSpeech.kt: التعرف الصوتي بالاتصال وبدونه (مشترك بين الاستدعاء الصوتي والميكروفون)
write_file("app/src/main/java/com/example/voiceassistant/speech/OfflineSpeech.kt", r'''package com.example.voiceassistant.speech

import android.content.Context
import android.net.ConnectivityManager
import android.net.NetworkCapabilities
import android.os.Build
import android.speech.SpeechRecognizer

/**
 * Helpers so speech recognition works with or without internet:
 *  - online  -> the normal recognizer;
 *  - offline -> the on-device recognizer when the phone has one (Android 13+), otherwise the normal recognizer
 *    asked to prefer its downloaded offline language pack (EXTRA_PREFER_OFFLINE).
 * Offline recognition needs the Arabic / English offline speech packs installed on the phone
 * (Settings > Google > Settings for Google apps > Search, Assistant & Voice > Voice > Offline speech recognition).
 */
object OfflineSpeech {

    /** True when the phone has a validated internet connection right now. */
    fun isOnline(context: Context): Boolean = try {
        val cm = context.getSystemService(ConnectivityManager::class.java)
        val caps = cm?.getNetworkCapabilities(cm.activeNetwork)
        caps != null &&
            caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET) &&
            caps.hasCapability(NetworkCapabilities.NET_CAPABILITY_VALIDATED)
    } catch (e: Exception) {
        true
    }

    private fun onDeviceAvailable(context: Context): Boolean =
        Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            SpeechRecognizer.isOnDeviceRecognitionAvailable(context)

    /** Any usable recognizer (online or on-device). */
    fun isAvailable(context: Context): Boolean =
        SpeechRecognizer.isRecognitionAvailable(context) || onDeviceAvailable(context)

    fun createRecognizer(context: Context, offline: Boolean): SpeechRecognizer =
        if (offline && onDeviceAvailable(context)) {
            SpeechRecognizer.createOnDeviceSpeechRecognizer(context)
        } else {
            SpeechRecognizer.createSpeechRecognizer(context)
        }

    /** Errors that mean "no usable connection": the caller should retry offline. */
    fun isNetworkError(code: Int): Boolean =
        code == SpeechRecognizer.ERROR_NETWORK ||
            code == SpeechRecognizer.ERROR_NETWORK_TIMEOUT ||
            code == SpeechRecognizer.ERROR_SERVER ||
            code == 11 // ERROR_SERVER_DISCONNECTED (API 31+)
}
''')

# 19. app/src/main/java/com/example/voiceassistant/speech/TextToSpeechManager.kt
write_file("app/src/main/java/com/example/voiceassistant/speech/TextToSpeechManager.kt", r'''package com.example.voiceassistant.speech

import android.content.Context
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import java.util.Locale

class TextToSpeechManager(context: Context) {

    /** Called (possibly from a background thread) when speaking starts or stops. */
    var onSpeakingChanged: ((Boolean) -> Unit)? = null

    @Volatile
    private var ready = false
    @Volatile
    private var pendingSpeech: Pair<String, Locale>? = null
    private var counter = 0
    private var engine: TextToSpeech? = null

    private val progressListener = object : UtteranceProgressListener() {
        override fun onStart(utteranceId: String?) {
            onSpeakingChanged?.invoke(true)
        }

        override fun onDone(utteranceId: String?) {
            onSpeakingChanged?.invoke(false)
        }

        @Deprecated("Deprecated in Java")
        override fun onError(utteranceId: String?) {
            onSpeakingChanged?.invoke(false)
        }

        override fun onError(utteranceId: String?, errorCode: Int) {
            onSpeakingChanged?.invoke(false)
        }

        override fun onStop(utteranceId: String?, interrupted: Boolean) {
            onSpeakingChanged?.invoke(false)
        }
    }

    init {
        engine = TextToSpeech(context.applicationContext) { status ->
            if (status == TextToSpeech.SUCCESS) {
                engine?.setOnUtteranceProgressListener(progressListener)
                ready = true
                // A sentence requested before the engine was ready (e.g. the welcome greeting).
                pendingSpeech?.let { p ->
                    pendingSpeech = null
                    speak(p.first, p.second)
                }
            }
        }
    }

    /** @return true if speaking was started, false if TTS isn't ready or the language is unsupported. */
    fun speak(text: String, locale: Locale): Boolean {
        val tts = engine
        if (!ready || tts == null || text.isBlank()) return false
        val result = tts.setLanguage(locale)
        if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
            return false
        }
        // TextToSpeech rejects input longer than its maximum (usually 4000 characters).
        val safeText = text.take(TextToSpeech.getMaxSpeechInputLength() - 1)
        counter += 1
        return tts.speak(safeText, TextToSpeech.QUEUE_FLUSH, null, "va-$counter") == TextToSpeech.SUCCESS
    }

    /** Speaks now if the engine is ready, otherwise as soon as it becomes ready. */
    fun speakWhenReady(text: String, locale: Locale) {
        if (ready) {
            speak(text, locale)
        } else {
            pendingSpeech = text to locale
        }
    }

    fun stop() {
        pendingSpeech = null
        engine?.stop()
    }

    fun shutdown() {
        engine?.stop()
        engine?.shutdown()
        engine = null
        ready = false
    }
}
''')

# 20. app/src/main/java/com/example/voiceassistant/speech/AudioPermissionHandler.kt
write_file("app/src/main/java/com/example/voiceassistant/speech/AudioPermissionHandler.kt", r'''package com.example.voiceassistant.speech

import android.Manifest
import android.content.Context
import android.content.pm.PackageManager
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.ui.platform.LocalContext
import androidx.core.content.ContextCompat

object AudioPermissionHandler {
    const val PERMISSION = Manifest.permission.RECORD_AUDIO

    fun hasPermission(context: Context): Boolean =
        ContextCompat.checkSelfPermission(context, PERMISSION) == PackageManager.PERMISSION_GRANTED
}

/**
 * Returns a function that makes sure RECORD_AUDIO is granted.
 * If it already is, [onGranted] runs immediately; otherwise the system dialog is shown first.
 */
@Composable
fun rememberAudioPermissionRequest(
    onGranted: () -> Unit,
    onDenied: () -> Unit = {}
): () -> Unit {
    val context = LocalContext.current
    val currentOnGranted by rememberUpdatedState(onGranted)
    val currentOnDenied by rememberUpdatedState(onDenied)

    val launcher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) currentOnGranted() else currentOnDenied()
    }

    return remember(context, launcher) {
        {
            if (AudioPermissionHandler.hasPermission(context)) {
                currentOnGranted()
            } else {
                launcher.launch(AudioPermissionHandler.PERMISSION)
            }
        }
    }
}
''')

# 21. app/src/main/java/com/example/voiceassistant/viewmodel/MainUiState.kt
write_file("app/src/main/java/com/example/voiceassistant/viewmodel/MainUiState.kt", r'''package com.example.voiceassistant.viewmodel

import com.example.voiceassistant.data.models.MemoryEntry
import com.example.voiceassistant.data.models.Message
import java.util.Locale

enum class AppLanguage(val tag: String, val locale: Locale, val label: String) {
    ARABIC("ar-SA", Locale.forLanguageTag("ar"), "العربية"),
    ENGLISH("en-US", Locale.US, "English");

    /** Picks the Arabic or English variant of a string. */
    fun tr(ar: String, en: String): String = if (this == ARABIC) ar else en

    companion object {
        /** Arabic if the text contains Arabic letters, English otherwise. */
        fun detect(text: String): AppLanguage =
            if (text.any { it in '\u0600'..'\u06FF' }) ARABIC else ENGLISH
    }
}

enum class AssistantStatus { IDLE, LISTENING, PROCESSING, SPEAKING, ERROR }

data class MainUiState(
    val messages: List<Message> = emptyList(),
    val status: AssistantStatus = AssistantStatus.IDLE,
    val partialText: String = "",
    val language: AppLanguage = AppLanguage.ARABIC,
    val errorMessage: String? = null,
    /** A runtime permission the UI should request right now (null = none). */
    val pendingPermission: String? = null,
    val isAccessibilityEnabled: Boolean = false,
    /** Continuous conversation: listen again automatically after the assistant finishes speaking. */
    val handsFree: Boolean = true,
    /** Name of the code file being read / edited right now (null = none). */
    val workingFileName: String? = null,
    /** Facts and preferences the assistant remembers (newest first). */
    val memories: List<MemoryEntry> = emptyList(),
    /** Projects (code files) the user worked on, newest first. */
    val recentProjects: List<MemoryEntry> = emptyList()
)
''')

# 22. app/src/main/java/com/example/voiceassistant/viewmodel/MainViewModel.kt
write_file("app/src/main/java/com/example/voiceassistant/viewmodel/MainViewModel.kt", r'''package com.example.voiceassistant.viewmodel

import android.app.Application
import android.content.pm.ApplicationInfo
import android.content.pm.PackageManager
import android.os.Build
import android.speech.SpeechRecognizer
import java.io.File
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.example.voiceassistant.VoiceAssistantApp
import com.example.voiceassistant.commands.CommandParser
import com.example.voiceassistant.commands.CommandResult
import com.example.voiceassistant.commands.IntentCommandHandler
import com.example.voiceassistant.commands.MemoryAction
import com.example.voiceassistant.commands.ParsedCommand
import com.example.voiceassistant.commands.SecurityAction
import com.example.voiceassistant.data.AiChatService
import com.example.voiceassistant.data.models.CodeBlock
import com.example.voiceassistant.data.AiError
import com.example.voiceassistant.data.AiResult
import com.example.voiceassistant.data.ImageResult
import com.example.voiceassistant.data.ChatHistoryManager
import com.example.voiceassistant.data.MemoryManager
import com.example.voiceassistant.data.UserProfileManager
import com.example.voiceassistant.data.models.MemoryEntry
import com.example.voiceassistant.data.models.MemoryType
import com.example.voiceassistant.data.SavedSession
import com.example.voiceassistant.data.ConversationRepository
import com.example.voiceassistant.service.ProactiveMessages
import com.example.voiceassistant.service.ProactiveScheduler
import com.example.voiceassistant.service.SecurityMonitorService
import com.example.voiceassistant.service.WakeWordService
import com.example.voiceassistant.service.VoiceAccessibilityService
import com.example.voiceassistant.speech.SpeechRecognizerManager
import com.example.voiceassistant.speech.TextToSpeechManager
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.withContext
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.getAndUpdate
import kotlinx.coroutines.flow.update
import kotlinx.coroutines.launch

class MainViewModel(application: Application) : AndroidViewModel(application) {

    private companion object {
        /** Delay between the end of the assistant's speech and the next listening session. */
        const val RESTART_DELAY_MS = 1000L

        /** After this many silent listening sessions in a row the hands-free loop stops. */
        const val MAX_SILENT_STRIKES = 3
    }

    private val repository: ConversationRepository =
        (application as VoiceAssistantApp).conversationRepository
    private val speech = SpeechRecognizerManager(application)
    private val tts = TextToSpeechManager(application)
    private val parser = CommandParser()
    private val handler = IntentCommandHandler(application)
    private val memoryManager = MemoryManager(application)
    private val ai = AiChatService(memoryManager)
    private val historyManager = ChatHistoryManager(application)
    private val userProfileManager = UserProfileManager(application)

    private val _savedSessions = MutableStateFlow(historyManager.getAllSessions())
    val savedSessions: StateFlow<List<SavedSession>> = _savedSessions.asStateFlow()

    /** Id of the saved session currently shown on screen (null = a fresh, never-saved chat). */
    private var currentSessionId: Long? = null

    /** True while the security monitor service is running. */
    val securityEnabled: StateFlow<Boolean> = SecurityMonitorService.running

    /** The wake-word switch (saved in SharedPreferences, loaded when the app starts). */
    val wakeWordEnabled: StateFlow<Boolean> = WakeWordService.enabled

    init {
        // Opened in the foreground: (re)start the wake-word service if it should be on but isn't running.
        WakeWordService.startIfEnabled(application)
    }

    private val _uiState = MutableStateFlow(
        MainUiState(
            isAccessibilityEnabled = VoiceAccessibilityService.isRunning,
            language = ProactiveScheduler.language(application),
            memories = memoryManager.getFacts(),
            recentProjects = memoryManager.getProjects()
        )
    )
    val uiState: StateFlow<MainUiState> = _uiState.asStateFlow()

    /** Emitted when the UI should move the app to the background (so on-screen actions hit other apps). */
    private val _backgroundRequests = MutableSharedFlow<Unit>(extraBufferCapacity = 1)
    val backgroundRequests: SharedFlow<Unit> = _backgroundRequests.asSharedFlow()

    private var pendingText: String? = null
    private var pendingSpeak = true

    // True right after the greeting asked "what is your name?" and nothing was answered yet.
    @Volatile
    private var awaitingName = false

    // Continuous conversation state
    @Volatile
    private var conversationActive = false

    @Volatile
    private var isForeground = false
    private var silentStrikes = 0

    @Volatile
    private var restartJob: Job? = null

    init {
        viewModelScope.launch {
            repository.messages.collect { list ->
                _uiState.update { it.copy(messages = list) }
            }
        }

        tts.onSpeakingChanged = { speaking ->
            val previous = _uiState.getAndUpdate { s ->
                when {
                    speaking -> s.copy(status = AssistantStatus.SPEAKING)
                    s.status == AssistantStatus.SPEAKING -> s.copy(status = AssistantStatus.IDLE)
                    else -> s
                }
            }
            // The assistant just finished talking -> maybe listen again in a second.
            if (!speaking && previous.status == AssistantStatus.SPEAKING) {
                scheduleAutoRestart()
            }
        }

        speech.listener = object : SpeechRecognizerManager.Listener {
            override fun onReady() {
                _uiState.update { it.copy(status = AssistantStatus.LISTENING) }
            }

            override fun onPartial(text: String) {
                _uiState.update { it.copy(partialText = text) }
            }

            override fun onResult(text: String) {
                handleUtterance(text)
            }

            override fun onError(code: Int) {
                handleRecognizerError(code)
            }

            override fun onEnd() {
                _uiState.update {
                    if (it.status == AssistantStatus.LISTENING) {
                        it.copy(status = AssistantStatus.PROCESSING)
                    } else it
                }
            }
        }

        if (repository.messages.value.isEmpty()) {
            repository.addAssistantMessage(
                _uiState.value.language.tr(
                    "مرحباً! اضغط على الميكروفون وتحدث. جرّب: «اتصل بأحمد» أو «شغل الواي فاي» أو اسألني أي سؤال.",
                    "Hi! Tap the mic and speak. Try: \"call Ahmed\", \"turn on Wi-Fi\" or just ask me anything."
                )
            )
        }
    }

    init {
        // If the profile lost the name but the memory still has it, restore it so the user is never asked again.
        if (userProfileManager.userName == null) {
            memoryManager.getFacts()
                .firstOrNull { it.metadata[MemoryManager.META_KEY] == MemoryManager.KEY_NAME }
                ?.content?.substringAfter(':')?.trim()
                ?.takeIf { it.isNotEmpty() }
                ?.let { userProfileManager.userName = it }
        }
        // The saved name (if any) goes to the AI before anything else happens.
        userProfileManager.userName?.let { ai.setUserName(it) }
        greetOnStart()
    }

    /** Spoken welcome when the app opens: good morning / good evening + "how are you?". */
    private fun greetOnStart() {
        val lang = _uiState.value.language
        val greeting = ProactiveMessages.greeting(lang, userName = userProfileManager.userName)
        // Only when the greeting asks for the name, the next short answer is taken as the name.
        awaitingName = userProfileManager.userName == null
        // Fresh conversation: also show the greeting in the chat.
        if (repository.messages.value.size <= 1) {
            repository.addAssistantMessage(greeting)
        }
        tts.speakWhenReady(greeting, lang.locale)
    }

    // ------------------------------------------------------------------ UI actions

    fun toggleListening() {
        when (_uiState.value.status) {
            AssistantStatus.LISTENING -> speech.stop()
            AssistantStatus.SPEAKING -> {
                // Tapping while the assistant talks interrupts it and ends the hands-free loop.
                conversationActive = false
                restartJob?.cancel()
                tts.stop()
                _uiState.update { it.copy(status = AssistantStatus.IDLE) }
            }
            AssistantStatus.PROCESSING -> Unit
            else -> {
                conversationActive = true
                silentStrikes = 0
                startListening()
            }
        }
    }

    /** Called when the app is opened as the default assistant (after the mic permission is granted). */
    fun startHandsFree() {
        conversationActive = true
        silentStrikes = 0
        val status = _uiState.value.status
        if (status == AssistantStatus.IDLE || status == AssistantStatus.ERROR) {
            startListening()
        }
    }

    fun setHandsFree(enabled: Boolean) {
        _uiState.update { it.copy(handsFree = enabled) }
        if (!enabled) {
            conversationActive = false
            restartJob?.cancel()
        }
    }

    fun setForeground(foreground: Boolean) {
        isForeground = foreground
        if (!foreground) {
            restartJob?.cancel()
            // Android blocks microphone capture for background apps, so don't keep listening.
            if (_uiState.value.status == AssistantStatus.LISTENING) {
                speech.cancel()
                _uiState.update { it.copy(status = AssistantStatus.IDLE, partialText = "") }
            }
        }
    }

    fun setLanguage(language: AppLanguage) {
        _uiState.update { it.copy(language = language) }
        // Background check-ins use the same language.
        ProactiveScheduler.saveLanguage(getApplication<Application>(), language)
    }

    fun clearConversation() {
        conversationActive = false
        restartJob?.cancel()
        tts.stop()
        speech.cancel()
        ai.clearHistory()
        ai.workingFile = null
        repository.clear()
        currentSessionId = null
        _uiState.update { it.copy(status = AssistantStatus.IDLE, partialText = "", errorMessage = null, workingFileName = null) }
    }

    /** Saves the conversation on screen (only if the user wrote something) and refreshes the list. */
    private fun saveCurrentSession() {
        val messages = repository.messages.value
        if (messages.none { it.isUser }) return
        val title = sessionTitle(messages)
        val id = currentSessionId ?: historyManager.newSessionId()
        currentSessionId = id
        // Disk work (JSON + file write) never runs on the main thread.
        viewModelScope.launch(Dispatchers.IO) {
            historyManager.saveSession(title, messages, id)
            _savedSessions.value = historyManager.getAllSessions()
        }
    }

    private fun sessionTitle(messages: List<com.example.voiceassistant.data.models.Message>): String {
        val source = messages.firstOrNull { it.isUser && it.text.isNotBlank() }
            ?: messages.firstOrNull { it.text.isNotBlank() }
        val line = source?.text?.lineSequence()?.firstOrNull { it.isNotBlank() }?.trim().orEmpty()
        return when {
            line.isEmpty() -> _uiState.value.language.tr("محادثة جديدة", "New chat")
            line.length > 40 -> line.take(40) + "…"
            else -> line
        }
    }

    /** Stops speech / listening and resets the AI context so chats never mix. */
    private fun resetForOtherChat() {
        conversationActive = false
        restartJob?.cancel()
        tts.stop()
        speech.cancel()
        ai.clearHistory()
        ai.workingFile = null
        _uiState.update { it.copy(status = AssistantStatus.IDLE, partialText = "", errorMessage = null, workingFileName = null) }
    }

    fun startNewChat() {
        saveCurrentSession()
        resetForOtherChat()
        repository.clear()
        currentSessionId = null
    }

    fun loadSession(id: Long) {
        if (id == currentSessionId || _savedSessions.value.none { it.id == id }) return
        saveCurrentSession()
        resetForOtherChat()
        currentSessionId = id
        viewModelScope.launch {
            // Only this one conversation is read from disk (off the main thread), never the whole history.
            val messages = withContext(Dispatchers.IO) { historyManager.loadMessages(id) }
            if (currentSessionId == id) repository.setMessages(messages)
        }
    }

    fun deleteSession(id: Long) {
        if (currentSessionId == id) currentSessionId = null
        _savedSessions.update { list -> list.filter { it.id != id } }   // the drawer updates instantly
        viewModelScope.launch(Dispatchers.IO) { historyManager.deleteSession(id) }
    }

    fun toggleWakeWord(enabled: Boolean) {
        val app = getApplication<Application>()
        if (!enabled) {
            WakeWordService.setEnabled(app, false)
            WakeWordService.stop(app)
            return
        }
        if (!WakeWordService.hasMicPermission(app)) {
            onMicPermissionDenied()
            return
        }
        try {
            WakeWordService.start(app)
            WakeWordService.setEnabled(app, true)
        } catch (e: Exception) {
            WakeWordService.setEnabled(app, false)
            setError(
                _uiState.value.language.tr(
                    "تعذّر تشغيل الاستدعاء الصوتي.",
                    "Couldn't turn the wake word on."
                )
            )
        }
    }

    fun toggleSecurityMonitoring(enabled: Boolean) {
        if (!setSecurityMonitoring(enabled)) {
            setError(
                _uiState.value.language.tr("تعذّر تشغيل الحماية.", "Couldn't turn protection on.")
            )
        }
    }

    fun scanInstalledApps() {
        viewModelScope.launch { runAppScan(_uiState.value.language, speak = true) }
    }

    private fun setSecurityMonitoring(enabled: Boolean): Boolean = try {
        val app = getApplication<Application>()
        if (enabled) SecurityMonitorService.start(app) else SecurityMonitorService.stop(app)
        true
    } catch (e: Exception) {
        false
    }

    private suspend fun handleSecurityCommand(
        command: ParsedCommand.Security,
        lang: AppLanguage,
        speak: Boolean
    ) {
        when (command.action) {
            SecurityAction.ENABLE -> {
                val started = setSecurityMonitoring(true)
                reply(
                    if (started) {
                        lang.tr("تم تشغيل الحماية.", "Protection is on.")
                    } else {
                        lang.tr("تعذّر تشغيل الحماية.", "Couldn't turn protection on.")
                    },
                    lang,
                    speak = speak
                )
            }
            SecurityAction.DISABLE -> {
                setSecurityMonitoring(false)
                reply(lang.tr("تم إيقاف الحماية.", "Protection is off."), lang, speak = speak)
            }
            SecurityAction.SCAN_APPS -> runAppScan(lang, speak)
        }
    }

    private suspend fun runAppScan(lang: AppLanguage, speak: Boolean) {
        val suspicious = withContext(Dispatchers.IO) { findSuspiciousApps() }
        val message = if (suspicious.isEmpty()) {
            lang.tr(
                "تم فحص التطبيقات. لم يتم اكتشاف أي تطبيق مشبوه.",
                "Apps scanned. No suspicious apps were found."
            )
        } else {
            val names = suspicious.take(3).joinToString(lang.tr("، ", ", "))
            lang.tr(
                "تم فحص التطبيقات. تم اكتشاف ${suspicious.size} تطبيق مشبوه: $names",
                "Apps scanned. Found ${suspicious.size} suspicious app(s): $names"
            )
        }
        reply(message, lang, speak = speak)
    }

    /** Installed (non-system) apps that ask for INTERNET together with SMS / call-log access. */
    private fun findSuspiciousApps(): List<String> {
        val app = getApplication<Application>()
        val pm = app.packageManager
        val risky = setOf(
            "android.permission.READ_SMS",
            "android.permission.RECEIVE_SMS",
            "android.permission.SEND_SMS",
            "android.permission.READ_CALL_LOG"
        )
        val packages = try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
                pm.getInstalledPackages(
                    PackageManager.PackageInfoFlags.of(PackageManager.GET_PERMISSIONS.toLong())
                )
            } else {
                @Suppress("DEPRECATION")
                pm.getInstalledPackages(PackageManager.GET_PERMISSIONS)
            }
        } catch (e: Exception) {
            emptyList()
        }

        val found = mutableListOf<String>()
        for (info in packages) {
            val appInfo = info.applicationInfo ?: continue
            if ((appInfo.flags and ApplicationInfo.FLAG_SYSTEM) != 0) continue
            if (info.packageName == app.packageName) continue
            val permissions = info.requestedPermissions?.toSet() ?: continue
            if ("android.permission.INTERNET" in permissions && permissions.any { it in risky }) {
                found.add(pm.getApplicationLabel(appInfo).toString())
            }
        }
        return found
    }

    fun refreshAccessibilityStatus() {
        _uiState.update { it.copy(isAccessibilityEnabled = VoiceAccessibilityService.isRunning) }
    }

    fun onMicPermissionDenied() {
        conversationActive = false
        val lang = _uiState.value.language
        setError(lang.tr("أحتاج إذن الميكروفون لكي أسمعك.", "I need the microphone permission to hear you."))
    }

    fun onPermissionResult(granted: Boolean) {
        val text = pendingText
        pendingText = null
        val speak = pendingSpeak
        pendingSpeak = true
        _uiState.update { it.copy(pendingPermission = null) }
        val lang = text?.let { AppLanguage.detect(it) } ?: _uiState.value.language
        if (granted && text != null) {
            process(text, speak)
        } else {
            reply(
                lang.tr(
                    "لا أستطيع تنفيذ الأمر بدون هذا الإذن.",
                    "I can't do that without the permission."
                ),
                lang,
                speak = speak
            )
        }
    }

    // ------------------------------------------------------------------ internals

    private fun startListening() {
        restartJob?.cancel()
        val lang = _uiState.value.language
        if (!speech.isAvailable()) {
            conversationActive = false
            setError(
                lang.tr(
                    "خدمة التعرف على الصوت غير متوفرة على هذا الجهاز.",
                    "Speech recognition isn't available on this device."
                )
            )
            return
        }
        tts.stop()
        _uiState.update {
            it.copy(status = AssistantStatus.LISTENING, partialText = "", errorMessage = null)
        }
        speech.start(lang.tag)
    }

    /**
     * Hands-free loop: one second after the assistant stops speaking (or after a silent
     * session) the microphone is started again, as long as the loop is still active.
     */
    private fun scheduleAutoRestart() {
        if (!conversationActive || !_uiState.value.handsFree) return
        restartJob?.cancel()
        restartJob = viewModelScope.launch {
            delay(RESTART_DELAY_MS)
            val s = _uiState.value
            if (conversationActive &&
                s.handsFree &&
                isForeground &&
                s.status == AssistantStatus.IDLE &&
                s.pendingPermission == null
            ) {
                startListening()
            }
        }
    }

    private fun handleUtterance(text: String) {
        val clean = text.trim()
        if (clean.isEmpty()) {
            onSilence(_uiState.value.language)
            return
        }
        silentStrikes = 0
        repository.addUserMessage(clean)
        // The user spoke -> the assistant answers out loud.
        process(clean, speak = true)
    }

    /** Nothing was heard. Keep the loop going a few times, then give up politely. */
    private fun onSilence(lang: AppLanguage) {
        val s = _uiState.value
        if (conversationActive && s.handsFree) {
            silentStrikes++
            if (silentStrikes < MAX_SILENT_STRIKES) {
                _uiState.update { it.copy(status = AssistantStatus.IDLE, partialText = "") }
                scheduleAutoRestart()
                return
            }
        }
        conversationActive = false
        silentStrikes = 0
        setError(lang.tr("لم أسمعك جيداً، حاول مرة أخرى.", "I didn't catch that, please try again."))
    }

    private fun process(text: String, speak: Boolean = true) {
        viewModelScope.launch {
            _uiState.update { it.copy(status = AssistantStatus.PROCESSING, partialText = "") }
            val lang = AppLanguage.detect(text)
            // Right after the assistant asked "what's your name?", a short plain answer ("أحمد") is the name.
            if (awaitingName) {
                awaitingName = false
                parser.bareName(text)?.let { name ->
                    saveUserName(name, lang, speak)
                    return@launch
                }
            }
            extractBaseFacts(text)
            val parsed = parser.parse(text)

            // Not a phone command -> have a normal conversation with the AI.
            if (parsed is ParsedCommand.Unknown) {
                if (isImageRequest(text)) generateImage(text, lang, speak) else askAi(text, lang, speak)
                return@launch
            }

            if (parsed is ParsedCommand.SetName) {
                saveUserName(parsed.name, lang, speak)
                return@launch
            }

            if (parsed is ParsedCommand.Memory) {
                handleMemoryCommand(parsed, lang, speak)
                return@launch
            }

            if (parsed is ParsedCommand.Security) {
                handleSecurityCommand(parsed, lang, speak)
                return@launch
            }

            // Screen actions must hit the *other* app, so step aside first.
            if (parsed is ParsedCommand.Accessibility &&
                parsed.action.targetsOtherApp &&
                VoiceAccessibilityService.isRunning
            ) {
                _backgroundRequests.tryEmit(Unit)
                delay(700)
            }

            when (val result = handler.execute(parsed, lang)) {
                is CommandResult.Success -> reply(result.message, lang, speak = speak)
                is CommandResult.Failure -> reply(result.message, lang, speak = speak)
                is CommandResult.NeedsPermission -> {
                    pendingText = text
                    pendingSpeak = speak
                    _uiState.update { it.copy(pendingPermission = result.permission) }
                    reply(result.message, lang, speak = speak)
                }
            }
        }
    }

    // ---- long-term memory ---------------------------------------------------------------------

    /** Pushes the stored memory into the UI state (the memory sheet reads it). */
    private fun refreshMemoryState() {
        _uiState.update {
            it.copy(memories = memoryManager.getFacts(), recentProjects = memoryManager.getProjects())
        }
    }

    /** Local regex only (no AI call): saves "أنا أحب القهوة", "أنا أعمل مهندساً", "أسكن في جدة" ... */
    private fun extractBaseFacts(text: String) {
        val fact = parser.extractFact(text) ?: return
        memoryManager.addFact(fact.text, if (fact.isPreference) MemoryType.PREFERENCE else MemoryType.FACT)
        refreshMemoryState()
    }

    /** The name is saved as a keyed fact, so a new name replaces the old one. */
    private fun rememberName(name: String) {
        memoryManager.addFact(
            "${_uiState.value.language.tr("الاسم", "Name")}: $name",
            MemoryType.FACT,
            key = MemoryManager.KEY_NAME
        )
        refreshMemoryState()
    }

    /** Saves the name permanently (UserProfileManager + memory + AI) and thanks the user. */
    private fun saveUserName(name: String, lang: AppLanguage, speak: Boolean) {
        userProfileManager.userName = name
        ai.setUserName(name)
        rememberName(name)
        reply(
            lang.tr(
                "شكراً لتعريفك بنفسك يا $name، سعيد جداً بمعرفتك!",
                "Thank you for introducing yourself, $name. I'm very happy to meet you!"
            ),
            lang,
            speak = speak
        )
    }

    /** A removed "name" fact also clears the saved name. */
    private fun onMemoryRemoved(entry: MemoryEntry) {
        if (entry.metadata[MemoryManager.META_KEY] == MemoryManager.KEY_NAME) {
            userProfileManager.userName = null
            ai.setUserName("")
        }
    }

    /** Delete button of the memory sheet. */
    fun removeMemory(id: Long) {
        memoryManager.remove(id)?.let { onMemoryRemoved(it) }
        refreshMemoryState()
    }

    /** "Apply to file" succeeded: the project moves to the top and keeps the AI's note about the edit. */
    fun onFileApplied(fileName: String, uri: String?, summary: String) {
        memoryManager.addProject(fileName, uri, summary)
        refreshMemoryState()
    }

    private fun memoryLabel(entry: MemoryEntry): String =
        if (entry.type == MemoryType.PROJECT) entry.metadata[MemoryManager.META_FILE_NAME] ?: entry.content
        else entry.content

    private fun projectLine(entry: MemoryEntry): String {
        val name = memoryLabel(entry)
        return if (entry.content.isNotBlank() && entry.content != name) "$name — ${entry.content}" else name
    }

    private fun describeMemory(lang: AppLanguage): String {
        val facts = memoryManager.getFacts().take(MemoryManager.MAX_PROMPT_FACTS)
        val projects = memoryManager.getProjects().take(MemoryManager.MAX_PROMPT_PROJECTS)
        if (facts.isEmpty() && projects.isEmpty()) {
            return lang.tr(
                "لا أتذكر شيئاً عنك بعد. جرّب أن تقول: تذكر أنني أحب القهوة.",
                "I don't remember anything about you yet. Try: remember that I like coffee."
            )
        }
        val sb = StringBuilder()
        if (facts.isNotEmpty()) {
            sb.append(lang.tr("هذا ما أتذكره عنك:", "Here is what I remember about you:"))
            facts.forEach { sb.append('\n').append(it.content) }
        }
        if (projects.isNotEmpty()) {
            if (sb.isNotEmpty()) sb.append("\n\n")
            sb.append(lang.tr("آخر مشاريعك:", "Your recent projects:"))
            projects.forEach { sb.append('\n').append(projectLine(it)) }
        }
        return sb.toString()
    }

    private suspend fun handleMemoryCommand(command: ParsedCommand.Memory, lang: AppLanguage, speak: Boolean) {
        when (command.action) {
            MemoryAction.ADD -> {
                val saved = memoryManager.addFact(command.argument.orEmpty())
                refreshMemoryState()
                reply(
                    if (saved != null) lang.tr("تمام، سأتذكر ذلك.", "Got it, I'll remember that.")
                    else lang.tr("لم أفهم ما الذي أتذكره.", "I didn't catch what to remember."),
                    lang,
                    speak = speak
                )
            }
            MemoryAction.LIST -> reply(describeMemory(lang), lang, speak = speak)
            MemoryAction.FORGET -> {
                val target = memoryManager.findBest(command.argument.orEmpty())
                val removed = target?.let { memoryManager.remove(it.id) }
                if (removed != null) onMemoryRemoved(removed)
                refreshMemoryState()
                reply(
                    if (removed != null) {
                        lang.tr("حسناً، نسيت: ${memoryLabel(removed)}", "Okay, I forgot: ${memoryLabel(removed)}")
                    } else {
                        lang.tr("لم أجد شيئاً مطابقاً في ذاكرتي.", "I couldn't find anything matching in my memory.")
                    },
                    lang,
                    speak = speak
                )
            }
            MemoryAction.RETURN_TO_PROJECT -> returnToProject(lang, speak)
        }
    }

    /** Reads a remembered file back through its saved Uri (null if the file or the access is gone). */
    private fun readProjectFile(name: String, uri: String): com.example.voiceassistant.data.WorkingFile? = try {
        val bytes = getApplication<Application>().contentResolver
            .openInputStream(android.net.Uri.parse(uri))?.use { it.readBytes() }
        if (bytes == null || bytes.size > maxWorkingFileBytes) {
            null
        } else {
            decodeUtf8(bytes)?.let { com.example.voiceassistant.data.WorkingFile(name, uri, it) }
        }
    } catch (e: Exception) {
        null
    }

    /** Lists the last 3 projects with their last note and re-opens the newest one as the working file. */
    private suspend fun returnToProject(lang: AppLanguage, speak: Boolean) {
        val projects = memoryManager.getProjects().take(MemoryManager.MAX_PROMPT_PROJECTS)
        if (projects.isEmpty()) {
            reply(
                lang.tr(
                    "لا توجد مشاريع محفوظة بعد. أرفق ملف كود وسأتذكره.",
                    "No saved projects yet. Attach a code file and I'll remember it."
                ),
                lang,
                speak = speak
            )
            return
        }
        val latest = projects.first()
        val name = memoryLabel(latest)
        val uri = latest.metadata[MemoryManager.META_FILE_URI]
        val file = if (uri != null) withContext(Dispatchers.IO) { readProjectFile(name, uri) } else null

        val sb = StringBuilder()
        if (file != null) {
            ai.workingFile = file
            _uiState.update { it.copy(workingFileName = file.name) }
            memoryManager.updateProjectLastUsed(latest.id)
            refreshMemoryState()
            sb.append(lang.tr("فتحت مشروعك السابق: $name", "Opened your previous project: $name"))
        } else {
            sb.append(
                lang.tr(
                    "مشروعك السابق هو $name، لكن تعذّر فتح الملف. أرفقه مرة أخرى.",
                    "Your previous project is $name, but I couldn't open the file. Please attach it again."
                )
            )
        }
        sb.append("\n\n").append(lang.tr("آخر مشاريعك:", "Your recent projects:"))
        projects.forEach { sb.append('\n').append(projectLine(it)) }
        reply(sb.toString(), lang, speak = speak)
    }

    private suspend fun askAi(text: String, lang: AppLanguage, speak: Boolean = true) {
        when (val result = ai.ask(text, lang)) {
            is AiResult.Success -> reply(result.text, lang, result.code, speak = speak)
            is AiResult.Error -> {
                // Configuration problems won't fix themselves, so stop the hands-free loop.
                if (result.kind == AiError.NOT_CONFIGURED || result.kind == AiError.BAD_KEY) {
                    conversationActive = false
                }
                replyAiError(result.kind, result.detail, lang, speak)
            }
        }
    }

    /** True when the user asks for a picture ("ارسم لي ...", "generate an image of ..."). */
    private fun isImageRequest(text: String): Boolean {
        val t = text.lowercase()
        // Code / file requests that merely mention a picture stay normal AI answers.
        val codeWords = Regex("(html|css|javascript|java|kotlin|python|setup|script|code|كود|أكواد|اكواد|برمجة|سكربت|صفحة|موقع|ملف|تطبيق)")
        if (codeWords.containsMatchIn(t)) return false
        val arabic = Regex("(ارسم|ارسمي|صمم|ولد|أنشئ|انشئ|اصنع|اعمل|أنتج|انتج|سوي|توليد|رسم).{0,30}(صورة|صوره|صور|لوحة|رسمة|رسمه|شعار|لوجو)")
        val english = Regex("(generate|create|draw|make|paint|design|produce).{0,30}(image|picture|photo|drawing|illustration|logo|painting)")
        val drawStart = Regex("^\\s*(ارسم|ارسمي|draw)\\s")
        return arabic.containsMatchIn(t) || english.containsMatchIn(t) || drawStart.containsMatchIn(t)
    }

    private suspend fun generateImage(prompt: String, lang: AppLanguage, speak: Boolean = true) {
        when (val result = ai.generateImage(prompt)) {
            is ImageResult.Success -> {
                val path = withContext(Dispatchers.IO) { saveImage(result.bytes) }
                if (path == null) {
                    reply(aiErrorMessage(AiError.OTHER, lang), lang, speak = speak)
                } else {
                    reply(lang.tr("تفضل، هذه هي الصورة.", "Here is your image."), lang, imagePath = path, speak = speak)
                }
            }
            is ImageResult.Error -> {
                if (result.kind == AiError.NOT_CONFIGURED || result.kind == AiError.BAD_KEY) {
                    conversationActive = false
                }
                replyAiError(result.kind, result.detail, lang, speak)
            }
        }
    }

    /** Speaks the friendly message and also prints the technical detail (not spoken) so the real cause is visible. */
    private fun replyAiError(kind: AiError, detail: String, lang: AppLanguage, speak: Boolean = true) {
        reply(aiErrorMessage(kind, lang), lang, speak = speak)
        if (detail.isNotBlank()) repository.addAssistantMessage("[$detail]")
    }

    private fun saveImage(bytes: ByteArray): String? = try {
        val dir = File(getApplication<Application>().filesDir, "images").apply { mkdirs() }
        val file = File(dir, "img_${System.currentTimeMillis()}.png")
        file.writeBytes(bytes)
        file.absolutePath
    } catch (e: Exception) {
        null
    }

    private fun aiErrorMessage(kind: AiError, lang: AppLanguage): String = when (kind) {
        AiError.NOT_CONFIGURED -> lang.tr(
            "لم يتم ضبط مفتاح الذكاء الاصطناعي. افتح القائمة الجانبية ثم «نماذج الذكاء الاصطناعي» وأدخل مفتاح النموذج المحدد.",
            "The AI key isn't set. Open the side menu, then \"AI models\", and enter the key of the selected model."
        )
        AiError.BAD_KEY -> lang.tr(
            "مفتاح الذكاء الاصطناعي غير صالح.",
            "The AI key is not valid."
        )
        AiError.RATE_LIMIT -> lang.tr(
            "تجاوزت حد الطلبات، حاول بعد قليل.",
            "Too many requests, please try again shortly."
        )
        AiError.NETWORK -> lang.tr(
            "تعذّر الاتصال بالإنترنت.",
            "I couldn't reach the internet."
        )
        AiError.EMPTY -> lang.tr(
            "لم أستطع الإجابة على ذلك.",
            "I couldn't come up with an answer."
        )
        AiError.OTHER -> lang.tr(
            "حدث خطأ أثناء الاتصال بالذكاء الاصطناعي.",
            "Something went wrong while contacting the AI."
        )
    }

    private fun reply(
        message: String,
        lang: AppLanguage,
        code: List<CodeBlock> = emptyList(),
        imagePath: String? = null,
        speak: Boolean = true
    ) {
        repository.addAssistantMessage(message, code, imagePath)
        // Typed requests are answered silently (the user reads the text); spoken requests are answered out loud.
        val speaking = speak && tts.speak(message, lang.locale)
        _uiState.update {
            it.copy(
                status = if (speaking) AssistantStatus.SPEAKING else AssistantStatus.IDLE,
                partialText = ""
            )
        }
        // If a spoken reply produced no speech there is no "finished speaking" event, so schedule the restart now.
        // A silent (typed) reply never restarts the microphone on its own.
        if (speak && !speaking) scheduleAutoRestart()
    }

    private fun handleRecognizerError(code: Int) {
        val lang = _uiState.value.language
        when (code) {
            SpeechRecognizer.ERROR_CLIENT -> {
                // we cancelled it ourselves
                _uiState.update { it.copy(status = AssistantStatus.IDLE, partialText = "") }
            }
            SpeechRecognizer.ERROR_NO_MATCH,
            SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> onSilence(lang)
            else -> {
                conversationActive = false
                val message = when (code) {
                    SpeechRecognizer.ERROR_NETWORK,
                    SpeechRecognizer.ERROR_NETWORK_TIMEOUT ->
                        lang.tr("مشكلة في الاتصال بالإنترنت.", "There's a network problem.")
                    SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS ->
                        lang.tr("أحتاج إذن الميكروفون.", "Microphone permission is required.")
                    SpeechRecognizer.ERROR_RECOGNIZER_BUSY ->
                        lang.tr("خدمة التعرف مشغولة، حاول بعد قليل.", "The recognizer is busy, try again shortly.")
                    else ->
                        lang.tr("تعذّر التعرف على الصوت.", "Speech recognition failed.")
                }
                setError(message)
            }
        }
    }

    private fun setError(message: String) {
        _uiState.update {
            it.copy(status = AssistantStatus.ERROR, partialText = "", errorMessage = message)
        }
    }

    override fun onCleared() {
        conversationActive = false
        restartJob?.cancel()
        speech.destroy()
        tts.shutdown()
        super.onCleared()
    }
}
''')

# 23. app/src/main/java/com/example/voiceassistant/service/VoiceAccessibilityService.kt
write_file("app/src/main/java/com/example/voiceassistant/service/VoiceAccessibilityService.kt", r'''package com.example.voiceassistant.service

import android.accessibilityservice.AccessibilityService
import android.content.Intent
import android.os.Build
import android.view.accessibility.AccessibilityEvent
import android.view.accessibility.AccessibilityNodeInfo
import com.example.voiceassistant.commands.TextNormalizer
import com.example.voiceassistant.commands.commands.AccessibilityAction

/** Result of trying to flip a switch / toggle by its name. */
enum class ToggleResult { SUCCESS, ALREADY_IN_STATE, NOT_FOUND, FAILED }

class VoiceAccessibilityService : AccessibilityService() {

    companion object {
        @Volatile
        var instance: VoiceAccessibilityService? = null
            private set

        val isRunning: Boolean
            get() = instance != null

        private const val MAX_DEPTH = 40
        private const val MAX_ANCESTOR_LEVELS = 4
    }

    override fun onServiceConnected() {
        super.onServiceConnected()
        instance = this
    }

    override fun onUnbind(intent: Intent?): Boolean {
        instance = null
        return super.onUnbind(intent)
    }

    override fun onDestroy() {
        instance = null
        super.onDestroy()
    }

    override fun onAccessibilityEvent(event: AccessibilityEvent?) {
        // Not needed: this service only performs actions on demand.
    }

    override fun onInterrupt() {}

    /** Executes a voice-requested screen action. Returns true on success. */
    fun execute(action: AccessibilityAction, argument: String?): Boolean = when (action) {
        AccessibilityAction.BACK -> performGlobalAction(GLOBAL_ACTION_BACK)
        AccessibilityAction.HOME -> performGlobalAction(GLOBAL_ACTION_HOME)
        AccessibilityAction.RECENTS -> performGlobalAction(GLOBAL_ACTION_RECENTS)
        AccessibilityAction.NOTIFICATIONS -> performGlobalAction(GLOBAL_ACTION_NOTIFICATIONS)
        AccessibilityAction.QUICK_SETTINGS -> performGlobalAction(GLOBAL_ACTION_QUICK_SETTINGS)
        AccessibilityAction.SCREENSHOT ->
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                performGlobalAction(GLOBAL_ACTION_TAKE_SCREENSHOT)
            } else false
        AccessibilityAction.LOCK_SCREEN ->
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                performGlobalAction(GLOBAL_ACTION_LOCK_SCREEN)
            } else false
        AccessibilityAction.SCROLL_DOWN -> scroll(forward = true)
        AccessibilityAction.SCROLL_UP -> scroll(forward = false)
        AccessibilityAction.CLICK_TEXT -> argument?.let { clickByText(it) } ?: false
    }

    // ------------------------------------------------------------------ switches / toggles

    /**
     * Finds a Switch / Toggle / checkable item whose label matches one of [names]
     * (for example "Wi-Fi" or "Bluetooth") on the current screen and clicks it.
     *
     * @param enable true = make sure it is ON, false = make sure it is OFF, null = just flip it.
     */
    fun setToggleByName(names: List<String>, enable: Boolean?): ToggleResult {
        val root = rootInActiveWindow ?: return ToggleResult.NOT_FOUND
        val targets = names
            .map { TextNormalizer.key(TextNormalizer.light(it)) }
            .filter { it.isNotEmpty() }
        if (targets.isEmpty()) return ToggleResult.NOT_FOUND

        val switches = ArrayList<AccessibilityNodeInfo>()
        collectCheckables(root, switches, 0)

        var best: AccessibilityNodeInfo? = null
        var bestScore = -1
        for (candidate in switches) {
            val score = matchScore(candidate, targets)
            if (score > bestScore) {
                bestScore = score
                best = candidate
            }
        }

        val node = best ?: return ToggleResult.NOT_FOUND
        if (enable != null && node.isChecked == enable) return ToggleResult.ALREADY_IN_STATE
        return if (clickNodeOrAncestor(node)) ToggleResult.SUCCESS else ToggleResult.FAILED
    }

    private fun collectCheckables(
        node: AccessibilityNodeInfo,
        out: MutableList<AccessibilityNodeInfo>,
        depth: Int
    ) {
        if (depth > MAX_DEPTH) return
        if (node.isCheckable) out.add(node)
        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            collectCheckables(child, out, depth + 1)
        }
    }

    private fun countCheckables(node: AccessibilityNodeInfo, depth: Int = 0): Int {
        if (depth > MAX_DEPTH) return 0
        var count = if (node.isCheckable) 1 else 0
        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            count += countCheckables(child, depth + 1)
        }
        return count
    }

    private fun collectTexts(node: AccessibilityNodeInfo, sb: StringBuilder, depth: Int) {
        if (depth > MAX_DEPTH) return
        node.text?.let { sb.append(it).append(' ') }
        node.contentDescription?.let { sb.append(it).append(' ') }
        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            collectTexts(child, sb, depth + 1)
        }
    }

    /**
     * Climbs from the switch to its row (at most a few levels, and never into a container that
     * holds other switches) and checks whether the row's text contains one of the names.
     * Closer matches and shorter labels score higher. Returns -1 when nothing matches.
     */
    private fun matchScore(switchNode: AccessibilityNodeInfo, targets: List<String>): Int {
        var current: AccessibilityNodeInfo? = switchNode
        var level = 0
        while (current != null && level <= MAX_ANCESTOR_LEVELS) {
            if (countCheckables(current) > 1) break
            val sb = StringBuilder()
            collectTexts(current, sb, 0)
            val label = TextNormalizer.key(TextNormalizer.light(sb.toString()))
            if (label.isNotEmpty() && targets.any { label.contains(it) }) {
                return 1000 - level * 100 - minOf(label.length, 99)
            }
            current = current.parent
            level++
        }
        return -1
    }

    private fun clickNodeOrAncestor(node: AccessibilityNodeInfo): Boolean {
        var current: AccessibilityNodeInfo? = node
        var level = 0
        while (current != null && level <= MAX_ANCESTOR_LEVELS) {
            if (current.isClickable && current.isEnabled) {
                return current.performAction(AccessibilityNodeInfo.ACTION_CLICK)
            }
            current = current.parent
            level++
        }
        return false
    }

    // ------------------------------------------------------------------ scroll / click by text

    private fun scroll(forward: Boolean): Boolean {
        val root = rootInActiveWindow ?: return false
        val node = findScrollable(root) ?: return false
        val action = if (forward) {
            AccessibilityNodeInfo.ACTION_SCROLL_FORWARD
        } else {
            AccessibilityNodeInfo.ACTION_SCROLL_BACKWARD
        }
        return node.performAction(action)
    }

    private fun findScrollable(node: AccessibilityNodeInfo): AccessibilityNodeInfo? {
        if (node.isScrollable) return node
        for (i in 0 until node.childCount) {
            val child = node.getChild(i) ?: continue
            val found = findScrollable(child)
            if (found != null) return found
        }
        return null
    }

    private fun clickByText(text: String): Boolean {
        val root = rootInActiveWindow ?: return false
        val matches = root.findAccessibilityNodeInfosByText(text)
        for (match in matches) {
            var current: AccessibilityNodeInfo? = match
            while (current != null) {
                if (current.isClickable && current.isEnabled) {
                    return current.performAction(AccessibilityNodeInfo.ACTION_CLICK)
                }
                current = current.parent
            }
        }
        return false
    }
}
''')

# 23b. app/src/main/java/com/example/voiceassistant/service/AssistantSession.kt  (NEW)
write_file("app/src/main/java/com/example/voiceassistant/service/AssistantSession.kt", r'''package com.example.voiceassistant.service

import android.content.Context
import android.content.Intent
import android.os.Bundle
import android.service.voice.VoiceInteractionService
import android.service.voice.VoiceInteractionSession
import android.service.voice.VoiceInteractionSessionService
import android.speech.RecognitionService
import android.speech.SpeechRecognizer
import com.example.voiceassistant.MainActivity

/**
 * Registers the app as a selectable "Digital assistant app"
 * (Settings > Apps > Default apps > Digital assistant app).
 */
class VaInteractionService : VoiceInteractionService()

/** Creates a session every time the user invokes the assistant (long-press Home, power button...). */
class VaSessionService : VoiceInteractionSessionService() {
    override fun onNewSession(args: Bundle?): VoiceInteractionSession = VaSession(this)
}

/** Opens the main screen with the "auto listen" flag so the microphone starts immediately. */
class VaSession(context: Context) : VoiceInteractionSession(context) {

    override fun onShow(args: Bundle?, showFlags: Int) {
        super.onShow(args, showFlags)

        val intent = Intent(context, MainActivity::class.java)
            .putExtra(MainActivity.EXTRA_AUTO_LISTEN, true)

        try {
            startAssistantActivity(intent)
        } catch (e: Exception) {
            try {
                intent.addFlags(
                    Intent.FLAG_ACTIVITY_NEW_TASK or
                        Intent.FLAG_ACTIVITY_CLEAR_TOP or
                        Intent.FLAG_ACTIVITY_SINGLE_TOP
                )
                context.startActivity(intent)
            } catch (_: Exception) {
                // Nothing else we can do.
            }
        }
        hide()
    }
}

/**
 * Minimal recognition service required by the voice-interaction declaration.
 * The app itself uses the system's default recognizer, so this one never recognizes anything.
 */
class VaRecognitionService : RecognitionService() {
    override fun onStartListening(recognizerIntent: Intent?, listener: Callback?) {
        listener?.error(SpeechRecognizer.ERROR_CLIENT)
    }

    override fun onCancel(listener: Callback?) {}

    override fun onStopListening(listener: Callback?) {}
}
''')

# 24. app/src/main/java/com/example/voiceassistant/commands/CommandResult.kt
write_file("app/src/main/java/com/example/voiceassistant/commands/CommandResult.kt", r'''package com.example.voiceassistant.commands

sealed class CommandResult {
    data class Success(val message: String) : CommandResult()
    data class Failure(val message: String) : CommandResult()

    /** The command can run once the user grants [permission]; it is then re-executed. */
    data class NeedsPermission(val permission: String, val message: String) : CommandResult()
}
''')

# 25. app/src/main/java/com/example/voiceassistant/commands/CommandParser.kt
write_file("app/src/main/java/com/example/voiceassistant/commands/CommandParser.kt", r'''package com.example.voiceassistant.commands

import com.example.voiceassistant.commands.commands.AccessibilityAction
import com.example.voiceassistant.commands.commands.InfoType
import com.example.voiceassistant.commands.commands.SettingsTarget

sealed class ParsedCommand {
    data class Call(val target: String) : ParsedCommand()
    data class Sms(val target: String, val body: String?) : ParsedCommand()

    /** [hour] == null means "just show my alarms". */
    data class Alarm(val hour: Int?, val minute: Int = 0) : ParsedCommand()
    data class WebSearch(val query: String) : ParsedCommand()

    /** [toggle]: true = turn ON, false = turn OFF, null = only open the settings page. */
    data class OpenSettings(val target: SettingsTarget, val toggle: Boolean? = null) : ParsedCommand()
    data class Accessibility(val action: AccessibilityAction, val argument: String? = null) : ParsedCommand()
    data class Info(val type: InfoType) : ParsedCommand()
    data class LaunchApp(val appName: String) : ParsedCommand()

    /** Spoken reminder; [triggerAtMillis] == null means the time could not be understood. */
    data class Reminder(val text: String, val triggerAtMillis: Long?) : ParsedCommand()

    /** Protection commands: turn the clipboard monitor on / off, or scan the installed apps. */
    data class Security(val action: SecurityAction) : ParsedCommand()

    /** The user told the assistant their name ("اسمي أحمد", "my name is Sam"). */
    data class SetName(val name: String) : ParsedCommand()

    /** Long-term memory command: remember / list / forget something, or go back to the last project. */
    data class Memory(val action: MemoryAction, val argument: String? = null) : ParsedCommand()
    object Unknown : ParsedCommand()
}

enum class SecurityAction { ENABLE, DISABLE, SCAN_APPS }

enum class MemoryAction { LIST, ADD, FORGET, RETURN_TO_PROJECT }

/** A personal fact found in a normal sentence; [isPreference] = a like / dislike. */
data class ExtractedFact(val text: String, val isPreference: Boolean)

/** Text helpers shared by the parser and the contact / app lookups. */
object TextNormalizer {

    /** Removes Arabic diacritics/tatweel, converts Arabic-Indic digits and tidies whitespace/punctuation. */
    fun light(raw: String): String {
        val sb = StringBuilder(raw.length)
        for (ch in raw) {
            when (ch) {
                in '\u064B'..'\u065F', '\u0640', '\u0670' -> Unit
                in '\u0660'..'\u0669' -> sb.append('0' + (ch - '\u0660'))
                in '\u06F0'..'\u06F9' -> sb.append('0' + (ch - '\u06F0'))
                '\u2019' -> sb.append('\'')
                else -> sb.append(ch)
            }
        }
        return sb.toString()
            .replace(Regex("\\s+"), " ")
            .trim()
            .trimEnd('.', ',', '\u060C', '\u061F', '?', '!', '\u061B')
            .trim()
    }

    /** Same-length matching key: unifies Arabic letter variants and lower-cases Latin text. */
    fun key(text: String): String {
        val sb = StringBuilder(text.length)
        for (ch in text) {
            sb.append(
                when (ch) {
                    '\u0623', '\u0625', '\u0622', '\u0671' -> '\u0627' // أ إ آ ٱ -> ا
                    '\u0649' -> '\u064A'                               // ى -> ي
                    '\u0629' -> '\u0647'                               // ة -> ه
                    else -> ch.lowercaseChar()
                }
            )
        }
        return sb.toString()
    }
}

/**
 * Turns a spoken sentence (Arabic or English) into a [ParsedCommand].
 *
 * Patterns are written against the normalized key (see [TextNormalizer.key]):
 * أ/إ/آ -> ا, ى -> ي, ة -> ه. Captured values are taken from the original text.
 */
class CommandParser {

    internal class Prepared(val light: String) {
        val key: String = TextNormalizer.key(light)

        fun groups(regex: Regex): List<String>? {
            val m = regex.matchEntire(key) ?: return null
            return (1 until m.groups.size).map { i ->
                val g = m.groups[i]
                if (g == null) "" else light.substring(g.range.first, g.range.last + 1).trim()
            }
        }

        fun containsAny(vararg words: String): Boolean = words.any { key.contains(it) }
    }

    // ---- patterns ---------------------------------------------------------------------------
    private val smsEnBody = Regex("""^(?:please )?(?:send (?:a |an )?(?:message|sms|text)|text|message)\s+(?:to )?(.+?)\s+(?:saying|that says|says|and say|say)\s+(.+)$""")
    private val smsEn = Regex("""^(?:please )?(?:send (?:a |an )?(?:message|sms|text)|text|message)\s+(?:to )?(.+)$""")
    private val smsArBody = Regex("""^(?:ارسل|ابعث|ارسلي|ابعثي)\s+(?:رساله|رسايل|sms)\s+(?:الي\s+)?(.+?)\s+(?:تقول|نصها|مفادها|بنص|وقل|وقول|مضمونها)\s+(.+)$""")
    private val smsAr = Regex("""^(?:ارسل|ابعث|ارسلي|ابعثي)\s+(?:رساله|رسايل|sms)\s+(?:الي\s+)?(.+)$""")

    private val callEn = Regex("""^(?:please )?(?:call|dial|phone|ring)\s+(?:to )?(?:number )?(.+)$""")
    private val callAr = Regex("""^(?:اتصل|كلم|رن|اتصلي|كلمي)\s+(?:بالرقم\s+|ب\s+)?(.+)$""")

    private val timeRegex = Regex("""(\d{1,2})(?:[:.](\d{2}))?""")
    private val pmRegex = Regex("""(?<![a-z])(?:pm|p\.m\.?)(?![a-z])""")
    private val amRegex = Regex("""(?<![a-z])(?:am|a\.m\.?)(?![a-z])""")

    private val searchEn = Regex("""^(?:please )?(?:search(?: for| about)?|google|look up|lookup)\s+(.+)$""")
    private val searchAr = Regex("""^(?:ابحث|دور|فتش)(?:\s+لي)?(?:\s+في\s+(?:جوجل|قوقل|غوغل|الانترنت|النت|الويب))?(?:\s+عن)?\s+(.+)$""")
    private val searchAr2 = Regex("""^(?:جوجل|قوقل|غوغل)\s+(.+)$""")

    private val backRegex = Regex("""^(?:please )?(?:go )?back(?: button)?$|^(?:ارجع|رجوع|ارجعي|ارجع للخلف|ارجع الي الخلف|للخلف|الي الخلف|زر الرجوع|اضغط رجوع)$""")
    private val clickEn = Regex("""^(?:click|tap|press)(?: on)?\s+(.+)$""")
    private val clickAr = Regex("""^(?:اضغط|انقر|دوس)(?:\s+علي)?\s+(.+)$""")

    private val greetingEn = Regex("""^(?:hi|hello|hey|good (?:morning|afternoon|evening))(?: there| claude)?$""")
    private val greetingAr = Regex("""^(?:مرحبا|اهلا|اهلا وسهلا|السلام عليكم|صباح الخير|مساء الخير|هلا)$""")

    private val launchEn = Regex("""^(?:please )?(?:open|launch|start|run)\s+(?:the )?(?:app )?(.+?)(?: app)?$""")
    private val launchAr = Regex("""^(?:افتح|شغل|افتحي|روح الي|اذهب الي|ابدا)\s+(?:لي\s+)?(?:تطبيق\s+)?(.+)$""")

    // ---- user name ("اسمي أحمد" / "أنا أحمد" / "my name is Ahmed") -------------------------
    private val nameAr = Regex("""^(?:انا\s+)?اسمي\s+(?:هو\s+)?(\S+(?:\s+\S+){0,2})$""")
    private val nameArShort = Regex("""^انا\s+(\S+(?:\s+\S+)?)$""")
    private val nameEn = Regex("""^(?:(?:hi|hello|hey)[ ,]+)?my name(?: is|'s)\s+(\S+(?:\s+\S+){0,2})$""")

    /** Words that follow "أنا" but are not a name ("أنا بخير", "أنا جعان" ...), in key form. */
    private val notNames = setOf(
        "بخير", "تمام", "كويس", "كويسه", "الحمد", "الحمدلله", "زعلان", "زعلانه", "حزين", "حزينه",
        "سعيد", "سعيده", "تعبان", "تعبانه", "متعب", "متعبه", "جعان", "جعانه", "جائع", "جائعه",
        "عطشان", "نايم", "نعسان", "مشغول", "مشغوله", "ممتاز", "طيب", "هنا", "جاهز", "جاهزه",
        "مستعد", "محتاج", "عايز", "عاوز", "اريد", "ابي", "ابغي", "ابغى", "اشعر", "احس", "لا",
        "مش", "لست", "فعلا", "جدا", "كده", "اسف", "اسفه", "متاكد", "اعتقد", "اظن", "احب", "اكره",
        "اعرف", "اقدر", "اسمع", "اتكلم", "اتحدث", "في", "مع", "من", "عند", "لسه", "الان", "بس",
        "فقط", "والله", "اوكي", "اوك", "مين", "ليش", "ليه", "كيف", "ماذا", "شو", "ايش", "وين",
        "متي", "لماذا", "ok", "fine", "good", "great", "tired", "hungry", "sad", "happy", "here", "ready",
        // --- added with the memory feature: verbs and states that are not names ---
        "اعمل", "اشتغل", "ادرس", "اسكن", "اعيش", "افضل", "احتاج", "ارغب", "اود",
        "احاول", "افكر", "اخطط", "اتعلم", "ابحث", "اذهب", "اروح", "اجي", "اكتب",
        "اقرا", "العب", "اشرب", "اكل", "اشوف", "استطيع", "اقول", "اسال", "اطلب",
        "انتظر", "غاضب", "غاضبه", "غضبان", "خايف", "خايفه", "خائف", "خائفه", "قلقان",
        "قلق", "مرهق", "مرهقه", "منهك", "مريض", "مريضه", "مبسوط", "مبسوطه", "مستعجل",
        "متحمس", "متحمسه", "زهقان", "محبط", "محبطه", "متضايق", "متضايقه", "منزعج", "منزعجه",
        "مرتاح", "مرتاحه", "مستمتع", "كسلان", "مهتم", "موجود", "موجوده", "صاحي", "مستيقظ",
        "فاضي", "راجع", "جاي", "رايح", "ذاهب", "خارج", "وحدي", "معك", "معاك",
        "بحاجه", "مضطر", "مجبور", "عطشانه", "نعسانه", "احسن", "اكثر", "اقل", "غير",
        "sorry", "back", "busy", "bored", "angry", "sick", "home", "online", "just",
        "not", "so", "very", "still", "sure", "new", "okay", "well", "scared",
        "excited", "worried", "confused", "glad", "late", "alone", "thirsty", "sleepy", "free"
    )

    private fun parseSetName(t: Prepared): ParsedCommand? {
        t.groups(nameAr)?.let { return nameCommand(it[0]) }
        t.groups(nameEn)?.let { return nameCommand(it[0]) }
        t.groups(nameArShort)?.let { g ->
            val words = g[0].split(" ")
            if (words.any { TextNormalizer.key(it) in notNames }) return null
            return nameCommand(g[0])
        }
        return null
    }

    private fun nameCommand(raw: String): ParsedCommand? {
        val name = raw.trim().take(30).replaceFirstChar { if (it.isLowerCase()) it.titlecase() else it.toString() }
        return if (name.isEmpty()) null else ParsedCommand.SetName(name)
    }

    /** Words that are never a name when they are the whole answer to "what is your name?" (key form). */
    private val notBareNames = setOf(
        "مرحبا", "اهلا", "هلا", "هاي", "السلام", "سلام", "عليكم", "صباح", "مساء", "الخير", "النور",
        "شكرا", "نعم", "ايوه", "ايوا", "اي", "لا", "كلا", "تمام", "اسمي", "انا", "توقف", "الغاء", "ايقاف",
        "hi", "hello", "hey", "yes", "no", "thanks", "thank", "you", "ok", "okay", "sure", "stop", "cancel",
        "good", "morning", "evening", "afternoon", "night", "my", "name", "is", "im"
    )

    /**
     * The short answer to "what is your name?" when it is just the name ("أحمد" / "Sam" / "محمد علي").
     * Only meant for the first message right after the assistant asked for the name. Returns null when the
     * text looks like anything else (a command, a question, a greeting, a longer sentence).
     */
    fun bareName(raw: String): String? {
        val clean = raw.trim().trim('.', '!', ',', '\u060C', '\u061F', '?').trim()
        if (clean.isEmpty() || clean.length > 30) return null
        if (clean.any { it.isDigit() || it == '\n' || it == '?' || it == '\u061F' }) return null
        val words = clean.split(Regex("\\s+"))
        if (words.size > 2) return null
        val keys = words.map { TextNormalizer.key(it) }
        if (keys.any { it in notNames || it in notBareNames }) return null
        if (parse(raw) !is ParsedCommand.Unknown) return null
        return (nameCommand(clean) as? ParsedCommand.SetName)?.name
    }

    // ---- long-term memory: commands ("تذكر أن ...", "ما تتذكره عني", "انسى ...", "ارجع لمشروعي السابق") ------
    private val memAddAr = Regex("""^(?:تذكر|تذكري|احفظ|احفظي)\s+(?:ان|اني|انني|انه)\s+(.+)$""")
    private val memAddEn = Regex("""^(?:please )?(?:remember|save|keep in mind) that\s+(.+)$""")
    private val memListAr = Regex("""^(?:ما|ماذا|شو|ايش)\s+(?:الذي\s+|اللي\s+)?(?:تتذكر|تعرف)(?:ه)?\s+عني$""")
    private val memListEn = Regex("""^(?:what do you (?:know|remember) about me|what(?:'s| is) in your memory)$""")
    private val memForgetAr = Regex("""^(?:انس|انسي)\s+(?:ان(?:ني|ي)?\s+)?(.+)$""")
    private val memForgetEn = Regex("""^(?:please )?forget\s+(?:that\s+|about\s+)?(.+)$""")
    private val memReturn = listOf(
        Regex("""^(?:ارجع|ارجعني|رجعني|افتح|افتحي)\s+(?:الي\s+|ل)?مشروعي(?:\s+(?:السابق|الاخير))?$"""),
        Regex("""^(?:ما|ماهي|ايش|شو)\s+(?:هي\s+)?(?:المشاريع|الملفات)\s+(?:التي|اللي|الي)\s+(?:عملت|اشتغلت|فتحت)\s+عليها$"""),
        Regex("""^(?:اعرض\s+|وريني\s+)?مشاريعي(?:\s+السابقه)?$"""),
        Regex("""^(?:go back to|return to|open) my (?:previous|last|recent) project$"""),
        Regex("""^(?:what|which) projects (?:did|have) i (?:work(?:ed)? on|opened)$""")
    )

    /** "انسى ذلك" / "forget it" mean nothing on their own, so they are not memory commands. */
    private val forgetIgnored = setOf("it", "that", "about it", "ذلك", "هذا", "هذه")

    private fun parseMemory(t: Prepared): ParsedCommand? {
        t.groups(memAddAr)?.let { return ParsedCommand.Memory(MemoryAction.ADD, it[0]) }
        t.groups(memAddEn)?.let { return ParsedCommand.Memory(MemoryAction.ADD, it[0]) }
        if (memListAr.matches(t.key) || memListEn.matches(t.key)) return ParsedCommand.Memory(MemoryAction.LIST)
        if (memReturn.any { it.matches(t.key) }) return ParsedCommand.Memory(MemoryAction.RETURN_TO_PROJECT)
        val forget = t.groups(memForgetAr) ?: t.groups(memForgetEn)
        if (forget != null && TextNormalizer.key(forget[0]) !in forgetIgnored) {
            return ParsedCommand.Memory(MemoryAction.FORGET, forget[0])
        }
        return null
    }

    // ---- long-term memory: facts found in normal sentences (local regex, no AI) --------------------
    // These run BEFORE nameArShort, so "أنا أحب القهوة" can never be taken for a name.
    // Likes / dislikes: "أنا" is optional for أحب / أكره only. أفضل (= "best" as a noun) and the verbs below
    // double as commands ("اعمل لي صورة", "أفضل مطعم ...") so they need "أنا".
    private val factLikeLoose = Regex("""^(?:انا\s+)?(احب|اكره)\s+(.+)$""")
    private val factLikeStrict = Regex("""^انا\s+(افضل)\s+(.+)$""")
    private val factWork = Regex("""^انا\s+(اعمل|اشتغل|ادرس)\s+(.+)$""")
    private val factLive = Regex("""^(?:انا\s+)?(?:اسكن|اعيش)\s+(?:في\s+)?(.+)$""")

    private val factVerbs = mapOf(
        "احب" to "يحب", "افضل" to "يفضل", "اكره" to "يكره",
        "اعمل" to "يعمل", "اشتغل" to "يعمل", "ادرس" to "يدرس"
    )

    private companion object {
        /** Longer texts are code / pasted material: no fact extraction. */
        const val MAX_FACT_SOURCE_CHARS = 500
        const val MAX_FACT_WORDS = 10
    }

    /**
     * Finds one personal fact in [raw], or null. Questions, multi-line text and texts over
     * [MAX_FACT_SOURCE_CHARS] characters are skipped. No network, no AI.
     */
    fun extractFact(raw: String): ExtractedFact? {
        if (raw.length > MAX_FACT_SOURCE_CHARS) return null
        if (raw.indexOf('?') >= 0 || raw.indexOf('\u061F') >= 0 || raw.indexOf('\n') >= 0) return null
        val t = Prepared(TextNormalizer.light(raw))
        t.groups(factLikeLoose)?.let { return factOf(it[0], it[1], true) }
        t.groups(factLikeStrict)?.let { return factOf(it[0], it[1], true) }
        t.groups(factWork)?.let { return factOf(it[0], it[1], false) }
        t.groups(factLive)?.let { return factValue("يسكن في", it[0], false) }
        return null
    }

    private fun factOf(verb: String, value: String, preference: Boolean): ExtractedFact? {
        val label = factVerbs[TextNormalizer.key(verb)] ?: return null
        return factValue(label, value, preference)
    }

    private fun factValue(label: String, value: String, preference: Boolean): ExtractedFact? {
        val v = value.trim()
        if (v.isEmpty()) return null
        // "أحب أن أسألك ..." is a request, not a preference.
        if (TextNormalizer.key(v).startsWith("ان ")) return null
        if (v.split(" ").size > MAX_FACT_WORDS) return null
        return ExtractedFact("$label: $v", preference)
    }

    /** A sentence holding a fact goes to the AI as a normal message; it must never become [ParsedCommand.SetName]. */
    private fun parseFactSentence(raw: String): ParsedCommand? =
        if (extractFact(raw) != null) ParsedCommand.Unknown else null

    // ---- entry point ------------------------------------------------------------------------
    fun parse(raw: String): ParsedCommand {
        val t = Prepared(TextNormalizer.light(raw))
        if (t.key.isEmpty()) return ParsedCommand.Unknown
        return parseMemory(t)
            ?: parseReminder(t)
            ?: parseFactSentence(raw)
            ?: parseSetName(t)
            ?: parseSms(t)
            ?: parseCall(t)
            ?: parseAlarm(t)
            ?: parseSearch(t)
            ?: parseAccessibility(t)
            ?: parseSettings(t)
            ?: parseSecurity(t)
            ?: parseInfo(t)
            ?: parseLaunch(t)
            ?: ParsedCommand.Unknown
    }

    // ---- reminders ("ذكرني بشرب الماء بعد 10 دقائق") -----------------------------------------
    private val reminderTrigger = Regex("""(?:ذكرني|ذكريني|نبهني|نبهيني|remind me|تذكير|تذكيري|اضبط لي تذكير|اضبط تذكير)""")

    private val relAr = Regex(
        """بعد\s+(?:(\d+(?:\.\d+)?)|([\u0621-\u064A]+))?\s*(ثانيه|ثواني|ثوان|دقيقه|دقيقتين|دقايق|دقائق|ساعه|ساعتين|ساعات|يوم|يومين|ايام)(?:\s+و\s*(نصف|نص|ربع))?"""
    )
    private val relEn = Regex(
        """(?<![a-z])(?:in|after)\s+(?:(\d+(?:\.\d+)?)|(an?|one|two|three|four|five|six|seven|eight|nine|ten|fifteen|twenty|thirty|forty five|forty|half an|half a|a half|quarter of an|a quarter of an))\s*(seconds?|secs?|minutes?|mins?|hours?|hrs?|days?)\b"""
    )
    private val clockPrefixed = Regex("""(?:الساعه|ساعه|(?<![a-z])at)\s*(\d{1,2})(?:[:.](\d{2}))?""")
    private val clockWordMinutes = Regex("""(?:(?:عند|في)\s+)?(?:الساعه|ساعه)\s*(\d{1,2})\s+و\s*([\u0621-\u064A]+|\d+)\s*(?:دقيقه|دقائق|دقايق)""")
    private val clockAmPm = Regex("""(\d{1,2})(?:[:.](\d{2}))?\s*(?:am|pm|a\.m\.?|p\.m\.?)(?![a-z])""")

    private val dayAfterTomorrow = Regex("""بعد\s+غد(?![\u0621-\u064A])|day after tomorrow""")
    private val dayTomorrow = Regex("""(?<![\u0621-\u064A])(?:غدا|بكره|بكرا)(?![\u0621-\u064A])|tomorrow""")
    private val dayToday = Regex("""(?<![\u0621-\u064A])اليوم(?![\u0621-\u064A])|today""")

    private val periodPm = Regex("""(?<![\u0621-\u064A])(?:مساء|عصرا|عصر|ليلا|ليل)(?![\u0621-\u064A])""")
    private val periodAm = Regex("""(?<![\u0621-\u064A])(?:صباحا|صباح|فجرا|فجر)(?![\u0621-\u064A])""")
    private val periodNoon = Regex("""(?<![\u0621-\u064A])(?:ظهرا|ظهر)(?![\u0621-\u064A])""")

    private val arNumberWords = mapOf(
        "واحد" to 1, "واحده" to 1, "اثنين" to 2, "اثنتين" to 2, "ثنتين" to 2,
        "ثلاث" to 3, "ثلاثه" to 3, "اربع" to 4, "اربعه" to 4, "خمس" to 5, "خمسه" to 5,
        "ست" to 6, "سته" to 6, "سبع" to 7, "سبعه" to 7, "ثمان" to 8, "ثمانيه" to 8,
        "تسع" to 9, "تسعه" to 9, "عشر" to 10, "عشره" to 10, "عشرين" to 20,
        "ثلاثين" to 30, "اربعين" to 40, "خمسين" to 50, "ستين" to 60
    )
    private val enNumberWords = mapOf(
        "a" to 1.0, "an" to 1.0, "one" to 1.0, "two" to 2.0, "three" to 3.0, "four" to 4.0,
        "five" to 5.0, "six" to 6.0, "seven" to 7.0, "eight" to 8.0, "nine" to 9.0, "ten" to 10.0,
        "fifteen" to 15.0, "twenty" to 20.0, "thirty" to 30.0, "forty" to 40.0, "forty five" to 45.0,
        "half an" to 0.5, "half a" to 0.5, "a half" to 0.5,
        "quarter of an" to 0.25, "a quarter of an" to 0.25
    )

    private fun unitMillis(unit: String): Long = when {
        unit.startsWith("ثان") || unit.startsWith("ثوان") || unit.startsWith("sec") -> 1_000L
        unit.startsWith("دق") || unit.startsWith("min") -> 60_000L
        unit.startsWith("ساع") || unit.startsWith("hour") || unit.startsWith("hr") -> 3_600_000L
        else -> 86_400_000L
    }

    /** Milliseconds from now for phrases like "بعد 10 دقائق" / "in half an hour"; null if none found. */
    private fun relativeDelay(key: String, ranges: MutableList<IntRange>): Long? {
        relAr.find(key)?.let { m ->
            val digits = m.groupValues[1]
            val word = m.groupValues[2]
            val unit = m.groupValues[3]
            val extra = m.groupValues[4]
            var amount = when {
                digits.isNotEmpty() -> digits.toDouble()
                word == "نصف" || word == "نص" -> 0.5
                word == "ربع" -> 0.25
                word.isNotEmpty() -> (arNumberWords[word] ?: 0).toDouble()
                unit == "ساعتين" || unit == "دقيقتين" || unit == "يومين" -> 2.0
                else -> 1.0
            }
            if (amount > 0.0) {
                when (extra) {
                    "نصف", "نص" -> amount += 0.5
                    "ربع" -> amount += 0.25
                }
                ranges.add(m.range)
                return (amount * unitMillis(unit)).toLong()
            }
        }
        relEn.find(key)?.let { m ->
            val digits = m.groupValues[1]
            val word = m.groupValues[2]
            val unit = m.groupValues[3]
            val amount = if (digits.isNotEmpty()) digits.toDouble() else (enNumberWords[word] ?: 0.0)
            if (amount > 0.0) {
                ranges.add(m.range)
                return (amount * unitMillis(unit)).toLong()
            }
        }
        return null
    }

    private fun timeOn(dayOffset: Int, hour: Int, minute: Int): Long {
        val cal = java.util.Calendar.getInstance()
        cal.add(java.util.Calendar.DAY_OF_YEAR, dayOffset)
        cal.set(java.util.Calendar.HOUR_OF_DAY, hour)
        cal.set(java.util.Calendar.MINUTE, minute)
        cal.set(java.util.Calendar.SECOND, 0)
        cal.set(java.util.Calendar.MILLISECOND, 0)
        return cal.timeInMillis
    }

    /** Absolute time like "غداً الساعة 5 مساءً" / "tomorrow at 5 pm"; null if no time of day was said. */
    private fun absoluteTime(key: String, ranges: MutableList<IntRange>): Long? {
        val dayOffset = when {
            dayAfterTomorrow.containsMatchIn(key) -> 2
            dayTomorrow.containsMatchIn(key) -> 1
            else -> 0
        }
        for (r in listOf(dayAfterTomorrow, dayTomorrow, dayToday)) {
            r.find(key)?.let { ranges.add(it.range) }
        }

        val clock = clockWordMinutes.find(key) ?: clockAmPm.find(key) ?: clockPrefixed.find(key)
        val pm = periodPm.containsMatchIn(key) || pmRegex.containsMatchIn(key)
        val am = periodAm.containsMatchIn(key) || amRegex.containsMatchIn(key)
        val noon = periodNoon.containsMatchIn(key)
        for (r in listOf(periodPm, periodAm, periodNoon, pmRegex, amRegex, clockAmPm, clockPrefixed, clockWordMinutes)) {
            r.find(key)?.let { ranges.add(it.range) }
        }

        if (clock == null) {
            // "tomorrow" alone -> 09:00; nothing at all -> unknown time
            return if (dayOffset > 0) timeOn(dayOffset, 9, 0) else null
        }

        val h0 = clock.groupValues[1].toInt()
        val minuteStr = clock.groupValues[2].ifEmpty { "0" }
        val minute = if (minuteStr.all { it.isDigit() }) minuteStr.toInt() else (arNumberWords[minuteStr] ?: 0)
        if (h0 > 23 || minute > 59) return null

        var hour = h0
        val hasPeriod = pm || am || noon
        when {
            pm && !am && hour in 1..11 -> hour += 12
            am && hour == 12 -> hour = 0
            noon && hour in 1..5 -> hour += 12
            !hasPeriod && hour in 1..6 -> hour += 12 // "at 5" most likely means 5 pm
        }

        val now = System.currentTimeMillis()
        var millis = timeOn(dayOffset, hour, minute)
        if (millis <= now) {
            if (!hasPeriod && dayOffset == 0 && h0 in 1..11) {
                // try the other half of the day before pushing to tomorrow
                val alt = timeOn(0, if (hour >= 12) h0 else h0 + 12, minute)
                millis = if (alt > now) alt else timeOn(1, hour, minute)
            } else if (dayOffset == 0) {
                millis = timeOn(1, hour, minute)
            }
        }
        return millis
    }

    private fun parseReminder(t: Prepared): ParsedCommand? {
        val trigger = reminderTrigger.find(t.key) ?: return null
        val ranges = mutableListOf(trigger.range)

        val delay = relativeDelay(t.key, ranges)
        val at = if (delay != null) System.currentTimeMillis() + delay else absoluteTime(t.key, ranges)

        // The reminder text = the sentence without the trigger and the time phrases.
        val sb = StringBuilder()
        var pos = 0
        for (r in ranges.sortedBy { it.first }) {
            if (r.first > pos) sb.append(t.light, pos, r.first)
            pos = maxOf(pos, r.last + 1)
        }
        if (pos < t.light.length) sb.append(t.light, pos, t.light.length)

        var text = sb.toString().replace(Regex("""\s+"""), " ").trim()
        text = text.replace(Regex("""^(?:please\s+|to\s+|about\s+|that\s+|of\s+|ان\s+|أن\s+|علي\s+|على\s+|عند\s+|في\s+)+""", RegexOption.IGNORE_CASE), "")
        text = text.replace(Regex("""(?:\s+(?:please|في|at|on|in|و))+$""", RegexOption.IGNORE_CASE), "").trim()
        val arabicTrigger = !trigger.value.startsWith("remind")
        if (arabicTrigger && text.length > 3 && text.startsWith("ب")) text = text.substring(1)
        text = text.trim().take(200)
        if (text.isEmpty()) {
            text = if (arabicTrigger) "التذكير" else "your reminder"
        }
        return ParsedCommand.Reminder(text, at)
    }

    // ---- individual parsers -----------------------------------------------------------------
    private fun parseSms(t: Prepared): ParsedCommand? {
        t.groups(smsEnBody)?.let { return ParsedCommand.Sms(it[0], it[1]) }
        t.groups(smsArBody)?.let { return ParsedCommand.Sms(it[0], it[1]) }
        t.groups(smsEn)?.let { return ParsedCommand.Sms(it[0], null) }
        t.groups(smsAr)?.let { return ParsedCommand.Sms(it[0], null) }
        return null
    }

    private fun parseCall(t: Prepared): ParsedCommand? {
        t.groups(callAr)?.let { return ParsedCommand.Call(it[0]) }
        t.groups(callEn)?.let { return ParsedCommand.Call(it[0]) }
        return null
    }

    private fun parseAlarm(t: Prepared): ParsedCommand? {
        if (!t.containsAny("منبه", "alarm", "wake me")) return null
        val m = timeRegex.find(t.key) ?: return ParsedCommand.Alarm(null)
        var hour = m.groupValues[1].toInt()
        val minute = m.groupValues[2].ifEmpty { "0" }.toInt()

        val pm = t.containsAny("مساء", "ليل", "عصر") || pmRegex.containsMatchIn(t.key)
        val am = t.containsAny("صباح", "فجر") || amRegex.containsMatchIn(t.key)
        val noon = t.containsAny("ظهر", "noon")
        when {
            pm && !am && hour in 1..11 -> hour += 12
            am && hour == 12 -> hour = 0
            noon && hour in 1..5 -> hour += 12
        }
        return if (hour in 0..23 && minute in 0..59) {
            ParsedCommand.Alarm(hour, minute)
        } else {
            ParsedCommand.Unknown
        }
    }

    private fun parseSearch(t: Prepared): ParsedCommand? {
        t.groups(searchAr)?.let { return ParsedCommand.WebSearch(it[0]) }
        t.groups(searchAr2)?.let { return ParsedCommand.WebSearch(it[0]) }
        t.groups(searchEn)?.let { return ParsedCommand.WebSearch(it[0]) }
        return null
    }

    private fun parseAccessibility(t: Prepared): ParsedCommand? {
        fun a(action: AccessibilityAction, arg: String? = null) =
            ParsedCommand.Accessibility(action, arg)

        val mentionsSettings = t.containsAny("اعدادات", "settings")

        val global: ParsedCommand.Accessibility? = when {
            t.containsAny("الاعدادات السريعه", "quick settings", "اللوحه السريعه") ->
                a(AccessibilityAction.QUICK_SETTINGS)
            t.containsAny("لقطه شاشه", "لقطه الشاشه", "صوره الشاشه", "سكرين شوت", "screenshot", "screen shot") ->
                a(AccessibilityAction.SCREENSHOT)
            t.containsAny("اقفل الشاشه", "قفل الشاشه", "اقفل الجهاز", "اقفل الهاتف", "lock screen", "lock the screen", "lock the phone", "lock phone") ->
                a(AccessibilityAction.LOCK_SCREEN)
            t.containsAny("التطبيقات الاخيره", "التطبيقات الحديثه", "recent apps", "recents", "app switcher") ->
                a(AccessibilityAction.RECENTS)
            !mentionsSettings && t.containsAny("الاشعارات", "notifications", "notification panel") ->
                a(AccessibilityAction.NOTIFICATIONS)
            t.containsAny("الشاشه الرئيسيه", "الصفحه الرئيسيه", "الرئيسيه", "go home", "home screen", "press home") || t.key == "home" ->
                a(AccessibilityAction.HOME)
            backRegex.matches(t.key) ->
                a(AccessibilityAction.BACK)
            t.containsAny("مرر لاسفل", "مرر للاسفل", "مرر الي الاسفل", "مرر الي تحت", "مرر لتحت", "انزل", "scroll down", "page down") ->
                a(AccessibilityAction.SCROLL_DOWN)
            t.containsAny("مرر لاعلي", "مرر للاعلي", "مرر الي الاعلي", "مرر لفوق", "مرر الي فوق", "اطلع", "scroll up", "page up") ->
                a(AccessibilityAction.SCROLL_UP)
            else -> null
        }
        if (global != null) return global

        t.groups(clickAr)?.let { return a(AccessibilityAction.CLICK_TEXT, it[0]) }
        t.groups(clickEn)?.let { return a(AccessibilityAction.CLICK_TEXT, it[0]) }
        return null
    }

    private fun parseSettings(t: Prepared): ParsedCommand? {
        val wantsSettings = t.containsAny(
            "افتح", "شغل", "فعل", "عطل", "اطفي", "اطفئ", "اوقف", "اقفل", "اغلق", "اعدادات",
            "open", "turn on", "turn off", "enable", "disable", "settings", "setting", "switch", "go to"
        )
        if (!wantsSettings) return null

        val target: SettingsTarget = when {
            t.containsAny("واي فاي", "وايفاي", "wifi", "wi-fi", "wi fi") -> SettingsTarget.WIFI
            t.containsAny("بلوتوث", "bluetooth") -> SettingsTarget.BLUETOOTH
            t.containsAny("وضع الطيران", "الطيران", "airplane", "flight mode") -> SettingsTarget.AIRPLANE
            t.containsAny("الاتاحه", "سهوله الوصول", "accessibility") -> SettingsTarget.ACCESSIBILITY
            t.containsAny("البطاريه", "battery") -> SettingsTarget.BATTERY
            t.containsAny("الصوت", "sound", "volume") -> SettingsTarget.SOUND
            t.containsAny("السطوع", "الشاشه", "brightness", "display") -> SettingsTarget.DISPLAY
            t.containsAny("الموقع", "location", "gps") -> SettingsTarget.LOCATION
            t.containsAny("اعدادات", "settings", "setting") -> SettingsTarget.MAIN
            else -> return null
        }

        // "شغل الواي فاي" / "turn off bluetooth" -> flip the switch; "افتح ..." -> only open the page.
        val turnOn = t.containsAny("شغل", "فعل", "turn on", "switch on", "enable")
        val turnOff = t.containsAny(
            "اطفي", "اطفئ", "عطل", "اوقف", "اقفل", "اغلق", "turn off", "switch off", "disable"
        )
        val toggle: Boolean? = when {
            turnOn && !turnOff -> true
            turnOff && !turnOn -> false
            else -> null
        }
        return ParsedCommand.OpenSettings(target, toggle)
    }

    private fun parseInfo(t: Prepared): ParsedCommand? {
        val type: InfoType = when {
            greetingAr.matches(t.key) || greetingEn.matches(t.key) -> InfoType.GREETING
            t.containsAny(
                "كم الساعه", "الساعه كم", "الساعه كام", "كام الساعه", "كم الوقت", "ما الوقت",
                "ما هو الوقت", "الوقت الان", "what time", "current time", "time is it", "tell me the time"
            ) -> InfoType.TIME
            t.containsAny(
                "ما التاريخ", "تاريخ اليوم", "كم التاريخ", "ما اليوم", "اي يوم", "ايش اليوم",
                "what's the date", "whats the date", "what is the date", "today's date", "what day", "date today"
            ) -> InfoType.DATE
            t.containsAny("البطاريه", "battery", "نسبه الشحن") -> InfoType.BATTERY
            t.containsAny(
                "مساعده", "ساعدني", "ماذا يمكنك", "ماذا تستطيع", "ماذا تفعل", "من انت",
                "what can you do", "who are you"
            ) || t.key == "help" -> InfoType.HELP
            t.containsAny("شكرا", "thanks", "thank you") -> InfoType.THANKS
            else -> return null
        }
        return ParsedCommand.Info(type)
    }

    private fun parseSecurity(t: Prepared): ParsedCommand? {
        val action: SecurityAction = when {
            t.containsAny(
                "افحص التطبيقات", "فحص التطبيقات", "افحص تطبيقات",
                "scan apps", "scan my apps", "scan installed apps", "check my apps", "check installed apps"
            ) -> SecurityAction.SCAN_APPS
            t.containsAny(
                "شغل الحمايه", "فعل الحمايه", "ابدا الحمايه", "تفعيل الحمايه",
                "turn on protection", "enable protection", "start protection", "turn on security", "enable security"
            ) -> SecurityAction.ENABLE
            t.containsAny(
                "اوقف الحمايه", "عطل الحمايه", "اطفي الحمايه", "اطفئ الحمايه", "الغ الحمايه", "ايقاف الحمايه",
                "turn off protection", "disable protection", "stop protection", "turn off security", "disable security"
            ) -> SecurityAction.DISABLE
            else -> return null
        }
        return ParsedCommand.Security(action)
    }

    private fun parseLaunch(t: Prepared): ParsedCommand? {
        t.groups(launchAr)?.let { return ParsedCommand.LaunchApp(it[0]) }
        t.groups(launchEn)?.let { return ParsedCommand.LaunchApp(it[0]) }
        return null
    }
}
''')

# 26. app/src/main/java/com/example/voiceassistant/commands/IntentCommandHandler.kt
write_file("app/src/main/java/com/example/voiceassistant/commands/IntentCommandHandler.kt", r'''package com.example.voiceassistant.commands

import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import com.example.voiceassistant.commands.commands.AccessibilityCommand
import com.example.voiceassistant.commands.commands.AlarmCommand
import com.example.voiceassistant.commands.commands.AppLaunchCommand
import com.example.voiceassistant.commands.commands.CallCommand
import com.example.voiceassistant.commands.commands.InfoCommand
import com.example.voiceassistant.commands.commands.ReminderCommand
import com.example.voiceassistant.commands.commands.SearchCommand
import com.example.voiceassistant.commands.commands.SettingsCommand
import com.example.voiceassistant.commands.commands.SmsCommand
import com.example.voiceassistant.viewmodel.AppLanguage
import kotlinx.coroutines.CancellationException

/** Starts an activity from a non-activity context. */
fun Context.startNewTask(intent: Intent) {
    intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
    startActivity(intent)
}

/** Routes a [ParsedCommand] to the command that knows how to execute it. */
class IntentCommandHandler(context: Context) {

    private val appContext = context.applicationContext

    suspend fun execute(command: ParsedCommand, lang: AppLanguage): CommandResult = try {
        when (command) {
            is ParsedCommand.Call -> CallCommand.execute(appContext, command, lang)
            is ParsedCommand.Sms -> SmsCommand.execute(appContext, command, lang)
            is ParsedCommand.Alarm -> AlarmCommand.execute(appContext, command, lang)
            is ParsedCommand.WebSearch -> SearchCommand.execute(appContext, command, lang)
            is ParsedCommand.OpenSettings -> SettingsCommand.execute(appContext, command, lang)
            is ParsedCommand.Accessibility -> AccessibilityCommand.execute(appContext, command, lang)
            is ParsedCommand.Info -> InfoCommand.execute(appContext, command, lang)
            is ParsedCommand.LaunchApp -> AppLaunchCommand.execute(appContext, command, lang)
            is ParsedCommand.Reminder -> ReminderCommand.execute(appContext, command, lang)
            // Needs the ViewModel (service state, app scan): MainViewModel handles it before reaching here.
            is ParsedCommand.Security -> CommandResult.Failure(
                lang.tr(
                    "أمر الحماية يُنفَّذ من الشاشة الرئيسية.",
                    "Protection commands are handled by the main screen."
                )
            )
            // Needs the ViewModel (profile + AI): MainViewModel handles it before reaching here.
            is ParsedCommand.SetName -> CommandResult.Failure(
                lang.tr(
                    "حفظ الاسم يُنفَّذ من الشاشة الرئيسية.",
                    "Saving the name is handled by the main screen."
                )
            )
            // Needs the ViewModel (memory store + working file): MainViewModel handles it before reaching here.
            is ParsedCommand.Memory -> CommandResult.Failure(
                lang.tr(
                    "أوامر الذاكرة تُنفَّذ من الشاشة الرئيسية.",
                    "Memory commands are handled by the main screen."
                )
            )
            ParsedCommand.Unknown -> CommandResult.Failure(
                lang.tr(
                    "لم أفهم الأمر. قل «مساعدة» لمعرفة ما يمكنني فعله.",
                    "I didn't understand that. Say \"help\" to see what I can do."
                )
            )
        }
    } catch (e: CancellationException) {
        throw e
    } catch (e: ActivityNotFoundException) {
        CommandResult.Failure(
            lang.tr(
                "لا يوجد تطبيق على الجهاز يستطيع تنفيذ هذا الأمر.",
                "No app on this device can handle that."
            )
        )
    } catch (e: SecurityException) {
        CommandResult.Failure(
            lang.tr(
                "ليس لدي الصلاحية لتنفيذ هذا الأمر.",
                "I don't have permission to do that."
            )
        )
    } catch (e: Exception) {
        CommandResult.Failure(
            lang.tr(
                "حدث خطأ أثناء تنفيذ الأمر.",
                "Something went wrong while running that command."
            )
        )
    }
}
''')

# 27. app/src/main/java/com/example/voiceassistant/commands/commands/AccessibilityCommand.kt
write_file("app/src/main/java/com/example/voiceassistant/commands/commands/AccessibilityCommand.kt", r'''package com.example.voiceassistant.commands.commands

import android.content.Context
import android.content.Intent
import android.provider.Settings
import com.example.voiceassistant.commands.CommandResult
import com.example.voiceassistant.commands.ParsedCommand
import com.example.voiceassistant.commands.startNewTask
import com.example.voiceassistant.service.VoiceAccessibilityService
import com.example.voiceassistant.viewmodel.AppLanguage

/**
 * @param targetsOtherApp true if the action must run against another app's window,
 * so the assistant moves itself to the background first.
 */
enum class AccessibilityAction(val targetsOtherApp: Boolean) {
    BACK(true),
    HOME(false),
    RECENTS(false),
    NOTIFICATIONS(false),
    QUICK_SETTINGS(false),
    SCREENSHOT(true),
    LOCK_SCREEN(false),
    SCROLL_DOWN(true),
    SCROLL_UP(true),
    CLICK_TEXT(true)
}

object AccessibilityCommand {

    fun execute(
        context: Context,
        command: ParsedCommand.Accessibility,
        lang: AppLanguage
    ): CommandResult {
        val service = VoiceAccessibilityService.instance
        if (service == null) {
            context.startNewTask(Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS))
            return CommandResult.Failure(
                lang.tr(
                    "خدمة الوصول غير مفعّلة. فعّل «Zevorix AI» من إعدادات الاتاحة ثم أعد الأمر.",
                    "The accessibility service is off. Enable \"Zevorix AI\" in Accessibility settings, then try again."
                )
            )
        }

        val ok = service.execute(command.action, command.argument)
        return if (ok) {
            CommandResult.Success(doneMessage(command, lang))
        } else {
            CommandResult.Failure(failMessage(command, lang))
        }
    }

    private fun doneMessage(command: ParsedCommand.Accessibility, lang: AppLanguage): String =
        when (command.action) {
            AccessibilityAction.BACK -> lang.tr("تم الرجوع.", "Went back.")
            AccessibilityAction.HOME -> lang.tr("الشاشة الرئيسية.", "Going home.")
            AccessibilityAction.RECENTS -> lang.tr("فتحت التطبيقات الأخيرة.", "Opened recent apps.")
            AccessibilityAction.NOTIFICATIONS -> lang.tr("فتحت الإشعارات.", "Opened notifications.")
            AccessibilityAction.QUICK_SETTINGS -> lang.tr("فتحت الإعدادات السريعة.", "Opened quick settings.")
            AccessibilityAction.SCREENSHOT -> lang.tr("التقطت لقطة للشاشة.", "Took a screenshot.")
            AccessibilityAction.LOCK_SCREEN -> lang.tr("قفلت الشاشة.", "Locked the screen.")
            AccessibilityAction.SCROLL_DOWN -> lang.tr("مررت للأسفل.", "Scrolled down.")
            AccessibilityAction.SCROLL_UP -> lang.tr("مررت للأعلى.", "Scrolled up.")
            AccessibilityAction.CLICK_TEXT -> lang.tr(
                "ضغطت على ${command.argument.orEmpty()}.",
                "Tapped ${command.argument.orEmpty()}."
            )
        }

    private fun failMessage(command: ParsedCommand.Accessibility, lang: AppLanguage): String =
        if (command.action == AccessibilityAction.CLICK_TEXT) {
            lang.tr(
                "لم أجد عنصراً يمكن الضغط عليه باسم ${command.argument.orEmpty()}.",
                "I couldn't find anything tappable called ${command.argument.orEmpty()}."
            )
        } else {
            lang.tr("تعذّر تنفيذ الأمر على الشاشة الحالية.", "I couldn't do that on the current screen.")
        }
}
''')

# 28. app/src/main/java/com/example/voiceassistant/commands/commands/AlarmCommand.kt
write_file("app/src/main/java/com/example/voiceassistant/commands/commands/AlarmCommand.kt", r'''package com.example.voiceassistant.commands.commands

import android.content.Context
import android.content.Intent
import android.provider.AlarmClock
import com.example.voiceassistant.commands.CommandResult
import com.example.voiceassistant.commands.ParsedCommand
import com.example.voiceassistant.commands.startNewTask
import com.example.voiceassistant.viewmodel.AppLanguage
import java.util.Locale

object AlarmCommand {

    fun execute(context: Context, command: ParsedCommand.Alarm, lang: AppLanguage): CommandResult {
        val hour = command.hour
        if (hour == null) {
            context.startNewTask(Intent(AlarmClock.ACTION_SHOW_ALARMS))
            return CommandResult.Success(
                lang.tr(
                    "فتحت المنبهات. قل مثلاً «اضبط منبه الساعة 7:30 صباحاً».",
                    "Opened your alarms. Say for example \"set an alarm for 7:30 am\"."
                )
            )
        }

        val intent = Intent(AlarmClock.ACTION_SET_ALARM).apply {
            putExtra(AlarmClock.EXTRA_HOUR, hour)
            putExtra(AlarmClock.EXTRA_MINUTES, command.minute)
            putExtra(AlarmClock.EXTRA_MESSAGE, "Zevorix AI")
            putExtra(AlarmClock.EXTRA_SKIP_UI, true)
        }
        context.startNewTask(intent)

        val time = String.format(Locale.US, "%02d:%02d", hour, command.minute)
        return CommandResult.Success(
            lang.tr("ضبطت المنبه على الساعة $time.", "Alarm set for $time.")
        )
    }
}
''')

# 29. app/src/main/java/com/example/voiceassistant/commands/commands/CallCommand.kt
write_file("app/src/main/java/com/example/voiceassistant/commands/commands/CallCommand.kt", r'''package com.example.voiceassistant.commands.commands

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.provider.ContactsContract.CommonDataKinds.Phone
import androidx.core.content.ContextCompat
import com.example.voiceassistant.commands.CommandResult
import com.example.voiceassistant.commands.ParsedCommand
import com.example.voiceassistant.commands.TextNormalizer
import com.example.voiceassistant.commands.startNewTask
import com.example.voiceassistant.viewmodel.AppLanguage

data class ContactMatch(val name: String, val number: String)

/** Finds a phone contact by (fuzzy, Arabic-aware) name. Requires READ_CONTACTS. */
object ContactResolver {

    private val phoneNumberRegex = Regex("^\\+?\\d{3,}$")

    fun hasPermission(context: Context): Boolean =
        ContextCompat.checkSelfPermission(context, Manifest.permission.READ_CONTACTS) ==
            PackageManager.PERMISSION_GRANTED

    /** Returns the cleaned number if [text] looks like a phone number, otherwise null. */
    fun asPhoneNumber(text: String): String? {
        val digits = text.replace(Regex("[\\s\\-().]"), "")
        return if (phoneNumberRegex.matches(digits)) digits else null
    }

    fun find(context: Context, query: String): ContactMatch? {
        val base = TextNormalizer.key(query.trim())
        // Arabic speech often glues the preposition to the name ("باحمد", "لاحمد"), so try without it too.
        val candidates = buildList {
            add(base)
            if (base.startsWith("\u0628") || base.startsWith("\u0644")) add(base.drop(1))
        }.filter { it.length >= 2 }.distinct()
        if (candidates.isEmpty()) return null

        var best: ContactMatch? = null
        var bestScore = 0

        context.contentResolver.query(
            Phone.CONTENT_URI,
            arrayOf(Phone.DISPLAY_NAME, Phone.NUMBER),
            null,
            null,
            null
        )?.use { cursor ->
            val nameIdx = cursor.getColumnIndexOrThrow(Phone.DISPLAY_NAME)
            val numberIdx = cursor.getColumnIndexOrThrow(Phone.NUMBER)
            while (cursor.moveToNext()) {
                val name = cursor.getString(nameIdx) ?: continue
                val number = cursor.getString(numberIdx) ?: continue
                val key = TextNormalizer.key(name)
                val words = key.split(" ")
                var score = 0
                for (c in candidates) {
                    val s = when {
                        key == c -> 4
                        words.any { it == c } -> 3
                        key.startsWith(c) || words.any { it.startsWith(c) } -> 2
                        key.contains(c) -> 1
                        else -> 0
                    }
                    if (s > score) score = s
                }
                if (score > bestScore) {
                    bestScore = score
                    best = ContactMatch(name, number)
                }
            }
        }
        return best
    }
}

object CallCommand {

    fun execute(context: Context, command: ParsedCommand.Call, lang: AppLanguage): CommandResult {
        val number: String
        val label: String

        val direct = ContactResolver.asPhoneNumber(command.target)
        if (direct != null) {
            number = direct
            label = direct
        } else {
            if (!ContactResolver.hasPermission(context)) {
                return CommandResult.NeedsPermission(
                    Manifest.permission.READ_CONTACTS,
                    lang.tr(
                        "أحتاج إذن جهات الاتصال للبحث عن الاسم.",
                        "I need contacts permission to look up that name."
                    )
                )
            }
            val match = ContactResolver.find(context, command.target)
                ?: return CommandResult.Failure(
                    lang.tr(
                        "لم أجد جهة اتصال باسم ${command.target}.",
                        "I couldn't find a contact named ${command.target}."
                    )
                )
            number = match.number
            label = match.name
        }

        val canCall = ContextCompat.checkSelfPermission(context, Manifest.permission.CALL_PHONE) ==
            PackageManager.PERMISSION_GRANTED
        val action = if (canCall) Intent.ACTION_CALL else Intent.ACTION_DIAL
        context.startNewTask(Intent(action, Uri.fromParts("tel", number, null)))

        return CommandResult.Success(
            if (canCall) {
                lang.tr("جارٍ الاتصال بـ ${label}.", "Calling ${label}.")
            } else {
                lang.tr("فتحت لوحة الاتصال برقم ${label}.", "Opened the dialer for ${label}.")
            }
        )
    }
}
''')

# 30. app/src/main/java/com/example/voiceassistant/commands/commands/SearchCommand.kt
write_file("app/src/main/java/com/example/voiceassistant/commands/commands/SearchCommand.kt", r'''package com.example.voiceassistant.commands.commands

import android.app.SearchManager
import android.content.ActivityNotFoundException
import android.content.Context
import android.content.Intent
import android.net.Uri
import com.example.voiceassistant.commands.CommandResult
import com.example.voiceassistant.commands.ParsedCommand
import com.example.voiceassistant.commands.startNewTask
import com.example.voiceassistant.viewmodel.AppLanguage

object SearchCommand {

    fun execute(context: Context, command: ParsedCommand.WebSearch, lang: AppLanguage): CommandResult {
        val query = command.query.trim()
        if (query.isEmpty()) {
            return CommandResult.Failure(
                lang.tr("ماذا تريد أن أبحث عنه؟", "What would you like me to search for?")
            )
        }

        try {
            val intent = Intent(Intent.ACTION_WEB_SEARCH).putExtra(SearchManager.QUERY, query)
            context.startNewTask(intent)
        } catch (e: ActivityNotFoundException) {
            val url = "https://www.google.com/search?q=" + Uri.encode(query)
            context.startNewTask(Intent(Intent.ACTION_VIEW, Uri.parse(url)))
        }

        return CommandResult.Success(
            lang.tr("أبحث عن ${query}.", "Searching for ${query}.")
        )
    }
}
''')

# 31. app/src/main/java/com/example/voiceassistant/commands/commands/SettingsCommand.kt
write_file("app/src/main/java/com/example/voiceassistant/commands/commands/SettingsCommand.kt", r'''package com.example.voiceassistant.commands.commands

import android.content.Context
import android.content.Intent
import android.provider.Settings
import com.example.voiceassistant.commands.CommandResult
import com.example.voiceassistant.commands.ParsedCommand
import com.example.voiceassistant.commands.startNewTask
import com.example.voiceassistant.service.ToggleResult
import com.example.voiceassistant.service.VoiceAccessibilityService
import com.example.voiceassistant.viewmodel.AppLanguage
import kotlinx.coroutines.delay

enum class SettingsTarget {
    MAIN, WIFI, BLUETOOTH, SOUND, DISPLAY, LOCATION, AIRPLANE, ACCESSIBILITY, BATTERY
}

object SettingsCommand {

    private const val FIRST_WAIT_MS = 900L
    private const val RETRY_WAIT_MS = 500L
    private const val MAX_ATTEMPTS = 6

    /**
     * "افتح الواي فاي" only opens the page. "شغل الواي فاي" / "اطفي البلوتوث" opens the page and then,
     * using the accessibility service, finds the switch by its name and clicks it.
     */
    suspend fun execute(
        context: Context,
        command: ParsedCommand.OpenSettings,
        lang: AppLanguage
    ): CommandResult {
        context.startNewTask(Intent(actionFor(command.target)))

        val wantOn = command.toggle
        val names = toggleNames(command.target)
        if (wantOn == null || names.isEmpty()) {
            return CommandResult.Success(
                lang.tr(
                    "فتحت ${labelAr(command.target)}.",
                    "Opened ${labelEn(command.target)}."
                )
            )
        }

        val service = VoiceAccessibilityService.instance
            ?: return CommandResult.Failure(
                lang.tr(
                    "فتحت ${labelAr(command.target)}. فعّل خدمة الوصول لكي أستطيع التشغيل والإطفاء بدون لمس.",
                    "Opened ${labelEn(command.target)}. Enable the accessibility service so I can switch it for you."
                )
            )

        val switchName = toggleLabel(command.target, lang)

        // Give the Settings screen time to appear, then look for the switch (retrying a few times).
        delay(FIRST_WAIT_MS)
        var result = ToggleResult.NOT_FOUND
        for (attempt in 0 until MAX_ATTEMPTS) {
            result = service.setToggleByName(names, wantOn)
            if (result != ToggleResult.NOT_FOUND) break
            delay(RETRY_WAIT_MS)
        }

        return when (result) {
            ToggleResult.SUCCESS -> CommandResult.Success(
                if (wantOn) {
                    lang.tr("شغّلت $switchName.", "Turned on $switchName.")
                } else {
                    lang.tr("أطفأت $switchName.", "Turned off $switchName.")
                }
            )

            ToggleResult.ALREADY_IN_STATE -> CommandResult.Success(
                if (wantOn) {
                    lang.tr("$switchName مفعّل بالفعل.", "$switchName is already on.")
                } else {
                    lang.tr("$switchName مطفأ بالفعل.", "$switchName is already off.")
                }
            )

            ToggleResult.NOT_FOUND -> CommandResult.Failure(
                lang.tr(
                    "فتحت الإعدادات لكني لم أجد مفتاح $switchName. اضغط عليه يدوياً.",
                    "I opened Settings but couldn't find the $switchName switch. Please tap it yourself."
                )
            )

            ToggleResult.FAILED -> CommandResult.Failure(
                lang.tr(
                    "وجدت مفتاح $switchName لكن تعذّر الضغط عليه.",
                    "I found the $switchName switch but couldn't tap it."
                )
            )
        }
    }

    private fun actionFor(target: SettingsTarget): String = when (target) {
        SettingsTarget.MAIN -> Settings.ACTION_SETTINGS
        SettingsTarget.WIFI -> Settings.ACTION_WIFI_SETTINGS
        SettingsTarget.BLUETOOTH -> Settings.ACTION_BLUETOOTH_SETTINGS
        SettingsTarget.SOUND -> Settings.ACTION_SOUND_SETTINGS
        SettingsTarget.DISPLAY -> Settings.ACTION_DISPLAY_SETTINGS
        SettingsTarget.LOCATION -> Settings.ACTION_LOCATION_SOURCE_SETTINGS
        SettingsTarget.AIRPLANE -> Settings.ACTION_AIRPLANE_MODE_SETTINGS
        SettingsTarget.ACCESSIBILITY -> Settings.ACTION_ACCESSIBILITY_SETTINGS
        SettingsTarget.BATTERY -> Settings.ACTION_BATTERY_SAVER_SETTINGS
    }

    /** Texts the Settings app may show next to the switch (Arabic names are already normalized). */
    private fun toggleNames(target: SettingsTarget): List<String> = when (target) {
        SettingsTarget.WIFI -> listOf("wi-fi", "wifi", "wi fi", "واي فاي", "وايفاي")
        SettingsTarget.BLUETOOTH -> listOf("bluetooth", "بلوتوث")
        SettingsTarget.AIRPLANE -> listOf("airplane", "flight mode", "الطيران")
        SettingsTarget.LOCATION -> listOf("use location", "location", "الموقع")
        SettingsTarget.BATTERY -> listOf("battery saver", "power saving", "توفير الطاقه", "توفير البطاريه")
        else -> emptyList()
    }

    private fun toggleLabel(target: SettingsTarget, lang: AppLanguage): String = when (target) {
        SettingsTarget.WIFI -> lang.tr("الواي فاي", "Wi-Fi")
        SettingsTarget.BLUETOOTH -> lang.tr("البلوتوث", "Bluetooth")
        SettingsTarget.AIRPLANE -> lang.tr("وضع الطيران", "Airplane mode")
        SettingsTarget.LOCATION -> lang.tr("الموقع", "Location")
        SettingsTarget.BATTERY -> lang.tr("توفير الطاقة", "Battery Saver")
        else -> lang.tr(labelAr(target), labelEn(target))
    }

    private fun labelAr(target: SettingsTarget): String = when (target) {
        SettingsTarget.MAIN -> "الإعدادات"
        SettingsTarget.WIFI -> "إعدادات الواي فاي"
        SettingsTarget.BLUETOOTH -> "إعدادات البلوتوث"
        SettingsTarget.SOUND -> "إعدادات الصوت"
        SettingsTarget.DISPLAY -> "إعدادات الشاشة"
        SettingsTarget.LOCATION -> "إعدادات الموقع"
        SettingsTarget.AIRPLANE -> "إعدادات وضع الطيران"
        SettingsTarget.ACCESSIBILITY -> "إعدادات الاتاحة"
        SettingsTarget.BATTERY -> "إعدادات البطارية"
    }

    private fun labelEn(target: SettingsTarget): String = when (target) {
        SettingsTarget.MAIN -> "Settings"
        SettingsTarget.WIFI -> "Wi-Fi settings"
        SettingsTarget.BLUETOOTH -> "Bluetooth settings"
        SettingsTarget.SOUND -> "Sound settings"
        SettingsTarget.DISPLAY -> "Display settings"
        SettingsTarget.LOCATION -> "Location settings"
        SettingsTarget.AIRPLANE -> "Airplane mode settings"
        SettingsTarget.ACCESSIBILITY -> "Accessibility settings"
        SettingsTarget.BATTERY -> "Battery settings"
    }
}
''')

# 32. app/src/main/java/com/example/voiceassistant/commands/commands/SmsCommand.kt
write_file("app/src/main/java/com/example/voiceassistant/commands/commands/SmsCommand.kt", r'''package com.example.voiceassistant.commands.commands

import android.Manifest
import android.content.Context
import android.content.Intent
import android.net.Uri
import com.example.voiceassistant.commands.CommandResult
import com.example.voiceassistant.commands.ParsedCommand
import com.example.voiceassistant.commands.startNewTask
import com.example.voiceassistant.viewmodel.AppLanguage

/**
 * Opens the default messaging app with the recipient and text pre-filled.
 * The user confirms by pressing send, so no SEND_SMS permission is needed.
 */
object SmsCommand {

    fun execute(context: Context, command: ParsedCommand.Sms, lang: AppLanguage): CommandResult {
        val number: String
        val label: String

        val direct = ContactResolver.asPhoneNumber(command.target)
        if (direct != null) {
            number = direct
            label = direct
        } else {
            if (!ContactResolver.hasPermission(context)) {
                return CommandResult.NeedsPermission(
                    Manifest.permission.READ_CONTACTS,
                    lang.tr(
                        "أحتاج إذن جهات الاتصال للبحث عن الاسم.",
                        "I need contacts permission to look up that name."
                    )
                )
            }
            val match = ContactResolver.find(context, command.target)
                ?: return CommandResult.Failure(
                    lang.tr(
                        "لم أجد جهة اتصال باسم ${command.target}.",
                        "I couldn't find a contact named ${command.target}."
                    )
                )
            number = match.number
            label = match.name
        }

        val intent = Intent(Intent.ACTION_SENDTO, Uri.fromParts("smsto", number, null)).apply {
            command.body?.takeIf { it.isNotBlank() }?.let { putExtra("sms_body", it) }
        }
        context.startNewTask(intent)

        return CommandResult.Success(
            lang.tr(
                "جهّزت الرسالة إلى ${label}. راجعها واضغط إرسال.",
                "Message to ${label} is ready. Review it and press send."
            )
        )
    }
}
''')

# 33. app/src/main/java/com/example/voiceassistant/commands/commands/InfoCommand.kt
write_file("app/src/main/java/com/example/voiceassistant/commands/commands/InfoCommand.kt", r'''package com.example.voiceassistant.commands.commands

import android.content.Context
import android.os.BatteryManager
import com.example.voiceassistant.commands.CommandResult
import com.example.voiceassistant.commands.ParsedCommand
import com.example.voiceassistant.viewmodel.AppLanguage
import java.text.DateFormat
import java.text.SimpleDateFormat
import java.util.Date

enum class InfoType { TIME, DATE, BATTERY, HELP, GREETING, THANKS }

object InfoCommand {

    fun execute(context: Context, command: ParsedCommand.Info, lang: AppLanguage): CommandResult =
        when (command.type) {
            InfoType.TIME -> {
                val time = DateFormat.getTimeInstance(DateFormat.SHORT, lang.locale).format(Date())
                CommandResult.Success(lang.tr("الساعة الآن $time.", "It's $time."))
            }

            InfoType.DATE -> {
                val date = SimpleDateFormat("EEEE d MMMM yyyy", lang.locale).format(Date())
                CommandResult.Success(lang.tr("اليوم $date.", "Today is $date."))
            }

            InfoType.BATTERY -> batteryInfo(context, lang)

            InfoType.HELP -> CommandResult.Success(
                lang.tr(
                    "يمكنني: الاتصال بجهة اتصال، إرسال رسالة، ضبط منبه، البحث في الويب، " +
                        "فتح التطبيقات والإعدادات، تشغيل وإطفاء الواي فاي والبلوتوث، " +
                        "والتحكم بالشاشة مثل رجوع والرئيسية والإشعارات والتمرير. " +
                        "ويمكنك أيضاً أن تسألني أي سؤال وسأجيبك.",
                    "I can: call a contact, send a message, set an alarm, search the web, " +
                        "open apps and settings, switch Wi-Fi and Bluetooth on or off, " +
                        "and control the screen: back, home, notifications, scrolling. " +
                        "You can also ask me anything and I'll answer."
                )
            )

            InfoType.GREETING -> CommandResult.Success(
                lang.tr("أهلاً بك! كيف أساعدك؟", "Hello! How can I help?")
            )

            InfoType.THANKS -> CommandResult.Success(
                lang.tr("عفواً! أنا في الخدمة.", "You're welcome!")
            )
        }

    private fun batteryInfo(context: Context, lang: AppLanguage): CommandResult {
        val manager = context.getSystemService(Context.BATTERY_SERVICE) as? BatteryManager
            ?: return CommandResult.Failure(
                lang.tr("لا أستطيع قراءة حالة البطارية.", "I can't read the battery status.")
            )
        val level = manager.getIntProperty(BatteryManager.BATTERY_PROPERTY_CAPACITY)
        val charging = manager.isCharging
        return CommandResult.Success(
            if (charging) {
                lang.tr(
                    "البطارية عند $level بالمئة وهي قيد الشحن.",
                    "Battery is at $level percent and charging."
                )
            } else {
                lang.tr("البطارية عند $level بالمئة.", "Battery is at $level percent.")
            }
        )
    }
}
''')

# 34. app/src/main/java/com/example/voiceassistant/commands/commands/AppLaunchCommand.kt
write_file("app/src/main/java/com/example/voiceassistant/commands/commands/AppLaunchCommand.kt", r'''package com.example.voiceassistant.commands.commands

import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.ResolveInfo
import com.example.voiceassistant.commands.CommandResult
import com.example.voiceassistant.commands.ParsedCommand
import com.example.voiceassistant.commands.TextNormalizer
import com.example.voiceassistant.commands.startNewTask
import com.example.voiceassistant.viewmodel.AppLanguage

object AppLaunchCommand {

    /** Spoken (usually Arabic) app names -> the English token found in the app's label / package. */
    private val aliases: Map<String, String> = mapOf(
        "واتساب" to "whatsapp",
        "واتس اب" to "whatsapp",
        "يوتيوب" to "youtube",
        "كروم" to "chrome",
        "جوجل كروم" to "chrome",
        "كاميرا" to "camera",
        "خرائط" to "maps",
        "خرائط جوجل" to "maps",
        "صور" to "photos",
        "معرض" to "gallery",
        "حاسبة" to "calculator",
        "ساعة" to "clock",
        "تقويم" to "calendar",
        "جيميل" to "gmail",
        "بريد" to "mail",
        "تيليجرام" to "telegram",
        "تلجرام" to "telegram",
        "انستقرام" to "instagram",
        "انستجرام" to "instagram",
        "فيسبوك" to "facebook",
        "ماسنجر" to "messenger",
        "سناب شات" to "snapchat",
        "سناب" to "snapchat",
        "تويتر" to "twitter",
        "تيك توك" to "tiktok",
        "نتفليكس" to "netflix",
        "سبوتيفاي" to "spotify",
        "هاتف" to "phone",
        "جهات الاتصال" to "contacts",
        "رسائل" to "messages",
        "ملفات" to "files",
        "ملاحظات" to "notes",
        "بلاي ستور" to "play store",
        "متجر بلاي" to "play store",
        "زوم" to "zoom"
    )

    private val normalizedAliases: Map<String, String> by lazy {
        aliases.mapKeys { TextNormalizer.key(it.key) }
    }

    fun execute(context: Context, command: ParsedCommand.LaunchApp, lang: AppLanguage): CommandResult {
        val pm = context.packageManager
        val launcher = Intent(Intent.ACTION_MAIN).addCategory(Intent.CATEGORY_LAUNCHER)
        val apps: List<ResolveInfo> = pm.queryIntentActivities(launcher, 0)

        val base = TextNormalizer.key(command.appName).trim()
        val stripped = base.removePrefix("\u0627\u0644") // leading "ال"
        val candidates = listOfNotNull(
            base,
            stripped,
            normalizedAliases[base],
            normalizedAliases[stripped]
        ).filter { it.length >= 2 }.distinct()

        var best: ResolveInfo? = null
        var bestScore = 0
        for (info in apps) {
            val label = TextNormalizer.key(info.loadLabel(pm).toString())
            val labelStripped = label.removePrefix("\u0627\u0644")
            val pkg = info.activityInfo.packageName.lowercase()

            var score = 0
            for (c in candidates) {
                val s = when {
                    label == c || labelStripped == c -> 4
                    label.startsWith(c) || labelStripped.startsWith(c) -> 3
                    label.contains(c) -> 2
                    c.length >= 3 && pkg.contains(c.replace(" ", "")) -> 1
                    label.length >= 3 && c.contains(label) -> 1
                    else -> 0
                }
                if (s > score) score = s
            }
            if (score > bestScore) {
                bestScore = score
                best = info
            }
        }

        val match = best ?: return CommandResult.Failure(
            lang.tr(
                "لم أجد تطبيقاً باسم ${command.appName}.",
                "I couldn't find an app called ${command.appName}."
            )
        )

        val appInfo = match.activityInfo
        val launch = Intent(Intent.ACTION_MAIN)
            .addCategory(Intent.CATEGORY_LAUNCHER)
            .setComponent(ComponentName(appInfo.packageName, appInfo.name))
        context.startNewTask(launch)

        val appLabel = match.loadLabel(pm).toString()
        return CommandResult.Success(
            lang.tr("فتحت ${appLabel}.", "Opening ${appLabel}.")
        )
    }
}
''')

# 35. app/src/main/java/com/example/voiceassistant/ui/theme/Color.kt
write_file("app/src/main/java/com/example/voiceassistant/ui/theme/Color.kt", r'''package com.example.voiceassistant.ui.theme

import androidx.compose.ui.graphics.Color

val Indigo40 = Color(0xFF4F5BD5)
val IndigoOn40 = Color(0xFFFFFFFF)
val IndigoContainer40 = Color(0xFFE0E0FF)
val Teal40 = Color(0xFF00796B)
val TealContainer40 = Color(0xFFB2F2E8)
val Red40 = Color(0xFFBA1A1A)
val RedContainer40 = Color(0xFFFFDAD6)
val Surface40 = Color(0xFFFBFAFF)
val SurfaceVariant40 = Color(0xFFE4E1EC)
val OnSurface40 = Color(0xFF1B1B1F)
val OnSurfaceVariant40 = Color(0xFF46464F)
val Outline40 = Color(0xFF777680)

val Indigo80 = Color(0xFFBBC3FF)
val IndigoOn80 = Color(0xFF0A1480)
val IndigoContainer80 = Color(0xFF2E3AB0)
val Teal80 = Color(0xFF4FDBC8)
val TealContainer80 = Color(0xFF005048)
val Red80 = Color(0xFFFFB4AB)
val RedContainer80 = Color(0xFF93000A)
val Surface80 = Color(0xFF121317)
val SurfaceVariant80 = Color(0xFF46464F)
val OnSurface80 = Color(0xFFE4E1E6)
val OnSurfaceVariant80 = Color(0xFFC7C5D0)
val Outline80 = Color(0xFF918F9A)
''')

# 36. app/src/main/java/com/example/voiceassistant/ui/theme/Type.kt
write_file("app/src/main/java/com/example/voiceassistant/ui/theme/Type.kt", r'''package com.example.voiceassistant.ui.theme

import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp

val Typography = Typography(
    titleLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.SemiBold,
        fontSize = 22.sp,
        lineHeight = 28.sp
    ),
    bodyLarge = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 24.sp
    ),
    bodyMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Normal,
        fontSize = 14.sp,
        lineHeight = 20.sp
    ),
    labelMedium = TextStyle(
        fontFamily = FontFamily.Default,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        lineHeight = 16.sp
    )
)
''')

# 37. app/src/main/java/com/example/voiceassistant/ui/theme/Theme.kt
write_file("app/src/main/java/com/example/voiceassistant/ui/theme/Theme.kt", r'''package com.example.voiceassistant.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable

private val LightColors = lightColorScheme(
    primary = Indigo40,
    onPrimary = IndigoOn40,
    primaryContainer = IndigoContainer40,
    tertiary = Teal40,
    tertiaryContainer = TealContainer40,
    error = Red40,
    errorContainer = RedContainer40,
    background = Surface40,
    surface = Surface40,
    onBackground = OnSurface40,
    onSurface = OnSurface40,
    surfaceVariant = SurfaceVariant40,
    onSurfaceVariant = OnSurfaceVariant40,
    outline = Outline40
)

private val DarkColors = darkColorScheme(
    primary = Indigo80,
    onPrimary = IndigoOn80,
    primaryContainer = IndigoContainer80,
    tertiary = Teal80,
    tertiaryContainer = TealContainer80,
    error = Red80,
    errorContainer = RedContainer80,
    background = Surface80,
    surface = Surface80,
    onBackground = OnSurface80,
    onSurface = OnSurface80,
    surfaceVariant = SurfaceVariant80,
    onSurfaceVariant = OnSurfaceVariant80,
    outline = Outline80
)

@Composable
fun VoiceAssistantTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColors else LightColors,
        typography = Typography,
        content = content
    )
}
''')

# 38. app/src/main/java/com/example/voiceassistant/ui/components/ChatBubble.kt
write_file("app/src/main/java/com/example/voiceassistant/ui/components/ChatBubble.kt", r'''package com.example.voiceassistant.ui.components

import androidx.compose.foundation.text.selection.SelectionContainer
import android.graphics.BitmapFactory
import android.net.Uri
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.widthIn
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.example.voiceassistant.data.models.CodeBlock
import com.example.voiceassistant.data.models.Message
import com.example.voiceassistant.viewmodel.AppLanguage
import java.io.File

@Composable
fun ChatBubble(
    message: Message,
    modifier: Modifier = Modifier,
    language: AppLanguage = AppLanguage.ARABIC,
    /** Called after "Apply to file" succeeded: (file name, original Uri, last note). */
    onFileApplied: (fileName: String, uri: String?, summary: String) -> Unit = { _, _, _ -> }
) {
    val isUser = message.isUser
    val container = if (isUser) {
        MaterialTheme.colorScheme.primary
    } else {
        MaterialTheme.colorScheme.surfaceVariant
    }
    val content = if (isUser) {
        MaterialTheme.colorScheme.onPrimary
    } else {
        MaterialTheme.colorScheme.onSurfaceVariant
    }
    val shape = RoundedCornerShape(
        topStart = 18.dp,
        topEnd = 18.dp,
        bottomStart = if (isUser) 18.dp else 4.dp,
        bottomEnd = if (isUser) 4.dp else 18.dp
    )

    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(6.dp)
    ) {
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = if (isUser) Arrangement.End else Arrangement.Start
        ) {
            Surface(
                color = container,
                contentColor = content,
                shape = shape,
                modifier = Modifier.widthIn(max = 320.dp)
            ) {
                SelectionContainer {
                    Text(
                        text = message.text,
                        modifier = Modifier.padding(horizontal = 14.dp, vertical = 10.dp),
                        style = MaterialTheme.typography.bodyLarge
                    )
                }
            }
        }
        message.code.forEach { block ->
            CodeCard(block, language) { name, uri -> onFileApplied(name, uri, message.text) }
        }
        message.imagePath?.let { path -> ImageCard(path, language) }
    }
}

/** Decodes a picture no wider than ~1080 px, so big generated images don't fill the memory. */
private fun decodeScaledBitmap(path: String, maxWidth: Int = 1080): android.graphics.Bitmap? {
    val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
    BitmapFactory.decodeFile(path, bounds)
    var sample = 1
    while (bounds.outWidth / (sample * 2) >= maxWidth) sample *= 2
    return BitmapFactory.decodeFile(path, BitmapFactory.Options().apply { inSampleSize = sample })
}

/** Shows a generated picture with a Save button. */
@Composable
private fun ImageCard(path: String, language: AppLanguage) {
    val context = LocalContext.current
    var bitmap by remember(path) { mutableStateOf<androidx.compose.ui.graphics.ImageBitmap?>(null) }
    LaunchedEffect(path) {
        bitmap = withContext(Dispatchers.IO) {
            try {
                decodeScaledBitmap(path)?.asImageBitmap()
            } catch (e: Exception) {
                null
            }
        }
    }

    val saver = rememberLauncherForActivityResult(
        ActivityResultContracts.CreateDocument("image/png")
    ) { uri ->
        if (uri != null) {
            val ok = try {
                context.contentResolver.openOutputStream(uri)?.use { out ->
                    out.write(File(path).readBytes())
                }
                true
            } catch (e: Exception) {
                false
            }
            Toast.makeText(
                context,
                if (ok) language.tr("تم الحفظ", "Saved") else language.tr("تعذّر الحفظ", "Couldn't save"),
                Toast.LENGTH_SHORT
            ).show()
        }
    }

    val currentBitmap = bitmap ?: return

    Surface(
        color = MaterialTheme.colorScheme.surfaceVariant,
        shape = RoundedCornerShape(12.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        Column {
            Image(
                bitmap = currentBitmap,
                contentDescription = null,
                contentScale = ContentScale.FillWidth,
                modifier = Modifier.fillMaxWidth()
            )
            TextButton(onClick = { saver.launch("image_" + System.currentTimeMillis() + ".png") }) {
                Text(language.tr("حفظ الصورة", "Save image"))
            }
        }
    }
}

/** Shows one code block (always left-to-right) with Copy and Save buttons. */
@Composable
private fun CodeCard(
    block: CodeBlock,
    language: AppLanguage,
    onApplied: (fileName: String, uri: String?) -> Unit = { _, _ -> }
) {
    val context = LocalContext.current
    val clipboard = LocalClipboardManager.current
    var editableCode by remember { mutableStateOf(block.content) }
    var copied by remember { mutableStateOf(false) }
    var applied by remember { mutableStateOf(false) }
    val ext = extensionFor(block.language)
    val fileName = block.fileName ?: when {
        ext == "html" -> "index.html"
        block.language.equals("setup", ignoreCase = true) ||
            (ext == "py" && block.content.contains("setup(")) -> "setup.py"
        else -> "code.$ext"
    }

    val saver = rememberLauncherForActivityResult(
        ActivityResultContracts.CreateDocument("application/octet-stream")
    ) { uri ->
        if (uri != null) {
            val ok = try {
                context.contentResolver.openOutputStream(uri)?.use {
                    it.write(editableCode.toByteArray(Charsets.UTF_8))
                }
                true
            } catch (e: Exception) {
                false
            }
            Toast.makeText(
                context,
                if (ok) language.tr("تم الحفظ", "Saved") else language.tr("تعذّر الحفظ", "Couldn't save"),
                Toast.LENGTH_SHORT
            ).show()
        }
    }

    val buttonColors = ButtonDefaults.textButtonColors(
        contentColor = MaterialTheme.colorScheme.inversePrimary
    )

    Surface(
        color = MaterialTheme.colorScheme.inverseSurface,
        contentColor = MaterialTheme.colorScheme.inverseOnSurface,
        shape = RoundedCornerShape(12.dp),
        modifier = Modifier.fillMaxWidth()
    ) {
        CompositionLocalProvider(LocalLayoutDirection provides LayoutDirection.Ltr) {
            Column {
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(start = 12.dp, end = 4.dp),
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(
                        text = block.fileName ?: block.language.ifBlank { "code" },
                        style = MaterialTheme.typography.labelMedium
                    )
                    Row {
                        TextButton(
                            colors = buttonColors,
                            onClick = {
                                clipboard.setText(AnnotatedString(editableCode))
                                copied = true
                            }
                        ) {
                            Text(
                                if (copied) language.tr("تم النسخ", "Copied")
                                else language.tr("نسخ", "Copy")
                            )
                        }
                        TextButton(
                            colors = buttonColors,
                            onClick = { saver.launch(fileName) }
                        ) {
                            Text(language.tr("حفظ", "Save"))
                        }
                        // The edited version of a file the user opened: write it straight back to the original.
                        if (block.sourceUri != null) {
                            TextButton(
                                colors = buttonColors,
                                onClick = {
                                    val ok = try {
                                        context.contentResolver
                                            .openOutputStream(Uri.parse(block.sourceUri), "wt")
                                            ?.use { it.write((editableCode + "\n").toByteArray(Charsets.UTF_8)) } != null
                                    } catch (e: Exception) {
                                        false
                                    }
                                    applied = ok
                                    if (ok) onApplied(fileName, block.sourceUri)
                                    Toast.makeText(
                                        context,
                                        if (ok) language.tr("تم تحديث الملف الأصلي", "Original file updated")
                                        else language.tr("تعذّر الكتابة على الملف الأصلي، استخدم حفظ", "Couldn't write to the original file, use Save"),
                                        Toast.LENGTH_SHORT
                                    ).show()
                                }
                            ) {
                                Text(
                                    if (applied) language.tr("تم التطبيق", "Applied")
                                    else language.tr("تطبيق على الملف", "Apply to file")
                                )
                            }
                        }
                    }
                }
                BasicTextField(
                    value = editableCode,
                    onValueChange = { editableCode = it },
                    textStyle = TextStyle(
                        fontFamily = FontFamily.Monospace,
                        fontSize = 12.sp,
                        color = MaterialTheme.colorScheme.inverseOnSurface
                    ),
                    modifier = Modifier
                        .horizontalScroll(rememberScrollState())
                        .padding(12.dp)
                )
            }
        }
    }
}

private fun extensionFor(lang: String): String = when (lang.lowercase()) {
    "html" -> "html"
    "css" -> "css"
    "javascript", "js" -> "js"
    "typescript", "ts" -> "ts"
    "kotlin", "kt" -> "kt"
    "kts" -> "kts"
    "java" -> "java"
    "python", "py" -> "py"
    "xml" -> "xml"
    "json" -> "json"
    "bash", "sh", "shell" -> "sh"
    "c" -> "c"
    "cpp", "c++" -> "cpp"
    "sql" -> "sql"
    "yaml", "yml" -> "yml"
    "markdown", "md" -> "md"
    "setup" -> "py"
    "php" -> "php"
    "go" -> "go"
    "rust", "rs" -> "rs"
    "swift" -> "swift"
    "dart" -> "dart"
    "bat", "batch" -> "bat"
    "gradle" -> "gradle"
    "toml" -> "toml"
    "ini" -> "ini"
    else -> "txt"
}

''')

# 39. app/src/main/java/com/example/voiceassistant/ui/components/MicButton.kt
write_file("app/src/main/java/com/example/voiceassistant/ui/components/MicButton.kt", r'''package com.example.voiceassistant.ui.components

import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.VolumeUp
import androidx.compose.material.icons.filled.Mic
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.FilledIconButton
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.scale
import androidx.compose.ui.unit.dp
import com.example.voiceassistant.viewmodel.AssistantStatus

@Composable
fun MicButton(
    status: AssistantStatus,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    compact: Boolean = false
) {
    val listening = status == AssistantStatus.LISTENING

    // compact = small round button that sits inside the chat input bar
    val boxSize = if (compact) 48.dp else 120.dp
    val buttonSize = if (compact) 44.dp else 80.dp
    val iconSize = if (compact) 22.dp else 36.dp
    val progressSize = if (compact) 22.dp else 32.dp

    val transition = rememberInfiniteTransition(label = "micPulse")
    val pulse by transition.animateFloat(
        initialValue = 1f,
        targetValue = if (listening) (if (compact) 1.3f else 1.45f) else 1f,
        animationSpec = infiniteRepeatable(
            animation = tween(durationMillis = 900),
            repeatMode = RepeatMode.Reverse
        ),
        label = "micPulseScale"
    )

    val containerColor = when (status) {
        AssistantStatus.LISTENING -> MaterialTheme.colorScheme.error
        AssistantStatus.ERROR -> MaterialTheme.colorScheme.errorContainer
        else -> MaterialTheme.colorScheme.primary
    }
    val contentColor = when (status) {
        AssistantStatus.ERROR -> MaterialTheme.colorScheme.error
        AssistantStatus.LISTENING -> MaterialTheme.colorScheme.onError
        else -> MaterialTheme.colorScheme.onPrimary
    }

    Box(modifier = modifier.size(boxSize), contentAlignment = Alignment.Center) {
        if (listening) {
            Box(
                modifier = Modifier
                    .size(buttonSize)
                    .scale(pulse)
                    .background(MaterialTheme.colorScheme.error.copy(alpha = 0.25f), CircleShape)
            )
        }
        FilledIconButton(
            onClick = onClick,
            modifier = Modifier.size(buttonSize),
            colors = IconButtonDefaults.filledIconButtonColors(
                containerColor = containerColor,
                contentColor = contentColor
            )
        ) {
            when (status) {
                AssistantStatus.PROCESSING -> CircularProgressIndicator(
                    modifier = Modifier.size(progressSize),
                    color = contentColor,
                    strokeWidth = if (compact) 2.dp else 3.dp
                )
                AssistantStatus.LISTENING -> Icon(
                    imageVector = Icons.Filled.Stop,
                    contentDescription = "Stop",
                    modifier = Modifier.size(iconSize)
                )
                AssistantStatus.SPEAKING -> Icon(
                    imageVector = Icons.AutoMirrored.Filled.VolumeUp,
                    contentDescription = "Speaking",
                    modifier = Modifier.size(iconSize)
                )
                else -> Icon(
                    imageVector = Icons.Filled.Mic,
                    contentDescription = "Microphone",
                    modifier = Modifier.size(iconSize)
                )
            }
        }
    }
}
''')

# 40. app/src/main/java/com/example/voiceassistant/ui/components/StatusIndicator.kt
write_file("app/src/main/java/com/example/voiceassistant/ui/components/StatusIndicator.kt", r'''package com.example.voiceassistant.ui.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.example.voiceassistant.viewmodel.AppLanguage
import com.example.voiceassistant.viewmodel.AssistantStatus

@Composable
fun StatusIndicator(
    status: AssistantStatus,
    partialText: String,
    errorMessage: String?,
    language: AppLanguage,
    modifier: Modifier = Modifier
) {
    val text = when (status) {
        AssistantStatus.IDLE -> language.tr("اضغط على الميكروفون وتحدث", "Tap the mic and speak")
        AssistantStatus.LISTENING -> partialText.ifBlank { language.tr("أستمع إليك…", "Listening…") }
        AssistantStatus.PROCESSING -> language.tr("جارٍ المعالجة…", "Working on it…")
        AssistantStatus.SPEAKING -> language.tr("أتحدث…", "Speaking…")
        AssistantStatus.ERROR -> errorMessage ?: language.tr("حدث خطأ", "Something went wrong")
    }

    val dotColor by animateColorAsState(
        targetValue = when (status) {
            AssistantStatus.IDLE -> MaterialTheme.colorScheme.outline
            AssistantStatus.LISTENING -> MaterialTheme.colorScheme.error
            AssistantStatus.PROCESSING -> MaterialTheme.colorScheme.tertiary
            AssistantStatus.SPEAKING -> MaterialTheme.colorScheme.primary
            AssistantStatus.ERROR -> MaterialTheme.colorScheme.error
        },
        label = "statusDotColor"
    )

    Row(
        modifier = modifier,
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.Center
    ) {
        Box(
            modifier = Modifier
                .size(10.dp)
                .background(dotColor, CircleShape)
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = text,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            maxLines = 2,
            overflow = TextOverflow.Ellipsis,
            textAlign = TextAlign.Center
        )
    }
}
''')

# 41. app/src/main/java/com/example/voiceassistant/ui/components/LanguageToggle.kt
write_file("app/src/main/java/com/example/voiceassistant/ui/components/LanguageToggle.kt", r'''package com.example.voiceassistant.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.voiceassistant.viewmodel.AppLanguage

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LanguageToggle(
    selected: AppLanguage,
    onSelected: (AppLanguage) -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        AppLanguage.entries.forEach { language ->
            FilterChip(
                selected = language == selected,
                onClick = { onSelected(language) },
                label = { Text(language.label) }
            )
        }
    }
}
''')

# 42. app/src/main/java/com/example/voiceassistant/ui/MainScreen.kt
write_file("app/src/main/java/com/example/voiceassistant/ui/MainScreen.kt", r'''package com.example.voiceassistant.ui

import android.app.Activity
import android.content.Intent
import android.provider.Settings
import androidx.compose.ui.platform.LocalContext
import com.example.voiceassistant.antitheft.SecuritySettingsActivity
import com.example.voiceassistant.ui.components.AiSettingsSheet
import androidx.compose.material.icons.filled.Settings as SettingsIcon
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.animation.core.animateDpAsState
import androidx.compose.foundation.clickable
import androidx.compose.foundation.interaction.MutableInteractionSource
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.ime
import androidx.compose.ui.platform.LocalDensity
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.isImeVisible
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.lazy.rememberLazyListState
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.filled.Psychology
import androidx.compose.material3.ModalBottomSheet
import com.example.voiceassistant.data.models.MemoryEntry
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.DeleteSweep
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Menu
import androidx.compose.material.icons.filled.RecordVoiceOver
import androidx.compose.material.icons.filled.Security
import androidx.compose.material3.Button
import androidx.compose.material3.DrawerValue
import androidx.compose.material3.ModalDrawerSheet
import androidx.compose.material3.ModalNavigationDrawer
import androidx.compose.material3.rememberDrawerState
import androidx.compose.material3.InputChip
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LocalContentColor
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.activity.compose.BackHandler
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.derivedStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import kotlinx.coroutines.launch
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalFocusManager
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.platform.LocalLayoutDirection
import androidx.compose.ui.unit.LayoutDirection
import androidx.compose.ui.unit.dp
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import com.example.voiceassistant.data.SavedSession
import com.example.voiceassistant.speech.rememberAudioPermissionRequest
import com.example.voiceassistant.ui.components.AnimeAvatar
import com.example.voiceassistant.ui.components.AnimeCharacters
import com.example.voiceassistant.ui.components.CharacterThumbnail
import androidx.compose.ui.layout.onSizeChanged
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.foundation.background
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.ui.draw.clip
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.HorizontalDivider
import com.example.voiceassistant.ui.components.ChatBubble
import com.example.voiceassistant.ui.components.ChatInputBar
import com.example.voiceassistant.ui.components.CharacterMenuButton
import com.example.voiceassistant.ui.components.LanguageToggle
import com.example.voiceassistant.ui.components.StatusIndicator
import com.example.voiceassistant.ui.components.rememberCharacterSelection
import com.example.voiceassistant.viewmodel.AppLanguage
import com.example.voiceassistant.viewmodel.MainViewModel

@OptIn(ExperimentalMaterial3Api::class, ExperimentalLayoutApi::class)
@Composable
fun MainScreen(
    autoListenToken: Int = 0,
    viewModel: MainViewModel = viewModel()
) {
    val state by viewModel.uiState.collectAsStateWithLifecycle()
    val savedSessions by viewModel.savedSessions.collectAsStateWithLifecycle()
    val drawerState = rememberDrawerState(DrawerValue.Closed)
    val drawerScope = rememberCoroutineScope()
    val securityEnabled by viewModel.securityEnabled.collectAsStateWithLifecycle()
    var showSecurityMenu by remember { mutableStateOf(false) }
    val wakeWordEnabled by viewModel.wakeWordEnabled.collectAsStateWithLifecycle()
    var showWakeWordMenu by remember { mutableStateOf(false) }
    var showMemorySheet by remember { mutableStateOf(false) }
    var showAiSettings by remember { mutableStateOf(false) }
    var showSettingsMenu by remember { mutableStateOf(false) }
    val context = LocalContext.current
    val listState = rememberLazyListState()
    // The chat list reads only these: live speech text and status changes no longer redraw every bubble.
    val chatMessages by remember { derivedStateOf { state.messages } }
    val chatLanguage by remember { derivedStateOf { state.language } }
    val onFileApplied = remember(viewModel) { viewModel::onFileApplied }
    // While the keyboard is open, the status / language / hands-free controls are hidden so the chat stays visible.
    // The microphone lives inside the input bar, so it is never hidden.
    // Real keyboard height in pixels: WindowInsets.isImeVisible can stay true after the keyboard is hidden on some devices.
    val imeVisible = WindowInsets.ime.getBottom(LocalDensity.current) > 0
    var inputFocused by remember { mutableStateOf(false) }
    // Focus the system gives the text field right at startup is not "typing": ignore it for the first 2 seconds.
    val screenOpenedAt = remember { System.currentTimeMillis() }
    val focusManager = LocalFocusManager.current
    // الشخصية المختارة (محفوظة في SharedPreferences) + حجم الشخصية: كبيرة عندما تكون المحادثة فارغة.
    val characters = rememberCharacterSelection()
    val avatarTap = remember { MutableInteractionSource() }
    // The welcome message doesn't count: the avatar stays big until the user says or types something.
    val conversationEmpty = state.messages.none { it.isUser }
    val keyboard = LocalSoftwareKeyboardController.current
    // Compact mode: keyboard open OR the text field has focus (works even if the IME insets aren't reported).
    val typing = imeVisible || inputFocused
    // The avatar shows (full size) only in a brand-new chat; it hides while typing and while a settings sheet is open.
    val keyboardOpen = typing
    val showAvatar = conversationEmpty && !keyboardOpen && !showAiSettings && !showMemorySheet
    BackHandler(enabled = inputFocused) {
        keyboard?.hide()
        focusManager.clearFocus()
    }

    // Microphone permission, then start / stop listening (mic button).
    val requestMic = rememberAudioPermissionRequest(
        onGranted = { viewModel.toggleListening() },
        onDenied = { viewModel.onMicPermissionDenied() }
    )

    // Same permission, but used when the app is opened as the default assistant: start listening at once.
    val requestMicAuto = rememberAudioPermissionRequest(
        onGranted = { viewModel.startHandsFree() },
        onDenied = { viewModel.onMicPermissionDenied() }
    )

    // Same permission, used by the wake-word switch: the service needs the microphone before it starts.
    val requestMicWakeWord = rememberAudioPermissionRequest(
        onGranted = { viewModel.toggleWakeWord(true) },
        onDenied = { viewModel.onMicPermissionDenied() }
    )

    // Runtime permissions requested on behalf of a command (e.g. contacts).
    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted -> viewModel.onPermissionResult(granted) }

    LifecycleEventEffect(Lifecycle.Event.ON_RESUME) {
        viewModel.setForeground(true)
        viewModel.refreshAccessibilityStatus()
    }

    LifecycleEventEffect(Lifecycle.Event.ON_PAUSE) {
        viewModel.setForeground(false)
    }

    // Opened through the default-assistant gesture -> listen immediately.
    LaunchedEffect(autoListenToken) {
        if (autoListenToken > 0) requestMicAuto()
    }

    // The text field can grab focus when the app starts: release it so the avatar isn't hidden.
    val emptyNow = rememberUpdatedState(conversationEmpty)
    LaunchedEffect(Unit) {
        // انتظر جزءاً من الثانية حتى تستقر الواجهة، ثم أغلق لوحة المفاتيح فوراً إذا كانت المحادثة جديدة
        kotlinx.coroutines.delay(150)
        if (emptyNow.value) {
            focusManager.clearFocus(force = true)
        }
    }

    LaunchedEffect(state.pendingPermission) {
        state.pendingPermission?.let { permissionLauncher.launch(it) }
    }

    LaunchedEffect(Unit) {
        viewModel.backgroundRequests.collect {
            (context as? Activity)?.moveTaskToBack(true)
        }
    }

    LaunchedEffect(state.messages.size) {
        if (state.messages.isNotEmpty() && !conversationEmpty) {
            listState.animateScrollToItem(state.messages.lastIndex)
        }
    }

    // ظهور/اختفاء لوحة المفاتيح: نثبّت آخر رسالة ظاهرة فوراً (بدون أنيميشن).
    LaunchedEffect(typing) {
        if (state.messages.isNotEmpty() && !conversationEmpty) {
            listState.scrollToItem(state.messages.lastIndex)
        }
    }

    val direction = if (state.language == AppLanguage.ARABIC) LayoutDirection.Rtl else LayoutDirection.Ltr

    CompositionLocalProvider(LocalLayoutDirection provides direction) {
        if (showMemorySheet) {
            MemorySheet(
                facts = state.memories,
                projects = state.recentProjects,
                language = state.language,
                onDelete = viewModel::removeMemory,
                onDismiss = { showMemorySheet = false }
            )
        }
        if (showAiSettings) {
            AiSettingsSheet(
                language = state.language,
                onDismiss = { showAiSettings = false }
            )
        }
        ModalNavigationDrawer(
            drawerState = drawerState,
            drawerContent = {
                SessionsDrawerContent(
                    sessions = savedSessions,
                    language = state.language,
                    onNewChat = {
                        viewModel.startNewChat()
                        drawerScope.launch { drawerState.close() }
                    },
                    onOpen = { id ->
                        viewModel.loadSession(id)
                        drawerScope.launch { drawerState.close() }
                    },
                    onDelete = viewModel::deleteSession,
                    onOpenSettings = {
                        drawerScope.launch { drawerState.close() }
                        showAiSettings = true
                    }
                )
            }
        ) {
        Scaffold(
            modifier = Modifier.imePadding(),
            topBar = {
                TopAppBar(
                    title = {
                        Text(
                            text = state.language.tr("Zevorix AI", "Zevorix AI"),
                            style = MaterialTheme.typography.titleLarge
                        )
                    },
                    navigationIcon = {
                        IconButton(onClick = { drawerScope.launch { drawerState.open() } }) {
                            Icon(
                                imageVector = Icons.Filled.Menu,
                                contentDescription = state.language.tr("القائمة", "Menu")
                            )
                        }
                    },
                    actions = {
                        Box {
                            IconButton(onClick = { showSettingsMenu = true }) {
                                Icon(
                                    imageVector = Icons.Filled.SettingsIcon,
                                    contentDescription = state.language.tr("الإعدادات", "Settings"),
                                    tint = if (securityEnabled || wakeWordEnabled) {
                                        MaterialTheme.colorScheme.primary
                                    } else {
                                        LocalContentColor.current
                                    }
                                )
                            }
                            DropdownMenu(
                                expanded = showSettingsMenu,
                                onDismissRequest = { showSettingsMenu = false }
                            ) {
                                DropdownMenuItem(
                                    text = { Text(state.language.tr("الحماية", "Protection")) },
                                    leadingIcon = { Icon(Icons.Filled.Security, contentDescription = null) },
                                    onClick = { viewModel.toggleSecurityMonitoring(!securityEnabled) },
                                    trailingIcon = {
                                        Switch(
                                            checked = securityEnabled,
                                            onCheckedChange = viewModel::toggleSecurityMonitoring
                                        )
                                    }
                                )
                                DropdownMenuItem(
                                    text = { Text(state.language.tr("الحماية من السرقة", "Anti-theft")) },
                                    onClick = {
                                        showSettingsMenu = false
                                        context.startActivity(
                                            Intent(context, SecuritySettingsActivity::class.java)
                                        )
                                    }
                                )
                                DropdownMenuItem(
                                    text = { Text(state.language.tr("فحص التطبيقات", "Scan apps")) },
                                    onClick = {
                                        showSettingsMenu = false
                                        viewModel.scanInstalledApps()
                                    }
                                )
                                DropdownMenuItem(
                                    text = { Text(state.language.tr("الاستدعاء الصوتي", "Wake word")) },
                                    leadingIcon = { Icon(Icons.Filled.RecordVoiceOver, contentDescription = null) },
                                    onClick = {
                                        if (wakeWordEnabled) viewModel.toggleWakeWord(false) else requestMicWakeWord()
                                    },
                                    trailingIcon = {
                                        Switch(
                                            checked = wakeWordEnabled,
                                            onCheckedChange = { on ->
                                                if (on) requestMicWakeWord() else viewModel.toggleWakeWord(false)
                                            }
                                        )
                                    }
                                )
                                HorizontalDivider()
                                DropdownMenuItem(
                                    text = { Text(state.language.tr("نماذج الذكاء الاصطناعي", "AI models")) },
                                    leadingIcon = { Icon(Icons.Filled.SettingsIcon, contentDescription = null) },
                                    onClick = {
                                        showSettingsMenu = false
                                        showAiSettings = true
                                    }
                                )
                                DropdownMenuItem(
                                    text = { Text(state.language.tr("الذاكرة", "Memory")) },
                                    leadingIcon = { Icon(Icons.Filled.Psychology, contentDescription = null) },
                                    onClick = {
                                        showSettingsMenu = false
                                        showMemorySheet = true
                                    }
                                )
                                DropdownMenuItem(
                                    text = { Text(state.language.tr("محادثة جديدة", "New chat")) },
                                    leadingIcon = { Icon(Icons.Filled.Add, contentDescription = null) },
                                    onClick = {
                                        showSettingsMenu = false
                                        viewModel.startNewChat()
                                    }
                                )
                                DropdownMenuItem(
                                    text = { Text(state.language.tr("مسح المحادثة", "Clear conversation")) },
                                    leadingIcon = { Icon(Icons.Filled.DeleteSweep, contentDescription = null) },
                                    onClick = {
                                        showSettingsMenu = false
                                        viewModel.clearConversation()
                                    }
                                )
                                HorizontalDivider()
                                Text(
                                    text = state.language.tr("اختر الشخصية", "Choose a character"),
                                    style = MaterialTheme.typography.labelMedium,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 6.dp)
                                )
                                AnimeCharacters.all.forEach { character ->
                                    DropdownMenuItem(
                                        text = { Text(character.name(state.language)) },
                                        leadingIcon = {
                                            Box(
                                                modifier = Modifier
                                                    .size(36.dp)
                                                    .clip(CircleShape)
                                                    .background(character.aura.copy(alpha = 0.4f))
                                            ) {
                                                CharacterThumbnail(character, Modifier.fillMaxSize())
                                            }
                                        },
                                        trailingIcon = {
                                            if (character.id == characters.current.id) {
                                                Icon(Icons.Filled.Check, contentDescription = null)
                                            }
                                        },
                                        onClick = {
                                            characters.select(character)
                                            showSettingsMenu = false
                                        }
                                    )
                                }
                            }
                        }
                    }
                )
            }
        ) { padding ->
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(padding)
            ) {
                if (!state.isAccessibilityEnabled && !typing) {
                    AccessibilityBanner(
                        language = state.language,
                        onEnable = {
                            context.startActivity(
                                Intent(Settings.ACTION_ACCESSIBILITY_SETTINGS)
                                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
                            )
                        }
                    )
                }

                Box(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth()
                ) {
                    if (conversationEmpty) {
                        // New chat: the full-size avatar takes the place of the welcome texts (the greeting is still spoken).
                        if (showAvatar) {
                            AnimeAvatar(
                                character = characters.current,
                                status = state.status,
                                contentDescription = state.language.tr(
                                    "الشخصية ${characters.current.nameAr} — اضغط للتبديل",
                                    "${characters.current.nameEn} — tap to switch"
                                ),
                                modifier = Modifier
                                    .fillMaxSize()
                                    .padding(16.dp)
                                    .clickable(
                                        interactionSource = avatarTap,
                                        indication = null,
                                        onClick = characters::next
                                    )
                            )
                        }
                    } else {
                        LazyColumn(
                            state = listState,
                            modifier = Modifier.fillMaxSize(),
                            contentPadding = PaddingValues(16.dp),
                            verticalArrangement = Arrangement.spacedBy(8.dp)
                        ) {
                            items(chatMessages, key = { it.id }) { message ->
                                ChatBubble(
                                    message,
                                    language = chatLanguage,
                                    onFileApplied = onFileApplied
                                )
                            }
                        }
                    }
                }

                Column(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(horizontal = 8.dp, vertical = if (typing) 2.dp else 8.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(if (typing) 0.dp else 8.dp)
                ) {
                    // The code file being read / edited: every typed or spoken request applies to it until closed.
                    state.workingFileName?.let { fileName ->
                        InputChip(
                            selected = true,
                            onClick = viewModel::clearWorkingFile,
                            label = {
                                Text(
                                    text = state.language.tr("الملف الحالي: $fileName", "Working on: $fileName"),
                                    maxLines = 1
                                )
                            },
                            trailingIcon = {
                                Icon(
                                    imageVector = Icons.Filled.Close,
                                    contentDescription = state.language.tr("إغلاق الملف", "Close file"),
                                    modifier = Modifier.size(18.dp)
                                )
                            }
                        )
                    }
                    // One row: [file] [image] [text field] [mic] [send]
                    ChatInputBar(
                        language = state.language,
                        micStatus = state.status,
                        onMicClick = {
                            // Close the keyboard first so the listening status is visible.
                            keyboard?.hide()
                            focusManager.clearFocus()
                            requestMic()
                        },
                        onSend = viewModel::sendTyped,
                        onFocusChange = { focused -> inputFocused = focused && System.currentTimeMillis() - screenOpenedAt > 2000L }
                    )
                    if (!typing) {
                        StatusIndicator(
                            status = state.status,
                            partialText = state.partialText,
                            errorMessage = state.errorMessage,
                            language = state.language
                        )
                        LanguageToggle(
                            selected = state.language,
                            onSelected = viewModel::setLanguage
                        )
                        FilterChip(
                            selected = state.handsFree,
                            onClick = { viewModel.setHandsFree(!state.handsFree) },
                            label = {
                                Text(state.language.tr("محادثة مستمرة", "Hands-free"))
                            }
                        )
                    }
                }
            }
        }
        }
    }
}

/** Bottom sheet listing what the assistant remembers; every row has a delete button that works at once. */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun MemorySheet(
    facts: List<MemoryEntry>,
    projects: List<MemoryEntry>,
    language: AppLanguage,
    onDelete: (Long) -> Unit,
    onDismiss: () -> Unit
) {
    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(start = 16.dp, end = 16.dp, bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(4.dp)
        ) {
            Text(
                text = language.tr("ذاكرة المساعد", "Assistant memory"),
                style = MaterialTheme.typography.titleLarge
            )
            if (facts.isEmpty() && projects.isEmpty()) {
                Text(
                    text = language.tr(
                        "لا شيء محفوظ بعد. قل: تذكر أنني أحب القهوة.",
                        "Nothing saved yet. Say: remember that I like coffee."
                    ),
                    style = MaterialTheme.typography.bodyMedium
                )
            }
            if (facts.isNotEmpty()) {
                Text(
                    text = language.tr("ما أعرفه عنك", "What I know about you"),
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.padding(top = 8.dp)
                )
                facts.forEach { entry ->
                    MemoryRow(
                        title = entry.content,
                        subtitle = null,
                        deleteLabel = language.tr("حذف", "Delete"),
                        onDelete = { onDelete(entry.id) }
                    )
                }
            }
            if (projects.isNotEmpty()) {
                Text(
                    text = language.tr("المشاريع", "Projects"),
                    style = MaterialTheme.typography.titleSmall,
                    color = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.padding(top = 8.dp)
                )
                projects.forEach { entry ->
                    val name = entry.metadata["fileName"] ?: entry.content
                    MemoryRow(
                        title = name,
                        subtitle = entry.content.takeIf { it.isNotBlank() && it != name },
                        deleteLabel = language.tr("حذف", "Delete"),
                        onDelete = { onDelete(entry.id) }
                    )
                }
            }
        }
    }
}

@Composable
private fun MemoryRow(
    title: String,
    subtitle: String?,
    deleteLabel: String,
    onDelete: () -> Unit
) {
    Row(
        modifier = Modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Column(modifier = Modifier.weight(1f)) {
            Text(text = title, style = MaterialTheme.typography.bodyLarge)
            if (subtitle != null) {
                Text(
                    text = subtitle,
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
        IconButton(onClick = onDelete) {
            Icon(imageVector = Icons.Filled.Delete, contentDescription = deleteLabel)
        }
    }
}

@Composable
private fun SessionsDrawerContent(
    sessions: List<SavedSession>,
    language: AppLanguage,
    onNewChat: () -> Unit,
    onOpen: (Long) -> Unit,
    onDelete: (Long) -> Unit,
    onOpenSettings: () -> Unit
) {
    val dateFormat = remember { java.text.SimpleDateFormat("yyyy-MM-dd HH:mm", java.util.Locale.US) }
    ModalDrawerSheet {
        Column(modifier = Modifier.fillMaxSize()) {
            Button(
                onClick = onNewChat,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp)
            ) {
                Icon(imageVector = Icons.Filled.Add, contentDescription = null)
                Text(
                    text = language.tr("محادثة جديدة", "New chat"),
                    modifier = Modifier.padding(start = 8.dp)
                )
            }
            androidx.compose.material3.OutlinedButton(
                onClick = onOpenSettings,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(start = 16.dp, end = 16.dp, bottom = 12.dp)
            ) {
                Icon(imageVector = Icons.Filled.SettingsIcon, contentDescription = null)
                Text(
                    text = language.tr("نماذج الذكاء الاصطناعي", "AI models"),
                    modifier = Modifier.padding(start = 8.dp)
                )
            }
            if (sessions.isEmpty()) {
                Text(
                    text = language.tr("لا توجد محادثات سابقة.", "No previous chats."),
                    modifier = Modifier.padding(horizontal = 16.dp),
                    style = MaterialTheme.typography.bodyMedium
                )
            } else {
                LazyColumn(
                    modifier = Modifier
                        .weight(1f)
                        .fillMaxWidth(),
                    contentPadding = PaddingValues(horizontal = 8.dp, vertical = 4.dp),
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    items(sessions, key = { it.id }) { session ->
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .clickable { onOpen(session.id) }
                                .padding(start = 12.dp, top = 4.dp, bottom = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(
                                    text = session.title,
                                    maxLines = 1,
                                    style = MaterialTheme.typography.bodyLarge
                                )
                                Text(
                                    text = dateFormat.format(java.util.Date(session.timestamp)),
                                    style = MaterialTheme.typography.bodySmall
                                )
                            }
                            IconButton(onClick = { onDelete(session.id) }) {
                                Icon(
                                    imageVector = Icons.Filled.Delete,
                                    contentDescription = language.tr("حذف", "Delete")
                                )
                            }
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun AccessibilityBanner(language: AppLanguage, onEnable: () -> Unit) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 8.dp),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.tertiaryContainer
        )
    ) {
        Row(
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = language.tr(
                    "فعّل خدمة الوصول لأوامر التحكم بالشاشة (رجوع، تمرير، ضغط، تشغيل الواي فاي…).",
                    "Enable the accessibility service for screen control (back, scroll, tap, Wi-Fi switch…)."
                ),
                modifier = Modifier.weight(1f),
                style = MaterialTheme.typography.bodyMedium
            )
            TextButton(onClick = onEnable) {
                Text(language.tr("تفعيل", "Enable"))
            }
        }
    }
}
''')

# ------------------------------------------------------------------------------
# الإضافة: الكتابة بلوحة المفاتيح + إرسال الصور والملفات
# هذا القسم لا يعدّل أي سطر من الكود الأصلي أعلاه. يضيف ملفات جديدة فقط،
# ويُدرج أسطراً جديدة عند نقاط محددة في الملفات المولّدة (بعد التحقق من أن
# كل نقطة تظهر مرة واحدة بالضبط).
# ------------------------------------------------------------------------------
def insert_before(path, anchor, insertion):
    """Inserts `insertion` right before the single occurrence of `anchor`."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if text.count(anchor) != 1:
        raise RuntimeError("Anchor is not unique in {}: {!r}".format(path, anchor[:70]))
    text = text.replace(anchor, insertion + anchor, 1)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


# 40. نموذج المرفق (صورة أو ملف) الذي يختاره المستخدم من لوحة الإدخال
write_file("app/src/main/java/com/example/voiceassistant/data/AttachmentData.kt", r'''package com.example.voiceassistant.data

/** A picture or file the user attached from the keyboard input bar. */
class AttachmentData(
    val name: String,
    val mime: String,
    val bytes: ByteArray,
    /** Uri of the picked file (lets an edited code file be written back to the original). */
    val uri: String? = null
) {
    companion object {
        /** Largest attachment accepted (keeps the request under the AI service limit). */
        const val MAX_BYTES = 15 * 1024 * 1024
    }
}
''')

# 41. شريط الإدخال: حقل كتابة + زر إرسال + زر صورة + زر ملف
write_file("app/src/main/java/com/example/voiceassistant/ui/components/ChatInputBar.kt", r'''package com.example.voiceassistant.ui.components

import android.content.Intent
import android.net.Uri
import android.app.Activity
import android.media.projection.MediaProjectionManager
import android.widget.Toast
import androidx.compose.material.icons.filled.PhoneAndroid
import androidx.compose.material.icons.filled.PhotoCamera
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.core.content.FileProvider
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect
import androidx.lifecycle.compose.LocalLifecycleOwner
import com.example.voiceassistant.service.ScreenCaptureBridge
import com.example.voiceassistant.service.ScreenCaptureService
import java.io.File
import android.provider.OpenableColumns
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.AttachFile
import androidx.compose.material.icons.filled.Close
import androidx.compose.material.icons.filled.Image
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import com.example.voiceassistant.data.AttachmentData
import com.example.voiceassistant.viewmodel.AppLanguage
import com.example.voiceassistant.viewmodel.AssistantStatus
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * Bottom bar in ONE row: [file] [image] [text field] [microphone] [send].
 * The microphone is always visible next to the text field.
 * onSend receives the typed text (may be empty when only a file is sent) and the attachment.
 */
@Composable
fun ChatInputBar(
    language: AppLanguage,
    micStatus: AssistantStatus,
    onMicClick: () -> Unit,
    onSend: (String, AttachmentData?) -> Unit,
    onFocusChange: (Boolean) -> Unit = {}
) {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    var text by remember { mutableStateOf("") }
    var attachment by remember { mutableStateOf<AttachmentData?>(null) }

    // Reads the chosen file (name, type and bytes) off the main thread.
    fun loadAttachment(uri: Uri?) {
        if (uri == null) return
        scope.launch {
            val loaded = withContext(Dispatchers.IO) {
                val resolver = context.contentResolver
                val mime = resolver.getType(uri) ?: "application/octet-stream"
                var name = "file"
                resolver.query(uri, null, null, null, null)?.use { cursor ->
                    val index = cursor.getColumnIndex(OpenableColumns.DISPLAY_NAME)
                    if (cursor.moveToFirst() && index >= 0) {
                        name = cursor.getString(index) ?: name
                    }
                }
                resolver.openInputStream(uri)?.use { stream ->
                    AttachmentData(name, mime, stream.readBytes(), uri.toString())
                }
            }
            if (loaded != null) attachment = loaded
        }
    }

    val pickImage = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri ->
        loadAttachment(uri)
    }
    // OpenDocument (instead of GetContent) so a code file can later be overwritten with the edited version.
    val pickFile = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) {
            val resolver = context.contentResolver
            try {
                resolver.takePersistableUriPermission(
                    uri,
                    Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_GRANT_WRITE_URI_PERMISSION
                )
            } catch (e: Exception) {
                // This provider is read-only: reading still works, writing back will fall back to "Save".
                try {
                    resolver.takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION)
                } catch (_: Exception) {
                }
            }
        }
        loadAttachment(uri)
    }

    // ---------------- Camera: take a photo, keep it in the app cache, send it to the AI ----------------
    val currentOnSend by rememberUpdatedState(onSend)
    val currentLanguage by rememberUpdatedState(language)
    var cameraPath by rememberSaveable { mutableStateOf<String?>(null) }

    val takePicture = rememberLauncherForActivityResult(ActivityResultContracts.TakePicture()) { success ->
        val path = cameraPath
        cameraPath = null
        if (path != null) {
            if (success) {
                scope.launch {
                    val file = File(path)
                    val bytes = withContext(Dispatchers.IO) {
                        try {
                            file.readBytes().also { file.delete() }
                        } catch (e: Exception) {
                            null
                        }
                    }
                    if (bytes != null && bytes.isNotEmpty()) {
                        currentOnSend(
                            currentLanguage.tr(
                                "حلل هذه الصورة واشرح ما فيها",
                                "Analyze this image and explain what is in it"
                            ),
                            AttachmentData(file.name, "image/jpeg", bytes, null)
                        )
                    }
                }
            } else {
                File(path).delete()
            }
        }
    }

    fun launchCamera() {
        try {
            val dir = File(context.cacheDir, "camera").apply { mkdirs() }
            val file = File(dir, "photo_${System.currentTimeMillis()}.jpg")
            val uri = FileProvider.getUriForFile(context, "${context.packageName}.fileprovider", file)
            cameraPath = file.absolutePath
            takePicture.launch(uri)
        } catch (e: Exception) {
            cameraPath = null
            Toast.makeText(
                context,
                language.tr("تعذّر فتح الكاميرا.", "Could not open the camera."),
                Toast.LENGTH_SHORT
            ).show()
        }
    }

    // ---------------- Screen capture: permission -> ScreenCaptureService -> screenshot -> AI ----------------
    fun deliverScreenshot(bytes: ByteArray) {
        currentOnSend(
            currentLanguage.tr(
                "اقرأ ما في هذه الشاشة واشرحه لي",
                "Read what is on this screen and explain it to me"
            ),
            AttachmentData("screenshot_${System.currentTimeMillis()}.jpg", "image/jpeg", bytes, null)
        )
    }

    val screenCaptureLauncher = rememberLauncherForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
        val data = result.data
        if (result.resultCode == Activity.RESULT_OK && data != null) {
            ScreenCaptureService.start(context, result.resultCode, data)
            // Hide the app so the screenshot shows what is on the phone screen (not this chat).
            (context as? Activity)?.moveTaskToBack(true)
        }
    }

    fun launchScreenCapture() {
        try {
            val manager = context.getSystemService(MediaProjectionManager::class.java)
            screenCaptureLauncher.launch(manager.createScreenCaptureIntent())
        } catch (e: Exception) {
            Toast.makeText(
                context,
                language.tr("تعذّر طلب إذن تسجيل الشاشة.", "Could not request screen recording permission."),
                Toast.LENGTH_SHORT
            ).show()
        }
    }

    // The screenshot is analysed when the app is visible again (so the request is not lost in the background).
    val lifecycleOwner = LocalLifecycleOwner.current
    LifecycleEventEffect(Lifecycle.Event.ON_RESUME) {
        ScreenCaptureBridge.take()?.let { deliverScreenshot(it) }
    }
    LaunchedEffect(Unit) {
        ScreenCaptureBridge.events.collect {
            if (lifecycleOwner.lifecycle.currentState.isAtLeast(Lifecycle.State.RESUMED)) {
                ScreenCaptureBridge.take()?.let { deliverScreenshot(it) }
            }
        }
    }

    fun send() {
        val clean = text.trim()
        if (clean.isEmpty() && attachment == null) return
        onSend(clean, attachment)
        text = ""
        attachment = null
    }

    Column(
        modifier = Modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        attachment?.let { att ->
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Filled.AttachFile,
                    contentDescription = null,
                    modifier = Modifier.size(18.dp)
                )
                Text(
                    text = att.name,
                    modifier = Modifier
                        .weight(1f)
                        .padding(start = 6.dp),
                    style = MaterialTheme.typography.bodySmall,
                    maxLines = 1
                )
                IconButton(onClick = { attachment = null }) {
                    Icon(
                        imageVector = Icons.Filled.Close,
                        contentDescription = language.tr("إزالة المرفق", "Remove attachment")
                    )
                }
            }
        }

        // Wide rectangular input field placed above the buttons row.
        OutlinedTextField(
            value = text,
            onValueChange = { text = it },
            modifier = Modifier
                .fillMaxWidth()
                .onFocusChanged { onFocusChange(it.isFocused) },
            placeholder = { Text(language.tr("اكتب رسالتك...", "Type a message...")) },
            maxLines = 4,
            // Enter key = new line (like a normal keyboard). Sending is done by the arrow button below the field.
            keyboardOptions = KeyboardOptions(imeAction = ImeAction.Default)
        )

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            IconButton(onClick = { pickFile.launch(arrayOf("*/*")) }) {
                Icon(
                    imageVector = Icons.Filled.AttachFile,
                    contentDescription = language.tr("إرسال ملف", "Send file")
                )
            }
            IconButton(onClick = { pickImage.launch("image/*") }) {
                Icon(
                    imageVector = Icons.Filled.Image,
                    contentDescription = language.tr("إرسال صورة", "Send image")
                )
            }
            IconButton(onClick = { launchCamera() }, modifier = Modifier.size(40.dp)) {
                Icon(
                    imageVector = Icons.Filled.PhotoCamera,
                    contentDescription = language.tr("التقاط صورة بالكاميرا", "Take a photo")
                )
            }
            IconButton(onClick = { launchScreenCapture() }, modifier = Modifier.size(40.dp)) {
                Icon(
                    imageVector = Icons.Filled.PhoneAndroid,
                    contentDescription = language.tr("لقطة شاشة", "Screenshot")
                )
            }
            MicButton(
                status = micStatus,
                onClick = onMicClick,
                compact = true
            )
            IconButton(onClick = { send() }) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.Send,
                    contentDescription = language.tr("إرسال", "Send")
                )
            }
        }
    }
}
''')

# 42. ConversationRepository: رسالة مستخدم تحمل صورة مرفقة
insert_before(
    "app/src/main/java/com/example/voiceassistant/data/ConversationRepository.kt",
    "    fun clear() {\n",
    r'''    /** Adds a user message that also shows an attached picture. */
    fun addUserMessageWithImage(text: String, imagePath: String?): Message =
        add(text, isUser = true, imagePath = imagePath)

''')

# 43. AiChatService: إرسال سؤال مع ملف (صورة / PDF / نص) إلى Gemini
insert_before(
    "app/src/main/java/com/example/voiceassistant/data/AiChatService.kt",
    "    private fun turn(role: String, text: String): JSONObject =\n",
    r'''    /** Sends a question together with one attached file (image, PDF or text) to the selected AI model. */
    suspend fun askWithFile(
        text: String,
        lang: AppLanguage,
        mime: String,
        name: String,
        bytes: ByteArray
    ): AiResult = withContext(Dispatchers.IO) {
        val providers = providerOrder()
        if (providers.isEmpty()) return@withContext AiResult.Error(AiError.NOT_CONFIGURED)

        var lastError: AiResult.Error = AiResult.Error(AiError.OTHER, "No models tried")
        for (provider in providers) {
            val result = when (provider) {
                AiProvider.GEMINI -> askWithFileGemini(text, lang, mime, name, bytes)
                AiProvider.OPENAI -> askWithFileOpenAi(text, lang, mime, name, bytes)
                AiProvider.CLAUDE -> askWithFileClaude(text, lang, mime, name, bytes)
            }
            if (result is AiResult.Success) return@withContext result
            if (result is AiResult.Error) lastError = result
        }
        return@withContext lastError
    }

    /** Text of a non-media attachment (valid UTF-8 only) or the reason it can't be read. */
    private fun fileAsText(bytes: ByteArray, lang: AppLanguage): Pair<String?, AiResult.Error?> {
        if (bytes.size > 1_000_000) {
            return null to AiResult.Error(AiError.OTHER, lang.tr("الملف النصي كبير جداً.", "Text file is too large."))
        }
        return try {
            val decoded = Charsets.UTF_8.newDecoder()
                .onMalformedInput(java.nio.charset.CodingErrorAction.REPORT)
                .decode(java.nio.ByteBuffer.wrap(bytes))
                .toString()
            decoded to null
        } catch (e: java.nio.charset.CharacterCodingException) {
            null to AiResult.Error(
                AiError.OTHER,
                lang.tr("نوع هذا الملف غير مدعوم (الصور و PDF والملفات النصية فقط).", "This file type is not supported (images, PDF and text files only).")
            )
        }
    }

    private suspend fun askWithFileOpenAi(
        text: String,
        lang: AppLanguage,
        mime: String,
        name: String,
        bytes: ByteArray
    ): AiResult = withContext(Dispatchers.IO) {
        if (OPENAI_API_KEY.isBlank()) return@withContext AiResult.Error(AiError.NOT_CONFIGURED)
        val content = JSONArray()
        if (mime.startsWith("image/")) {
            val url = "data:$mime;base64," + java.util.Base64.getEncoder().encodeToString(bytes)
            content.put(JSONObject().put("type", "text").put("text", text))
            content.put(JSONObject().put("type", "image_url").put("image_url", JSONObject().put("url", url)))
        } else if (mime == "application/pdf") {
            return@withContext AiResult.Error(
                AiError.OTHER,
                lang.tr("ChatGPT لا يقرأ ملفات PDF هنا. اختر Gemini أو Claude من إعدادات النماذج.", "ChatGPT can't read PDF files here. Pick Gemini or Claude in AI models.")
            )
        } else {
            val (decoded, problem) = fileAsText(bytes, lang)
            if (decoded == null) return@withContext problem ?: AiResult.Error(AiError.OTHER)
            content.put(JSONObject().put("type", "text").put("text", "$text\n\n--- ${lang.tr("محتوى الملف", "File content")}: $name ---\n$decoded"))
        }
        val (full, error) = callOpenAi(content, lang)
        if (full == null) return@withContext error ?: AiResult.Error(AiError.OTHER)
        val (spoken, code) = splitCode(full, lang)
        remember("$text [$name]", full)
        AiResult.Success(spoken, code)
    }

    private suspend fun askWithFileClaude(
        text: String,
        lang: AppLanguage,
        mime: String,
        name: String,
        bytes: ByteArray
    ): AiResult = withContext(Dispatchers.IO) {
        if (CLAUDE_API_KEY.isBlank()) return@withContext AiResult.Error(AiError.NOT_CONFIGURED)
        val content = JSONArray()
        if (mime.startsWith("image/") || mime == "application/pdf") {
            val kind = if (mime == "application/pdf") "document" else "image"
            val source = JSONObject()
                .put("type", "base64")
                .put("media_type", mime)
                .put("data", java.util.Base64.getEncoder().encodeToString(bytes))
            content.put(JSONObject().put("type", kind).put("source", source))
            content.put(JSONObject().put("type", "text").put("text", text))
        } else {
            val (decoded, problem) = fileAsText(bytes, lang)
            if (decoded == null) return@withContext problem ?: AiResult.Error(AiError.OTHER)
            content.put(JSONObject().put("type", "text").put("text", "$text\n\n--- ${lang.tr("محتوى الملف", "File content")}: $name ---\n$decoded"))
        }
        val (full, error) = callClaude(content, lang)
        if (full == null) return@withContext error ?: AiResult.Error(AiError.OTHER)
        val (spoken, code) = splitCode(full, lang)
        remember("$text [$name]", full)
        AiResult.Success(spoken, code)
    }

    /** Gemini version of askWithFile (image, PDF or text). */
    private suspend fun askWithFileGemini(
        text: String,
        lang: AppLanguage,
        mime: String,
        name: String,
        bytes: ByteArray
    ): AiResult = withContext(Dispatchers.IO) {
        if (GEMINI_API_KEY.isBlank()) return@withContext AiResult.Error(AiError.NOT_CONFIGURED)

        val isMedia = mime.startsWith("image/") || mime == "application/pdf"
        val parts = JSONArray()
        if (isMedia) {
            parts.put(JSONObject().put("text", text))
            parts.put(
                JSONObject().put(
                    "inline_data",
                    JSONObject()
                        .put("mime_type", mime)
                        .put("data", java.util.Base64.getEncoder().encodeToString(bytes))
                )
            )
        } else {
            // Any other file is sent as plain text, so it must be valid UTF-8 and reasonably small.
            if (bytes.size > 1_000_000) {
                return@withContext AiResult.Error(AiError.OTHER, lang.tr("الملف النصي كبير جداً.", "Text file is too large."))
            }
            val decoded = try {
                Charsets.UTF_8.newDecoder()
                    .onMalformedInput(java.nio.charset.CodingErrorAction.REPORT)
                    .decode(java.nio.ByteBuffer.wrap(bytes))
                    .toString()
            } catch (e: java.nio.charset.CharacterCodingException) {
                return@withContext AiResult.Error(AiError.OTHER, lang.tr("نوع هذا الملف غير مدعوم (الصور و PDF والملفات النصية فقط).", "This file type is not supported (images, PDF and text files only)."))
            }
            parts.put(JSONObject().put("text", "$text\n\n--- ${lang.tr("محتوى الملف", "File content")}: $name ---\n$decoded"))
        }

        try {
            val contents = JSONArray()
            synchronized(lock) {
                history.forEach { (role, t) -> contents.put(turn(role, t)) }
            }
            contents.put(JSONObject().put("role", "user").put("parts", parts))

            val body = JSONObject()
                .put(
                    "system_instruction",
                    JSONObject().put("parts", JSONArray().put(JSONObject().put("text", systemPrompt(lang))))
                )
                .put("contents", contents)
                .put("generationConfig", JSONObject().put("maxOutputTokens", 16384))

            var lastError: AiResult.Error = AiResult.Error(AiError.OTHER, "No models tried")
            for (modelName in activeModels()) {
                try {
                    val request = Request.Builder()
                        .url("$GEMINI_BASE$modelName:generateContent")
                        .header("x-goog-api-key", GEMINI_API_KEY)
                        .post(body.toString().toRequestBody("application/json; charset=utf-8".toMediaType()))
                        .build()

                    val result: AiResult? = longClient.newCall(request).execute().use { response ->
                        val raw = response.body?.string().orEmpty()
                        if (!response.isSuccessful) {
                            if (response.code == 404) unavailableModels.add(modelName)
                            lastError = AiResult.Error(kindForGemini(response.code, raw), apiError(response.code, raw))
                            null
                        } else {
                            val full = extractGeminiText(raw)
                            if (full.isBlank()) {
                                lastError = AiResult.Error(AiError.EMPTY)
                                null
                            } else {
                                val (spoken, code) = splitCode(full, lang)
                                remember("$text [$name]", full)
                                AiResult.Success(spoken, code)
                            }
                        }
                    }
                    if (result != null) return@withContext result
                } catch (e: IOException) {
                    lastError = AiResult.Error(AiError.NETWORK, e.toString().take(160))
                } catch (e: CancellationException) {
                    throw e
                } catch (e: Exception) {
                    lastError = AiResult.Error(AiError.OTHER, e.toString().take(160))
                }
            }
            return@withContext lastError
        } catch (e: IOException) {
            AiResult.Error(AiError.NETWORK, e.toString().take(160))
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            AiResult.Error(AiError.OTHER, e.toString().take(160))
        }
    }

''')

# 44. MainViewModel: إرسال النص المكتوب (مع مرفق اختياري)
insert_before(
    "app/src/main/java/com/example/voiceassistant/viewmodel/MainViewModel.kt",
    "    private fun process(text: String, speak: Boolean = true) {\n",
    r'''    private val maxWorkingFileBytes = 300_000

    private fun decodeUtf8(bytes: ByteArray): String? = try {
        Charsets.UTF_8.newDecoder()
            .onMalformedInput(java.nio.charset.CodingErrorAction.REPORT)
            .onUnmappableCharacter(java.nio.charset.CodingErrorAction.REPORT)
            .decode(java.nio.ByteBuffer.wrap(bytes))
            .toString()
            .removePrefix("\uFEFF")
    } catch (e: java.nio.charset.CharacterCodingException) {
        null
    }

    /** Stops editing the current code file (the chip next to the input bar). */
    fun clearWorkingFile() {
        ai.workingFile = null
        _uiState.update { it.copy(workingFileName = null) }
    }

    /** Text typed on the keyboard, optionally with one attached picture or file. */
    fun sendTyped(text: String, attachment: com.example.voiceassistant.data.AttachmentData? = null) {
        if (_uiState.value.status == AssistantStatus.PROCESSING) return
        val clean = text.trim()
        if (clean.isEmpty() && attachment == null) return
        val lang = if (clean.isEmpty()) _uiState.value.language else AppLanguage.detect(clean)

        if (attachment != null &&
            attachment.bytes.size > com.example.voiceassistant.data.AttachmentData.MAX_BYTES
        ) {
            reply(lang.tr("الملف كبير جداً (الحد الأقصى 15 ميغابايت).", "The file is too large (15 MB max)."), lang, speak = false)
            return
        }

        silentStrikes = 0
        viewModelScope.launch {
            // Plain typed text goes through the same path as spoken text (phone commands, AI, images).
            if (attachment == null) {
                repository.addUserMessage(clean)
                // Typed -> silent: the user reads the answer, nothing is spoken.
                process(clean, speak = false)
                return@launch
            }

            // Code / text file: it becomes the "working file", so later requests (typed or spoken) can
            // read, explain and edit it. Images and PDFs still go through askWithFile below.
            val isMedia = attachment.mime.startsWith("image/") || attachment.mime == "application/pdf"
            if (!isMedia) {
                val content = withContext(Dispatchers.Default) { decodeUtf8(attachment.bytes) }
                if (content == null) {
                    reply(
                        lang.tr(
                            "نوع هذا الملف غير مدعوم (الصور و PDF والملفات النصية والأكواد فقط).",
                            "This file type is not supported (images, PDF, text and code files only)."
                        ),
                        lang,
                        speak = false
                    )
                    return@launch
                }
                if (attachment.bytes.size > maxWorkingFileBytes) {
                    reply(
                        lang.tr(
                            "الملف كبير جداً للتعديل (الحد الأقصى 300 كيلوبايت).",
                            "The file is too large to edit (300 KB max)."
                        ),
                        lang,
                        speak = false
                    )
                    return@launch
                }
                ai.workingFile = com.example.voiceassistant.data.WorkingFile(attachment.name, attachment.uri, content)
                // Project memory: remember this file across sessions.
                memoryManager.addProject(attachment.name, attachment.uri)
                refreshMemoryState()
                _uiState.update {
                    it.copy(workingFileName = attachment.name, status = AssistantStatus.PROCESSING, partialText = "")
                }
                val fileHeader = "📎 ${attachment.name}"
                repository.addUserMessage(if (clean.isEmpty()) fileHeader else "$fileHeader\n$clean")
                askAi(
                    clean.ifEmpty {
                        lang.tr(
                            "اقرأ هذا الملف ولخّص ما يفعله وأي مشاكل واضحة فيه.",
                            "Read this file, summarize what it does and any obvious problems in it."
                        )
                    },
                    lang,
                    speak = false
                )
                return@launch
            }

            // A picture is shown in the chat; any file is shown by its name.
            val imagePath = if (attachment.mime.startsWith("image/")) {
                withContext(Dispatchers.IO) { saveImage(attachment.bytes) }
            } else {
                null
            }
            val header = "📎 ${attachment.name}"
            repository.addUserMessageWithImage(
                if (clean.isEmpty()) header else "$header\n$clean",
                imagePath
            )
            _uiState.update { it.copy(status = AssistantStatus.PROCESSING, partialText = "") }

            val prompt = clean.ifEmpty { lang.tr("حلّل هذا الملف واشرحه.", "Analyze this file and explain it.") }
            when (val result = ai.askWithFile(prompt, lang, attachment.mime, attachment.name, attachment.bytes)) {
                is AiResult.Success -> reply(result.text, lang, result.code, speak = false)
                is AiResult.Error -> replyAiError(result.kind, result.detail, lang, speak = false)
            }
        }
    }

''')

# 45. MainScreen: استيراد شريط الإدخال ووضعه فوق زر الميكروفون
_main_screen_path = "app/src/main/java/com/example/voiceassistant/ui/MainScreen.kt"
with open(_main_screen_path, "r", encoding="utf-8") as _f:
    _main_screen_has_input_bar = "import com.example.voiceassistant.ui.components.ChatInputBar\n" in _f.read()
if not _main_screen_has_input_bar:
    insert_before(
        _main_screen_path,
        "import com.example.voiceassistant.ui.components.LanguageToggle\n",
        "import com.example.voiceassistant.ui.components.ChatInputBar\n")


# ------------------------------------------------------------------------------
# الإضافة: الكاميرا + لقطة الشاشة (FileProvider + ScreenCaptureService)
# ------------------------------------------------------------------------------
write_file("app/src/main/res/xml/file_paths.xml", r'''<?xml version="1.0" encoding="utf-8"?>
<paths>
    <!-- Photos taken by the camera app are stored in <cache>/camera/ -->
    <cache-path name="camera" path="camera/" />
</paths>
''')

write_file("app/src/main/java/com/example/voiceassistant/service/ScreenCaptureService.kt", r'''package com.example.voiceassistant.service

import android.app.Activity
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.graphics.Bitmap
import android.graphics.PixelFormat
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.Image
import android.media.ImageReader
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Handler
import android.os.HandlerThread
import android.os.IBinder
import android.os.Looper
import android.view.WindowManager
import android.widget.Toast
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import androidx.core.content.ContextCompat
import com.example.voiceassistant.MainActivity
import java.io.ByteArrayOutputStream
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow
import kotlinx.coroutines.flow.asSharedFlow
import kotlin.math.max
import kotlin.math.min

/**
 * Hands the screenshot (JPEG bytes) from [ScreenCaptureService] to the UI.
 * Both live in the same process; the bytes wait here until the chat screen is visible.
 */
object ScreenCaptureBridge {
    private val lock = Any()
    private var pending: ByteArray? = null

    private val _events = MutableSharedFlow<Unit>(extraBufferCapacity = 1)
    val events: SharedFlow<Unit> = _events.asSharedFlow()

    fun publish(bytes: ByteArray) {
        synchronized(lock) { pending = bytes }
        _events.tryEmit(Unit)
    }

    /** Returns the waiting screenshot once (null when there is none). */
    fun take(): ByteArray? = synchronized(lock) {
        val bytes = pending
        pending = null
        bytes
    }
}

/**
 * Foreground service that takes ONE screenshot with MediaProjection, gives the JPEG bytes to
 * [ScreenCaptureBridge] and stops itself.
 */
class ScreenCaptureService : Service() {

    companion object {
        private const val EXTRA_RESULT_CODE = "result_code"
        private const val EXTRA_DATA = "projection_data"
        private const val CHANNEL_ID = "va_screen_capture"
        private const val NOTIFICATION_ID = 7421
        private const val RESULT_NOTIFICATION_ID = 7422

        /** Time to let the permission dialog and the app window disappear before the screenshot. */
        private const val CAPTURE_DELAY_MS = 1200L

        /** Give up when the system never delivers a frame. */
        private const val FRAME_TIMEOUT_MS = 5000L

        /** Longest side of the screenshot sent to the AI (keeps the request small). */
        private const val MAX_SIDE = 1600

        fun start(context: Context, resultCode: Int, data: Intent) {
            val intent = Intent(context, ScreenCaptureService::class.java)
                .putExtra(EXTRA_RESULT_CODE, resultCode)
                .putExtra(EXTRA_DATA, data)
            ContextCompat.startForegroundService(context, intent)
        }
    }

    private val mainHandler = Handler(Looper.getMainLooper())
    private var workThread: HandlerThread? = null
    private var projection: MediaProjection? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var imageReader: ImageReader? = null

    @Volatile
    private var finished = false

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val resultCode = intent?.getIntExtra(EXTRA_RESULT_CODE, Activity.RESULT_CANCELED)
            ?: Activity.RESULT_CANCELED
        @Suppress("DEPRECATION")
        val data: Intent? = if (Build.VERSION.SDK_INT >= 33) {
            intent?.getParcelableExtra(EXTRA_DATA, Intent::class.java)
        } else {
            intent?.getParcelableExtra(EXTRA_DATA)
        }
        if (data == null || resultCode != Activity.RESULT_OK) {
            stopSelf()
            return START_NOT_STICKY
        }

        // Must be a foreground service BEFORE the projection is created (required on Android 14+).
        try {
            ServiceCompat.startForeground(
                this,
                NOTIFICATION_ID,
                buildNotification(),
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION
            )
        } catch (e: Exception) {
            fail()
            return START_NOT_STICKY
        }

        mainHandler.postDelayed({ capture(resultCode, data) }, CAPTURE_DELAY_MS)
        return START_NOT_STICKY
    }

    private fun capture(resultCode: Int, data: Intent) {
        if (finished) return
        try {
            val thread = HandlerThread("screen-capture").also { it.start() }
            workThread = thread
            val workHandler = Handler(thread.looper)

            val manager = getSystemService(MediaProjectionManager::class.java)
            val mp = manager.getMediaProjection(resultCode, data)
            projection = mp
            // Android 14+: a callback must be registered before the virtual display is created.
            mp.registerCallback(object : MediaProjection.Callback() {
                override fun onStop() {
                    mainHandler.post { if (!finished) fail() }
                }
            }, workHandler)

            val bounds = screenSize()
            val scale = min(1f, MAX_SIDE.toFloat() / max(bounds.first, bounds.second))
            val width = max(2, (bounds.first * scale).toInt() / 2 * 2)
            val height = max(2, (bounds.second * scale).toInt() / 2 * 2)
            val dpi = resources.displayMetrics.densityDpi

            val reader = ImageReader.newInstance(width, height, PixelFormat.RGBA_8888, 2)
            imageReader = reader
            reader.setOnImageAvailableListener({ r ->
                if (finished) return@setOnImageAvailableListener
                val image = try {
                    r.acquireLatestImage()
                } catch (e: Exception) {
                    null
                } ?: return@setOnImageAvailableListener
                val bytes = try {
                    toJpeg(image)
                } catch (e: Exception) {
                    null
                } finally {
                    image.close()
                }
                mainHandler.post { if (bytes != null) succeed(bytes) else fail() }
            }, workHandler)

            virtualDisplay = mp.createVirtualDisplay(
                "va-screenshot",
                width,
                height,
                dpi,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                reader.surface,
                null,
                workHandler
            )
            mainHandler.postDelayed({ if (!finished) fail() }, FRAME_TIMEOUT_MS)
        } catch (e: Exception) {
            fail()
        }
    }

    /** Real screen size in pixels (width, height). */
    private fun screenSize(): Pair<Int, Int> {
        val wm = getSystemService(WindowManager::class.java)
        return if (Build.VERSION.SDK_INT >= 30) {
            val b = wm.maximumWindowMetrics.bounds
            b.width() to b.height()
        } else {
            val m = resources.displayMetrics
            m.widthPixels to m.heightPixels
        }
    }

    private fun toJpeg(image: Image): ByteArray {
        val plane = image.planes[0]
        val pixelStride = plane.pixelStride
        val rowPadding = plane.rowStride - pixelStride * image.width
        val padded = Bitmap.createBitmap(
            image.width + rowPadding / pixelStride,
            image.height,
            Bitmap.Config.ARGB_8888
        )
        padded.copyPixelsFromBuffer(plane.buffer)
        val cropped = Bitmap.createBitmap(padded, 0, 0, image.width, image.height)
        val out = ByteArrayOutputStream()
        cropped.compress(Bitmap.CompressFormat.JPEG, 85, out)
        if (cropped !== padded) cropped.recycle()
        padded.recycle()
        return out.toByteArray()
    }

    private fun succeed(bytes: ByteArray) {
        if (finished) return
        finished = true
        ScreenCaptureBridge.publish(bytes)
        release()
        showResultNotification()
        // Try to bring the app back (Android may block this from the background: the notification is the fallback).
        try {
            startActivity(
                Intent(this, MainActivity::class.java)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_REORDER_TO_FRONT or Intent.FLAG_ACTIVITY_SINGLE_TOP)
            )
        } catch (e: Exception) {
            // ignored
        }
        stopSelf()
    }

    private fun fail() {
        if (finished) return
        finished = true
        release()
        val lang = ProactiveScheduler.language(this)
        Toast.makeText(
            this,
            lang.tr("تعذّر التقاط الشاشة.", "Could not capture the screen."),
            Toast.LENGTH_LONG
        ).show()
        stopSelf()
    }

    /** Frees the display, the reader and the projection (one screenshot only). */
    private fun release() {
        mainHandler.removeCallbacksAndMessages(null)
        try { virtualDisplay?.release() } catch (_: Exception) { }
        virtualDisplay = null
        try { imageReader?.setOnImageAvailableListener(null, null) } catch (_: Exception) { }
        try { imageReader?.close() } catch (_: Exception) { }
        imageReader = null
        try { projection?.stop() } catch (_: Exception) { }
        projection = null
        workThread?.quitSafely()
        workThread = null
        stopForeground(STOP_FOREGROUND_REMOVE)
    }

    override fun onDestroy() {
        if (!finished) {
            finished = true
            release()
        }
        super.onDestroy()
    }

    private fun ensureChannel() {
        val manager = getSystemService(NotificationManager::class.java)
        if (manager.getNotificationChannel(CHANNEL_ID) == null) {
            val lang = ProactiveScheduler.language(this)
            manager.createNotificationChannel(
                NotificationChannel(
                    CHANNEL_ID,
                    lang.tr("لقطة الشاشة", "Screen capture"),
                    NotificationManager.IMPORTANCE_LOW
                )
            )
        }
    }

    private fun buildNotification(): Notification {
        ensureChannel()
        val lang = ProactiveScheduler.language(this)
        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_menu_view)
            .setContentTitle(lang.tr("Zevorix AI", "Zevorix AI"))
            .setContentText(lang.tr("جارٍ التقاط الشاشة…", "Capturing the screen…"))
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .build()
    }

    private fun showResultNotification() {
        try {
            ensureChannel()
            val lang = ProactiveScheduler.language(this)
            val open = PendingIntent.getActivity(
                this,
                0,
                Intent(this, MainActivity::class.java)
                    .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP),
                PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
            )
            val notification = NotificationCompat.Builder(this, CHANNEL_ID)
                .setSmallIcon(android.R.drawable.ic_menu_view)
                .setContentTitle(lang.tr("تم التقاط الشاشة", "Screen captured"))
                .setContentText(lang.tr("اضغط للعودة إلى المساعد وتحليل اللقطة.", "Tap to return to the assistant and analyze it."))
                .setContentIntent(open)
                .setAutoCancel(true)
                .build()
            getSystemService(NotificationManager::class.java).notify(RESULT_NOTIFICATION_ID, notification)
        } catch (e: Exception) {
            // The notification is only a convenience.
        }
    }
}
''')


# ------------------------------------------------------------------------------
# الإضافة: شخصيات الأنمي المتحركة (تستبدل شكل الروبوت) + التبديل بينها
# ------------------------------------------------------------------------------
write_file("app/src/main/java/com/example/voiceassistant/ui/components/AnimeCharacter.kt", r'''package com.example.voiceassistant.ui.components

import android.content.Context
import android.content.SharedPreferences
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.lerp
import androidx.compose.ui.platform.LocalContext
import com.example.voiceassistant.viewmodel.AppLanguage

/** شكل الشعر: يحدد طريقة رسم الشعر الخلفي والأمامي. */
enum class HairStyle { TWIN_TAILS, BOB, SPIKY, LONG }

/** إكسسوار مميز لكل شخصية. */
enum class Accessory { RIBBONS, CAT_EARS, HEADBAND, HAIRPIN }

/**
 * شخصية أنمي مرسومة بالكامل بالكود (Canvas) — بدون صور ولا مكتبات خارجية.
 * لإضافة شخصية جديدة: أضف عنصراً إلى [AnimeCharacters.all] فقط.
 */
data class AnimeCharacter(
    val id: String,
    val nameAr: String,
    val nameEn: String,
    val hairStyle: HairStyle,
    val accessory: Accessory,
    val hair: Color,
    val hairShade: Color,
    val eye: Color,
    val skin: Color,
    val outfit: Color,
    val accent: Color,
    val aura: Color
) {
    val skinShade: Color get() = lerp(skin, Color(0xFF8D4F3F), 0.22f)
    val eyeDark: Color get() = lerp(eye, Color.Black, 0.5f)

    fun name(language: AppLanguage): String = language.tr(nameAr, nameEn)
}

object AnimeCharacters {
    val all: List<AnimeCharacter> = listOf(
        AnimeCharacter(
            id = "hikari", nameAr = "هيكاري", nameEn = "Hikari",
            hairStyle = HairStyle.TWIN_TAILS, accessory = Accessory.RIBBONS,
            hair = Color(0xFFFFB04A), hairShade = Color(0xFFE07B1F),
            eye = Color(0xFF39A8FF), skin = Color(0xFFFFE3D1),
            outfit = Color(0xFF2F3E8F), accent = Color(0xFFE53950),
            aura = Color(0xFFFFC27A)
        ),
        AnimeCharacter(
            id = "ryo", nameAr = "ريو", nameEn = "Ryo",
            hairStyle = HairStyle.SPIKY, accessory = Accessory.HEADBAND,
            hair = Color(0xFF3D6BFF), hairShade = Color(0xFF2342B8),
            eye = Color(0xFFFFB300), skin = Color(0xFFF8D5BC),
            outfit = Color(0xFF00897B), accent = Color(0xFFFFD54F),
            aura = Color(0xFF7FA2FF)
        ),
        AnimeCharacter(
            id = "luna", nameAr = "لونا", nameEn = "Luna",
            hairStyle = HairStyle.LONG, accessory = Accessory.HAIRPIN,
            hair = Color(0xFFD1C4F5), hairShade = Color(0xFF9575CD),
            eye = Color(0xFFE040FB), skin = Color(0xFFFFE9DD),
            outfit = Color(0xFF1A237E), accent = Color(0xFFFFD54F),
            aura = Color(0xFFB39DDB)
        ),
        AnimeCharacter(
            id = "momo", nameAr = "مومو", nameEn = "Momo",
            hairStyle = HairStyle.BOB, accessory = Accessory.CAT_EARS,
            hair = Color(0xFF7FDCC8), hairShade = Color(0xFF3FB8A0),
            eye = Color(0xFFFF6F91), skin = Color(0xFFFFE0CC),
            outfit = Color(0xFFF48FB1), accent = Color(0xFFFF80AB),
            aura = Color(0xFF9CE8D8)
        )
    )

    fun byId(id: String?): AnimeCharacter = all.firstOrNull { it.id == id } ?: all.first()
}

/** يحفظ الشخصية المختارة في SharedPreferences لتبقى بعد إغلاق التطبيق. */
class CharacterSelection(private val prefs: SharedPreferences) {

    var current: AnimeCharacter by mutableStateOf(
        AnimeCharacters.byId(prefs.getString(KEY, null))
    )
        private set

    fun select(character: AnimeCharacter) {
        current = character
        prefs.edit().putString(KEY, character.id).apply()
    }

    /** الشخصية التالية (للتبديل بالضغط على الشخصية). */
    fun next() {
        val all = AnimeCharacters.all
        val index = all.indexOfFirst { it.id == current.id }
        select(all[(index + 1) % all.size])
    }

    private companion object {
        const val KEY = "avatar_character"
    }
}

@Composable
fun rememberCharacterSelection(): CharacterSelection {
    val context = LocalContext.current
    return remember {
        CharacterSelection(
            context.applicationContext.getSharedPreferences("avatar_prefs", Context.MODE_PRIVATE)
        )
    }
}
''')

write_file("app/src/main/java/com/example/voiceassistant/ui/components/AnimeCharacterPainter.kt", r'''package com.example.voiceassistant.ui.components

import androidx.compose.ui.geometry.CornerRadius
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.geometry.Size
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.graphics.drawscope.clipPath
import androidx.compose.ui.graphics.drawscope.scale
import androidx.compose.ui.graphics.lerp
import kotlin.math.abs
import kotlin.math.max
import kotlin.math.sin

internal const val TWO_PI = 6.2831855f

private val Ink = Color(0xFF2B2233)
private val MouthInside = Color(0xFF7A2335)
private val Tongue = Color(0xFFFF8FA3)
private val BlushColor = Color(0xFFFF5C7A)
private val SweatColor = Color(0xFF8EC9FF)

/**
 * "وضعية" الشخصية في لحظة معينة. كل القيم بين 0 و 1 (ما لم يُذكر غير ذلك).
 * AnimeAvatar يبني هذه الوضعية في كل إطار حسب حالة المساعد.
 */
data class AvatarPose(
    /** 1 = العين مفتوحة، 0 = مغلقة (للرمش). */
    val blink: Float = 1f,
    val eyeScale: Float = 1f,
    /** فتحة الفم (للكلام). */
    val mouthOpen: Float = 0f,
    /** 1 = ابتسامة، 0 = مستقيم، -1 = عبوس. */
    val mouthCurve: Float = 1f,
    /** اتجاه النظر -1..1. */
    val lookX: Float = 0f,
    val lookY: Float = 0f,
    val browLift: Float = 0f,
    val browSad: Float = 0f,
    val blush: Float = 0.3f,
    /** فقاعة التفكير (PROCESSING). */
    val thinking: Float = 0f,
    /** حلقات الاستماع (LISTENING). */
    val ring: Float = 0f,
    /** قطرة العرق (ERROR). */
    val sweat: Float = 0f,
    /** النجوم المتلألئة (SPEAKING). */
    val sparkle: Float = 0f,
    /** مرحلة حركة دورية 0..1 تُستخدم للنقاط والحلقات والنجوم. */
    val phase: Float = 0f
)

/** يرسم الشخصية داخل مربع (يستعمل size.minDimension) — كل الإحداثيات بالأسفل نسب من 0 إلى 1. */
fun DrawScope.drawAnimeCharacter(character: AnimeCharacter, pose: AvatarPose) {
    scale(scale = size.minDimension, pivot = Offset.Zero) {
        drawAura(character, pose)
        drawBackHair(character)
        drawBody(character)
        drawFace(character, pose)
        drawFrontHair(character)
        drawOverlays(character, pose)
    }
}

// ------------------------------------------------------------------ الخلفية

private fun DrawScope.drawAura(c: AnimeCharacter, pose: AvatarPose) {
    val center = Offset(0.5f, 0.5f)
    drawCircle(
        brush = Brush.radialGradient(
            colors = listOf(c.aura.copy(alpha = 0.55f), c.aura.copy(alpha = 0f)),
            center = center,
            radius = 0.5f
        ),
        radius = 0.5f,
        center = center
    )
    if (pose.ring > 0.01f) {
        listOf(pose.phase, (pose.phase + 0.5f) % 1f).forEach { p ->
            drawCircle(
                color = c.accent.copy(alpha = (1f - p) * 0.6f * pose.ring),
                radius = 0.34f + 0.16f * p,
                center = center,
                style = Stroke(width = 0.008f)
            )
        }
    }
}

// ------------------------------------------------------------------ الشعر الخلفي

private fun tailPath(mirror: Boolean): Path {
    fun x(v: Float) = if (mirror) 1f - v else v
    return Path().apply {
        moveTo(x(0.25f), 0.30f)
        cubicTo(x(0.04f), 0.36f, x(0.00f), 0.72f, x(0.10f), 0.97f)
        cubicTo(x(0.21f), 0.82f, x(0.27f), 0.62f, x(0.31f), 0.46f)
        close()
    }
}

private fun longBackPath(): Path = Path().apply {
    moveTo(0.22f, 0.32f)
    cubicTo(0.12f, 0.50f, 0.14f, 0.80f, 0.12f, 0.98f)
    lineTo(0.88f, 0.98f)
    cubicTo(0.86f, 0.80f, 0.88f, 0.50f, 0.78f, 0.32f)
    close()
}

private fun DrawScope.drawBackHair(c: AnimeCharacter) {
    val longBrush = Brush.verticalGradient(
        colors = listOf(c.hair, c.hairShade),
        startY = 0.3f,
        endY = 1f
    )
    when (c.hairStyle) {
        HairStyle.TWIN_TAILS -> {
            drawPath(tailPath(false), longBrush)
            drawPath(tailPath(true), longBrush)
        }
        HairStyle.LONG -> drawPath(longBackPath(), longBrush)
        HairStyle.BOB -> drawRoundRect(
            color = c.hairShade,
            topLeft = Offset(0.19f, 0.20f),
            size = Size(0.62f, 0.50f),
            cornerRadius = CornerRadius(0.20f)
        )
        HairStyle.SPIKY -> drawRoundRect(
            color = c.hairShade,
            topLeft = Offset(0.20f, 0.20f),
            size = Size(0.60f, 0.36f),
            cornerRadius = CornerRadius(0.15f)
        )
    }
}

// ------------------------------------------------------------------ الجسم

private fun DrawScope.drawBody(c: AnimeCharacter) {
    // الرقبة
    drawRoundRect(
        color = c.skinShade,
        topLeft = Offset(0.445f, 0.68f),
        size = Size(0.11f, 0.15f),
        cornerRadius = CornerRadius(0.03f)
    )
    // الكتفان / الملابس
    val body = Path().apply {
        moveTo(0.12f, 1f)
        cubicTo(0.12f, 0.84f, 0.30f, 0.77f, 0.50f, 0.77f)
        cubicTo(0.70f, 0.77f, 0.88f, 0.84f, 0.88f, 1f)
        close()
    }
    drawPath(body, c.outfit)
    drawPath(
        body,
        Brush.verticalGradient(
            colors = listOf(Color.White.copy(alpha = 0.14f), Color.Transparent),
            startY = 0.77f,
            endY = 1f
        )
    )
    // فتحة الياقة
    val collar = Path().apply {
        moveTo(0.41f, 0.775f)
        lineTo(0.50f, 0.875f)
        lineTo(0.59f, 0.775f)
        close()
    }
    drawPath(collar, c.skin)
    drawBow(c.accent, Offset(0.5f, 0.885f), 0.045f)
}

// ------------------------------------------------------------------ الوجه

private fun facePath(): Path = Path().apply {
    moveTo(0.24f, 0.42f)
    cubicTo(0.24f, 0.14f, 0.76f, 0.14f, 0.76f, 0.42f)
    cubicTo(0.76f, 0.58f, 0.64f, 0.73f, 0.50f, 0.75f)
    cubicTo(0.36f, 0.73f, 0.24f, 0.58f, 0.24f, 0.42f)
    close()
}

private fun DrawScope.drawFace(c: AnimeCharacter, pose: AvatarPose) {
    // الأذنان
    drawOval(c.skin, Offset(0.215f, 0.49f), Size(0.04f, 0.07f))
    drawOval(c.skin, Offset(0.745f, 0.49f), Size(0.04f, 0.07f))

    val face = facePath()
    drawPath(face, c.skin)
    // ظل خفيف تحت الغرة
    clipPath(face) {
        drawRect(
            brush = Brush.verticalGradient(
                colors = listOf(c.skinShade.copy(alpha = 0.55f), Color.Transparent),
                startY = 0.28f,
                endY = 0.46f
            ),
            topLeft = Offset(0.2f, 0.2f),
            size = Size(0.6f, 0.3f)
        )
    }

    // احمرار الخدين
    if (pose.blush > 0.01f) {
        val blush = BlushColor.copy(alpha = (pose.blush * 0.5f).coerceIn(0f, 1f))
        drawOval(blush, Offset(0.29f, 0.615f), Size(0.09f, 0.04f))
        drawOval(blush, Offset(0.62f, 0.615f), Size(0.09f, 0.04f))
    }

    drawBrow(c, pose, 0.385f, left = true)
    drawBrow(c, pose, 0.615f, left = false)
    drawEye(c, pose, 0.385f, 0.525f, left = true)
    drawEye(c, pose, 0.615f, 0.525f, left = false)

    // الأنف
    drawCircle(c.skinShade.copy(alpha = 0.8f), 0.005f, Offset(0.5f, 0.625f))
    drawMouth(pose)
}

private fun DrawScope.drawBrow(c: AnimeCharacter, pose: AvatarPose, cx: Float, left: Boolean) {
    val inner = if (left) 1f else -1f // الاتجاه نحو منتصف الوجه
    val baseY = 0.425f - pose.browLift * 0.018f
    val outer = Offset(cx - inner * 0.058f, baseY + pose.browSad * 0.010f)
    val innerPt = Offset(cx + inner * 0.058f, baseY - pose.browSad * 0.026f)
    drawLine(c.hairShade, outer, innerPt, strokeWidth = 0.012f, cap = StrokeCap.Round)
}

private fun DrawScope.drawEye(
    c: AnimeCharacter,
    pose: AvatarPose,
    cx: Float,
    cy: Float,
    left: Boolean
) {
    val w = 0.135f * pose.eyeScale
    val h = max(0.004f, 0.17f * pose.eyeScale * pose.blink)
    val rect = Rect(cx - w / 2f, cy - h / 2f, cx + w / 2f, cy + h / 2f)
    val eyePath = Path().apply { addOval(rect) }

    drawPath(eyePath, Color.White)
    clipPath(eyePath) {
        val irisW = 0.098f * pose.eyeScale
        val irisH = 0.15f * pose.eyeScale
        val ix = cx + pose.lookX * 0.018f
        val iy = cy + pose.lookY * 0.02f
        drawOval(
            brush = Brush.verticalGradient(
                colors = listOf(c.eyeDark, c.eye, lerp(c.eye, Color.White, 0.25f)),
                startY = iy - irisH / 2f,
                endY = iy + irisH / 2f
            ),
            topLeft = Offset(ix - irisW / 2f, iy - irisH / 2f),
            size = Size(irisW, irisH)
        )
        // البؤبؤ
        drawOval(Color(0xFF1B1B2B), Offset(ix - 0.027f, iy - 0.04f), Size(0.054f, 0.08f))
        // لمعة العين
        drawCircle(Color.White, 0.02f, Offset(ix - 0.022f, iy - 0.035f))
        drawCircle(Color.White.copy(alpha = 0.85f), 0.009f, Offset(ix + 0.02f, iy + 0.03f))
    }
    // الرمش العلوي
    drawArc(
        color = Ink,
        startAngle = 180f,
        sweepAngle = 180f,
        useCenter = false,
        topLeft = rect.topLeft,
        size = rect.size,
        style = Stroke(width = 0.012f, cap = StrokeCap.Round)
    )
    // ذيل الرمش الخارجي
    val dir = if (left) -1f else 1f
    drawLine(
        color = Ink,
        start = Offset(cx + dir * w / 2f, cy - h * 0.1f),
        end = Offset(cx + dir * (w / 2f + 0.014f), cy - h * 0.32f - 0.004f),
        strokeWidth = 0.011f,
        cap = StrokeCap.Round
    )
}

private fun DrawScope.drawMouth(pose: AvatarPose) {
    val cx = 0.5f
    val cy = 0.675f
    if (pose.mouthOpen > 0.06f) {
        val w = 0.05f + pose.mouthOpen * 0.03f
        val h = 0.012f + pose.mouthOpen * 0.05f
        val rect = Rect(cx - w / 2f, cy - h / 2f + 0.005f, cx + w / 2f, cy + h / 2f + 0.005f)
        val mouth = Path().apply { addOval(rect) }
        drawPath(mouth, MouthInside)
        clipPath(mouth) {
            drawOval(Tongue, Offset(cx - w * 0.35f, cy + h * 0.05f), Size(w * 0.7f, h * 0.6f))
        }
        return
    }
    val amount = abs(pose.mouthCurve)
    if (amount < 0.1f) {
        drawLine(
            color = Ink,
            start = Offset(cx - 0.025f, cy),
            end = Offset(cx + 0.025f, cy),
            strokeWidth = 0.010f,
            cap = StrokeCap.Round
        )
    } else {
        val depth = 0.04f * amount
        val smile = pose.mouthCurve > 0f
        val cy0 = if (smile) cy - depth / 2f else cy + depth / 2f
        drawArc(
            color = Ink,
            startAngle = if (smile) 20f else 200f,
            sweepAngle = 140f,
            useCenter = false,
            topLeft = Offset(cx - 0.035f, cy0 - depth),
            size = Size(0.07f, depth * 2f),
            style = Stroke(width = 0.010f, cap = StrokeCap.Round)
        )
    }
}

// ------------------------------------------------------------------ الشعر الأمامي

/** الغرة: خط سفلي متعرّج يبدأ من اليمين إلى اليسار. */
private fun Path.bangsToLeft() {
    lineTo(0.75f, 0.39f)
    lineTo(0.70f, 0.40f)
    lineTo(0.655f, 0.335f)
    lineTo(0.60f, 0.395f)
    lineTo(0.55f, 0.33f)
    lineTo(0.50f, 0.395f)
    lineTo(0.45f, 0.33f)
    lineTo(0.40f, 0.395f)
    lineTo(0.345f, 0.335f)
    lineTo(0.30f, 0.40f)
    lineTo(0.25f, 0.39f)
    close()
}

private fun roundCapPath(): Path = Path().apply {
    moveTo(0.215f, 0.50f)
    cubicTo(0.15f, 0.06f, 0.85f, 0.06f, 0.785f, 0.50f)
    bangsToLeft()
}

private fun spikyCapPath(): Path = Path().apply {
    moveTo(0.215f, 0.50f)
    lineTo(0.15f, 0.24f)
    lineTo(0.27f, 0.28f)
    lineTo(0.25f, 0.07f)
    lineTo(0.40f, 0.18f)
    lineTo(0.50f, 0.02f)
    lineTo(0.60f, 0.18f)
    lineTo(0.75f, 0.07f)
    lineTo(0.73f, 0.28f)
    lineTo(0.85f, 0.24f)
    lineTo(0.785f, 0.50f)
    bangsToLeft()
}

private fun DrawScope.sideLocks(c: AnimeCharacter, top: Float, height: Float, width: Float) {
    val r = CornerRadius(width / 2f)
    drawRoundRect(c.hair, Offset(0.205f, top), Size(width, height), r)
    drawRoundRect(c.hair, Offset(0.795f - width, top), Size(width, height), r)
}

private fun DrawScope.drawCatEars(c: AnimeCharacter) {
    listOf(false, true).forEach { mirror ->
        fun x(v: Float) = if (mirror) 1f - v else v
        val outer = Path().apply {
            moveTo(x(0.25f), 0.26f)
            lineTo(x(0.27f), 0.04f)
            lineTo(x(0.43f), 0.17f)
            close()
        }
        val inner = Path().apply {
            moveTo(x(0.285f), 0.22f)
            lineTo(x(0.295f), 0.10f)
            lineTo(x(0.38f), 0.17f)
            close()
        }
        drawPath(outer, c.hair)
        drawPath(inner, c.accent.copy(alpha = 0.75f))
    }
}

private fun DrawScope.drawFrontHair(c: AnimeCharacter) {
    if (c.accessory == Accessory.CAT_EARS) drawCatEars(c)

    val cap = if (c.hairStyle == HairStyle.SPIKY) spikyCapPath() else roundCapPath()
    drawPath(
        cap,
        Brush.verticalGradient(
            colors = listOf(lerp(c.hair, Color.White, 0.2f), c.hair),
            startY = 0.05f,
            endY = 0.42f
        )
    )
    // لمعة الشعر
    drawArc(
        color = Color.White.copy(alpha = 0.35f),
        startAngle = 205f,
        sweepAngle = 55f,
        useCenter = false,
        topLeft = Offset(0.30f, 0.20f),
        size = Size(0.40f, 0.26f),
        style = Stroke(width = 0.016f, cap = StrokeCap.Round)
    )

    when (c.hairStyle) {
        HairStyle.BOB -> sideLocks(c, top = 0.30f, height = 0.38f, width = 0.085f)
        HairStyle.LONG -> sideLocks(c, top = 0.30f, height = 0.52f, width = 0.07f)
        HairStyle.TWIN_TAILS -> sideLocks(c, top = 0.30f, height = 0.26f, width = 0.06f)
        HairStyle.SPIKY -> sideLocks(c, top = 0.34f, height = 0.18f, width = 0.05f)
    }

    when (c.accessory) {
        Accessory.RIBBONS -> {
            drawBow(c.accent, Offset(0.25f, 0.31f), 0.05f)
            drawBow(c.accent, Offset(0.75f, 0.31f), 0.05f)
        }
        Accessory.HEADBAND -> {
            val band = Path().apply {
                moveTo(0.215f, 0.36f)
                cubicTo(0.30f, 0.20f, 0.70f, 0.20f, 0.785f, 0.36f)
            }
            drawPath(band, c.accent, style = Stroke(width = 0.03f, cap = StrokeCap.Round))
            drawRoundRect(
                color = Color(0xFFCFD8DC),
                topLeft = Offset(0.465f, 0.22f),
                size = Size(0.07f, 0.04f),
                cornerRadius = CornerRadius(0.01f)
            )
        }
        Accessory.HAIRPIN -> {
            drawSparkle(Offset(0.66f, 0.30f), 0.035f, c.accent)
            drawCircle(Color.White.copy(alpha = 0.8f), 0.006f, Offset(0.66f, 0.30f))
        }
        Accessory.CAT_EARS -> Unit
    }
}

// ------------------------------------------------------------------ تأثيرات الحالات

private fun DrawScope.drawOverlays(c: AnimeCharacter, pose: AvatarPose) {
    // PROCESSING: فقاعة تفكير بثلاث نقاط تقفز
    if (pose.thinking > 0.01f) {
        val a = pose.thinking.coerceIn(0f, 1f)
        val white = Color.White.copy(alpha = 0.92f * a)
        drawRoundRect(white, Offset(0.65f, 0.03f), Size(0.30f, 0.12f), CornerRadius(0.06f))
        drawCircle(white, 0.014f, Offset(0.67f, 0.18f))
        drawCircle(white, 0.008f, Offset(0.655f, 0.205f))
        for (i in 0..2) {
            val bounce = max(0f, sin((pose.phase - i * 0.18f) * TWO_PI))
            drawCircle(
                color = c.accent.copy(alpha = a),
                radius = 0.016f + 0.006f * bounce,
                center = Offset(0.72f + i * 0.075f, 0.09f - 0.012f * bounce)
            )
        }
    }

    // SPEAKING: نجوم متلألئة
    if (pose.sparkle > 0.01f) {
        val spots = listOf(
            Offset(0.10f, 0.24f) to 0f,
            Offset(0.90f, 0.34f) to 0.33f,
            Offset(0.06f, 0.55f) to 0.66f
        )
        spots.forEach { (pos, offset) ->
            val t = (sin((pose.phase + offset) * TWO_PI) + 1f) / 2f
            drawSparkle(
                center = pos,
                r = 0.02f + 0.03f * t,
                color = c.accent.copy(alpha = (pose.sparkle * (0.35f + 0.65f * t)).coerceIn(0f, 1f))
            )
        }
    }

    // ERROR: قطرة عرق
    if (pose.sweat > 0.01f) {
        val x = 0.79f
        val y = 0.50f
        val drop = Path().apply {
            moveTo(x, y - 0.045f)
            cubicTo(x + 0.03f, y - 0.01f, x + 0.03f, y + 0.03f, x, y + 0.03f)
            cubicTo(x - 0.03f, y + 0.03f, x - 0.03f, y - 0.01f, x, y - 0.045f)
            close()
        }
        drawPath(drop, SweatColor.copy(alpha = pose.sweat.coerceIn(0f, 1f)))
    }
}

// ------------------------------------------------------------------ أدوات مساعدة

private fun DrawScope.drawBow(color: Color, center: Offset, size: Float) {
    val left = Path().apply {
        moveTo(center.x, center.y)
        lineTo(center.x - size, center.y - size * 0.8f)
        lineTo(center.x - size, center.y + size * 0.8f)
        close()
    }
    val right = Path().apply {
        moveTo(center.x, center.y)
        lineTo(center.x + size, center.y - size * 0.8f)
        lineTo(center.x + size, center.y + size * 0.8f)
        close()
    }
    drawPath(left, color)
    drawPath(right, color)
    drawCircle(lerp(color, Color.Black, 0.25f), size * 0.35f, center)
}

/** نجمة رباعية الرؤوس. */
private fun DrawScope.drawSparkle(center: Offset, r: Float, color: Color) {
    val cx = center.x
    val cy = center.y
    val star = Path().apply {
        moveTo(cx, cy - r)
        cubicTo(cx, cy, cx, cy, cx + r, cy)
        cubicTo(cx, cy, cx, cy, cx, cy + r)
        cubicTo(cx, cy, cx, cy, cx - r, cy)
        cubicTo(cx, cy, cx, cy, cx, cy - r)
        close()
    }
    drawPath(star, color)
}
''')

write_file("app/src/main/java/com/example/voiceassistant/ui/components/AnimeAvatar.kt", r'''package com.example.voiceassistant.ui.components

import androidx.compose.animation.Crossfade
import androidx.compose.animation.core.Animatable
import androidx.compose.animation.core.FastOutSlowInEasing
import androidx.compose.animation.core.LinearEasing
import androidx.compose.animation.core.RepeatMode
import androidx.compose.animation.core.animateFloat
import androidx.compose.animation.core.animateFloatAsState
import androidx.compose.animation.core.infiniteRepeatable
import androidx.compose.animation.core.rememberInfiniteTransition
import androidx.compose.animation.core.tween
import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.remember
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.graphics.TransformOrigin
import androidx.compose.ui.graphics.drawscope.scale
import androidx.compose.ui.graphics.graphicsLayer
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import com.example.voiceassistant.viewmodel.AssistantStatus
import kotlin.math.cos
import kotlin.math.sin
import kotlin.random.Random
import kotlinx.coroutines.delay

/**
 * شخصية الأنمي المتحركة. تتفاعل مع حالة المساعد:
 *  - IDLE:       تنفّس هادئ + رمش + ابتسامة.
 *  - LISTENING:  تميل برأسها، عيون أوسع، حواجب مرفوعة، حلقات صوتية تنتشر.
 *  - PROCESSING: تنظر للأعلى وتتحرك عيناها + فقاعة تفكير بثلاث نقاط.
 *  - SPEAKING:   الفم يتحرك مع الكلام + ارتداد خفيف + نجوم متلألئة.
 *  - ERROR:      حاجبان حزينان + عبوس + قطرة عرق.
 *
 * عند تغيير [character] يحدث تلاشٍ ناعم بين الشخصيتين.
 */
@Composable
fun AnimeAvatar(
    character: AnimeCharacter,
    status: AssistantStatus,
    modifier: Modifier = Modifier,
    contentDescription: String? = null
) {
    val semanticsModifier = if (contentDescription != null) {
        Modifier.semantics { this.contentDescription = contentDescription }
    } else {
        Modifier
    }

    Crossfade(
        targetState = character,
        modifier = modifier.then(semanticsModifier),
        animationSpec = tween(350),
        label = "avatarCrossfade"
    ) { current ->
        Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            AnimatedCharacter(
                character = current,
                status = status,
                modifier = Modifier
                    .fillMaxHeight()
                    .aspectRatio(1f)
            )
        }
    }
}

@Composable
private fun AnimatedCharacter(
    character: AnimeCharacter,
    status: AssistantStatus,
    modifier: Modifier
) {
    val listening = status == AssistantStatus.LISTENING
    val processing = status == AssistantStatus.PROCESSING
    val speaking = status == AssistantStatus.SPEAKING
    val error = status == AssistantStatus.ERROR

    // ---- التعابير: تنتقل بنعومة عند تغيّر الحالة
    val smooth = tween<Float>(durationMillis = 350)
    val tilt = animateFloatAsState(
        targetValue = when {
            listening -> 5f
            error -> -4f
            processing -> -2f
            else -> 0f
        },
        animationSpec = smooth, label = "tilt"
    )
    val eyeScale = animateFloatAsState(
        targetValue = when {
            listening -> 1.12f
            error -> 0.94f
            else -> 1f
        },
        animationSpec = smooth, label = "eyeScale"
    )
    val browLift = animateFloatAsState(if (listening) 1f else 0f, animationSpec = smooth, label = "browLift")
    val browSad = animateFloatAsState(if (error) 1f else 0f, animationSpec = smooth, label = "browSad")
    val blush = animateFloatAsState(
        targetValue = when {
            speaking -> 0.8f
            listening -> 0.5f
            error -> 0f
            else -> 0.3f
        },
        animationSpec = smooth, label = "blush"
    )
    val curve = animateFloatAsState(
        targetValue = when {
            error -> -1f
            processing -> 0f
            listening -> 0.4f
            else -> 1f
        },
        animationSpec = smooth, label = "curve"
    )
    val thinking = animateFloatAsState(if (processing) 1f else 0f, animationSpec = smooth, label = "thinking")
    val ring = animateFloatAsState(if (listening) 1f else 0f, animationSpec = smooth, label = "ring")
    val sweat = animateFloatAsState(if (error) 1f else 0f, animationSpec = smooth, label = "sweat")
    val sparkle = animateFloatAsState(if (speaking) 1f else 0f, animationSpec = smooth, label = "sparkle")
    val talkAmount = animateFloatAsState(if (speaking) 1f else 0f, animationSpec = tween(150), label = "talkAmount")

    // ---- حركات دائمة
    val infinite = rememberInfiniteTransition(label = "avatarLoop")
    val float = infinite.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(2600, easing = FastOutSlowInEasing), RepeatMode.Reverse),
        label = "float"
    )
    val phase = infinite.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(1400, easing = LinearEasing)),
        label = "phase"
    )
    // فتح/إغلاق الفم: موجتان بسرعتين مختلفتين لإحساس طبيعي
    val talkA = infinite.animateFloat(
        initialValue = 0f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(170, easing = LinearEasing), RepeatMode.Reverse),
        label = "talkA"
    )
    val talkB = infinite.animateFloat(
        initialValue = 0.55f,
        targetValue = 1f,
        animationSpec = infiniteRepeatable(tween(430, easing = LinearEasing), RepeatMode.Reverse),
        label = "talkB"
    )

    // ---- الرمش العشوائي
    val blink = remember { Animatable(1f) }
    LaunchedEffect(Unit) {
        while (true) {
            delay(Random.nextLong(2200L, 5200L))
            blink.animateTo(0f, tween(70))
            blink.animateTo(1f, tween(120))
        }
    }

    Canvas(
        modifier = modifier.graphicsLayer {
            val s = size.height
            val breathing = (float.value - 0.5f) * 0.03f * s
            val bounce = talkA.value * 0.012f * s * talkAmount.value
            translationY = breathing - bounce
            rotationZ = tilt.value + sin(phase.value * TWO_PI) * 2f * thinking.value
            transformOrigin = TransformOrigin(0.5f, 0.85f)
        }
    ) {
        val t = phase.value * TWO_PI
        val think = thinking.value
        drawAnimeCharacter(
            character,
            AvatarPose(
                blink = blink.value,
                eyeScale = eyeScale.value,
                mouthOpen = talkA.value * talkB.value * talkAmount.value,
                mouthCurve = curve.value,
                lookX = cos(t) * think,
                lookY = (-0.6f + sin(t) * 0.3f) * think,
                browLift = browLift.value,
                browSad = browSad.value,
                blush = blush.value,
                thinking = think,
                ring = ring.value,
                sweat = sweat.value,
                sparkle = sparkle.value,
                phase = phase.value
            )
        )
    }
}

/** صورة مصغّرة ثابتة للوجه (للقائمة وزر الاختيار) — بدون أنيميشن لتخفيف الحمل. */
@Composable
fun CharacterThumbnail(character: AnimeCharacter, modifier: Modifier = Modifier) {
    Canvas(modifier = modifier.aspectRatio(1f)) {
        scale(scale = 1.75f, pivot = Offset(size.width * 0.5f, size.height * 0.42f)) {
            drawAnimeCharacter(character, AvatarPose())
        }
    }
}
''')

write_file("app/src/main/java/com/example/voiceassistant/ui/components/CharacterPicker.kt", r'''package com.example.voiceassistant.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.DropdownMenu
import androidx.compose.material3.DropdownMenuItem
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import com.example.voiceassistant.viewmodel.AppLanguage

/**
 * زر دائري (وجه الشخصية الحالية) يفتح قائمة اختيار الشخصيات.
 * يوضع داخل actions الخاصة بـ TopAppBar.
 */
@Composable
fun CharacterMenuButton(
    selected: AnimeCharacter,
    language: AppLanguage,
    onSelected: (AnimeCharacter) -> Unit,
    modifier: Modifier = Modifier
) {
    var expanded by remember { mutableStateOf(false) }
    val label = language.tr("تغيير الشخصية", "Change character")

    Box(modifier = modifier) {
        IconButton(onClick = { expanded = true }) {
            Box(
                modifier = Modifier
                    .size(32.dp)
                    .clip(CircleShape)
                    .background(selected.aura.copy(alpha = 0.4f))
                    .border(1.5.dp, MaterialTheme.colorScheme.primary, CircleShape)
                    .semantics { contentDescription = label }
            ) {
                CharacterThumbnail(selected, Modifier.fillMaxSize())
            }
        }

        DropdownMenu(expanded = expanded, onDismissRequest = { expanded = false }) {
            Text(
                text = language.tr("اختر الشخصية", "Choose a character"),
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 6.dp)
            )
            AnimeCharacters.all.forEach { character ->
                DropdownMenuItem(
                    text = { Text(character.name(language)) },
                    leadingIcon = {
                        Box(
                            modifier = Modifier
                                .size(36.dp)
                                .clip(CircleShape)
                                .background(character.aura.copy(alpha = 0.4f))
                        ) {
                            CharacterThumbnail(character, Modifier.fillMaxSize())
                        }
                    },
                    trailingIcon = {
                        if (character.id == selected.id) {
                            Icon(Icons.Filled.Check, contentDescription = null)
                        }
                    },
                    onClick = {
                        onSelected(character)
                        expanded = false
                    }
                )
            }
        }
    }
}
''')



# ------------------------------------------------------------------------------
# الإضافة: التذكيرات الصوتية + التفاعل الاستباقي
# ------------------------------------------------------------------------------

# 46. تذكيرات صوتية: الأمر + الجدولة + المستقبِل + الخدمة الأمامية
write_file("app/src/main/java/com/example/voiceassistant/commands/commands/ReminderCommand.kt", r'''package com.example.voiceassistant.commands.commands

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.net.Uri
import android.os.Build
import android.provider.Settings
import androidx.core.content.ContextCompat
import com.example.voiceassistant.commands.CommandResult
import com.example.voiceassistant.commands.ParsedCommand
import com.example.voiceassistant.commands.startNewTask
import com.example.voiceassistant.service.ReminderScheduler
import com.example.voiceassistant.viewmodel.AppLanguage
import java.util.Calendar
import java.util.Locale

/** «ذكرني بشرب الماء بعد 10 دقائق» -> an exact alarm that speaks the reminder even if the app is closed. */
object ReminderCommand {

    fun execute(context: Context, command: ParsedCommand.Reminder, lang: AppLanguage): CommandResult {
        val at = command.triggerAtMillis ?: return CommandResult.Failure(
            lang.tr(
                "متى تريد أن أذكّرك؟ قل مثلاً «ذكرني بشرب الماء بعد 10 دقائق» أو «ذكرني بموعد الطبيب غداً الساعة 5 مساءً».",
                "When should I remind you? Say for example \"remind me to drink water in 10 minutes\" or \"remind me about the doctor tomorrow at 5 pm\"."
            )
        )

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU &&
            ContextCompat.checkSelfPermission(context, Manifest.permission.POST_NOTIFICATIONS) !=
            PackageManager.PERMISSION_GRANTED
        ) {
            return CommandResult.NeedsPermission(
                Manifest.permission.POST_NOTIFICATIONS,
                lang.tr("أحتاج إذن الإشعارات لكي أذكّرك.", "I need the notification permission to remind you.")
            )
        }

        val exact = ReminderScheduler.schedule(context, command.text, at)
        val whenText = describe(at, lang)
        val ok = lang.tr(
            "حسناً، سأذكّرك بـ«${command.text}» $whenText.",
            "Okay, I'll remind you about \"${command.text}\" $whenText."
        )
        if (exact) return CommandResult.Success(ok)

        // "Alarms & reminders" is off (Android 12+): the reminder still works but may be a bit late.
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            try {
                context.startNewTask(
                    Intent(Settings.ACTION_REQUEST_SCHEDULE_EXACT_ALARM, Uri.parse("package:${context.packageName}"))
                )
            } catch (e: Exception) {
                // settings page not available on this device
            }
        }
        return CommandResult.Success(
            ok + " " + lang.tr(
                "فعّل «التنبيهات والتذكيرات» من الإعدادات ليكون التذكير في وقته بالضبط.",
                "Turn on \"Alarms & reminders\" in Settings so it fires exactly on time."
            )
        )
    }

    private fun describe(at: Long, lang: AppLanguage): String {
        val now = Calendar.getInstance()
        val target = Calendar.getInstance().apply { timeInMillis = at }
        val time = String.format(
            Locale.US, "%02d:%02d",
            target.get(Calendar.HOUR_OF_DAY), target.get(Calendar.MINUTE)
        )
        val dayDiff = dayNumber(target) - dayNumber(now)
        return when {
            dayDiff <= 0 -> lang.tr("الساعة $time", "at $time")
            dayDiff == 1L -> lang.tr("غداً الساعة $time", "tomorrow at $time")
            else -> String.format(
                Locale.US, "%02d/%02d %s",
                target.get(Calendar.DAY_OF_MONTH), target.get(Calendar.MONTH) + 1, time
            ).let { lang.tr("بتاريخ $it", "on $it") }
        }
    }

    private fun dayNumber(c: Calendar): Long {
        val zone = c.timeZone.getOffset(c.timeInMillis).toLong()
        return (c.timeInMillis + zone) / 86_400_000L
    }
}
''')

write_file("app/src/main/java/com/example/voiceassistant/service/NotificationHelper.kt", r'''package com.example.voiceassistant.service

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import androidx.core.app.NotificationCompat
import com.example.voiceassistant.MainActivity
import com.example.voiceassistant.viewmodel.AppLanguage

/** Notification channels (Android 8+) and the notifications used by reminders and check-ins. */
object NotificationHelper {

    const val CHANNEL_REMINDERS = "va_reminders"
    const val CHANNEL_PROACTIVE = "va_proactive"
    const val CHANNEL_SPEAKING = "va_speaking"

    /** Safe to call many times; channels are only created once by the system. */
    fun createChannels(context: Context) {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val nm = context.getSystemService(NotificationManager::class.java) ?: return

        val reminders = NotificationChannel(
            CHANNEL_REMINDERS,
            "التذكيرات / Reminders",
            NotificationManager.IMPORTANCE_HIGH
        ).apply {
            description = "تذكيرات صوتية بمواعيدك / Spoken reminders"
            enableVibration(true)
        }
        val proactive = NotificationChannel(
            CHANNEL_PROACTIVE,
            "السؤال عن الأحوال / Check-ins",
            NotificationManager.IMPORTANCE_DEFAULT
        ).apply {
            description = "رسائل ودية من المساعد بين الحين والآخر / Friendly check-ins"
        }
        val speaking = NotificationChannel(
            CHANNEL_SPEAKING,
            "النطق / Speaking",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "يظهر أثناء نطق المساعد في الخلفية / Shown while speaking in the background"
            setShowBadge(false)
        }
        nm.createNotificationChannels(listOf(reminders, proactive, speaking))
    }

    private fun openAppIntent(context: Context, requestCode: Int): PendingIntent {
        val intent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP
        }
        return PendingIntent.getActivity(
            context,
            requestCode,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
    }

    fun postReminder(context: Context, id: Int, text: String, missed: Boolean = false) {
        createChannels(context)
        val lang = AppLanguage.detect(text)
        val title = if (missed) {
            lang.tr("تذكير فائت", "Missed reminder")
        } else {
            lang.tr("تذكير", "Reminder")
        }
        val notification = NotificationCompat.Builder(context, CHANNEL_REMINDERS)
            .setSmallIcon(android.R.drawable.ic_popup_reminder)
            .setContentTitle(title)
            .setContentText(text)
            .setStyle(NotificationCompat.BigTextStyle().bigText(text))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_REMINDER)
            .setAutoCancel(true)
            .setContentIntent(openAppIntent(context, id))
            .build()
        notify(context, 20000 + id, notification)
    }

    fun postProactive(context: Context, text: String) {
        createChannels(context)
        val lang = AppLanguage.detect(text)
        val notification = NotificationCompat.Builder(context, CHANNEL_PROACTIVE)
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentTitle(lang.tr("Zevorix AI", "Zevorix AI"))
            .setContentText(text)
            .setStyle(NotificationCompat.BigTextStyle().bigText(text))
            .setPriority(NotificationCompat.PRIORITY_DEFAULT)
            .setAutoCancel(true)
            .setContentIntent(openAppIntent(context, 9001))
            .build()
        notify(context, 9001, notification)
    }

    private fun notify(context: Context, id: Int, notification: android.app.Notification) {
        try {
            context.getSystemService(NotificationManager::class.java)?.notify(id, notification)
        } catch (e: Exception) {
            // Missing notification permission or similar: nothing else we can do here.
        }
    }
}
''')

write_file("app/src/main/java/com/example/voiceassistant/service/ProactiveMessages.kt", r'''package com.example.voiceassistant.service

import com.example.voiceassistant.viewmodel.AppLanguage
import java.util.Calendar
import kotlin.random.Random

/** The short sentences the assistant says on its own (greeting, check-ins, reminders). */
object ProactiveMessages {

    /**
     * Time-of-day greeting. Without a saved [userName] it also asks (kindly) for the user's name;
     * with a name it greets the user personally and asks how they are doing.
     */
    fun greeting(
        lang: AppLanguage,
        hour: Int = Calendar.getInstance().get(Calendar.HOUR_OF_DAY),
        userName: String? = null
    ): String {
        val name = userName?.trim().orEmpty()
        if (name.isEmpty()) {
            val opener = when (hour) {
                in 5..11 -> lang.tr("صباح الخير!", "Good morning!")
                in 12..17 -> lang.tr("مساء الخير!", "Good afternoon!")
                in 18..22 -> lang.tr("مساء الخير!", "Good evening!")
                else -> lang.tr("أهلاً بك!", "Hello there!")
            }
            return opener + " " + lang.tr(
                "أنا Zevorix AI، مساعدك الصوتي. بالمناسبة، أشعر بالفضول لمعرفة اسمك، ما هو؟",
                "I'm Zevorix AI, your voice assistant. By the way, I'm curious to know your name. What is it?"
            )
        }
        return when (hour) {
            in 5..11 -> lang.tr(
                "صباح الخير يا $name! كيف حالك هذا الصباح؟",
                "Good morning, $name! How are you doing this morning?"
            )
            in 12..17 -> lang.tr(
                "مساء الخير يا $name! كيف حالك اليوم؟",
                "Good afternoon, $name! How are you doing today?"
            )
            in 18..22 -> lang.tr(
                "مساء الخير يا $name! كيف كان يومك؟ كيف حالك الآن؟",
                "Good evening, $name! How was your day? How are you feeling?"
            )
            else -> lang.tr(
                "أهلاً بك يا $name! كيف حالك؟",
                "Hello there, $name! How are you?"
            )
        }
    }

    /** One of a few friendly check-in sentences. */
    fun checkIn(lang: AppLanguage): String {
        val options = if (lang == AppLanguage.ARABIC) {
            listOf(
                "أتمنى أن يكون يومك سعيداً، هل تحتاج مساعدتي في شيء؟",
                "كيف حالك الآن؟ أنا هنا إذا احتجت أي مساعدة.",
                "مرحباً! أردت أن أطمئن عليك. هل أستطيع مساعدتك في شيء؟"
            )
        } else {
            listOf(
                "I hope you're having a lovely day. Is there anything I can help you with?",
                "How are you doing right now? I'm here if you need anything.",
                "Hi! Just checking in on you. Can I help with anything?"
            )
        }
        return options[Random.nextInt(options.size)]
    }

    /** What is spoken out loud when a reminder fires. */
    fun reminderSpeech(text: String): String {
        val lang = AppLanguage.detect(text)
        return lang.tr("تذكير: $text", "Reminder: $text")
    }
}
''')

write_file("app/src/main/java/com/example/voiceassistant/service/ReminderScheduler.kt", r'''package com.example.voiceassistant.service

import android.app.AlarmManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.os.Build
import org.json.JSONArray
import org.json.JSONObject

/**
 * Schedules reminders with AlarmManager (setExactAndAllowWhileIdle) so they fire even when the
 * app is closed or the phone is in Doze. Pending reminders are kept in SharedPreferences so they
 * can be re-armed after a reboot ([ReminderReceiver]).
 */
object ReminderScheduler {

    const val ACTION_REMINDER = "com.example.voiceassistant.action.REMINDER"
    const val EXTRA_ID = "reminder_id"
    const val EXTRA_TEXT = "reminder_text"

    private const val PREFS = "va_reminders"
    private const val KEY_LIST = "list"
    private const val KEY_NEXT_ID = "next_id"

    data class Reminder(val id: Int, val text: String, val atMillis: Long)

    /** Android 12+ lets the user revoke "Alarms & reminders"; without it only inexact alarms work. */
    fun canScheduleExact(context: Context): Boolean {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.S) return true
        val am = context.getSystemService(AlarmManager::class.java) ?: return false
        return am.canScheduleExactAlarms()
    }

    /** @return true if the alarm is exact, false if it had to fall back to an inexact alarm. */
    @Synchronized
    fun schedule(context: Context, text: String, atMillis: Long): Boolean {
        val app = context.applicationContext
        val reminder = Reminder(nextId(app), text, atMillis)
        save(app, load(app) + reminder)
        return setAlarm(app, reminder)
    }

    @Synchronized
    fun remove(context: Context, id: Int) {
        val app = context.applicationContext
        save(app, load(app).filter { it.id != id })
    }

    /** Re-arms every stored reminder (after reboot / app update). Overdue ones become notifications. */
    @Synchronized
    fun rescheduleAll(context: Context) {
        val app = context.applicationContext
        val now = System.currentTimeMillis()
        val all = load(app)
        val keep = mutableListOf<Reminder>()
        for (r in all) {
            if (r.atMillis > now) {
                setAlarm(app, r)
                keep.add(r)
            } else {
                NotificationHelper.postReminder(app, r.id, r.text, missed = true)
            }
        }
        save(app, keep)
    }

    private fun pendingIntent(context: Context, id: Int, text: String): PendingIntent {
        val intent = Intent(context, ReminderReceiver::class.java).apply {
            action = ACTION_REMINDER
            putExtra(EXTRA_ID, id)
            putExtra(EXTRA_TEXT, text)
        }
        return PendingIntent.getBroadcast(
            context,
            id,
            intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
    }

    private fun setAlarm(context: Context, r: Reminder): Boolean {
        val am = context.getSystemService(AlarmManager::class.java) ?: return false
        val pi = pendingIntent(context, r.id, r.text)
        if (canScheduleExact(context)) {
            try {
                am.setExactAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, r.atMillis, pi)
                return true
            } catch (e: SecurityException) {
                // permission was revoked in the meantime -> fall through to the inexact alarm
            }
        }
        am.setAndAllowWhileIdle(AlarmManager.RTC_WAKEUP, r.atMillis, pi)
        return false
    }

    // ---- tiny persistence layer ------------------------------------------------------------

    private fun nextId(context: Context): Int {
        val prefs = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        val id = prefs.getInt(KEY_NEXT_ID, 1000)
        prefs.edit().putInt(KEY_NEXT_ID, if (id >= 1_000_000) 1000 else id + 1).apply()
        return id
    }

    private fun load(context: Context): List<Reminder> {
        val raw = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getString(KEY_LIST, null)
            ?: return emptyList()
        return try {
            val arr = JSONArray(raw)
            (0 until arr.length()).map { i ->
                val o = arr.getJSONObject(i)
                Reminder(o.getInt("id"), o.getString("text"), o.getLong("at"))
            }
        } catch (e: Exception) {
            emptyList()
        }
    }

    private fun save(context: Context, list: List<Reminder>) {
        val arr = JSONArray()
        list.forEach {
            arr.put(JSONObject().put("id", it.id).put("text", it.text).put("at", it.atMillis))
        }
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit().putString(KEY_LIST, arr.toString()).apply()
    }
}
''')

write_file("app/src/main/java/com/example/voiceassistant/service/ReminderReceiver.kt", r'''package com.example.voiceassistant.service

import android.app.AlarmManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent

/**
 * Receives (a) the exact alarm of a reminder and (b) boot / update events.
 *
 * When a reminder fires it always posts a notification first (the fallback), then tries to start
 * [SpeakingService] so the reminder is also spoken out loud.
 */
class ReminderReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            ReminderScheduler.ACTION_REMINDER -> {
                val id = intent.getIntExtra(ReminderScheduler.EXTRA_ID, 0)
                val text = intent.getStringExtra(ReminderScheduler.EXTRA_TEXT).orEmpty()
                if (text.isBlank()) return
                ReminderScheduler.remove(context, id)
                NotificationHelper.postReminder(context, id, text)
                try {
                    SpeakingService.start(context, ProactiveMessages.reminderSpeech(text), alarm = true)
                } catch (e: Exception) {
                    // The notification is already visible; speech simply isn't possible right now.
                }
            }

            Intent.ACTION_BOOT_COMPLETED,
            Intent.ACTION_MY_PACKAGE_REPLACED,
            AlarmManager.ACTION_SCHEDULE_EXACT_ALARM_PERMISSION_STATE_CHANGED -> {
                ReminderScheduler.rescheduleAll(context)
                ProactiveScheduler.schedule(context)
            }
        }
    }
}
''')

write_file("app/src/main/java/com/example/voiceassistant/service/SpeakingService.kt", r'''package com.example.voiceassistant.service

import android.app.Notification
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.media.AudioAttributes
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.PowerManager
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import androidx.core.content.ContextCompat
import com.example.voiceassistant.viewmodel.AppLanguage
import java.util.ArrayDeque
import java.util.Locale

/**
 * Foreground service that speaks a sentence with TextToSpeech while the app is closed
 * (reminders and proactive check-ins). It stops itself when everything has been said.
 */
class SpeakingService : Service() {

    companion object {
        const val EXTRA_TEXT = "speak_text"
        const val EXTRA_ALARM = "speak_alarm"
        private const val FOREGROUND_ID = 7001
        private const val MAX_LIFETIME_MS = 60_000L

        /** @throws IllegalStateException on Android 12+ when the system forbids starting it right now. */
        fun start(context: Context, text: String, alarm: Boolean) {
            val intent = Intent(context, SpeakingService::class.java)
                .putExtra(EXTRA_TEXT, text)
                .putExtra(EXTRA_ALARM, alarm)
            ContextCompat.startForegroundService(context, intent)
        }
    }

    private val mainHandler = Handler(Looper.getMainLooper())
    private val pending = ArrayDeque<Pair<String, Boolean>>()
    private var engine: TextToSpeech? = null
    private var ready = false
    private var active = 0
    private var wakeLock: PowerManager.WakeLock? = null
    private var counter = 0

    private val listener = object : UtteranceProgressListener() {
        override fun onStart(utteranceId: String?) = Unit

        override fun onDone(utteranceId: String?) = utteranceFinished()

        @Deprecated("Deprecated in Java")
        override fun onError(utteranceId: String?) = utteranceFinished()

        override fun onError(utteranceId: String?, errorCode: Int) = utteranceFinished()

        override fun onStop(utteranceId: String?, interrupted: Boolean) = utteranceFinished()
    }

    override fun onCreate() {
        super.onCreate()
        NotificationHelper.createChannels(this)
        acquireWakeLock()
        engine = TextToSpeech(applicationContext) { status ->
            mainHandler.post {
                if (status == TextToSpeech.SUCCESS) {
                    engine?.setOnUtteranceProgressListener(listener)
                    ready = true
                    flush()
                } else {
                    finish()
                }
            }
        }
        // Safety net: never keep the foreground service alive forever.
        mainHandler.postDelayed({ finish() }, MAX_LIFETIME_MS)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val text = intent?.getStringExtra(EXTRA_TEXT).orEmpty()
        val alarm = intent?.getBooleanExtra(EXTRA_ALARM, false) ?: false

        // Must be called within a few seconds of startForegroundService().
        try {
            val type = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
            } else {
                0
            }
            ServiceCompat.startForeground(this, FOREGROUND_ID, buildNotification(text), type)
        } catch (e: Exception) {
            stopSelf()
            return START_NOT_STICKY
        }

        if (text.isNotBlank()) {
            pending.add(text to alarm)
            active++
        }
        if (ready) flush()
        if (active <= 0 && ready) finish()
        return START_NOT_STICKY
    }

    private fun flush() {
        val tts = engine ?: return
        while (pending.isNotEmpty()) {
            val (text, alarm) = pending.poll() ?: break
            val lang = AppLanguage.detect(text)
            val result = tts.setLanguage(lang.locale)
            if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                tts.setLanguage(Locale.getDefault())
            }
            tts.setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(if (alarm) AudioAttributes.USAGE_ALARM else AudioAttributes.USAGE_ASSISTANT)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build()
            )
            counter++
            val safe = text.take(TextToSpeech.getMaxSpeechInputLength() - 1)
            val code = tts.speak(safe, TextToSpeech.QUEUE_ADD, null, "va-svc-$counter")
            if (code != TextToSpeech.SUCCESS) utteranceFinished()
        }
    }

    private fun utteranceFinished() {
        mainHandler.post {
            active--
            if (active <= 0 && pending.isEmpty()) finish()
        }
    }

    private fun finish() {
        ServiceCompat.stopForeground(this, ServiceCompat.STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    private fun buildNotification(text: String): Notification {
        val lang = AppLanguage.detect(text)
        return NotificationCompat.Builder(this, NotificationHelper.CHANNEL_SPEAKING)
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentTitle(lang.tr("Zevorix AI", "Zevorix AI"))
            .setContentText(text.ifBlank { lang.tr("جارٍ النطق…", "Speaking…") })
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .build()
    }

    private fun acquireWakeLock() {
        try {
            val pm = getSystemService(PowerManager::class.java)
            wakeLock = pm?.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "voiceassistant:speaking")
                ?.apply { acquire(MAX_LIFETIME_MS) }
        } catch (e: Exception) {
            wakeLock = null
        }
    }

    override fun onDestroy() {
        mainHandler.removeCallbacksAndMessages(null)
        engine?.stop()
        engine?.shutdown()
        engine = null
        try {
            if (wakeLock?.isHeld == true) wakeLock?.release()
        } catch (e: Exception) {
            // already released
        }
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
''')

# 47. التفاعل الاستباقي: WorkManager كل 6 ساعات (إشعار + نطق)
write_file("app/src/main/java/com/example/voiceassistant/service/ProactiveWorker.kt", r'''package com.example.voiceassistant.service

import android.content.Context
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import androidx.work.ExistingPeriodicWorkPolicy
import androidx.work.PeriodicWorkRequestBuilder
import androidx.work.WorkManager
import androidx.work.Worker
import androidx.work.WorkerParameters
import com.example.voiceassistant.viewmodel.AppLanguage
import java.util.Calendar
import java.util.concurrent.CountDownLatch
import java.util.concurrent.TimeUnit

/** Schedules the periodic "how are you?" check-in with WorkManager (survives app close and reboot). */
object ProactiveScheduler {

    /** How often the assistant asks how you are (4 or 6 hours is a good range). */
    const val INTERVAL_HOURS = 6L

    private const val UNIQUE_NAME = "va_proactive_checkin"
    private const val PREFS = "va_proactive"
    private const val KEY_LANG = "lang"

    fun schedule(context: Context) {
        val request = PeriodicWorkRequestBuilder<ProactiveWorker>(INTERVAL_HOURS, TimeUnit.HOURS)
            .setInitialDelay(INTERVAL_HOURS, TimeUnit.HOURS)
            .build()
        WorkManager.getInstance(context.applicationContext)
            .enqueueUniquePeriodicWork(UNIQUE_NAME, ExistingPeriodicWorkPolicy.KEEP, request)
    }

    fun cancel(context: Context) {
        WorkManager.getInstance(context.applicationContext).cancelUniqueWork(UNIQUE_NAME)
    }

    /** Remembers the app language so background check-ins use the same one. */
    fun saveLanguage(context: Context, language: AppLanguage) {
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit().putString(KEY_LANG, language.name).apply()
    }

    fun language(context: Context): AppLanguage {
        val name = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .getString(KEY_LANG, null)
        return AppLanguage.values().firstOrNull { it.name == name } ?: AppLanguage.ARABIC
    }

    /** No spoken check-ins at night (22:00 - 08:00). */
    fun isQuietHour(): Boolean {
        val hour = Calendar.getInstance().get(Calendar.HOUR_OF_DAY)
        return hour >= 22 || hour < 8
    }
}

/** Shows a notification and says a short friendly sentence (TTS) every few hours. */
class ProactiveWorker(context: Context, params: WorkerParameters) : Worker(context, params) {

    override fun doWork(): Result {
        val ctx = applicationContext
        if (ProactiveScheduler.isQuietHour()) return Result.success()

        val lang = ProactiveScheduler.language(ctx)
        val text = ProactiveMessages.checkIn(lang)

        NotificationHelper.postProactive(ctx, text)
        try {
            SpeakingService.start(ctx, text, alarm = false)
        } catch (e: Exception) {
            // Background workers can't always start a foreground service: speak from the worker itself.
            speakDirectly(text, lang)
        }
        return Result.success()
    }

    /** Blocking one-shot TTS (the worker thread is a background thread, so waiting is fine). */
    private fun speakDirectly(text: String, lang: AppLanguage) {
        val latch = CountDownLatch(1)
        var engine: TextToSpeech? = null
        engine = TextToSpeech(applicationContext) { status ->
            val tts = engine
            if (status == TextToSpeech.SUCCESS && tts != null) {
                tts.setLanguage(lang.locale)
                tts.setOnUtteranceProgressListener(object : UtteranceProgressListener() {
                    override fun onStart(utteranceId: String?) = Unit
                    override fun onDone(utteranceId: String?) = latch.countDown()

                    @Deprecated("Deprecated in Java")
                    override fun onError(utteranceId: String?) = latch.countDown()
                })
                if (tts.speak(text, TextToSpeech.QUEUE_FLUSH, null, "va-worker") != TextToSpeech.SUCCESS) {
                    latch.countDown()
                }
            } else {
                latch.countDown()
            }
        }
        try {
            latch.await(30, TimeUnit.SECONDS)
        } catch (e: InterruptedException) {
            Thread.currentThread().interrupt()
        } finally {
            engine?.stop()
            engine?.shutdown()
        }
    }
}
''')


# Security monitor: foreground service that watches the clipboard for suspicious links / scam phrases
write_file("app/src/main/java/com/example/voiceassistant/service/SecurityMonitorService.kt", r'''package com.example.voiceassistant.service

import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.ClipboardManager
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import androidx.core.content.ContextCompat
import com.example.voiceassistant.MainActivity
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Foreground service that listens for clipboard changes and speaks a warning (through
 * [SpeakingService]) when the copied text contains a link or a typical scam phrase.
 */
class SecurityMonitorService : Service() {

    companion object {
        private const val CHANNEL_SECURITY = "va_security"
        private const val FOREGROUND_ID = 7002
        private const val WARNING_COOLDOWN_MS = 5_000L

        private val suspiciousWords = listOf("حسابك محظور", "تحديث بياناتك", "فيروس", "اختراق")

        private val _running = MutableStateFlow(false)

        /** True while the service is alive (the UI switch follows this). */
        val running: StateFlow<Boolean> = _running.asStateFlow()

        /** @throws IllegalStateException on Android 12+ when the system forbids starting it right now. */
        fun start(context: Context) {
            ContextCompat.startForegroundService(
                context,
                Intent(context, SecurityMonitorService::class.java)
            )
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, SecurityMonitorService::class.java))
        }
    }

    private var clipboard: ClipboardManager? = null
    private var lastWarnedText: String? = null
    private var lastWarnedAt = 0L

    private val clipListener = ClipboardManager.OnPrimaryClipChangedListener { checkClipboard() }

    override fun onCreate() {
        super.onCreate()
        createChannel()
        clipboard = getSystemService(ClipboardManager::class.java)
        clipboard?.addPrimaryClipChangedListener(clipListener)
        _running.value = true
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Must be called within a few seconds of startForegroundService().
        try {
            val type = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                ServiceInfo.FOREGROUND_SERVICE_TYPE_DATA_SYNC
            } else {
                0
            }
            ServiceCompat.startForeground(this, FOREGROUND_ID, buildNotification(), type)
        } catch (e: Exception) {
            stopSelf()
            return START_NOT_STICKY
        }
        return START_STICKY
    }

    /** Android 15 limits dataSync foreground services in time: stop cleanly when the system asks. */
    override fun onTimeout(startId: Int, fgsType: Int) {
        stopSelf()
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        clipboard?.removePrimaryClipChangedListener(clipListener)
        clipboard = null
        _running.value = false
        super.onDestroy()
    }

    private fun checkClipboard() {
        val text = try {
            clipboard?.primaryClip
                ?.takeIf { it.itemCount > 0 }
                ?.getItemAt(0)
                ?.coerceToText(this)
                ?.toString()
        } catch (e: Exception) {
            null
        }
        if (text.isNullOrBlank() || !isSuspicious(text)) return

        // Some devices report one copy twice: warn only once.
        val now = System.currentTimeMillis()
        if (text == lastWarnedText && now - lastWarnedAt < WARNING_COOLDOWN_MS) return
        lastWarnedText = text
        lastWarnedAt = now

        val warning = ProactiveScheduler.language(this).tr(
            "تحذير أمني: تم اكتشاف نص أو رابط مشبوه في الحافظة",
            "Security warning: a suspicious text or link was found on the clipboard"
        )
        try {
            SpeakingService.start(applicationContext, warning, alarm = true)
        } catch (e: Exception) {
            // The system refused to start the speaking service right now: nothing else we can do.
        }
    }

    private fun isSuspicious(text: String): Boolean =
        text.contains("http", ignoreCase = true) || suspiciousWords.any { text.contains(it) }

    private fun createChannel() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val nm = getSystemService(NotificationManager::class.java) ?: return
        val channel = NotificationChannel(
            CHANNEL_SECURITY,
            "الحماية / Security",
            NotificationManager.IMPORTANCE_LOW
        ).apply {
            description = "إشعار دائم أثناء مراقبة الحافظة / Shown while the clipboard is monitored"
            setShowBadge(false)
        }
        nm.createNotificationChannel(channel)
    }

    private fun buildNotification(): android.app.Notification {
        val lang = ProactiveScheduler.language(this)
        val openApp = PendingIntent.getActivity(
            this,
            9002,
            Intent(this, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP
            },
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        return NotificationCompat.Builder(this, CHANNEL_SECURITY)
            .setSmallIcon(android.R.drawable.ic_lock_idle_lock)
            .setContentTitle(lang.tr("الحماية نشطة", "Protection is active"))
            .setContentText(
                lang.tr(
                    "مراقبة الحافظة بحثاً عن الروابط والنصوص المشبوهة",
                    "Watching the clipboard for suspicious links and texts"
                )
            )
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setContentIntent(openApp)
            .build()
    }
}
''')

# Wake word: foreground service that keeps a SpeechRecognizer running and opens the app on the wake phrase
write_file("app/src/main/java/com/example/voiceassistant/service/WakeWordService.kt", r'''package com.example.voiceassistant.service

import android.Manifest
import android.app.Activity
import android.app.Application
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.os.Build
import android.os.Bundle
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import androidx.core.content.ContextCompat
import com.example.voiceassistant.MainActivity
import com.example.voiceassistant.speech.OfflineSpeech
import java.util.Locale
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/**
 * Foreground service (microphone) that listens continuously with the built-in [SpeechRecognizer].
 * When it hears a wake phrase it opens [MainActivity] with [MainActivity.EXTRA_AUTO_LISTEN] and
 * posts a notification. While the app itself is on screen the service pauses, because the app
 * uses the microphone.
 */
class WakeWordService : Service() {

    companion object {
        private const val PREFS_NAME = "wake_word"
        private const val KEY_ENABLED = "enabled"
        private const val CHANNEL_ACTIVE = "va_wakeword"
        private const val CHANNEL_ALERT = "va_wakeword_alert"
        private const val FOREGROUND_ID = 7010
        private const val ALERT_ID = 7011
        private const val RESTART_DELAY_MS = 150L
        private const val BUSY_DELAY_MS = 1000L
        private const val RESUME_AFTER_WAKE_MS = 6000L

        /** Phrases that wake the assistant (compared after [normalize]). */
        val WAKE_PHRASES = listOf("يا مساعد", "هيا مساعد", "hey assistant", "zevorix", "hey zevorix", "يا زيفوريكس")

        private val _enabled = MutableStateFlow(false)

        /** The user's switch (persisted in SharedPreferences). */
        val enabled: StateFlow<Boolean> = _enabled.asStateFlow()

        private val _running = MutableStateFlow(false)

        /** True while the service is alive. */
        val running: StateFlow<Boolean> = _running.asStateFlow()

        @Volatile
        private var visibleActivities = 0

        @Volatile
        private var instance: WakeWordService? = null

        private fun prefs(context: Context) =
            context.applicationContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

        /** Reads the saved switch state into [enabled]. */
        fun loadState(context: Context) {
            _enabled.value = prefs(context).getBoolean(KEY_ENABLED, false)
        }

        fun setEnabled(context: Context, value: Boolean) {
            prefs(context).edit().putBoolean(KEY_ENABLED, value).apply()
            _enabled.value = value
        }

        fun hasMicPermission(context: Context): Boolean =
            ContextCompat.checkSelfPermission(context, Manifest.permission.RECORD_AUDIO) ==
                PackageManager.PERMISSION_GRANTED

        /** @throws IllegalStateException on Android 12+ when the system forbids starting it right now. */
        fun start(context: Context) {
            ContextCompat.startForegroundService(
                context,
                Intent(context, WakeWordService::class.java)
            )
        }

        fun stop(context: Context) {
            context.stopService(Intent(context, WakeWordService::class.java))
        }

        /** Starts the service when the switch is on, the permission is granted and it isn't running yet. */
        fun startIfEnabled(context: Context): Boolean {
            if (!_enabled.value || _running.value || !hasMicPermission(context)) return false
            return try {
                start(context)
                true
            } catch (e: Exception) {
                false
            }
        }

        /** Counts visible activities so the service can release the microphone while the app is open. */
        fun trackForeground(app: Application) {
            app.registerActivityLifecycleCallbacks(object : Application.ActivityLifecycleCallbacks {
                override fun onActivityStarted(activity: Activity) {
                    visibleActivities++
                    instance?.onVisibilityChanged()
                }

                override fun onActivityStopped(activity: Activity) {
                    visibleActivities = maxOf(0, visibleActivities - 1)
                    instance?.onVisibilityChanged()
                }

                override fun onActivityCreated(activity: Activity, savedInstanceState: Bundle?) {}
                override fun onActivityResumed(activity: Activity) {}
                override fun onActivityPaused(activity: Activity) {}
                override fun onActivitySaveInstanceState(activity: Activity, outState: Bundle) {}
                override fun onActivityDestroyed(activity: Activity) {}
            })
        }

        /** Lower-case, no diacritics, unified Arabic letter forms, single spaces. */
        fun normalize(text: String): String {
            val sb = StringBuilder(text.length)
            for (ch in text.lowercase(Locale.ROOT)) {
                when {
                    ch in '\u064B'..'\u065F' || ch == '\u0640' -> Unit
                    ch == 'أ' || ch == 'إ' || ch == 'آ' -> sb.append('ا')
                    ch == 'ى' -> sb.append('ي')
                    ch == 'ة' -> sb.append('ه')
                    else -> sb.append(ch)
                }
            }
            return sb.toString().replace(Regex("\\s+"), " ").trim()
        }

        fun containsWakeWord(text: String): Boolean {
            val normalized = normalize(text)
            return WAKE_PHRASES.any { normalized.contains(normalize(it)) }
        }
    }

    private val handler = Handler(Looper.getMainLooper())
    private var recognizer: SpeechRecognizer? = null
    private var paused = false
    private var destroyed = false
    private var useArabic = true

    // After a network error the service listens with on-device recognition for a minute, then tries online again.
    private var offlineUntil = 0L

    private val restartRunnable = Runnable { startListening() }

    private val listener = object : RecognitionListener {
        override fun onReadyForSpeech(params: Bundle?) {}
        override fun onBeginningOfSpeech() {}
        override fun onRmsChanged(rmsdB: Float) {}
        override fun onBufferReceived(buffer: ByteArray?) {}
        override fun onEndOfSpeech() {}
        override fun onEvent(eventType: Int, params: Bundle?) {}

        override fun onPartialResults(partialResults: Bundle?) {
            checkForWakeWord(partialResults)
        }

        override fun onResults(results: Bundle?) {
            if (!checkForWakeWord(results)) scheduleRestart(RESTART_DELAY_MS)
        }

        override fun onError(error: Int) {
            when (error) {
                SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> {
                    setEnabled(applicationContext, false)
                    stopSelf()
                }
                SpeechRecognizer.ERROR_NO_MATCH,
                SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> scheduleRestart(RESTART_DELAY_MS)
                else -> {
                    // No internet / server problem: keep listening, now preferring on-device recognition.
                    if (OfflineSpeech.isNetworkError(error)) {
                        offlineUntil = System.currentTimeMillis() + 60_000L
                        scheduleRestart(RESTART_DELAY_MS)
                    } else {
                        scheduleRestart(BUSY_DELAY_MS)
                    }
                }
            }
        }
    }

    override fun onCreate() {
        super.onCreate()
        createChannels()
        instance = this
        _running.value = true
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        if (!hasMicPermission(this)) {
            setEnabled(applicationContext, false)
            stopSelf()
            return START_NOT_STICKY
        }
        // Must be called within a few seconds of startForegroundService().
        try {
            val type = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.R) {
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE
            } else {
                0
            }
            ServiceCompat.startForeground(this, FOREGROUND_ID, buildActiveNotification(), type)
        } catch (e: Exception) {
            stopSelf()
            return START_NOT_STICKY
        }
        if (!OfflineSpeech.isAvailable(this)) {
            stopSelf()
            return START_NOT_STICKY
        }
        if (visibleActivities == 0) resumeListening() else pauseListening()
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        destroyed = true
        instance = null
        handler.removeCallbacksAndMessages(null)
        destroyRecognizer()
        _running.value = false
        super.onDestroy()
    }

    /** Called when the app comes to / leaves the screen: release the microphone while it's visible. */
    private fun onVisibilityChanged() {
        if (visibleActivities > 0) pauseListening() else resumeListening()
    }

    private fun pauseListening() {
        paused = true
        handler.removeCallbacks(restartRunnable)
        destroyRecognizer()
    }

    private fun resumeListening() {
        if (destroyed || visibleActivities > 0) return
        paused = false
        handler.removeCallbacks(restartRunnable)
        handler.post(restartRunnable)
    }

    private fun scheduleRestart(delayMs: Long) {
        if (destroyed || paused) return
        // Alternate Arabic / English so both wake phrases can be recognised.
        useArabic = !useArabic
        handler.removeCallbacks(restartRunnable)
        handler.postDelayed(restartRunnable, delayMs)
    }

    private fun startListening() {
        if (destroyed || paused) return
        destroyRecognizer()
        try {
            val offline = System.currentTimeMillis() < offlineUntil || !OfflineSpeech.isOnline(this)
            val r = OfflineSpeech.createRecognizer(this, offline)
            r.setRecognitionListener(listener)
            recognizer = r
            val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
                putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
                putExtra(RecognizerIntent.EXTRA_LANGUAGE, if (useArabic) "ar-SA" else "en-US")
                putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
                putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3)
                putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, packageName)
                putExtra(RecognizerIntent.EXTRA_PREFER_OFFLINE, offline)
            }
            r.startListening(intent)
        } catch (e: Exception) {
            scheduleRestart(BUSY_DELAY_MS)
        }
    }

    private fun destroyRecognizer() {
        recognizer?.let {
            try {
                it.cancel()
                it.destroy()
            } catch (e: Exception) {
                // Already released.
            }
        }
        recognizer = null
    }

    /** @return true when a wake phrase was found (the service is then paused). */
    private fun checkForWakeWord(bundle: Bundle?): Boolean {
        if (paused || visibleActivities > 0) return false
        val texts = bundle?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION) ?: return false
        if (texts.none { containsWakeWord(it) }) return false
        onWakeWord()
        return true
    }

    private fun onWakeWord() {
        pauseListening()
        val launch = Intent(this, MainActivity::class.java)
            .putExtra(MainActivity.EXTRA_AUTO_LISTEN, true)
            .addFlags(
                Intent.FLAG_ACTIVITY_NEW_TASK or
                    Intent.FLAG_ACTIVITY_CLEAR_TOP or
                    Intent.FLAG_ACTIVITY_SINGLE_TOP
            )
        try {
            startActivity(launch)
        } catch (e: Exception) {
            // Android may block starting an activity from the background: the notification below opens it.
        }
        postWakeNotification(launch)
        // If the app didn't come to the screen, start listening for the wake word again.
        handler.postDelayed({ resumeListening() }, RESUME_AFTER_WAKE_MS)
    }

    private fun postWakeNotification(launch: Intent) {
        val lang = ProactiveScheduler.language(this)
        val openApp = PendingIntent.getActivity(
            this,
            9010,
            launch,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        val notification = NotificationCompat.Builder(this, CHANNEL_ALERT)
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentTitle(lang.tr("تم استدعاء المساعد", "Assistant called"))
            .setContentText(lang.tr("اضغط لفتح المساعد", "Tap to open the assistant"))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_CALL)
            .setAutoCancel(true)
            .setContentIntent(openApp)
            .build()
        try {
            getSystemService(NotificationManager::class.java)?.notify(ALERT_ID, notification)
        } catch (e: Exception) {
            // Notification permission denied: nothing else to do.
        }
    }

    private fun createChannels() {
        if (Build.VERSION.SDK_INT < Build.VERSION_CODES.O) return
        val nm = getSystemService(NotificationManager::class.java) ?: return
        nm.createNotificationChannel(
            NotificationChannel(
                CHANNEL_ACTIVE,
                "الاستدعاء الصوتي / Wake word",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "إشعار دائم أثناء الاستماع لكلمة الاستدعاء / Shown while listening for the wake word"
                setShowBadge(false)
            }
        )
        nm.createNotificationChannel(
            NotificationChannel(
                CHANNEL_ALERT,
                "نداء المساعد / Assistant call",
                NotificationManager.IMPORTANCE_HIGH
            )
        )
    }

    private fun buildActiveNotification(): Notification {
        val lang = ProactiveScheduler.language(this)
        val openApp = PendingIntent.getActivity(
            this,
            9011,
            Intent(this, MainActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP
            },
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )
        return NotificationCompat.Builder(this, CHANNEL_ACTIVE)
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentTitle(lang.tr("الاستدعاء الصوتي نشط", "Wake word is active"))
            .setContentText(
                lang.tr(
                    "قل «يا مساعد» أو «hey assistant» أو «Zevorix» لفتح المساعد",
                    "Say \"hey assistant\", \"Zevorix\" or «يا مساعد» to open the assistant"
                )
            )
            .setOngoing(true)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setContentIntent(openApp)
            .build()
    }
}
''')


# User profile: remembers the user's name between launches
write_file("app/src/main/java/com/example/voiceassistant/data/UserProfileManager.kt", r'''package com.example.voiceassistant.data

import android.content.Context

/** Stores the user's name in SharedPreferences so it survives closing the app. */
class UserProfileManager(context: Context) {

    private val prefs = context.applicationContext
        .getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    var userName: String?
        get() = prefs.getString(KEY_NAME, null)?.takeIf { it.isNotBlank() }
        set(value) {
            val editor = prefs.edit()
            if (value.isNullOrBlank()) editor.remove(KEY_NAME) else editor.putString(KEY_NAME, value.trim())
            // commit() = written to disk immediately, so the name survives even if the app is killed right after.
            editor.commit()
        }

    private companion object {
        const val PREFS_NAME = "user_profile"
        const val KEY_NAME = "user_name"
    }
}
''')


# ------------------------------------------------------------------------------
# ميزات الحماية من السرقة (Anti-Theft)
# ------------------------------------------------------------------------------
# 1. الإعدادات المشتركة (SharedPreferences)
write_file("app/src/main/java/com/example/voiceassistant/antitheft/AntiTheftSettings.kt", r'''package com.example.voiceassistant.antitheft

import android.content.Context

/**
 * Anti-theft settings stored in SharedPreferences: the trusted phone number, the security PIN
 * and the last known SIM operator (used to detect a SIM change after a reboot).
 */
object AntiTheftSettings {

    private const val PREFS_NAME = "anti_theft"
    private const val KEY_PHONE = "trusted_phone"
    private const val KEY_PIN = "security_pin"
    private const val KEY_OPERATOR = "last_operator"

    private fun prefs(context: Context) =
        context.applicationContext.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun trustedPhone(context: Context): String? =
        prefs(context).getString(KEY_PHONE, null)?.takeIf { it.isNotBlank() }

    fun pin(context: Context): String? =
        prefs(context).getString(KEY_PIN, null)?.takeIf { it.isNotBlank() }

    fun isConfigured(context: Context): Boolean =
        trustedPhone(context) != null && pin(context) != null

    fun save(context: Context, phone: String, securityPin: String) {
        prefs(context).edit()
            .putString(KEY_PHONE, phone.trim())
            .putString(KEY_PIN, securityPin.trim())
            .apply()
    }

    fun lastOperator(context: Context): String? =
        prefs(context).getString(KEY_OPERATOR, null)

    fun setLastOperator(context: Context, operator: String) {
        prefs(context).edit().putString(KEY_OPERATOR, operator).apply()
    }

    /** Compares two numbers by their last 9 digits, so "+966 5x..." and "05x..." match. */
    fun sameNumber(a: String, b: String): Boolean {
        val digitsA = a.filter { it.isDigit() }
        val digitsB = b.filter { it.isDigit() }
        if (digitsA.isEmpty() || digitsB.isEmpty()) return false
        return digitsA.takeLast(9) == digitsB.takeLast(9)
    }

    fun isValidPhone(phone: String): Boolean = phone.count { it.isDigit() } >= 7

    fun isValidPin(securityPin: String): Boolean =
        securityPin.length in 4..8 && securityPin.all { it.isDigit() }
}
''')

# 2. آخر موقع معروف
write_file("app/src/main/java/com/example/voiceassistant/antitheft/LocationHelper.kt", r'''package com.example.voiceassistant.antitheft

import android.annotation.SuppressLint
import android.content.Context
import android.location.Location
import android.location.LocationManager

object LocationHelper {

    /** Newest last-known fix from GPS, network or passive providers (null when none exists). */
    @SuppressLint("MissingPermission")
    fun lastKnownLocation(context: Context): Location? {
        val lm = context.getSystemService(Context.LOCATION_SERVICE) as? LocationManager ?: return null
        val providers = listOf(
            LocationManager.GPS_PROVIDER,
            LocationManager.NETWORK_PROVIDER,
            LocationManager.PASSIVE_PROVIDER
        )
        return providers
            .mapNotNull { provider ->
                try {
                    lm.getLastKnownLocation(provider)
                } catch (e: SecurityException) {
                    null
                }
            }
            .maxByOrNull { it.time }
    }

    fun mapsLink(location: Location): String =
        "https://maps.google.com/?q=${location.latitude},${location.longitude}"

    /** Message body: a header line followed by the last known position (or a note if none). */
    fun describe(context: Context, header: String): String {
        val location = lastKnownLocation(context)
        return if (location != null) {
            "$header\nآخر موقع معروف: ${mapsLink(location)}"
        } else {
            "$header\nتعذّر تحديد الموقع حالياً."
        }
    }
}
''')

# 3. إرسال الرسائل عبر SmsManager
write_file("app/src/main/java/com/example/voiceassistant/antitheft/SmsSender.kt", r'''package com.example.voiceassistant.antitheft

import android.content.Context
import android.os.Build
import android.telephony.SmsManager
import android.util.Log

object SmsSender {

    private const val TAG = "SmsSender"

    /** Sends [text] as SMS (split automatically when long). @return true when handed to the system. */
    fun send(context: Context, number: String, text: String): Boolean {
        return try {
            val manager = smsManager(context)
            val parts = manager.divideMessage(text)
            manager.sendMultipartTextMessage(number, null, parts, null, null)
            true
        } catch (e: Exception) {
            Log.w(TAG, "SMS to trusted number failed", e)
            false
        }
    }

    @Suppress("DEPRECATION")
    private fun smsManager(context: Context): SmsManager =
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
            context.getSystemService(SmsManager::class.java)
        } else {
            SmsManager.getDefault()
        }
}
''')

# 4. استقبال طلب الموقع عبر SMS
write_file("app/src/main/java/com/example/voiceassistant/antitheft/LocationSmsReceiver.kt", r'''package com.example.voiceassistant.antitheft

import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.provider.Telephony

/**
 * Replies with the device location when the trusted number sends a message that contains
 * the security PIN as a word, e.g. "1234" or "where 1234".
 */
class LocationSmsReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Telephony.Sms.Intents.SMS_RECEIVED_ACTION) return

        val messages = Telephony.Sms.Intents.getMessagesFromIntent(intent) ?: return
        if (messages.isEmpty()) return
        val sender = messages[0].originatingAddress ?: return
        val body = messages.joinToString(separator = "") { it.messageBody.orEmpty() }

        val trusted = AntiTheftSettings.trustedPhone(context) ?: return
        val pin = AntiTheftSettings.pin(context) ?: return

        // The PIN alone is not enough: the message must come from the trusted number.
        if (!AntiTheftSettings.sameNumber(sender, trusted)) return
        val containsPin = body.split(Regex("\\s+")).any { it == pin }
        if (!containsPin) return

        SmsSender.send(
            context,
            trusted,
            LocationHelper.describe(context, "موقع الجهاز بناءً على طلبك:")
        )
    }
}
''')

# 5. كشف تغيير الشريحة بعد الإقلاع
write_file("app/src/main/java/com/example/voiceassistant/antitheft/SimChangeReceiver.kt", r'''package com.example.voiceassistant.antitheft

import android.Manifest
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.telephony.TelephonyManager
import androidx.core.content.ContextCompat

/**
 * Runs after every boot: compares the SIM operator with the one saved last time and,
 * if it changed, tells the trusted number by SMS.
 */
class SimChangeReceiver : BroadcastReceiver() {

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action != Intent.ACTION_BOOT_COMPLETED) return

        val current = currentOperator(context)
        if (current.isNullOrBlank()) return // No readable SIM yet: nothing to compare.

        val previous = AntiTheftSettings.lastOperator(context)
        if (previous == null) {
            AntiTheftSettings.setLastOperator(context, current) // First run: just remember it.
            return
        }
        if (previous == current) return

        AntiTheftSettings.trustedPhone(context)?.let { trusted ->
            SmsSender.send(
                context,
                trusted,
                "تنبيه: تم تغيير الشريحة في الجهاز.\nمشغل الشبكة الجديد: $current\nالمشغل السابق: $previous"
            )
        }
        // Store the new operator so the same change is not reported on every boot.
        AntiTheftSettings.setLastOperator(context, current)
    }

    /** Operator name of the inserted SIM (available right after boot), falling back to the network's. */
    private fun currentOperator(context: Context): String? {
        val granted = ContextCompat.checkSelfPermission(
            context,
            Manifest.permission.READ_PHONE_STATE
        ) == PackageManager.PERMISSION_GRANTED
        if (!granted) return null
        val tm = context.getSystemService(Context.TELEPHONY_SERVICE) as? TelephonyManager ?: return null
        return try {
            tm.simOperatorName.takeIf { it.isNotBlank() } ?: tm.networkOperatorName
        } catch (e: SecurityException) {
            null
        }
    }
}
''')

# 6. مدير الجهاز (Device Admin)
write_file("app/src/main/java/com/example/voiceassistant/antitheft/AntiTheftDeviceAdminReceiver.kt", r'''package com.example.voiceassistant.antitheft

import android.app.admin.DeviceAdminReceiver
import android.content.Context
import android.content.Intent

/**
 * Device Admin receiver.
 * - [onDisableRequested] runs when someone starts turning the admin off (a step that wipe
 *   attempts usually need). The trusted number gets a warning with the last location.
 * - [onDisabled] runs once the admin is off, and sends a confirmation.
 *
 * Limitation: a factory reset from recovery mode does not go through this receiver.
 */
class AntiTheftDeviceAdminReceiver : DeviceAdminReceiver() {

    override fun onDisableRequested(context: Context, intent: Intent): CharSequence {
        sendTrustedAlert(context, "تحذير: يتم محاولة فرمطة الجهاز!")
        return "سيتم إرسال تنبيه إلى الرقم الموثوق عند إلغاء مدير الجهاز. / The trusted number will be alerted."
    }

    override fun onDisabled(context: Context, intent: Intent) {
        sendTrustedAlert(context, "تنبيه: تم إلغاء تفعيل مدير الجهاز على الجهاز.")
    }

    private fun sendTrustedAlert(context: Context, header: String) {
        val trusted = AntiTheftSettings.trustedPhone(context) ?: return
        SmsSender.send(context, trusted, LocationHelper.describe(context, header))
    }
}
''')

# 7. ملف سياسات مدير الجهاز
write_file("app/src/main/res/xml/device_admin.xml", r'''<?xml version="1.0" encoding="utf-8"?>
<!-- Device Admin policies. None are requested: the admin is used only to be notified
     when someone tries to disable it. -->
<device-admin xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-policies />
</device-admin>
''')

# 8. شاشة إعدادات الحماية من السرقة
write_file("app/src/main/java/com/example/voiceassistant/antitheft/SecuritySettingsActivity.kt", r'''package com.example.voiceassistant.antitheft

import android.Manifest
import android.app.admin.DevicePolicyManager
import android.content.ComponentName
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.compose.setContent
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.compose.LifecycleEventEffect
import com.example.voiceassistant.R
import com.example.voiceassistant.ui.theme.VoiceAssistantTheme

/** Permissions requested in one dialog. Background location is asked for separately. */
private val REQUIRED_PERMISSIONS = arrayOf(
    Manifest.permission.RECEIVE_SMS,
    Manifest.permission.SEND_SMS,
    Manifest.permission.READ_PHONE_STATE,
    Manifest.permission.ACCESS_FINE_LOCATION,
    Manifest.permission.ACCESS_COARSE_LOCATION
)

class SecuritySettingsActivity : ComponentActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            VoiceAssistantTheme {
                SecuritySettingsScreen()
            }
        }
    }
}

@Composable
private fun SecuritySettingsScreen() {
    val context = LocalContext.current

    var trustedPhone by remember { mutableStateOf(AntiTheftSettings.trustedPhone(context).orEmpty()) }
    var securityPin by remember { mutableStateOf(AntiTheftSettings.pin(context).orEmpty()) }
    var message by remember { mutableStateOf<String?>(null) }

    var permissionsOk by remember { mutableStateOf(false) }
    var backgroundOk by remember { mutableStateOf(false) }
    var adminOk by remember { mutableStateOf(false) }

    fun refreshStatus() {
        permissionsOk = REQUIRED_PERMISSIONS.all {
            ContextCompat.checkSelfPermission(context, it) == PackageManager.PERMISSION_GRANTED
        }
        backgroundOk = Build.VERSION.SDK_INT < Build.VERSION_CODES.Q ||
            ContextCompat.checkSelfPermission(context, Manifest.permission.ACCESS_BACKGROUND_LOCATION) ==
            PackageManager.PERMISSION_GRANTED
        adminOk = context.getSystemService(DevicePolicyManager::class.java)
            ?.isAdminActive(adminComponent(context)) == true
    }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { refreshStatus() }

    val backgroundLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { refreshStatus() }

    val adminLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { refreshStatus() }

    LaunchedEffect(Unit) { refreshStatus() }
    LifecycleEventEffect(Lifecycle.Event.ON_RESUME) { refreshStatus() }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .verticalScroll(rememberScrollState())
            .padding(20.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        Text(
            text = "الحماية من السرقة / Anti-theft",
            style = MaterialTheme.typography.headlineSmall
        )
        Text(
            text = "أرسل كلمة السر من الرقم الموثوق لاستلام موقع الجهاز. / " +
                "Send the PIN from the trusted number to receive the device location.",
            style = MaterialTheme.typography.bodyMedium
        )

        OutlinedTextField(
            value = trustedPhone,
            onValueChange = { trustedPhone = it },
            label = { Text("رقم الهاتف الموثوق / Trusted phone number") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Phone),
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )

        OutlinedTextField(
            value = securityPin,
            onValueChange = { securityPin = it.filter { c -> c.isDigit() }.take(8) },
            label = { Text("كلمة السر (4 إلى 8 أرقام) / Security PIN") },
            keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.NumberPassword),
            visualTransformation = PasswordVisualTransformation(),
            singleLine = true,
            modifier = Modifier.fillMaxWidth()
        )

        Button(
            onClick = {
                message = when {
                    !AntiTheftSettings.isValidPhone(trustedPhone) ->
                        "أدخل رقم هاتف صحيحاً. / Enter a valid phone number."
                    !AntiTheftSettings.isValidPin(securityPin) ->
                        "كلمة السر من 4 إلى 8 أرقام. / The PIN must be 4 to 8 digits."
                    else -> {
                        AntiTheftSettings.save(context, trustedPhone, securityPin)
                        "تم حفظ الإعدادات. / Settings saved."
                    }
                }
            },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("حفظ / Save")
        }

        message?.let { Text(text = it, style = MaterialTheme.typography.bodyMedium) }

        Text(
            text = "الحالة / Status",
            style = MaterialTheme.typography.titleMedium
        )
        StatusRow("الأذونات / Permissions", permissionsOk)
        StatusRow("الموقع في الخلفية / Background location", backgroundOk)
        StatusRow("مدير الجهاز / Device Admin", adminOk)

        OutlinedButton(
            onClick = { permissionLauncher.launch(REQUIRED_PERMISSIONS) },
            modifier = Modifier.fillMaxWidth()
        ) {
            Text("منح أذونات الرسائل والموقع / Grant SMS & location permissions")
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            OutlinedButton(
                onClick = { backgroundLauncher.launch(Manifest.permission.ACCESS_BACKGROUND_LOCATION) },
                enabled = permissionsOk && !backgroundOk,
                modifier = Modifier.fillMaxWidth()
            ) {
                Text("السماح بالموقع في الخلفية / Allow background location")
            }
        }

        OutlinedButton(
            onClick = { adminLauncher.launch(adminIntent(context)) },
            enabled = !adminOk,
            modifier = Modifier.fillMaxWidth()
        ) {
            Text(
                if (adminOk) {
                    "مدير الجهاز مفعّل / Device Admin is active"
                } else {
                    "تفعيل مدير الجهاز / Activate Device Admin"
                }
            )
        }
    }
}

@Composable
private fun StatusRow(label: String, ok: Boolean) {
    Text(
        text = "$label: " + (if (ok) "ممنوح / OK" else "غير ممنوح / Missing"),
        style = MaterialTheme.typography.bodyMedium
    )
}

private fun adminComponent(context: Context): ComponentName =
    ComponentName(context, AntiTheftDeviceAdminReceiver::class.java)

private fun adminIntent(context: Context): Intent =
    Intent(DevicePolicyManager.ACTION_ADD_DEVICE_ADMIN)
        .putExtra(DevicePolicyManager.EXTRA_DEVICE_ADMIN, adminComponent(context))
        .putExtra(
            DevicePolicyManager.EXTRA_ADD_EXPLANATION,
            context.getString(R.string.device_admin_explanation)
        )
''')


# ------------------------------------------------------------------------------
# الإضافة: إعدادات نماذج الذكاء الاصطناعي (Gemini / ChatGPT / Claude) ومفاتيح API
# ------------------------------------------------------------------------------
write_file("app/src/main/java/com/example/voiceassistant/data/AiSettings.kt", r'''package com.example.voiceassistant.data

import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import com.example.voiceassistant.BuildConfig
import java.util.concurrent.ConcurrentHashMap
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/** The AI models the user can switch between. [defaultModel] is used until the user types another name. */
enum class AiProvider(val title: String, val defaultModel: String) {
    GEMINI("Gemini", "auto"),
    OPENAI("ChatGPT", "gpt-4o-mini"),
    CLAUDE("Claude", "claude-3-haiku-20240307")
}

/** What the settings screen shows. Never contains a key itself. */
data class AiSettingsState(
    val selected: AiProvider = AiProvider.GEMINI,
    val fallback: Boolean = true,
    /** Gemini answers with live Google Search results (Grounding). */
    val webSearch: Boolean = true,
    /** The user typed a key in the app for this provider. */
    val hasUserKey: Map<AiProvider, Boolean> = emptyMap(),
    /** A key was built into the app (GitHub Secrets / BuildConfig) for this provider. */
    val hasBuildKey: Map<AiProvider, Boolean> = emptyMap(),
    val models: Map<AiProvider, String> = emptyMap()
)

/**
 * Selected model + API keys.
 * - Keys typed in the app are stored encrypted (EncryptedSharedPreferences, AES-256).
 * - Keys built into the APK come from BuildConfig, which app/build.gradle.kts fills from GitHub Secrets
 *   (environment variables) or from the git-ignored keys.properties. They are never written in the source code.
 * - A key typed in the app always wins over the built-in one.
 */
object AiSettings {
    private const val TAG = "AiSettings"
    private const val FILE = "ai_settings_secure"
    private const val KEY_SELECTED = "selected_provider"
    private const val KEY_FALLBACK = "fallback_enabled"
    private const val KEY_SEARCH = "web_search_enabled"

    @Volatile
    private var prefs: SharedPreferences? = null

    // Only used if the encrypted store can't be opened on this device (values then live until the app is closed).
    private val memoryOnly = ConcurrentHashMap<String, String>()

    private val _state = MutableStateFlow(AiSettingsState())
    val state: StateFlow<AiSettingsState> = _state.asStateFlow()

    fun init(context: Context) {
        if (prefs != null) return
        synchronized(this) {
            if (prefs != null) return
            prefs = openSecure(context.applicationContext)
            publish()
        }
    }

    private fun openSecure(app: Context): SharedPreferences? {
        repeat(2) { attempt ->
            try {
                val masterKey = MasterKey.Builder(app)
                    .setKeyScheme(MasterKey.KeyScheme.AES256_GCM)
                    .build()
                return EncryptedSharedPreferences.create(
                    app,
                    FILE,
                    masterKey,
                    EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
                    EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM
                )
            } catch (e: Exception) {
                Log.w(TAG, "Encrypted settings unavailable (attempt ${attempt + 1}): $e")
                // A corrupted keystore entry makes the old file unreadable: start the file again once.
                if (attempt == 0) app.deleteSharedPreferences(FILE)
            }
        }
        return null
    }

    private fun read(key: String): String = prefs?.getString(key, null) ?: memoryOnly[key].orEmpty()

    private fun write(key: String, value: String) {
        val p = prefs
        if (p != null) {
            if (value.isEmpty()) p.edit().remove(key).apply() else p.edit().putString(key, value).apply()
        } else if (value.isEmpty()) {
            memoryOnly.remove(key)
        } else {
            memoryOnly[key] = value
        }
    }

    fun selectedProvider(): AiProvider =
        runCatching { AiProvider.valueOf(read(KEY_SELECTED)) }.getOrDefault(AiProvider.GEMINI)

    fun fallbackEnabled(): Boolean = read(KEY_FALLBACK) != "0"

    /** Live web search (Google Search grounding) for Gemini. On by default. */
    fun webSearchEnabled(): Boolean = read(KEY_SEARCH) != "0"

    private fun userKey(provider: AiProvider): String = read("key_" + provider.name).trim()

    private fun buildKey(provider: AiProvider): String = when (provider) {
        AiProvider.GEMINI -> BuildConfig.GEMINI_API_KEY
        AiProvider.OPENAI -> BuildConfig.OPENAI_API_KEY
        AiProvider.CLAUDE -> BuildConfig.CLAUDE_API_KEY
    }.trim()

    /** The key to use: the one typed in the app, otherwise the built-in one ("" = none). */
    fun apiKey(provider: AiProvider): String = userKey(provider).ifBlank { buildKey(provider) }

    /** Model name to send (OpenAI / Claude). Gemini uses its own automatic model chain. */
    fun model(provider: AiProvider): String =
        read("model_" + provider.name).trim().ifBlank { provider.defaultModel }

    fun setSelectedProvider(provider: AiProvider) {
        write(KEY_SELECTED, provider.name)
        publish()
    }

    fun setFallbackEnabled(enabled: Boolean) {
        write(KEY_FALLBACK, if (enabled) "1" else "0")
        publish()
    }

    fun setWebSearchEnabled(enabled: Boolean) {
        write(KEY_SEARCH, if (enabled) "1" else "0")
        publish()
    }

    fun setUserKey(provider: AiProvider, key: String) {
        write("key_" + provider.name, key.trim())
        publish()
    }

    fun clearUserKey(provider: AiProvider) {
        write("key_" + provider.name, "")
        publish()
    }

    fun setModel(provider: AiProvider, model: String) {
        val clean = model.trim()
        write("model_" + provider.name, if (clean == provider.defaultModel) "" else clean)
        publish()
    }

    private fun publish() {
        val providers = AiProvider.values()
        _state.value = AiSettingsState(
            selected = selectedProvider(),
            fallback = fallbackEnabled(),
            webSearch = webSearchEnabled(),
            hasUserKey = providers.associateWith { userKey(it).isNotBlank() },
            hasBuildKey = providers.associateWith { buildKey(it).isNotBlank() },
            models = providers.associateWith { model(it) }
        )
    }
}
''')

write_file("app/src/main/java/com/example/voiceassistant/ui/components/AiSettingsSheet.kt", r'''package com.example.voiceassistant.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.VisibilityOff
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import com.example.voiceassistant.data.AiProvider
import com.example.voiceassistant.data.AiSettings
import com.example.voiceassistant.data.AiSettingsState
import com.example.voiceassistant.viewmodel.AppLanguage

/**
 * Model switching + API keys: choose Gemini / ChatGPT / Claude, type each key (stored encrypted on the device),
 * and decide whether another model answers when the selected one fails.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AiSettingsSheet(language: AppLanguage, onDismiss: () -> Unit) {
    val state by AiSettings.state.collectAsState()
    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp)
                .navigationBarsPadding()
                .imePadding()
                .padding(bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = language.tr("نماذج الذكاء الاصطناعي", "AI models"),
                style = MaterialTheme.typography.titleLarge
            )
            Text(
                text = language.tr(
                    "اختر النموذج الذي يجيب في الدردشة، وأدخل مفتاح API الخاص به. المفاتيح تُخزَّن مشفّرة على هذا الجهاز فقط.",
                    "Pick the model that answers in the chat and enter its API key. Keys are stored encrypted on this device only."
                ),
                style = MaterialTheme.typography.bodySmall
            )
            AiProvider.values().forEach { provider ->
                ProviderCard(provider = provider, language = language, state = state)
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = language.tr(
                        "استخدام نموذج آخر عند فشل النموذج المحدد",
                        "Use another model if the selected one fails"
                    ),
                    modifier = Modifier.weight(1f),
                    style = MaterialTheme.typography.bodyMedium
                )
                Switch(
                    checked = state.fallback,
                    onCheckedChange = { AiSettings.setFallbackEnabled(it) }
                )
            }
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = language.tr(
                        "البحث المباشر في الويب (Gemini): أخبار ومعلومات حديثة",
                        "Live web search (Gemini): news and fresh information"
                    ),
                    modifier = Modifier.weight(1f),
                    style = MaterialTheme.typography.bodyMedium
                )
                Switch(
                    checked = state.webSearch,
                    onCheckedChange = { AiSettings.setWebSearchEnabled(it) }
                )
            }
        }
    }
}

@Composable
private fun ProviderCard(provider: AiProvider, language: AppLanguage, state: AiSettingsState) {
    var keyInput by remember(provider) { mutableStateOf("") }
    var showKey by remember(provider) { mutableStateOf(false) }
    val savedModel = state.models[provider].orEmpty()
    var modelInput by remember(provider, savedModel) { mutableStateOf(savedModel) }

    val hasUserKey = state.hasUserKey[provider] == true
    val hasBuildKey = state.hasBuildKey[provider] == true
    val hasModelField = provider != AiProvider.GEMINI
    val modelChanged = hasModelField && modelInput.trim().ifBlank { provider.defaultModel } != savedModel

    Card(modifier = Modifier.fillMaxWidth()) {
        Column(
            modifier = Modifier.padding(12.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                RadioButton(
                    selected = state.selected == provider,
                    onClick = { AiSettings.setSelectedProvider(provider) }
                )
                Text(
                    text = provider.title,
                    modifier = Modifier.weight(1f),
                    style = MaterialTheme.typography.titleMedium
                )
                Text(
                    text = when {
                        hasUserKey -> language.tr("مفتاح التطبيق ✓", "App key ✓")
                        hasBuildKey -> language.tr("مفتاح مدمج ✓", "Built-in key ✓")
                        else -> language.tr("بدون مفتاح", "No key")
                    },
                    style = MaterialTheme.typography.bodySmall,
                    color = if (hasUserKey || hasBuildKey) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error
                )
            }

            OutlinedTextField(
                value = keyInput,
                onValueChange = { keyInput = it },
                modifier = Modifier.fillMaxWidth(),
                singleLine = true,
                label = { Text(language.tr("مفتاح API", "API key")) },
                placeholder = { Text(if (hasUserKey) "••••••••" else "") },
                visualTransformation = if (showKey) VisualTransformation.None else PasswordVisualTransformation(),
                keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Password, imeAction = ImeAction.Done),
                trailingIcon = {
                    IconButton(onClick = { showKey = !showKey }) {
                        Icon(
                            imageVector = if (showKey) Icons.Filled.VisibilityOff else Icons.Filled.Visibility,
                            contentDescription = null
                        )
                    }
                }
            )

            if (hasModelField) {
                OutlinedTextField(
                    value = modelInput,
                    onValueChange = { modelInput = it },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    label = { Text(language.tr("اسم النموذج", "Model name")) },
                    placeholder = { Text(provider.defaultModel) },
                    keyboardOptions = KeyboardOptions(imeAction = ImeAction.Done)
                )
            }

            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(
                    onClick = {
                        if (keyInput.isNotBlank()) AiSettings.setUserKey(provider, keyInput)
                        if (modelChanged) AiSettings.setModel(provider, modelInput)
                        keyInput = ""
                        showKey = false
                    },
                    enabled = keyInput.isNotBlank() || modelChanged
                ) {
                    Text(language.tr("حفظ", "Save"))
                }
                if (hasUserKey) {
                    OutlinedButton(onClick = { AiSettings.clearUserKey(provider) }) {
                        Text(language.tr("حذف المفتاح", "Remove key"))
                    }
                }
            }
        }
    }
}
''')


# ==============================================================================
# الإضافة الجديدة: التحكم بالكشاف (Flashlight) والصوت (Volume)
# ==============================================================================

# 1. إنشاء ملف HardwareCommand.kt الجديد
write_file("app/src/main/java/com/example/voiceassistant/commands/commands/HardwareCommand.kt", r'''package com.example.voiceassistant.commands.commands

import android.content.Context
import android.hardware.camera2.CameraManager
import android.media.AudioManager
import com.example.voiceassistant.commands.CommandResult
import com.example.voiceassistant.commands.HardwareAction
import com.example.voiceassistant.commands.ParsedCommand
import com.example.voiceassistant.viewmodel.AppLanguage

object HardwareCommand {

    fun execute(context: Context, command: ParsedCommand.Hardware, lang: AppLanguage): CommandResult {
        return when (command.action) {
            HardwareAction.FLASHLIGHT_ON -> setFlashlight(context, true, lang)
            HardwareAction.FLASHLIGHT_OFF -> setFlashlight(context, false, lang)
            HardwareAction.VOLUME_UP -> adjustVolume(context, AudioManager.ADJUST_RAISE, lang, "رفع الصوت", "Volume up")
            HardwareAction.VOLUME_DOWN -> adjustVolume(context, AudioManager.ADJUST_LOWER, lang, "خفض الصوت", "Volume down")
            HardwareAction.VOLUME_MUTE -> muteVolume(context, lang)
        }
    }

    private fun setFlashlight(context: Context, enable: Boolean, lang: AppLanguage): CommandResult {
        return try {
            val cameraManager = context.getSystemService(Context.CAMERA_SERVICE) as CameraManager
            val cameraId = cameraManager.cameraIdList.firstOrNull { id ->
                val characteristics = cameraManager.getCameraCharacteristics(id)
                characteristics.get(android.hardware.camera2.CameraCharacteristics.FLASH_INFO_AVAILABLE) == true
            }
            if (cameraId != null) {
                cameraManager.setTorchMode(cameraId, enable)
                CommandResult.Success(if (enable) lang.tr("تم تشغيل الكشاف.", "Flashlight turned on.") else lang.tr("تم إطفاء الكشاف.", "Flashlight turned off."))
            } else {
                CommandResult.Failure(lang.tr("لا يوجد كشاف في هذا الجهاز.", "No flashlight available on this device."))
            }
        } catch (e: Exception) {
            CommandResult.Failure(lang.tr("تعذّر التحكم بالكشاف.", "Couldn't control the flashlight."))
        }
    }

    private fun adjustVolume(context: Context, direction: Int, lang: AppLanguage, arMsg: String, enMsg: String): CommandResult {
        return try {
            val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as AudioManager
            audioManager.adjustStreamVolume(AudioManager.STREAM_MUSIC, direction, AudioManager.FLAG_SHOW_UI)
            CommandResult.Success(lang.tr("تم $arMsg.", "$enMsg done."))
        } catch (e: Exception) {
            CommandResult.Failure(lang.tr("تعذّر تغيير مستوى الصوت.", "Couldn't change the volume."))
        }
    }

    private fun muteVolume(context: Context, lang: AppLanguage): CommandResult {
        return try {
            val audioManager = context.getSystemService(Context.AUDIO_SERVICE) as AudioManager
            audioManager.adjustStreamVolume(AudioManager.STREAM_MUSIC, AudioManager.ADJUST_MUTE, AudioManager.FLAG_SHOW_UI)
            CommandResult.Success(lang.tr("تم كتم الصوت.", "Volume muted."))
        } catch (e: Exception) {
            CommandResult.Failure(lang.tr("تعذّر كتم الصوت.", "Couldn't mute the volume."))
        }
    }
}
''')

# 2. إضافة Hardware إلى ParsedCommand (داخل الـ sealed class) + enum HardwareAction في CommandParser.kt
insert_before(
    "app/src/main/java/com/example/voiceassistant/commands/CommandParser.kt",
    "    object Unknown : ParsedCommand()\n",
    r'''    /** Flashlight on/off and volume up/down/mute. */
    data class Hardware(val action: HardwareAction) : ParsedCommand()
'''
)

insert_before(
    "app/src/main/java/com/example/voiceassistant/commands/CommandParser.kt",
    "enum class SecurityAction { ENABLE, DISABLE, SCAN_APPS }",
    r'''enum class HardwareAction { FLASHLIGHT_ON, FLASHLIGHT_OFF, VOLUME_UP, VOLUME_DOWN, VOLUME_MUTE }

'''
)

# 3. إضافة دالة التحليل parseHardware إلى CommandParser.kt (قبل parseLaunch حتى لا يلتقطها «افتح ...»)
insert_before(
    "app/src/main/java/com/example/voiceassistant/commands/CommandParser.kt",
    "?: parseLaunch(t)\n            ?: ParsedCommand.Unknown",
    r'''?: parseHardware(t)
            '''
)

# إضافة دالة parseHardware نفسها قبل parseLaunch
insert_before(
    "app/src/main/java/com/example/voiceassistant/commands/CommandParser.kt",
    "private fun parseLaunch(t: Prepared): ParsedCommand? {",
    r'''private fun parseHardware(t: Prepared): ParsedCommand? {
        val action = when {
            t.containsAny("شغل الكشاف", "افتح الكشاف", "شغل الضوء", "افتح الضوء", "turn on flashlight", "turn on the light") -> HardwareAction.FLASHLIGHT_ON
            t.containsAny("اطفي الكشاف", "اغلق الكشاف", "اطفي الضوء", "اغلق الضوء", "turn off flashlight", "turn off the light") -> HardwareAction.FLASHLIGHT_OFF
            t.containsAny("علي الصوت", "رفع الصوت", "زود الصوت", "volume up", "turn up the volume") -> HardwareAction.VOLUME_UP
            t.containsAny("وطي الصوت", "نزل الصوت", "اخفض الصوت", "قلل الصوت", "volume down", "turn down the volume") -> HardwareAction.VOLUME_DOWN
            t.containsAny("اكتم الصوت", "اسكت الصوت", "mute volume", "mute the sound") -> HardwareAction.VOLUME_MUTE
            else -> return null
        }
        return ParsedCommand.Hardware(action)
    }

    '''
)

# 4. ربط الأمر في IntentCommandHandler.kt
insert_before(
    "app/src/main/java/com/example/voiceassistant/commands/IntentCommandHandler.kt",
    "is ParsedCommand.Reminder -> ReminderCommand.execute(appContext, command, lang)",
    r'''is ParsedCommand.Hardware -> HardwareCommand.execute(appContext, command, lang)
            '''
)

# إضافة الاستيراد في IntentCommandHandler.kt
insert_before(
    "app/src/main/java/com/example/voiceassistant/commands/IntentCommandHandler.kt",
    "import com.example.voiceassistant.commands.commands.InfoCommand",
    r'''import com.example.voiceassistant.commands.commands.HardwareCommand
'''
)

print(">> Hardware features (Flashlight & Volume) have been injected successfully.")


# ==============================================================================
# الإضافة الجديدة: الكتابة على الشاشة (Type Text) والإرسال (Send Text)
# ==============================================================================

# 1. تحديث VoiceAccessibilityService.kt لدعم الكتابة في حقول الإدخال
with open("app/src/main/java/com/example/voiceassistant/service/VoiceAccessibilityService.kt", "r", encoding="utf-8") as f:
    _acc_code = f.read()

_acc_type = '''
    /** يبحث عن حقل كتابة على الشاشة ويكتب فيه النص المطلوب. */
    fun performTypeText(text: String): Boolean {
        val root = rootInActiveWindow ?: return false
        
        // 1. البحث عن حقل الكتابة النشط
        val focused = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT)
        if (focused != null && (focused.isEditable || focused.className == "android.widget.EditText")) {
            val args = android.os.Bundle()
            args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
            if (focused.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)) return true
        }

        // 2. إذا لم يوجد نشط، نبحث في كل الشاشة عن EditText
        val allNodes = ArrayList<AccessibilityNodeInfo>()
        collectAllNodes(root, allNodes, 0)
        for (node in allNodes) {
            if (node.isEditable || node.className == "android.widget.EditText") {
                node.performAction(AccessibilityNodeInfo.ACTION_FOCUS)
                val args = android.os.Bundle()
                args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
                if (node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)) return true
            }
        }
        return false
    }
'''

_acc_code = _acc_code.replace(
    "    private fun clickByText(text: String): Boolean {",
    _acc_type + "\n    private fun clickByText(text: String): Boolean {"
)

with open("app/src/main/java/com/example/voiceassistant/service/VoiceAccessibilityService.kt", "w", encoding="utf-8", newline="\n") as f:
    f.write(_acc_code)


# 2. تحديث CommandParser.kt لدعم أوامر الكتابة والإرسال
with open("app/src/main/java/com/example/voiceassistant/commands/CommandParser.kt", "r", encoding="utf-8") as f:
    _parser = f.read()

# إضافة الأوامر الجديدة
_parser = _parser.replace(
    "    data class Hardware(val action: HardwareAction) : ParsedCommand()",
    '''    data class Hardware(val action: HardwareAction) : ParsedCommand()

    /** كتابة نص على الشاشة (يقوم الذكاء الاصطناعي بتوليده أولاً). */
    data class TypeText(val prompt: String) : ParsedCommand()
    
    /** الضغط على زر الإرسال. */
    object SendText : ParsedCommand()'''
)

# إضافة كلمات التعرف والـ Regex
_parser = _parser.replace(
    "    private val timeRegex = Regex(\"\"\"(\\d{1,2})(?:[:.](\\d{2}))?\"\"\")",
    '''    private val typeAr = Regex("""^(?:اكتب|اكتبي|دون)(?:\\s+لي)?\\s+(.+)$""")
    private val typeEn = Regex("""^(?:type|write)(?:\\s+me)?\\s+(.+)$""")
    private val sendRegex = Regex("""^(?:ارسل|أرسل|ارسلها|send|send it|send message)$""")
    
    private val timeRegex = Regex(\"\"\"(\\d{1,2})(?:[:.](\\d{2}))?\"\"\")'''
)

# إضافة دالة التحليل parseWriting
# (طلبات الأكواد والملفات مثل «اكتب لي كود html» تبقى محادثة عادية مع الذكاء الاصطناعي)
_parser = _parser.replace(
    "    private fun parseLaunch(t: Prepared): ParsedCommand? {",
    '''    private fun parseWriting(t: Prepared): ParsedCommand? {
        if (sendRegex.matches(t.key)) return ParsedCommand.SendText
        if (t.containsAny(
                "كود", "اكواد", "برنامج", "سكريبت", "سكربت", "ملف", "صفحه", "موقع", "تطبيق",
                "html", "css", "java", "kotlin", "python", "script", "code", "file", "program", "function", "class", "website"
            )
        ) return null
        t.groups(typeAr)?.let { return ParsedCommand.TypeText(it[0]) }
        t.groups(typeEn)?.let { return ParsedCommand.TypeText(it[0]) }
        return null
    }

    private fun parseLaunch(t: Prepared): ParsedCommand? {'''
)

# إضافة استدعاء parseWriting في دالة parse الرئيسية (قبل parseAccessibility)
_parser = _parser.replace(
    "?: parseAccessibility(t)\n            ?: parseSettings(t)",
    "?: parseWriting(t)\n            ?: parseAccessibility(t)\n            ?: parseSettings(t)"
)

with open("app/src/main/java/com/example/voiceassistant/commands/CommandParser.kt", "w", encoding="utf-8", newline="\n") as f:
    f.write(_parser)


# 3. تحديث IntentCommandHandler.kt
with open("app/src/main/java/com/example/voiceassistant/commands/IntentCommandHandler.kt", "r", encoding="utf-8") as f:
    _handler = f.read()

_handler = _handler.replace(
    "            ParsedCommand.Unknown -> CommandResult.Failure(",
    '''            is ParsedCommand.TypeText -> CommandResult.Failure("يتم تنفيذ هذا الأمر من الشاشة الرئيسية.")
            is ParsedCommand.SendText -> CommandResult.Failure("يتم تنفيذ هذا الأمر من الشاشة الرئيسية.")
            ParsedCommand.Unknown -> CommandResult.Failure('''
)

with open("app/src/main/java/com/example/voiceassistant/commands/IntentCommandHandler.kt", "w", encoding="utf-8", newline="\n") as f:
    f.write(_handler)


# 4. تحديث AiChatService.kt لتوليد النص الجاهز للكتابة
with open("app/src/main/java/com/example/voiceassistant/data/AiChatService.kt", "r", encoding="utf-8") as f:
    _ai = f.read()

_ai = _ai.replace(
    "    suspend fun ask(text: String, lang: AppLanguage): AiResult = withContext(Dispatchers.IO) {",
    '''    /** يطلب من الذكاء الاصطناعي توليد نص جاهز للكتابة (بدون مقدمات أو تعليقات). */
    suspend fun generateTextToType(prompt: String, lang: AppLanguage): AiResult {
        val strictPrompt = lang.tr(
            "المستخدم يريد كتابة النص التالي على الشاشة. أجب بهذا النص حرفياً فقط وبدون أي كلام إضافي أو علامات اقتباس: $prompt",
            "The user wants to type this on the screen. Reply with exactly this text only, no extra words or quotes: $prompt"
        )
        return ask(strictPrompt, lang)
    }

    suspend fun ask(text: String, lang: AppLanguage): AiResult = withContext(Dispatchers.IO) {'''
)

with open("app/src/main/java/com/example/voiceassistant/data/AiChatService.kt", "w", encoding="utf-8", newline="\n") as f:
    f.write(_ai)


# 5. تحديث MainViewModel.kt لمعالجة أوامر الكتابة والإرسال
with open("app/src/main/java/com/example/voiceassistant/viewmodel/MainViewModel.kt", "r", encoding="utf-8") as f:
    _vm = f.read()

_vm = _vm.replace(
    "            if (parsed is ParsedCommand.Memory) {",
    '''            if (parsed is ParsedCommand.TypeText) {
                _uiState.update { it.copy(status = AssistantStatus.PROCESSING, partialText = "") }
                reply(lang.tr("جارٍ توليد النص وكتابته...", "Generating and typing text..."), lang, speak = false)
                
                val result = ai.generateTextToType(parsed.prompt, lang)
                if (result is AiResult.Success) {
                    if (VoiceAccessibilityService.isRunning) {
                        _backgroundRequests.tryEmit(Unit)
                        delay(700)
                    }
                    val success = VoiceAccessibilityService.instance?.performTypeText(result.text) == true
                    if (success) {
                        reply(lang.tr("تمت كتابة النص. قل «أرسل» للإرسال.", "Typed. Say send to send."), lang, speak = speak)
                    } else {
                        reply(lang.tr("لم أجد حقل كتابة على الشاشة. تأكد من فتح التطبيق والضغط على المربع.", "Couldn't find a text field."), lang, speak = speak)
                    }
                } else {
                    val errDetails = (result as? AiResult.Error)?.detail ?: "Unknown Error"
                    reply(lang.tr("فشل التوليد. السبب: $errDetails", "Failed. Reason: $errDetails"), lang, speak = speak)
                }
                return@launch
            }

            if (parsed is ParsedCommand.SendText) {
                val service = VoiceAccessibilityService.instance
                if (service == null) {
                    reply(lang.tr("خدمة الوصول غير مفعلة.", "Accessibility service is off."), lang, speak = speak)
                    return@launch
                }
                _backgroundRequests.tryEmit(Unit)
                delay(700)
                // نحاول الضغط على أزرار الإرسال الشائعة
                val sent = service.performSmartClick("Send") || 
                           service.performSmartClick("إرسال") || 
                           service.performSmartClick("سهم") || 
                           service.performSmartClick("ارسال")
                if (sent) {
                    reply(lang.tr("تم الإرسال بنجاح.", "Sent successfully."), lang, speak = speak)
                } else {
                    reply(lang.tr("لم أجد زر الإرسال. اضغط عليه يدوياً.", "Couldn't find the send button."), lang, speak = speak)
                }
                return@launch
            }

            if (parsed is ParsedCommand.Memory) {'''
)

with open("app/src/main/java/com/example/voiceassistant/viewmodel/MainViewModel.kt", "w", encoding="utf-8", newline="\n") as f:
    f.write(_vm)

print(">> Smart Type & Send features injected successfully.")


# ==============================================================================
# الإضافة الجديدة: التحكم الكامل بالشاشة (قراءة الشاشة + الضغط الذكي + سياق AI)
# ==============================================================================

# 1. تحديث VoiceAccessibilityService.kt لدعم قراءة الشاشة والضغط الذكي
with open("app/src/main/java/com/example/voiceassistant/service/VoiceAccessibilityService.kt", "r", encoding="utf-8") as f:
    _acc_code = f.read()

# إضافة دالة قراءة الشاشة ودالة الضغط الذكي قبل النهاية
_acc_add = '''
    /** يقرأ كل النصوص الظاهرة على الشاشة حالياً (لا يقرأ نافذة المساعد نفسه، ويقصّ النص الطويل). */
    fun readScreenText(): String {
        val root = rootInActiveWindow ?: return ""
        if (root.packageName?.toString() == packageName) return ""
        val sb = StringBuilder()
        collectTexts(root, sb, 0)
        return sb.toString().replace(Regex("\\\\s+"), " ").trim().take(4000)
    }

    /** ضغط ذكي: يبحث عن النص بشكل مطابق، ثم يبحث بشكل تقريبي داخل التطبيق. */
    fun performSmartClick(query: String): Boolean {
        val root = rootInActiveWindow ?: return false
        
        // 1. بحث مطابق (Exact Match)
        val exact = root.findAccessibilityNodeInfosByText(query)
        if (exact != null && exact.isNotEmpty()) {
            for (node in exact) {
                if (clickNodeOrAncestor(node)) return true
            }
        }

        // 2. بحث تقريبي (Fuzzy Match) - يبحث في كل النصوص والأوصاف
        val allNodes = ArrayList<AccessibilityNodeInfo>()
        collectAllNodes(root, allNodes, 0)
        val qKey = TextNormalizer.key(query)
        for (node in allNodes) {
            val nodeText = node.text?.toString() ?: ""
            val nodeDesc = node.contentDescription?.toString() ?: ""
            val label = TextNormalizer.key(nodeText + " " + nodeDesc)
            if (label.contains(qKey) && clickNodeOrAncestor(node)) {
                return true
            }
        }
        return false
    }

    private fun collectAllNodes(node: AccessibilityNodeInfo, out: MutableList<AccessibilityNodeInfo>, depth: Int) {
        if (depth > MAX_DEPTH) return
        out.add(node)
        for (i in 0 until node.childCount) {
            node.getChild(i)?.let { collectAllNodes(it, out, depth + 1) }
        }
    }
'''

_acc_code = _acc_code.replace(
    "    private fun clickByText(text: String): Boolean {",
    _acc_add + "\n    private fun clickByText(text: String): Boolean {"
)

# execute() يجب أن يغطي READ_SCREEN أيضاً (when شاملة)
_acc_code = _acc_code.replace(
    "        AccessibilityAction.CLICK_TEXT -> argument?.let { clickByText(it) } ?: false\n",
    "        AccessibilityAction.CLICK_TEXT -> argument?.let { clickByText(it) } ?: false\n"
    "        AccessibilityAction.READ_SCREEN -> readScreenText().isNotBlank()\n"
)

with open("app/src/main/java/com/example/voiceassistant/service/VoiceAccessibilityService.kt", "w", encoding="utf-8", newline="\n") as f:
    f.write(_acc_code)


# 2. تحديث CommandParser.kt لدعم "اقرأ الشاشة" و "اضغط على..."
with open("app/src/main/java/com/example/voiceassistant/commands/CommandParser.kt", "r", encoding="utf-8") as f:
    _parser_code = f.read()

# تحديث دالة parseAccessibility لاكتشاف أوامر القراءة والضغط
# (المفاتيح مُطبَّعة: ة -> ه، لذلك «الشاشه» وليس «الشاشة»)
_parser_code = _parser_code.replace(
    't.containsAny("الاعدادات السريعه", "quick settings", "اللوحه السريعه") ->\n                a(AccessibilityAction.QUICK_SETTINGS)',
    '''t.containsAny("اقرا الشاشه", "اقرا لي الشاشه", "ماذا يوجد في الشاشه", "ماذا على الشاشه", "read screen", "read the screen", "what is on the screen") ->
                a(AccessibilityAction.READ_SCREEN)
            t.containsAny("الاعدادات السريعه", "quick settings", "اللوحه السريعه") ->
                a(AccessibilityAction.QUICK_SETTINGS)'''
)

# تحديث كلمات الضغط لتشمل "اختر" و "اضغط"
_parser_code = _parser_code.replace(
    'private val clickAr = Regex("""^(?:اضغط|انقر|دوس)(?:\\s+علي)?\\s+(.+)$""")',
    'private val clickAr = Regex("""^(?:اضغط|انقر|دوس|اختر)(?:\\s+علي|\\s+على)?\\s+(.+)$""")'
)

with open("app/src/main/java/com/example/voiceassistant/commands/CommandParser.kt", "w", encoding="utf-8", newline="\n") as f:
    f.write(_parser_code)


# 3. تحديث AccessibilityCommand.kt لإضافة READ_SCREEN وتنفيذ قراءة الشاشة واستخدام الضغط الذكي
with open("app/src/main/java/com/example/voiceassistant/commands/commands/AccessibilityCommand.kt", "r", encoding="utf-8") as f:
    _acc_cmd = f.read()

# إضافة READ_SCREEN إلى الـ Enum (القراءة تستهدف التطبيق الآخر، فيتنحى المساعد جانباً أولاً)
_acc_cmd = _acc_cmd.replace(
    "    CLICK_TEXT(true)\n}",
    "    CLICK_TEXT(true),\n    READ_SCREEN(true)\n}"
)

_acc_cmd = _acc_cmd.replace(
    "val ok = service.execute(command.action, command.argument)",
    '''val ok = if (command.action == AccessibilityAction.READ_SCREEN) {
            val text = service.readScreenText()
            if (text.isNotBlank()) {
                return CommandResult.Success(lang.tr("الشاشة تعرض: $text", "The screen shows: $text"))
            } else {
                return CommandResult.Failure(lang.tr("الشاشة فارغة.", "The screen is empty."))
            }
        } else if (command.action == AccessibilityAction.CLICK_TEXT && command.argument != null) {
            service.performSmartClick(command.argument)
        } else {
            service.execute(command.action, command.argument)
        }'''
)

_acc_cmd = _acc_cmd.replace(
    "AccessibilityAction.CLICK_TEXT -> lang.tr(",
    "AccessibilityAction.READ_SCREEN -> lang.tr(\"تمت القراءة.\", \"Read.\")\n            AccessibilityAction.CLICK_TEXT -> lang.tr("
)

with open("app/src/main/java/com/example/voiceassistant/commands/commands/AccessibilityCommand.kt", "w", encoding="utf-8", newline="\n") as f:
    f.write(_acc_cmd)


# 4. تحديث AiChatService.kt لحقن نصوص الشاشة داخل سياق الذكاء الاصطناعي
with open("app/src/main/java/com/example/voiceassistant/data/AiChatService.kt", "r", encoding="utf-8") as f:
    _ai_code = f.read()

_old_prompt = "        // Long-term memory: read from RAM, no extra request. \"\" when nothing is stored.\n        val memory = memoryManager?.renderForPrompt(lang).orEmpty()\n        return if (memory.isEmpty()) withName else withName + \"\\n\\n\" + memory"
_new_prompt = '''        // Long-term memory: read from RAM, no extra request. "" when nothing is stored.
        val memory = memoryManager?.renderForPrompt(lang).orEmpty()
        val withMemory = if (memory.isEmpty()) withName else withName + "\\n\\n" + memory

        // سياق الشاشة: إذا كانت خدمة الوصول تعمل، نرسل نصوص الشاشة الحالية للذكاء الاصطناعي ليفهم ما يراه المستخدم.
        val screenText = com.example.voiceassistant.service.VoiceAccessibilityService.instance?.readScreenText()
        return if (screenText.isNullOrBlank()) {
            withMemory
        } else {
            withMemory + "\\n\\n" + lang.tr(
                "الشاشة الحالية تعرض النصوص التالية (استخدمها للإجابة إذا سأل المستخدم عما يراه أو ماذا يفعل الآن):\\n$screenText",
                "The current screen displays the following texts (use them if the user asks what they see or what to do next):\\n$screenText"
            )
        }'''

if _old_prompt in _ai_code:
    _ai_code = _ai_code.replace(_old_prompt, _new_prompt)
    with open("app/src/main/java/com/example/voiceassistant/data/AiChatService.kt", "w", encoding="utf-8", newline="\n") as f:
        f.write(_ai_code)
else:
    print(">> WARNING: Could not inject screen context into AiChatService.kt")

print(">> Full Screen Control & AI Context injected successfully.")


print(">> Done. {} files created in: {}".format(FILES_CREATED[0], os.getcwd()))
print(">> Next steps:")
print("   1. API keys: add GEMINI_API_KEY / OPENAI_API_KEY / CLAUDE_API_KEY as GitHub Secrets (they go into BuildConfig),")
print("      and/or type them in the app: side menu > AI models (stored encrypted, they override the built-in ones).")
print("   2. gradle assembleDebug  (or push to GitHub and let the workflow build it).")
print("   3. Install, then Settings > Apps > Default apps > Digital assistant app > Zevorix AI.")
print("   4. Enable the accessibility service for screen control and Wi-Fi/Bluetooth switches.")
print("   5. Allow notifications when asked (Android 13+). For on-time reminders also enable")
print("      Settings > Apps > Zevorix AI > Alarms & reminders (Android 12+).")
print("   6. Anti-theft: open the shield menu > Anti-theft, save the trusted number and PIN, grant the permissions, then activate Device Admin.")
print("   7. Try: \"ذكرني بشرب الماء بعد 10 دقائق\"  /  \"ذكرني بموعد الطبيب غداً الساعة 5 مساءً\".")

# ==============================================================================
# الإضافة الجديدة: إظهار عدّاد التوكنات (Token Counter) في الواجهة
# ==============================================================================

# 1. إضافة عدّاد التوكنات في القائمة الجانبية (SessionsDrawerContent)
with open("app/src/main/java/com/example/voiceassistant/ui/MainScreen.kt", "r", encoding="utf-8") as f:
    _main_code = f.read()

_drawer_target = '''            androidx.compose.material3.OutlinedButton(
                onClick = onOpenSettings,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(start = 16.dp, end = 16.dp, bottom = 12.dp)
            ) {
                Icon(imageVector = Icons.Filled.SettingsIcon, contentDescription = null)
                Text(
                    text = language.tr("نماذج الذكاء الاصطناعي", "AI models"),
                    modifier = Modifier.padding(start = 8.dp)
                )
            }'''

_drawer_replacement = _drawer_target + '''

            val tokenUsage by com.example.voiceassistant.data.TokenCounter.usage.collectAsStateWithLifecycle()
            Text(
                text = language.tr("التوكنات المستهلكة: ${tokenUsage.total}", "Tokens used: ${tokenUsage.total}"),
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp)
            )'''

if _drawer_target in _main_code:
    _main_code = _main_code.replace(_drawer_target, _drawer_replacement)
    with open("app/src/main/java/com/example/voiceassistant/ui/MainScreen.kt", "w", encoding="utf-8", newline="\n") as f:
        f.write(_main_code)
else:
    print(">> WARNING: Could not inject token counter into MainScreen.kt")

# 2. إضافة عدّاد التوكنات في شاشة إعدادات الذكاء الاصطناعي (AiSettingsSheet)
with open("app/src/main/java/com/example/voiceassistant/ui/components/AiSettingsSheet.kt", "r", encoding="utf-8") as f:
    _settings_code = f.read()

_settings_target = '''            Text(
                text = language.tr("نماذج الذكاء الاصطناعي", "AI models"),
                style = MaterialTheme.typography.titleLarge
            )'''

_settings_replacement = _settings_target + '''

            val tokenUsage by com.example.voiceassistant.data.TokenCounter.usage.collectAsStateWithLifecycle()
            Text(
                text = language.tr("التوكنات المستهلكة في هذه الجلسة: ${tokenUsage.total}", "Tokens used this session: ${tokenUsage.total}"),
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(bottom = 8.dp)
            )'''

if _settings_target in _settings_code:
    _settings_code = _settings_code.replace(_settings_target, _settings_replacement)
    _lc_import = "import androidx.lifecycle.compose.collectAsStateWithLifecycle\n"
    if _lc_import not in _settings_code:
        _settings_code = _settings_code.replace(
            "import androidx.compose.ui.unit.dp\n",
            "import androidx.compose.ui.unit.dp\n" + _lc_import, 1)
    with open("app/src/main/java/com/example/voiceassistant/ui/components/AiSettingsSheet.kt", "w", encoding="utf-8", newline="\n") as f:
        f.write(_settings_code)
else:
    print(">> WARNING: Could not inject token counter into AiSettingsSheet.kt")

print(">> Token Counter UI injected successfully.")


# ==============================================================================
# ثلاث ميزات جديدة (تُضاف في نهاية setup.py، لا تحذف ولا تغيّر أي ميزة سابقة):
#   1) السيناريوهات الصوتية (Custom Routines / Macros)
#   2) الجسر الذكي للحافظة (Smart Clipboard Bridging)
#   3) الرؤية الحية (Live Vision): زر الكاميرا يصف الصورة وينطق الرد تلقائياً
# كل نقطة إدراج يتم التحقق من أنها تظهر مرة واحدة بالضبط، وإلا يتوقف السكربت بخطأ واضح.
# ==============================================================================
_PKG = "app/src/main/java/com/example/voiceassistant"


def _replace_once(path, old, new):
    """Replaces the single occurrence of `old` (fails loudly if it is missing or repeated)."""
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    if text.count(old) != 1:
        raise RuntimeError("Expected exactly one match in {}: {!r} (found {})".format(path, old[:70], text.count(old)))
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text.replace(old, new, 1))


# ------------------------------------------------------------------------------
# الميزة 1: السيناريوهات الصوتية
# ------------------------------------------------------------------------------

# 1-أ. التخزين: SharedPreferences كـ JSON
write_file(_PKG + "/data/RoutineStore.kt", r'''package com.example.voiceassistant.data

import android.content.Context
import com.example.voiceassistant.commands.TextNormalizer
import org.json.JSONArray
import org.json.JSONObject

/** A named list of voice commands that run one after another ("صباح الخير" -> several commands). */
data class Routine(val name: String, val steps: List<String>)

/** Keeps the routines in SharedPreferences as one JSON array. */
class RoutineStore(context: Context) {

    private val prefs = context.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE)

    fun load(): List<Routine> = try {
        val array = JSONArray(prefs.getString(KEY, "[]") ?: "[]")
        val result = ArrayList<Routine>()
        for (i in 0 until array.length()) {
            val obj = array.optJSONObject(i) ?: continue
            val name = obj.optString("name").trim()
            val stepsJson = obj.optJSONArray("steps") ?: continue
            val steps = ArrayList<String>()
            for (j in 0 until stepsJson.length()) {
                val step = stepsJson.optString(j).trim()
                if (step.isNotEmpty()) steps.add(step)
            }
            if (name.isNotEmpty() && steps.isNotEmpty()) result.add(Routine(name, steps))
        }
        result
    } catch (e: Exception) {
        emptyList()
    }

    fun save(routines: List<Routine>) {
        val array = JSONArray()
        routines.forEach { routine ->
            array.put(JSONObject().put("name", routine.name).put("steps", JSONArray(routine.steps)))
        }
        prefs.edit().putString(KEY, array.toString()).apply()
    }

    companion object {
        private const val PREFS = "voice_routines"
        private const val KEY = "routines_json"
        const val MAX_STEPS = 20

        private val triggerWords = Regex(
            "^(?:شغل|نفذ|ابدا|فعل|run|start|execute|play)\\s+(?:(?:ال)?(?:سيناريو|روتين)\\s+|(?:the\\s+)?(?:routine|scenario|macro)\\s+)?"
        )

        /** Same normalization as the command parser, minus punctuation, so a spoken phrase can equal a name. */
        fun normalize(text: String): String =
            TextNormalizer.key(TextNormalizer.light(text))
                .replace(Regex("[\\p{Punct}\\u060C\\u061F\\u061B«»\"]"), " ")
                .replace(Regex("\\s+"), " ")
                .trim()

        /** The routine triggered by [spoken]: its exact name, or "شغل سيناريو <name>" / "run routine <name>". */
        fun find(spoken: String, routines: List<Routine>): Routine? {
            if (routines.isEmpty()) return null
            val key = normalize(spoken)
            if (key.isEmpty()) return null
            val stripped = key.replace(triggerWords, "").trim()
            return routines.firstOrNull {
                val n = normalize(it.name)
                n.isNotEmpty() && (n == key || n == stripped)
            }
        }
    }
}
''')

# 1-ب. الواجهة: BottomSheet لإضافة / تعديل / تشغيل / حذف السيناريوهات
write_file(_PKG + "/ui/components/RoutinesSheet.kt", r'''package com.example.voiceassistant.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Edit
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.example.voiceassistant.data.Routine
import com.example.voiceassistant.viewmodel.AppLanguage

/** Bottom sheet to create / edit / run / delete voice routines (one command per line, run in order). */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RoutinesSheet(
    routines: List<Routine>,
    language: AppLanguage,
    onSave: (oldName: String?, name: String, steps: List<String>) -> Unit,
    onDelete: (String) -> Unit,
    onRun: (String) -> Unit,
    onDismiss: () -> Unit
) {
    var editorOpen by remember { mutableStateOf(false) }
    var editingName by remember { mutableStateOf<String?>(null) }
    var nameText by remember { mutableStateOf("") }
    var stepsText by remember { mutableStateOf("") }

    ModalBottomSheet(onDismissRequest = onDismiss) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(start = 16.dp, end = 16.dp, bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = language.tr("السيناريوهات الصوتية", "Voice routines"),
                style = MaterialTheme.typography.titleLarge
            )

            if (editorOpen) {
                OutlinedTextField(
                    value = nameText,
                    onValueChange = { nameText = it },
                    modifier = Modifier.fillMaxWidth(),
                    singleLine = true,
                    label = { Text(language.tr("اسم السيناريو (مثال: صباح الخير)", "Routine name (e.g. Good morning)")) }
                )
                OutlinedTextField(
                    value = stepsText,
                    onValueChange = { stepsText = it },
                    modifier = Modifier.fillMaxWidth(),
                    minLines = 4,
                    label = { Text(language.tr("الأوامر: أمر في كل سطر", "Commands: one per line")) },
                    placeholder = {
                        Text(language.tr("شغل الواي فاي\nكم الساعة\nاقرأ الأخبار", "turn on wifi\nwhat time is it\nsearch the news"))
                    }
                )
                Text(
                    text = language.tr(
                        "تُنفَّذ الأوامر بالترتيب. لتشغيله قل اسم السيناريو أو «شغل سيناريو <الاسم>».",
                        "Commands run in order. To run it, say the routine name or \"run routine <name>\"."
                    ),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Button(
                        enabled = nameText.isNotBlank() && stepsText.isNotBlank(),
                        onClick = {
                            onSave(editingName, nameText, stepsText.lines())
                            editorOpen = false
                        }
                    ) {
                        Text(language.tr("حفظ", "Save"))
                    }
                    OutlinedButton(onClick = { editorOpen = false }) {
                        Text(language.tr("إلغاء", "Cancel"))
                    }
                }
            } else {
                if (routines.isEmpty()) {
                    Text(
                        text = language.tr(
                            "لا توجد سيناريوهات بعد. أنشئ واحداً يجمع عدة أوامر وينفذها بكلمة واحدة.",
                            "No routines yet. Create one that bundles several commands behind a single phrase."
                        ),
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                routines.forEach { routine ->
                    Card(modifier = Modifier.fillMaxWidth()) {
                        Row(
                            modifier = Modifier
                                .fillMaxWidth()
                                .padding(start = 16.dp, end = 4.dp, top = 4.dp, bottom = 4.dp),
                            verticalAlignment = Alignment.CenterVertically
                        ) {
                            Column(modifier = Modifier.weight(1f)) {
                                Text(routine.name, style = MaterialTheme.typography.titleMedium)
                                Text(
                                    text = language.tr("${routine.steps.size} أوامر", "${routine.steps.size} commands"),
                                    style = MaterialTheme.typography.bodySmall,
                                    color = MaterialTheme.colorScheme.onSurfaceVariant
                                )
                            }
                            IconButton(onClick = { onRun(routine.name) }) {
                                Icon(Icons.Filled.PlayArrow, contentDescription = language.tr("تشغيل", "Run"))
                            }
                            IconButton(onClick = {
                                editingName = routine.name
                                nameText = routine.name
                                stepsText = routine.steps.joinToString("\n")
                                editorOpen = true
                            }) {
                                Icon(Icons.Filled.Edit, contentDescription = language.tr("تعديل", "Edit"))
                            }
                            IconButton(onClick = { onDelete(routine.name) }) {
                                Icon(Icons.Filled.Delete, contentDescription = language.tr("حذف", "Delete"))
                            }
                        }
                    }
                }
                Button(onClick = {
                    editingName = null
                    nameText = ""
                    stepsText = ""
                    editorOpen = true
                }) {
                    Icon(Icons.Filled.Add, contentDescription = null)
                    Text(language.tr("  سيناريو جديد", "  New routine"))
                }
            }
        }
    }
}
''')

# 1-ج. CommandParser: أمر تشغيل السيناريو + أمر الحافظة (يُفحصان قبل بقية الأوامر)
_parser_path = _PKG + "/commands/CommandParser.kt"

insert_before(
    _parser_path,
    "    object Unknown : ParsedCommand()",
    r'''    /** Runs a saved routine (macro) by its name. */
    data class RunRoutine(val name: String) : ParsedCommand()

    /** "Read the clipboard, summarize it and send it to <person>" ([app] is "whatsapp" or "telegram"). */
    data class ClipboardShare(
        val person: String,
        val app: String = "whatsapp",
        val summarize: Boolean = true
    ) : ParsedCommand()

''')

insert_before(
    _parser_path,
    "    private fun parseWriting(t: Prepared): ParsedCommand? {",
    r'''    // ---- custom routines + clipboard bridge ---------------------------------------------------
    /** Set by MainViewModel: returns the name of the routine that [spoken] triggers, or null. */
    @Volatile
    var routineLookup: ((String) -> String?)? = null

    private fun parseRoutine(t: Prepared): ParsedCommand? =
        routineLookup?.invoke(t.key)?.let { ParsedCommand.RunRoutine(it) }

    private val clipSendAr = Regex("""(?:ارسل|ابعث)(?:ها|ه)?\s+(?:(?:الي|الى|ل)\s+)?(.+)$""")
    private val clipSendEn = Regex("""(?:send|forward|share)\s+(?:it\s+|that\s+|this\s+)?(?:to\s+)?(.+)$""")
    private val messengerSuffix = Regex(
        """\s+(?:(?:عبر|علي|على|في|via|on|in|using|through)\s+)?(?:تطبيق\s+|app\s+)?(واتساب|واتس اب|وتساب|whatsapp|تلغرام|تيليجرام|تليجرام|تلجرام|telegram)\s*$"""
    )

    /** "اقرأ الحافظة ولخصها وأرسلها لأحمد" / "read the clipboard, summarize it and send it to Ahmed on telegram". */
    private fun parseClipboardShare(t: Prepared): ParsedCommand? {
        val key = t.key
        if (!key.contains("حافظه") && !key.contains("clipboard")) return null
        val match = clipSendAr.find(key) ?: clipSendEn.find(key) ?: return null
        val group = match.groups[1] ?: return null
        // key and light have the same length, so the indexes of the normalized text fit the original text.
        var person = t.light.substring(group.range.first, group.range.last + 1).trim()
        var app = "whatsapp"
        val suffix = messengerSuffix.find(TextNormalizer.key(person))
        if (suffix != null) {
            val appName = suffix.groups[1]?.value.orEmpty()
            app = if (appName.startsWith("ت") || appName.contains("telegram")) "telegram" else "whatsapp"
            person = person.substring(0, suffix.range.first).trim()
        }
        if (person.isEmpty()) return null
        val summarize = key.contains("لخص") || key.contains("summar")
        return ParsedCommand.ClipboardShare(person, app, summarize)
    }

''')

_replace_once(
    _parser_path,
    "        return parseMemory(t)",
    "        return parseRoutine(t)\n            ?: parseClipboardShare(t)\n            ?: parseMemory(t)"
)

# 1-د. IntentCommandHandler: when شاملة (الأمران يُنفَّذان من MainViewModel)
insert_before(
    _PKG + "/commands/IntentCommandHandler.kt",
    "            ParsedCommand.Unknown -> CommandResult.Failure(",
    '''            is ParsedCommand.RunRoutine -> CommandResult.Failure("يتم تنفيذ هذا الأمر من الشاشة الرئيسية.")
            is ParsedCommand.ClipboardShare -> CommandResult.Failure("يتم تنفيذ هذا الأمر من الشاشة الرئيسية.")
''')

# ------------------------------------------------------------------------------
# MainViewModel: السيناريوهات + جسر الحافظة
# ------------------------------------------------------------------------------
_vm_path = _PKG + "/viewmodel/MainViewModel.kt"

insert_before(
    _vm_path,
    "import com.example.voiceassistant.service.ProactiveMessages\n",
    "import com.example.voiceassistant.commands.commands.ContactResolver\n"
    "import com.example.voiceassistant.commands.startNewTask\n"
    "import com.example.voiceassistant.data.Routine\n"
    "import com.example.voiceassistant.data.RoutineStore\n"
)

# يُعالَج الأمران قبل أمر الكتابة على الشاشة
insert_before(
    _vm_path,
    "            if (parsed is ParsedCommand.TypeText) {",
    '''            if (parsed is ParsedCommand.RunRoutine) {
                runRoutine(parsed.name, lang, speak)
                return@launch
            }

            if (parsed is ParsedCommand.ClipboardShare) {
                handleClipboardShare(parsed, text, lang, speak)
                return@launch
            }

''')

insert_before(
    _vm_path,
    "    private fun process(text: String, speak: Boolean = true) {\n",
    r'''    // ---------------- Custom routines (macros) ----------------
    private val routineStore = RoutineStore(application)
    private val _routines = MutableStateFlow(routineStore.load())
    val routines: StateFlow<List<Routine>> = _routines.asStateFlow()

    @Volatile
    private var routineRunning = false

    // Pause between two steps, so the previous app / reply has time to settle.
    private val routineStepDelayMs = 1200L

    init {
        // A sentence equal to a routine name (or "شغل سيناريو <name>") runs that routine.
        // While a routine runs the lookup is off, so a step can never start the routine again.
        parser.routineLookup = { spoken ->
            if (routineRunning) null else RoutineStore.find(spoken, _routines.value)?.name
        }
    }

    /** Creates or edits a routine; [oldName] is the name before editing (null = a new one). */
    fun saveRoutine(oldName: String?, name: String, steps: List<String>) {
        val cleanName = name.trim()
        val cleanSteps = steps.map { it.trim() }.filter { it.isNotEmpty() }.take(RoutineStore.MAX_STEPS)
        if (cleanName.isEmpty() || cleanSteps.isEmpty()) return
        val newKey = RoutineStore.normalize(cleanName)
        val updated = _routines.value
            .filterNot { it.name == oldName || RoutineStore.normalize(it.name) == newKey }
            .plus(Routine(cleanName, cleanSteps))
        _routines.value = updated
        routineStore.save(updated)
    }

    fun deleteRoutine(name: String) {
        val updated = _routines.value.filterNot { it.name == name }
        _routines.value = updated
        routineStore.save(updated)
    }

    /** Runs a routine from the routines sheet (silent: the user is looking at the screen). */
    fun runRoutineFromUi(name: String) {
        if (routineRunning || _uiState.value.status == AssistantStatus.PROCESSING) return
        viewModelScope.launch { runRoutine(name, _uiState.value.language, speak = false) }
    }

    /** Waits until the current command finished (processing and speaking), at most [timeoutMs]. */
    private suspend fun waitUntilIdle(timeoutMs: Long = 60_000L) {
        val start = System.currentTimeMillis()
        while (System.currentTimeMillis() - start < timeoutMs) {
            val status = _uiState.value.status
            if (status != AssistantStatus.PROCESSING && status != AssistantStatus.SPEAKING) return
            delay(200)
        }
    }

    /** Runs the steps of a routine one after another, each one like a normal spoken / typed command. */
    private suspend fun runRoutine(name: String, lang: AppLanguage, speak: Boolean) {
        val routine = _routines.value.firstOrNull { it.name == name }
        if (routine == null) {
            reply(lang.tr("لم أجد السيناريو «$name».", "I couldn't find the routine \"$name\"."), lang, speak = speak)
            return
        }
        if (routineRunning) {
            reply(lang.tr("هناك سيناريو قيد التنفيذ.", "A routine is already running."), lang, speak = speak)
            return
        }
        routineRunning = true
        try {
            reply(
                lang.tr(
                    "بدأت السيناريو «${routine.name}» (${routine.steps.size} أوامر).",
                    "Starting the routine \"${routine.name}\" (${routine.steps.size} commands)."
                ),
                lang,
                speak = speak
            )
            waitUntilIdle()
            for (step in routine.steps) {
                repository.addUserMessage(step)
                process(step, speak)
                delay(300)
                waitUntilIdle()
                delay(routineStepDelayMs)
            }
            reply(
                lang.tr("انتهى السيناريو «${routine.name}».", "The routine \"${routine.name}\" is done."),
                lang,
                speak = speak
            )
        } finally {
            routineRunning = false
        }
    }

    // ---------------- Smart clipboard bridge ----------------

    /** The clipboard text (Android only lets the foreground app read it). */
    private fun readClipboardText(): String? = try {
        val context = getApplication<Application>()
        val clipboard = context.getSystemService(android.content.ClipboardManager::class.java)
        clipboard?.primaryClip
            ?.takeIf { it.itemCount > 0 }
            ?.getItemAt(0)
            ?.coerceToText(context)
            ?.toString()
    } catch (e: Exception) {
        null
    }

    private fun copyToClipboard(text: String) {
        val clipboard = getApplication<Application>().getSystemService(android.content.ClipboardManager::class.java)
        clipboard?.setPrimaryClip(android.content.ClipData.newPlainText("summary", text))
    }

    /** WhatsApp / Telegram want an international number without "+" or spaces. */
    private fun toInternationalDigits(raw: String): String {
        val cleaned = raw.replace(Regex("[\\s\\-().]"), "")
        if (cleaned.startsWith("+")) return cleaned.drop(1).filter { it.isDigit() }
        if (cleaned.startsWith("00")) return cleaned.drop(2).filter { it.isDigit() }
        val telephony = getApplication<Application>().getSystemService(android.telephony.TelephonyManager::class.java)
        val country = (telephony?.simCountryIso?.takeIf { it.isNotBlank() } ?: java.util.Locale.getDefault().country).uppercase()
        val e164 = try {
            android.telephony.PhoneNumberUtils.formatNumberToE164(cleaned, country)
        } catch (e: Exception) {
            null
        }
        return (e164 ?: cleaned).filter { it.isDigit() }
    }

    /** Opens the chat with [digits] in WhatsApp / Telegram. [prefill] is only used by WhatsApp. */
    private fun openMessengerChat(telegram: Boolean, digits: String, prefill: String?): Boolean {
        val uri = if (telegram) {
            android.net.Uri.parse("tg://resolve?phone=$digits")
        } else {
            val suffix = prefill?.let { "?text=" + android.net.Uri.encode(it) }.orEmpty()
            android.net.Uri.parse("https://wa.me/$digits$suffix")
        }
        val packages = if (telegram) {
            listOf("org.telegram.messenger", "org.telegram.messenger.web", "org.thunderdog.challegram")
        } else {
            listOf("com.whatsapp", "com.whatsapp.w4b")
        }
        for (pkg in packages) {
            try {
                getApplication<Application>().startNewTask(
                    android.content.Intent(android.content.Intent.ACTION_VIEW, uri).setPackage(pkg)
                )
                return true
            } catch (e: android.content.ActivityNotFoundException) {
                // try the next package
            }
        }
        return false
    }

    /**
     * "Read the clipboard, summarize it and send it to <person>":
     * clipboard -> AI summary -> open WhatsApp / Telegram -> performTypeText -> performSmartClick("Send").
     */
    private suspend fun handleClipboardShare(
        command: ParsedCommand.ClipboardShare,
        originalText: String,
        lang: AppLanguage,
        speak: Boolean
    ) {
        val app = getApplication<Application>()
        val telegram = command.app == "telegram"
        val appLabel = if (telegram) lang.tr("تيليجرام", "Telegram") else lang.tr("واتساب", "WhatsApp")

        // 1. The clipboard can only be read while this app is in the foreground.
        val clip = readClipboardText()?.trim().orEmpty()
        if (clip.isEmpty()) {
            reply(
                lang.tr(
                    "الحافظة فارغة أو لا أستطيع قراءتها الآن. انسخ النص وافتح التطبيق ثم أعد الأمر.",
                    "The clipboard is empty or I can't read it right now. Copy the text, open the app and try again."
                ),
                lang,
                speak = speak
            )
            return
        }

        // 2. Who is the message for? (a phone number, or a contact name)
        val direct = ContactResolver.asPhoneNumber(command.person)
        val number: String
        val label: String
        if (direct != null) {
            number = direct
            label = direct
        } else {
            if (!ContactResolver.hasPermission(app)) {
                pendingText = originalText
                pendingSpeak = speak
                _uiState.update { it.copy(pendingPermission = android.Manifest.permission.READ_CONTACTS) }
                reply(
                    lang.tr(
                        "أحتاج إذن جهات الاتصال للبحث عن الاسم.",
                        "I need contacts permission to look up that name."
                    ),
                    lang,
                    speak = speak
                )
                return
            }
            val match = withContext(Dispatchers.IO) { ContactResolver.find(app, command.person) }
            if (match == null) {
                reply(
                    lang.tr(
                        "لم أجد جهة اتصال باسم ${command.person}.",
                        "I couldn't find a contact named ${command.person}."
                    ),
                    lang,
                    speak = speak
                )
                return
            }
            number = match.number
            label = match.name
        }

        // 3. Summarize with the AI (or send the clipboard as it is).
        val message = if (command.summarize) {
            _uiState.update { it.copy(status = AssistantStatus.PROCESSING, partialText = "") }
            val body = clip.take(8000)
            val prompt = lang.tr(
                "لخّص النص التالي في بضعة أسطر قصيرة وواضحة وبنفس لغته ليُرسل كرسالة. اكتب الملخص فقط بدون مقدمات أو عناوين أو علامات اقتباس:\n\n$body",
                "Summarize the following text in a few short, clear lines in its own language, to be sent as a message. Output only the summary, with no intro, headings or quotes:\n\n$body"
            )
            when (val result = ai.ask(prompt, lang)) {
                is AiResult.Success -> result.text.trim()
                is AiResult.Error -> {
                    replyAiError(result.kind, result.detail, lang, speak)
                    return
                }
            }
        } else {
            clip
        }
        if (message.isEmpty()) {
            reply(lang.tr("الملخص فارغ.", "The summary is empty."), lang, speak = speak)
            return
        }
        repository.addAssistantMessage("📋 $message")

        // 4. Open the chat. Without the accessibility service WhatsApp gets the text in the link itself.
        val accessibilityOn = VoiceAccessibilityService.isRunning
        val digits = toInternationalDigits(number)
        val opened = openMessengerChat(telegram, digits, message.takeIf { !accessibilityOn && !telegram })
        if (!opened) {
            reply(
                lang.tr(
                    "تعذّر فتح $appLabel. تأكد أنه مثبّت على الهاتف.",
                    "Couldn't open $appLabel. Make sure it is installed."
                ),
                lang,
                speak = speak
            )
            return
        }
        if (!accessibilityOn) {
            if (telegram) copyToClipboard(message)
            reply(
                lang.tr(
                    if (telegram) "فتحت محادثة $label في تيليجرام ونسخت الملخص: الصقه واضغط إرسال، أو فعّل خدمة الوصول لأرسله تلقائياً."
                    else "فتحت محادثة $label في واتساب والملخص جاهز في خانة الكتابة: اضغط إرسال، أو فعّل خدمة الوصول لأرسله تلقائياً.",
                    if (telegram) "Opened $label in Telegram and copied the summary: paste it and press send, or enable the accessibility service to send it automatically."
                    else "Opened $label in WhatsApp with the summary ready: press send, or enable the accessibility service to send it automatically."
                ),
                lang,
                speak = speak
            )
            return
        }

        // 5. Type the summary into the other app and press its send button.
        delay(3500)
        var typed = false
        var attempt = 0
        while (!typed && attempt < 6) {
            typed = VoiceAccessibilityService.instance?.performTypeText(message) == true
            if (!typed) delay(900)
            attempt++
        }
        if (!typed) {
            reply(
                lang.tr(
                    "فتحت المحادثة لكن لم أجد خانة الكتابة. الملخص موجود في الدردشة.",
                    "I opened the chat but couldn't find the text box. The summary is in the chat."
                ),
                lang,
                speak = speak
            )
            return
        }
        delay(700)
        var sent = false
        attempt = 0
        while (!sent && attempt < 4) {
            val service = VoiceAccessibilityService.instance
            sent = service != null && (
                service.performSmartClick("Send") ||
                    service.performSmartClick("إرسال") ||
                    service.performSmartClick("ارسال")
                )
            if (!sent) delay(600)
            attempt++
        }
        reply(
            if (sent) {
                lang.tr("تم إرسال الملخص إلى $label.", "Sent the summary to $label.")
            } else {
                lang.tr(
                    "كتبت الملخص في محادثة $label لكن لم أجد زر الإرسال، اضغطه بنفسك.",
                    "I typed the summary in $label's chat but couldn't find the send button. Please press it."
                )
            },
            lang,
            speak = speak
        )
    }

''')

# ------------------------------------------------------------------------------
# MainScreen: زر السيناريوهات داخل قائمة الترس + عرض الـ BottomSheet
# ------------------------------------------------------------------------------
_screen_path = _PKG + "/ui/MainScreen.kt"

insert_before(
    _screen_path,
    "import androidx.compose.material.icons.filled.Psychology\n",
    "import androidx.compose.material.icons.filled.PlayArrow\n"
)
insert_before(
    _screen_path,
    "import com.example.voiceassistant.ui.components.LanguageToggle\n",
    "import com.example.voiceassistant.ui.components.RoutinesSheet\n"
)
insert_before(
    _screen_path,
    "    var showSettingsMenu by remember { mutableStateOf(false) }\n",
    "    var showRoutines by remember { mutableStateOf(false) }\n"
    "    val routines by viewModel.routines.collectAsStateWithLifecycle()\n"
)
insert_before(
    _screen_path,
    "        if (showAiSettings) {\n",
    '''        if (showRoutines) {
            RoutinesSheet(
                routines = routines,
                language = state.language,
                onSave = viewModel::saveRoutine,
                onDelete = viewModel::deleteRoutine,
                onRun = { name ->
                    showRoutines = false
                    viewModel.runRoutineFromUi(name)
                },
                onDismiss = { showRoutines = false }
            )
        }
''')
insert_before(
    _screen_path,
    "                                DropdownMenuItem(\n"
    "                                    text = { Text(state.language.tr(\"الذاكرة\", \"Memory\")) },\n",
    '''                                DropdownMenuItem(
                                    text = { Text(state.language.tr("السيناريوهات", "Routines")) },
                                    leadingIcon = { Icon(Icons.Filled.PlayArrow, contentDescription = null) },
                                    onClick = {
                                        showSettingsMenu = false
                                        showRoutines = true
                                    }
                                )
''')

# ------------------------------------------------------------------------------
# الميزة 3: الرؤية الحية (الكاميرا -> Gemini Vision عبر askWithFile -> نطق الرد تلقائياً)
# ------------------------------------------------------------------------------
_replace_once(
    _PKG + "/data/AttachmentData.kt",
    "    val uri: String? = null\n",
    "    val uri: String? = null,\n"
    "    /** True for a camera shot (Live Vision): the AI answer is read out loud automatically. */\n"
    "    val speakReply: Boolean = false\n"
)

_input_bar_path = _PKG + "/ui/components/ChatInputBar.kt"
_replace_once(_input_bar_path, '"حلل هذه الصورة واشرح ما فيها",', '"ماذا ترى في هذه الصورة؟",')
_replace_once(_input_bar_path, '"Analyze this image and explain what is in it"', '"What do you see in this picture?"')
_replace_once(
    _input_bar_path,
    'AttachmentData(file.name, "image/jpeg", bytes, null)',
    'AttachmentData(file.name, "image/jpeg", bytes, null, speakReply = true)'
)

_replace_once(
    _vm_path,
    '''            when (val result = ai.askWithFile(prompt, lang, attachment.mime, attachment.name, attachment.bytes)) {
                is AiResult.Success -> reply(result.text, lang, result.code, speak = false)
                is AiResult.Error -> replyAiError(result.kind, result.detail, lang, speak = false)
            }''',
    '''            // Live Vision: a camera shot is answered out loud, with short plain sentences.
            val askPrompt = if (attachment.speakReply) {
                prompt + lang.tr(
                    "\\n\\n(سيُنطق ردك بصوت عالٍ: أجب بجمل قصيرة وواضحة، وإن وُجد نص في الصورة فاقرأه، بدون رموز أو قوائم أو تنسيق.)",
                    "\\n\\n(Your answer will be read aloud: reply in short, clear sentences, read any text in the picture, and use no symbols, lists or formatting.)"
                )
            } else {
                prompt
            }
            when (val result = ai.askWithFile(askPrompt, lang, attachment.mime, attachment.name, attachment.bytes)) {
                is AiResult.Success -> reply(result.text, lang, result.code, speak = attachment.speakReply)
                is AiResult.Error -> replyAiError(result.kind, result.detail, lang, speak = attachment.speakReply)
            }'''
)

# واتساب / تيليجرام يجب أن يكونا مرئيين لـ startActivity على أندرويد 11+ (package visibility)
_replace_once(
    "app/src/main/AndroidManifest.xml",
    "    <queries>\n",
    '''    <queries>
        <package android:name="com.whatsapp" />
        <package android:name="com.whatsapp.w4b" />
        <package android:name="org.telegram.messenger" />
        <package android:name="org.telegram.messenger.web" />
'''
)

print(">> New features injected: Voice Routines, Smart Clipboard Bridge, Live Vision.")


# ==============================================================================
# performTypeText: خطة بديلة (Fallback) للتطبيقات التي ترفض ACTION_SET_TEXT (DeepSeek, WebView...)
# يُستبدل نص الدالة الحالية فقط، ولا يتغير أي شيء آخر.
# ==============================================================================
if "_replace_once" not in globals():
    def _replace_once(path, old, new):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        if text.count(old) != 1:
            raise RuntimeError("Expected exactly one match in {}: {!r} (found {})".format(path, old[:70], text.count(old)))
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace(old, new, 1))

_replace_once(
    "app/src/main/java/com/example/voiceassistant/service/VoiceAccessibilityService.kt",
    '''    fun performTypeText(text: String): Boolean {
        val root = rootInActiveWindow ?: return false
        
        // 1. البحث عن حقل الكتابة النشط
        val focused = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT)
        if (focused != null && (focused.isEditable || focused.className == "android.widget.EditText")) {
            val args = android.os.Bundle()
            args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
            if (focused.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)) return true
        }

        // 2. إذا لم يوجد نشط، نبحث في كل الشاشة عن EditText
        val allNodes = ArrayList<AccessibilityNodeInfo>()
        collectAllNodes(root, allNodes, 0)
        for (node in allNodes) {
            if (node.isEditable || node.className == "android.widget.EditText") {
                node.performAction(AccessibilityNodeInfo.ACTION_FOCUS)
                val args = android.os.Bundle()
                args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
                if (node.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)) return true
            }
        }
        return false
    }
''',
    r'''    fun performTypeText(text: String): Boolean {
        val root = rootInActiveWindow ?: return false

        val isField = { n: AccessibilityNodeInfo -> n.isEditable || n.className == "android.widget.EditText" }
        val setText = { n: AccessibilityNodeInfo ->
            val args = android.os.Bundle()
            args.putCharSequence(AccessibilityNodeInfo.ACTION_ARGUMENT_SET_TEXT_CHARSEQUENCE, text)
            n.performAction(AccessibilityNodeInfo.ACTION_SET_TEXT, args)
        }

        // 1. الطريقة الأساسية (ACTION_SET_TEXT): الحقل النشط أولاً، ثم أي حقل في الشاشة.
        val focused = root.findFocus(AccessibilityNodeInfo.FOCUS_INPUT)
        if (focused != null && isField(focused) && setText(focused)) return true

        val allNodes = ArrayList<AccessibilityNodeInfo>()
        collectAllNodes(root, allNodes, 0)
        val fields = allNodes.filter { isField(it) }
        for (node in fields) {
            node.performAction(AccessibilityNodeInfo.ACTION_FOCUS)
            if (setText(node)) return true
        }

        // 2. الخطة البديلة: نسخ النص إلى الحافظة، ثم تركيز الحقل ولصقه (يعمل مع DeepSeek وحقول الـ WebView).
        try {
            val clipboard = getSystemService(android.content.ClipboardManager::class.java)
            clipboard?.setPrimaryClip(android.content.ClipData.newPlainText("text", text))
        } catch (e: Exception) {
            // الحافظة غير متاحة: نكمل بالخطوة الأخيرة
        }
        // الحقل النشط، ثم كل حقل، ثم أي عنصر يعلن أنه يقبل اللصق (حقول الـ WebView قد لا تُعلن أنها EditText).
        val pasteCapable = allNodes.filter { n ->
            n.actionList.any { it.id == AccessibilityNodeInfo.ACTION_PASTE }
        }
        for (node in (listOfNotNull(focused) + fields + pasteCapable).distinct()) {
            node.performAction(AccessibilityNodeInfo.ACTION_FOCUS)
            // حقول الـ WebView تحتاج غالباً نقرة لتأخذ التركيز.
            if (!node.isFocused && isField(node)) node.performAction(AccessibilityNodeInfo.ACTION_CLICK)
            if (node.performAction(AccessibilityNodeInfo.ACTION_PASTE)) return true
        }

        // 3. آخر خيار: إدخال النص عبر لوحة المفاتيح كأنه كتابة (Android 13+، ويحتاج
        //    flagInputMethodEditor في إعدادات خدمة الوصول، وإلا يكون getInputMethod() فارغاً).
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            try {
                val connection = inputMethod?.currentInputConnection
                if (connection != null) {
                    connection.commitText(text, 1, null)
                    return true
                }
            } catch (e: Exception) {
                // لا توجد لوحة مفاتيح نشطة
            }
        }
        return false
    }
''')
print(">> performTypeText fallback (clipboard paste + input method) injected.")


# ==============================================================================
# وضع المترجم (Translator Mode): مفتاح في قائمة الترس.
# عند تفعيله: كلامك العربي يُترجم وينطق بالإنجليزية، والإنجليزي يُترجم وينطق بالعربية،
# و«اكتب مرحبا» تكتب hello على الشاشة (والعكس). عند إيقافه يعمل التطبيق كما كان.
# أوامر الهاتف (اتصال، منبه، فتح تطبيق، أرسل ...) تبقى تعمل كالمعتاد.
# ==============================================================================
if "_replace_once" not in globals():
    def _replace_once(path, old, new):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        if text.count(old) != 1:
            raise RuntimeError("Expected exactly one match in {}: {!r} (found {})".format(path, old[:70], text.count(old)))
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace(old, new, 1))

_tr_vm_path = "app/src/main/java/com/example/voiceassistant/viewmodel/MainViewModel.kt"
_tr_screen_path = "app/src/main/java/com/example/voiceassistant/ui/MainScreen.kt"

# الحالة (محفوظة في SharedPreferences) + دالة الترجمة
insert_before(
    _tr_vm_path,
    "    private fun process(text: String, speak: Boolean = true) {\n",
    r'''    // ---------------- Translator mode ----------------
    private val translatorPrefs = application.getSharedPreferences("voice_translator", android.content.Context.MODE_PRIVATE)
    private val _translatorMode = MutableStateFlow(translatorPrefs.getBoolean("enabled", false))

    /** True while the translator mode is on (the switch in the settings menu). */
    val translatorMode: StateFlow<Boolean> = _translatorMode.asStateFlow()

    fun setTranslatorMode(enabled: Boolean) {
        if (_translatorMode.value == enabled) return
        _translatorMode.value = enabled
        translatorPrefs.edit().putBoolean("enabled", enabled).apply()
        val lang = _uiState.value.language
        reply(
            if (enabled) {
                lang.tr(
                    "تم تفعيل وضع المترجم: ما تقوله بالعربية أرد به بالإنجليزية والعكس.",
                    "Translator mode is on: what you say in Arabic I answer in English, and vice versa."
                )
            } else {
                lang.tr("تم إيقاف وضع المترجم.", "Translator mode is off.")
            },
            lang,
            speak = false
        )
    }

    /**
     * Translator mode: Arabic -> English and English -> Arabic.
     * A normal sentence is translated and spoken; "اكتب مرحبا" types the translation on the screen.
     */
    private suspend fun handleTranslation(parsed: ParsedCommand, text: String, lang: AppLanguage, speak: Boolean) {
        val typing = parsed is ParsedCommand.TypeText
        val source = (parsed as? ParsedCommand.TypeText)?.prompt ?: text
        val target = if (AppLanguage.detect(source) == AppLanguage.ARABIC) AppLanguage.ENGLISH else AppLanguage.ARABIC
        val prompt = if (target == AppLanguage.ENGLISH) {
            "Translate the following Arabic text into natural English. Output ONLY the translation, with no quotes, notes or explanations:\n\n$source"
        } else {
            "ترجم النص الإنجليزي التالي إلى العربية الفصحى البسيطة. اكتب الترجمة فقط بدون علامات اقتباس أو ملاحظات أو شرح:\n\n$source"
        }

        _uiState.update { it.copy(status = AssistantStatus.PROCESSING, partialText = "") }
        when (val result = ai.ask(prompt, target)) {
            is AiResult.Success -> {
                val translated = result.text.trim().trim('"', '“', '”', '«', '»').trim()
                if (translated.isEmpty()) {
                    reply(lang.tr("تعذّرت الترجمة.", "Couldn't translate that."), lang, speak = speak)
                    return
                }
                if (!typing) {
                    // The translation is the answer: shown in the chat and spoken in the other language.
                    reply(translated, target, speak = speak)
                    return
                }
                repository.addAssistantMessage("🌐 $translated")
                // Step aside first, so the text goes into the other app and not into this chat.
                if (VoiceAccessibilityService.isRunning) {
                    _backgroundRequests.tryEmit(Unit)
                    delay(700)
                }
                val success = VoiceAccessibilityService.instance?.performTypeText(translated) == true
                reply(
                    if (success) {
                        lang.tr("كتبت الترجمة. قل «أرسل» للإرسال.", "Typed the translation. Say send to send.")
                    } else {
                        lang.tr(
                            "لم أجد حقل كتابة على الشاشة. تأكد من فتح التطبيق والضغط على المربع.",
                            "Couldn't find a text field."
                        )
                    },
                    lang,
                    speak = speak
                )
            }
            is AiResult.Error -> replyAiError(result.kind, result.detail, lang, speak)
        }
    }

''')

# في process(): في وضع المترجم يُترجم الكلام العادي وأمر «اكتب» (أوامر الهاتف الأخرى لا تتغير)
insert_before(
    _tr_vm_path,
    "            if (parsed is ParsedCommand.Unknown) {\n",
    '''            if (_translatorMode.value && (parsed is ParsedCommand.Unknown || parsed is ParsedCommand.TypeText)) {
                handleTranslation(parsed, text, lang, speak)
                return@launch
            }

''')

# قائمة الترس: مفتاح «المترجم»
insert_before(
    _tr_screen_path,
    "import androidx.compose.material.icons.filled.Psychology\n",
    "import androidx.compose.material.icons.filled.Translate\n"
)
insert_before(
    _tr_screen_path,
    "    val routines by viewModel.routines.collectAsStateWithLifecycle()\n",
    "    val translatorMode by viewModel.translatorMode.collectAsStateWithLifecycle()\n"
)
insert_before(
    _tr_screen_path,
    "                                DropdownMenuItem(\n"
    "                                    text = { Text(state.language.tr(\"السيناريوهات\", \"Routines\")) },\n",
    '''                                DropdownMenuItem(
                                    text = { Text(state.language.tr("المترجم", "Translator")) },
                                    leadingIcon = { Icon(Icons.Filled.Translate, contentDescription = null) },
                                    onClick = { viewModel.setTranslatorMode(!translatorMode) },
                                    trailingIcon = {
                                        Switch(
                                            checked = translatorMode,
                                            onCheckedChange = viewModel::setTranslatorMode
                                        )
                                    }
                                )
''')
print(">> Translator mode injected.")


# ==============================================================================
# الاستدعاء الصوتي الفوري: WakeWordService أسرع وأدق (عدّل هذا الملف فقط)
#  - المُتعرِّف لا يُهدم ويُنشأ في كل دورة بل يُعاد استخدامه، والفاصل بين الدورات 40ms بدل 150ms
#  - كل جلسة تقبل اللغتين معاً (العربية + الإنجليزية) بدل التناوب الأعمى
#  - مطابقة مرنة لعبارتي «يا مساعد» / «hey assistant» بكل صيغ الإملاء والكتابة الصوتية الشائعة
#  - فحص النتائج المؤقتة (UNSTABLE_TEXT) أيضاً، فيُستدعى المساعد فور نطق العبارة دون انتظار نهاية الجملة
# ==============================================================================
if "_replace_once" not in globals():
    def _replace_once(path, old, new):
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
        if text.count(old) != 1:
            raise RuntimeError("Expected exactly one match in {}: {!r} (found {})".format(path, old[:70], text.count(old)))
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text.replace(old, new, 1))

_ww_path = "app/src/main/java/com/example/voiceassistant/service/WakeWordService.kt"

# 1. فاصل أقصر بين دورات الاستماع
_replace_once(_ww_path, "private const val RESTART_DELAY_MS = 150L", "private const val RESTART_DELAY_MS = 40L")

# 2. مطابقة مرنة للعبارتين
_replace_once(
    _ww_path,
    '''        fun containsWakeWord(text: String): Boolean {
            val normalized = normalize(text)
            return WAKE_PHRASES.any { normalized.contains(normalize(it)) }
        }
''',
    r'''        // المُتعرِّف يكتب العبارة بصيغ مختلفة: «يامساعد»، «hey assistance»، أو العبارة بحروف الأخرى.
        private val wakeRegexes = listOf(
            Regex("(?:يا|ايا|هيا|هاي|ياا)\\s?(?:مساعد|مسعد|مساعيد|مساعت)"),
            Regex("(?:هاي|هي|هيي|هيه)\\s?(?:اسيستانت|اسيستنت|اسستنت|اسيستنس|اسيستانس|اسسيستنت)"),
            Regex("(?:hey|hay|hei|hi|hello|okay|ok)\\s?(?:assistant|assistance|assistent|asistant|assistants|assist ant|assis tent|assistence)"),
            Regex("\\bya+\\s?m[uo]+s[ae]+[iy]?[dt]\\b"),
            // Zevorix: spelling variants (zevorix, zevorex, zeforiks, ze vorix) and the Arabic spelling (زيفوريكس, زفوركس).
            Regex("\\bz[ei]+\\s?[vf]o+r[ie]*[xk]s?\\b"),
            Regex("ز[يا]?[فڤ]و?ر[ي]?[كق]س")
        )

        fun containsWakeWord(text: String): Boolean {
            val normalized = normalize(text)
            if (WAKE_PHRASES.any { normalized.contains(normalize(it)) }) return true
            val plain = normalized.replace(Regex("[^\\p{L}\\p{N}\\s]"), " ").replace(Regex("\\s+"), " ").trim()
            return wakeRegexes.any { it.containsMatchIn(plain) }
        }
''')

# 3. إعادة استخدام المُتعرِّف
_replace_once(
    _ww_path,
    "    private var useArabic = true\n",
    "    private var useArabic = true\n"
    "    private var recognizerOffline = false\n"
    "    private var recreateRecognizer = false\n"
)
_replace_once(
    _ww_path,
    "        override fun onError(error: Int) {\n            when (error) {",
    "        override fun onError(error: Int) {\n"
    "            // Only \"heard nothing\" errors keep the recognizer reusable; anything else builds a fresh one.\n"
    "            if (error != SpeechRecognizer.ERROR_NO_MATCH && error != SpeechRecognizer.ERROR_SPEECH_TIMEOUT) {\n"
    "                recreateRecognizer = true\n"
    "            }\n"
    "            when (error) {"
)
_replace_once(
    _ww_path,
    '''        destroyRecognizer()
        try {
            val offline = System.currentTimeMillis() < offlineUntil || !OfflineSpeech.isOnline(this)
            val r = OfflineSpeech.createRecognizer(this, offline)
            r.setRecognitionListener(listener)
            recognizer = r
''',
    '''        try {
            val offline = System.currentTimeMillis() < offlineUntil || !OfflineSpeech.isOnline(this)
            val existing = recognizer
            val r = if (existing != null && !recreateRecognizer && recognizerOffline == offline) {
                existing
            } else {
                destroyRecognizer()
                recreateRecognizer = false
                recognizerOffline = offline
                OfflineSpeech.createRecognizer(this, offline).also {
                    it.setRecognitionListener(listener)
                    recognizer = it
                }
            }
''')

# 4. جلسة تقبل اللغتين + جلسات أطول (أقل إعادة تشغيل)
_replace_once(
    _ww_path,
    "                putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 3)\n",
    "                putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 5)\n"
    "                // The other wake phrase is in the other language: let the recognizer accept both.\n"
    "                putExtra(\"android.speech.extra.EXTRA_ADDITIONAL_LANGUAGES\", arrayOf(if (useArabic) \"en-US\" else \"ar-SA\"))\n"
    "                putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_COMPLETE_SILENCE_LENGTH_MILLIS, 8000L)\n"
    "                putExtra(RecognizerIntent.EXTRA_SPEECH_INPUT_POSSIBLY_COMPLETE_SILENCE_LENGTH_MILLIS, 8000L)\n"
)

# 5. فحص النتائج المؤقتة غير المستقرة أيضاً (أسرع كشفاً)
_replace_once(
    _ww_path,
    "        val texts = bundle?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION) ?: return false\n",
    "        val texts = ArrayList<String>()\n"
    "        bundle?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)?.let { texts.addAll(it) }\n"
    "        bundle?.getStringArrayList(\"android.speech.extra.UNSTABLE_TEXT\")?.let { texts.addAll(it) }\n"
    "        if (texts.isEmpty()) return false\n"
)
print(">> Wake word: faster and more tolerant detection injected.")


# ==============================================================================
# الأصوات البشرية الحقيقية (ذكور وإناث) + زر «الصوت» في قائمة الإعدادات
#  - أصوات Gemini Text-to-Speech العصبية (Kore / Puck ...) بدل صوت الهاتف الآلي.
#  - شاشة اختيار الصوت: قسم نسائي وقسم رجالي مع زر تجربة لكل صوت، ومفتاح للرجوع إلى صوت الهاتف.
#  - الاحتياط التلقائي: بدون إنترنت أو بدون مفتاح Gemini أو عند فشل الطلب يُنطق الرد بصوت الهاتف المدمج.
#  - تعمل في المحادثة المباشرة وأيضاً في التذكيرات والتنبيهات (SpeakingService).
# ==============================================================================

# ------------------------------------------------------------------ 1. الأصوات + الإعدادات المحفوظة
write_file(_PKG + "/speech/VoiceSettings.kt", r'''package com.example.voiceassistant.speech

import android.content.Context
import android.content.SharedPreferences
import com.example.voiceassistant.data.AiProvider
import com.example.voiceassistant.data.AiSettings
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

enum class VoiceGender { FEMALE, MALE }

/** One of the human-sounding voices of Gemini text-to-speech ([id] is the name the API expects). */
data class HumanVoice(
    val id: String,
    val gender: VoiceGender,
    val nameAr: String,
    val nameEn: String,
    val styleAr: String,
    val styleEn: String
)

object HumanVoices {
    const val DEFAULT_ID = "Kore"

    val all: List<HumanVoice> = listOf(
        HumanVoice("Kore", VoiceGender.FEMALE, "كوري", "Kore", "واضحة وواثقة", "Clear and firm"),
        HumanVoice("Aoede", VoiceGender.FEMALE, "أويدي", "Aoede", "منسابة ومريحة", "Breezy"),
        HumanVoice("Leda", VoiceGender.FEMALE, "ليدا", "Leda", "شابة ونشيطة", "Youthful"),
        HumanVoice("Zephyr", VoiceGender.FEMALE, "زيفير", "Zephyr", "مشرقة", "Bright"),
        HumanVoice("Sulafat", VoiceGender.FEMALE, "سلافة", "Sulafat", "دافئة", "Warm"),
        HumanVoice("Charon", VoiceGender.MALE, "كارون", "Charon", "رصينة ومعلِّمة", "Informative"),
        HumanVoice("Puck", VoiceGender.MALE, "باك", "Puck", "مرحة وحيوية", "Upbeat"),
        HumanVoice("Orus", VoiceGender.MALE, "أورس", "Orus", "قوية وحازمة", "Firm"),
        HumanVoice("Fenrir", VoiceGender.MALE, "فينرير", "Fenrir", "متحمسة", "Excitable"),
        HumanVoice("Achird", VoiceGender.MALE, "أكيرد", "Achird", "ودودة", "Friendly")
    )

    val females: List<HumanVoice> = all.filter { it.gender == VoiceGender.FEMALE }
    val males: List<HumanVoice> = all.filter { it.gender == VoiceGender.MALE }

    fun find(id: String?): HumanVoice? = all.firstOrNull { it.id == id }
}

data class VoiceSettingsState(
    /** True = Gemini human voices; false = the phone's built-in text-to-speech voice. */
    val humanEnabled: Boolean = true,
    val voiceId: String = HumanVoices.DEFAULT_ID
)

/** The chosen voice, saved in SharedPreferences so it survives closing the app. */
object VoiceSettings {
    private const val PREFS = "voice_settings"
    private const val KEY_HUMAN = "human_enabled"
    private const val KEY_VOICE = "voice_id"

    @Volatile
    private var prefs: SharedPreferences? = null

    private val _state = MutableStateFlow(VoiceSettingsState())
    val state: StateFlow<VoiceSettingsState> = _state.asStateFlow()

    fun init(context: Context) {
        if (prefs != null) return
        synchronized(this) {
            if (prefs != null) return
            val p = context.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            prefs = p
            _state.value = VoiceSettingsState(
                humanEnabled = p.getBoolean(KEY_HUMAN, true),
                voiceId = HumanVoices.find(p.getString(KEY_VOICE, null))?.id ?: HumanVoices.DEFAULT_ID
            )
        }
    }

    fun humanEnabled(): Boolean = _state.value.humanEnabled

    fun voiceId(): String = _state.value.voiceId

    fun setHumanEnabled(enabled: Boolean) {
        prefs?.edit()?.putBoolean(KEY_HUMAN, enabled)?.apply()
        _state.value = _state.value.copy(humanEnabled = enabled)
    }

    fun setVoice(id: String) {
        val voice = HumanVoices.find(id) ?: return
        prefs?.edit()?.putString(KEY_VOICE, voice.id)?.apply()
        _state.value = _state.value.copy(voiceId = voice.id)
    }

    /** Human voices need the switch on, a Gemini key and internet; otherwise the phone's own voice speaks. */
    fun canUseHuman(context: Context): Boolean =
        _state.value.humanEnabled &&
            AiSettings.apiKey(AiProvider.GEMINI).isNotBlank() &&
            OfflineSpeech.isOnline(context)
}
''')

# ------------------------------------------------------------------ 2. مشغّل الأصوات البشرية (Gemini TTS -> PCM -> AudioTrack)
write_file(_PKG + "/speech/HumanVoicePlayer.kt", r'''package com.example.voiceassistant.speech

import android.media.AudioAttributes
import android.media.AudioFormat
import android.media.AudioTrack
import android.os.Handler
import android.os.Looper
import android.util.Base64
import android.util.LruCache
import com.example.voiceassistant.data.AiProvider
import com.example.voiceassistant.data.AiSettings
import java.util.concurrent.LinkedBlockingQueue
import java.util.concurrent.TimeUnit
import okhttp3.Call
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import org.json.JSONArray
import org.json.JSONObject

/**
 * Speaks with Gemini's neural text-to-speech voices (natural male and female human voices).
 *
 * The reply is cleaned (no code / links / emoji), cut into short pieces and each piece is turned into audio
 * (16-bit PCM, 24 kHz) by the Gemini API while the previous piece is already playing, so speech starts after
 * the first short sentence. Nothing here touches the phone's own TextToSpeech engine.
 *
 * Callbacks arrive on the main thread and are NOT sent when the speech was cancelled by [stop] or by a newer [speak].
 */
class HumanVoicePlayer {

    private class Reply(val pcm: ByteArray?, val status: Int)

    private val main = Handler(Looper.getMainLooper())
    private val http = OkHttpClient.Builder()
        .connectTimeout(12, TimeUnit.SECONDS)
        .writeTimeout(15, TimeUnit.SECONDS)
        .readTimeout(45, TimeUnit.SECONDS)
        .build()
    private val lock = Any()
    private val cache = object : LruCache<String, ByteArray>(CACHE_BYTES) {
        override fun sizeOf(key: String, value: ByteArray): Int = value.size
    }

    @Volatile
    private var generation = 0

    @Volatile
    private var currentTrack: AudioTrack? = null

    @Volatile
    private var currentCall: Call? = null

    /** Set when the newer TTS endpoint doesn't exist for this key: the older generateContent endpoint is used. */
    @Volatile
    private var legacyOnly = false

    /**
     * @param onStarted the first audio is playing.
     * @param onFinished everything was said (""), or the part of the text that could NOT be spoken
     *   (network / quota problem) so the caller can say it with another voice.
     */
    fun speak(
        text: String,
        voiceId: String,
        alarm: Boolean,
        onStarted: () -> Unit,
        onFinished: (String) -> Unit
    ) {
        val chunks = splitForSpeech(prepareText(text))
        if (chunks.isEmpty()) {
            main.post { onFinished("") }
            return
        }
        val gen = synchronized(lock) {
            generation += 1
            abortCurrent()
            generation
        }
        Thread { playAll(gen, chunks, voiceId, alarm, onStarted, onFinished) }
            .apply { isDaemon = true }
            .start()
    }

    fun stop() {
        synchronized(lock) {
            generation += 1
            abortCurrent()
        }
    }

    private fun abortCurrent() {
        currentCall?.cancel()
        currentCall = null
        val track = currentTrack
        if (track != null) {
            try {
                track.pause()
                track.flush()
            } catch (e: IllegalStateException) {
                // already released
            }
        }
    }

    // ------------------------------------------------------------------ playback

    private fun playAll(
        gen: Int,
        chunks: List<String>,
        voiceId: String,
        alarm: Boolean,
        onStarted: () -> Unit,
        onFinished: (String) -> Unit
    ) {
        val queue = LinkedBlockingQueue<ByteArray>()
        Thread { fetchAll(gen, chunks, voiceId, queue) }.apply { isDaemon = true }.start()

        var track: AudioTrack? = null
        var frames = 0L
        var played = 0
        var failed = false
        try {
            while (gen == generation) {
                val item = queue.poll(60, TimeUnit.SECONDS)
                if (item == null || item === FAILED) {
                    failed = true
                    break
                }
                if (item === DONE) break
                var t = track
                if (t == null) {
                    t = createTrack(alarm)
                    track = t
                    currentTrack = t
                    t.play()
                    main.post { if (gen == generation) onStarted() }
                }
                val written = writePcm(t, item, gen)
                frames += written
                if (written < item.size / 2) {
                    if (gen == generation) failed = true
                    break
                }
                played += 1
            }
            val playing = track
            if (playing != null && gen == generation) drain(playing, frames, gen)
        } catch (e: Exception) {
            failed = true
        } finally {
            val t = track
            if (t != null) {
                try {
                    t.stop()
                } catch (e: IllegalStateException) {
                    // already stopped
                }
                t.release()
                if (currentTrack === t) currentTrack = null
            }
        }
        if (gen != generation) return
        val remaining = if (failed) chunks.drop(played).joinToString(" ") else ""
        main.post { if (gen == generation) onFinished(remaining) }
    }

    private fun fetchAll(gen: Int, chunks: List<String>, voiceId: String, queue: LinkedBlockingQueue<ByteArray>) {
        for (chunk in chunks) {
            if (gen != generation) return
            val pcm = synthesize(chunk, voiceId, gen)
            if (gen != generation) return
            if (pcm == null) {
                queue.put(FAILED)
                return
            }
            queue.put(pcm)
        }
        queue.put(DONE)
    }

    private fun createTrack(alarm: Boolean): AudioTrack {
        val minBuffer = AudioTrack.getMinBufferSize(
            SAMPLE_RATE,
            AudioFormat.CHANNEL_OUT_MONO,
            AudioFormat.ENCODING_PCM_16BIT
        )
        return AudioTrack.Builder()
            .setAudioAttributes(
                AudioAttributes.Builder()
                    .setUsage(if (alarm) AudioAttributes.USAGE_ALARM else AudioAttributes.USAGE_ASSISTANT)
                    .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                    .build()
            )
            .setAudioFormat(
                AudioFormat.Builder()
                    .setEncoding(AudioFormat.ENCODING_PCM_16BIT)
                    .setSampleRate(SAMPLE_RATE)
                    .setChannelMask(AudioFormat.CHANNEL_OUT_MONO)
                    .build()
            )
            .setBufferSizeInBytes(maxOf(minBuffer, SAMPLE_RATE * 2))
            .setTransferMode(AudioTrack.MODE_STREAM)
            .build()
    }

    /** Writes in small slices so a [stop] is noticed within about 100 ms. Returns the frames written. */
    private fun writePcm(track: AudioTrack, pcm: ByteArray, gen: Int): Long {
        var offset = 0
        while (offset < pcm.size && gen == generation) {
            val length = minOf(WRITE_SLICE, pcm.size - offset)
            val written = track.write(pcm, offset, length)
            if (written <= 0) break
            offset += written
        }
        return (offset / 2).toLong()
    }

    /** Waits until everything written has really been played (so the microphone doesn't hear the end of the speech). */
    private fun drain(track: AudioTrack, frames: Long, gen: Int) {
        val deadline = System.currentTimeMillis() + frames * 1000L / SAMPLE_RATE + 2000L
        while (gen == generation && System.currentTimeMillis() < deadline) {
            val head = try {
                track.playbackHeadPosition.toLong() and 0xFFFFFFFFL
            } catch (e: IllegalStateException) {
                return
            }
            if (head >= frames) return
            Thread.sleep(30)
        }
    }

    // ------------------------------------------------------------------ Gemini text-to-speech

    private fun synthesize(text: String, voiceId: String, gen: Int): ByteArray? {
        val cacheKey = voiceId + "|" + text
        val cached = cache.get(cacheKey)
        if (cached != null) return cached
        val key = AiSettings.apiKey(AiProvider.GEMINI)
        if (key.isBlank()) return null

        var pcm: ByteArray? = null
        var status = 0
        if (!legacyOnly) {
            val reply = requestInteractions(text, voiceId, key)
            pcm = reply.pcm
            status = reply.status
            if (pcm == null && status == 404) legacyOnly = true
        }
        // Another request shape only when the first one isn't understood (not for network / quota errors).
        if (pcm == null && gen == generation && (legacyOnly || status == 200 || status == 400 || status == 404)) {
            pcm = requestLegacy(text, voiceId, key).pcm
        }
        if (pcm != null) cache.put(cacheKey, pcm)
        return pcm
    }

    /** Gemini 3.8 TTS (Interactions API). Raw 24 kHz 16-bit PCM is requested so no WAV header has to be removed. */
    private fun requestInteractions(text: String, voiceId: String, key: String): Reply {
        val body = JSONObject()
            .put("model", MODEL_NEW)
            .put(
                "input",
                JSONArray().put(
                    JSONObject()
                        .put("type", "user_input")
                        .put(
                            "content",
                            JSONArray().put(JSONObject().put("type", "text").put("text", text))
                        )
                )
            )
            .put(
                "response_format",
                JSONObject()
                    .put("type", "audio")
                    .put("mime_type", "audio/l16")
                    .put("sample_rate", SAMPLE_RATE)
            )
            .put(
                "generation_config",
                JSONObject().put("speech_config", JSONArray().put(JSONObject().put("voice", voiceId)))
            )
        val request = Request.Builder()
            .url(BASE_URL + "/interactions")
            .header("x-goog-api-key", key)
            .post(body.toString().toRequestBody(JSON_TYPE))
            .build()
        return execute(request) { json -> parseInteraction(json) }
    }

    /** Older generateContent TTS endpoint (fallback). */
    private fun requestLegacy(text: String, voiceId: String, key: String): Reply {
        val voiceConfig = JSONObject()
            .put("prebuiltVoiceConfig", JSONObject().put("voiceName", voiceId))
        val body = JSONObject()
            .put(
                "contents",
                JSONArray().put(
                    JSONObject().put("parts", JSONArray().put(JSONObject().put("text", text)))
                )
            )
            .put(
                "generationConfig",
                JSONObject()
                    .put("responseModalities", JSONArray().put("AUDIO"))
                    .put("speechConfig", JSONObject().put("voiceConfig", voiceConfig))
            )
        val request = Request.Builder()
            .url(BASE_URL + "/models/" + MODEL_LEGACY + ":generateContent")
            .header("x-goog-api-key", key)
            .post(body.toString().toRequestBody(JSON_TYPE))
            .build()
        return execute(request) { json -> parseLegacy(json) }
    }

    private fun execute(request: Request, parse: (JSONObject) -> ByteArray?): Reply {
        val call = http.newCall(request)
        currentCall = call
        val reply: Reply = try {
            call.execute().use { response ->
                val raw = response.body?.string().orEmpty()
                if (response.isSuccessful) {
                    val pcm = try {
                        parse(JSONObject(raw))
                    } catch (e: Exception) {
                        null
                    }
                    Reply(pcm, 200)
                } else {
                    Reply(null, response.code)
                }
            }
        } catch (e: Exception) {
            Reply(null, 0)
        } finally {
            if (currentCall === call) currentCall = null
        }
        return reply
    }

    private fun parseInteraction(json: JSONObject): ByteArray? {
        val steps = json.optJSONArray("steps") ?: return null
        var data = ""
        for (i in 0 until steps.length()) {
            val step = steps.optJSONObject(i) ?: continue
            if (step.optString("type") != "model_output") continue
            val content = step.optJSONArray("content") ?: continue
            for (j in 0 until content.length()) {
                val part = content.optJSONObject(j) ?: continue
                if (part.optString("type") == "audio" && part.optString("data").isNotEmpty()) {
                    data = part.optString("data")
                }
            }
        }
        return if (data.isEmpty()) null else toPcm(data)
    }

    private fun parseLegacy(json: JSONObject): ByteArray? {
        val candidates = json.optJSONArray("candidates") ?: return null
        val content = candidates.optJSONObject(0)?.optJSONObject("content") ?: return null
        val parts = content.optJSONArray("parts") ?: return null
        for (i in 0 until parts.length()) {
            val inline = parts.optJSONObject(i)?.optJSONObject("inlineData") ?: continue
            val data = inline.optString("data")
            if (data.isNotEmpty()) return toPcm(data)
        }
        return null
    }

    /** Base64 -> raw PCM. If the server sent a WAV file anyway, its header is skipped. */
    private fun toPcm(base64: String): ByteArray? {
        var bytes = try {
            Base64.decode(base64, Base64.DEFAULT)
        } catch (e: IllegalArgumentException) {
            return null
        }
        val isWav = bytes.size > 44 &&
            bytes[0] == 'R'.code.toByte() && bytes[1] == 'I'.code.toByte() &&
            bytes[2] == 'F'.code.toByte() && bytes[3] == 'F'.code.toByte()
        if (isWav) {
            var position = 12
            var start = 44
            while (position + 8 <= bytes.size) {
                val id = String(bytes, position, 4, Charsets.US_ASCII)
                val size = (bytes[position + 4].toInt() and 0xFF) or
                    ((bytes[position + 5].toInt() and 0xFF) shl 8) or
                    ((bytes[position + 6].toInt() and 0xFF) shl 16) or
                    ((bytes[position + 7].toInt() and 0xFF) shl 24)
                if (id == "data") {
                    start = position + 8
                    break
                }
                if (size < 0) break
                position += 8 + size + (size and 1)
            }
            bytes = bytes.copyOfRange(minOf(start, bytes.size), bytes.size)
        }
        if (bytes.size % 2 != 0) bytes = bytes.copyOf(bytes.size - 1)
        return if (bytes.isEmpty()) null else bytes
    }

    // ------------------------------------------------------------------ text preparation

    /** Removes what shouldn't be read aloud: code blocks, links, markdown signs and emoji. */
    private fun prepareText(raw: String): String {
        var t = CODE_BLOCK.replace(raw, " ")
        t = INLINE_CODE.replace(t) { it.groupValues[1] }
        t = URL_PATTERN.replace(t, " ")
        t = MARKUP.replace(t, " ")
        t = SYMBOLS.replace(t, " ")
        t = SPACES.replace(t, " ")
        t = NEWLINES.replace(t, "\n")
        t = t.trim()
        if (t.length > MAX_CHARS) {
            val cut = t.lastIndexOfAny(charArrayOf('.', '!', '?', '؟', '\n'), MAX_CHARS)
            t = if (cut > MAX_CHARS / 2) t.substring(0, cut + 1) else t.substring(0, MAX_CHARS)
        }
        return t
    }

    /** A short first piece (speech starts quickly) and longer pieces after it, always cut at sentence ends. */
    private fun splitForSpeech(text: String): List<String> {
        val chunks = ArrayList<String>()
        val current = StringBuilder()
        var limit = FIRST_CHUNK_CHARS

        fun close() {
            if (current.isNotEmpty()) {
                chunks.add(current.toString())
                current.setLength(0)
                limit = NEXT_CHUNK_CHARS
            }
        }

        fun add(piece: String) {
            if (piece.isBlank()) return
            if (current.isNotEmpty() && current.length + 1 + piece.length > limit) close()
            if (current.isNotEmpty()) current.append(' ')
            current.append(piece)
        }

        for (line in text.split('\n')) {
            for (sentence in SENTENCE_END.split(line)) {
                var rest = sentence.trim()
                while (rest.length > limit) {
                    val cut = cutPoint(rest, limit)
                    add(rest.substring(0, cut).trim())
                    rest = rest.substring(cut).trim()
                }
                add(rest)
            }
        }
        close()
        return chunks
    }

    private fun cutPoint(text: String, max: Int): Int {
        val window = text.substring(0, max)
        val index = maxOf(window.lastIndexOf('،'), window.lastIndexOf(','), window.lastIndexOf(' '))
        return if (index > max / 3) index + 1 else max
    }

    private companion object {
        const val BASE_URL = "https://generativelanguage.googleapis.com/v1beta"
        const val MODEL_NEW = "gemini-3.8-flash-lite-tts"
        const val MODEL_LEGACY = "gemini-3.1-flash-tts-preview"
        const val SAMPLE_RATE = 24000
        const val WRITE_SLICE = 4800
        const val CACHE_BYTES = 6 * 1024 * 1024
        const val MAX_CHARS = 1500
        const val FIRST_CHUNK_CHARS = 110
        const val NEXT_CHUNK_CHARS = 420

        val DONE = ByteArray(0)
        val FAILED = ByteArray(0)
        val JSON_TYPE = "application/json; charset=utf-8".toMediaType()

        val CODE_BLOCK = Regex("```[\\s\\S]*?```")
        val INLINE_CODE = Regex("`([^`]*)`")
        val URL_PATTERN = Regex("https?://\\S+")
        val MARKUP = Regex("[*_#>~|=^\\[\\]{}\\\\]+")
        val SYMBOLS = Regex("[\\p{So}\\p{Cs}\\p{Cn}]")
        val SPACES = Regex("[ \\t\\u00A0]+")
        val NEWLINES = Regex("\\s*\\n\\s*")
        val SENTENCE_END = Regex("(?<=[.!?؟…。])\\s+")
    }
}
''')

# ------------------------------------------------------------------ 3. TextToSpeechManager: الصوت البشري أولاً ثم صوت الهاتف احتياطاً
write_file(_PKG + "/speech/TextToSpeechManager.kt", r'''package com.example.voiceassistant.speech

import android.content.Context
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import java.util.Locale

/**
 * Speaks the assistant's replies.
 * The chosen human voice (Gemini) is used when it is available (switch on + Gemini key + internet); otherwise,
 * or when it fails half way, the phone's own TextToSpeech engine says the text.
 */
class TextToSpeechManager(context: Context) {

    /** Called (possibly from a background thread) when speaking starts or stops. */
    var onSpeakingChanged: ((Boolean) -> Unit)? = null

    private val appContext = context.applicationContext
    private val human = HumanVoicePlayer()

    @Volatile
    private var humanActive = false

    @Volatile
    private var ready = false
    @Volatile
    private var pendingSpeech: Pair<String, Locale>? = null
    private var counter = 0
    private var engine: TextToSpeech? = null

    private val progressListener = object : UtteranceProgressListener() {
        override fun onStart(utteranceId: String?) {
            onSpeakingChanged?.invoke(true)
        }

        override fun onDone(utteranceId: String?) {
            onSpeakingChanged?.invoke(false)
        }

        @Deprecated("Deprecated in Java")
        override fun onError(utteranceId: String?) {
            onSpeakingChanged?.invoke(false)
        }

        override fun onError(utteranceId: String?, errorCode: Int) {
            onSpeakingChanged?.invoke(false)
        }

        override fun onStop(utteranceId: String?, interrupted: Boolean) {
            onSpeakingChanged?.invoke(false)
        }
    }

    init {
        VoiceSettings.init(appContext)
        engine = TextToSpeech(appContext) { status ->
            if (status == TextToSpeech.SUCCESS) {
                engine?.setOnUtteranceProgressListener(progressListener)
                ready = true
                // A sentence requested before the engine was ready (e.g. the welcome greeting).
                pendingSpeech?.let { p ->
                    pendingSpeech = null
                    speakSystem(p.first, p.second)
                }
            }
        }
    }

    /** @return true if speaking was started, false if nothing could be spoken (the caller then restarts the microphone). */
    fun speak(text: String, locale: Locale): Boolean {
        if (text.isBlank()) return false
        if (VoiceSettings.canUseHuman(appContext)) {
            speakHuman(text, locale)
            return true
        }
        return speakSystem(text, locale)
    }

    /** Speaks now if possible, otherwise as soon as the phone's engine becomes ready. */
    fun speakWhenReady(text: String, locale: Locale) {
        if (text.isNotBlank() && VoiceSettings.canUseHuman(appContext)) {
            speakHuman(text, locale)
        } else if (ready) {
            speakSystem(text, locale)
        } else {
            pendingSpeech = text to locale
        }
    }

    fun stop() {
        pendingSpeech = null
        if (humanActive) {
            humanActive = false
            human.stop()
            onSpeakingChanged?.invoke(false)
        }
        engine?.stop()
    }

    fun shutdown() {
        human.stop()
        humanActive = false
        engine?.stop()
        engine?.shutdown()
        engine = null
        ready = false
    }

    private fun speakHuman(text: String, locale: Locale) {
        humanActive = true
        human.speak(
            text = text,
            voiceId = VoiceSettings.voiceId(),
            alarm = false,
            onStarted = { onSpeakingChanged?.invoke(true) },
            onFinished = { remaining ->
                humanActive = false
                // What the human voice could not say (no connection / quota) is said by the phone's voice.
                val continued = remaining.isNotBlank() && speakSystem(remaining, locale)
                if (!continued) onSpeakingChanged?.invoke(false)
            }
        )
    }

    /** The phone's own voice. @return true if speaking was started. */
    private fun speakSystem(text: String, locale: Locale): Boolean {
        val tts = engine
        if (!ready || tts == null || text.isBlank()) return false
        val result = tts.setLanguage(locale)
        if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
            return false
        }
        // TextToSpeech rejects input longer than its maximum (usually 4000 characters).
        val safeText = text.take(TextToSpeech.getMaxSpeechInputLength() - 1)
        counter += 1
        return tts.speak(safeText, TextToSpeech.QUEUE_FLUSH, null, "va-" + counter) == TextToSpeech.SUCCESS
    }
}
''')

# ------------------------------------------------------------------ 4. SpeakingService: التذكيرات والتنبيهات بالصوت البشري أيضاً
write_file(_PKG + "/service/SpeakingService.kt", r'''package com.example.voiceassistant.service

import android.app.Notification
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.ServiceInfo
import android.media.AudioAttributes
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.PowerManager
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import androidx.core.content.ContextCompat
import com.example.voiceassistant.speech.HumanVoicePlayer
import com.example.voiceassistant.speech.VoiceSettings
import com.example.voiceassistant.viewmodel.AppLanguage
import java.util.ArrayDeque
import java.util.Locale

/**
 * Foreground service that speaks a sentence while the app is closed (reminders and proactive check-ins).
 * It uses the chosen human voice when available and the phone's TextToSpeech otherwise.
 * It stops itself when everything has been said.
 */
class SpeakingService : Service() {

    companion object {
        const val EXTRA_TEXT = "speak_text"
        const val EXTRA_ALARM = "speak_alarm"
        private const val FOREGROUND_ID = 7001
        private const val MAX_LIFETIME_MS = 60_000L

        /** @throws IllegalStateException on Android 12+ when the system forbids starting it right now. */
        fun start(context: Context, text: String, alarm: Boolean) {
            val intent = Intent(context, SpeakingService::class.java)
                .putExtra(EXTRA_TEXT, text)
                .putExtra(EXTRA_ALARM, alarm)
            ContextCompat.startForegroundService(context, intent)
        }
    }

    private val mainHandler = Handler(Looper.getMainLooper())
    // Said by the phone's own voice.
    private val pending = ArrayDeque<Pair<String, Boolean>>()
    // Said by the human (Gemini) voice, one after the other.
    private val humanQueue = ArrayDeque<Pair<String, Boolean>>()
    private var human: HumanVoicePlayer? = null
    private var humanBusy = false
    private var engine: TextToSpeech? = null
    private var ready = false
    private var active = 0
    private var wakeLock: PowerManager.WakeLock? = null
    private var counter = 0

    private val listener = object : UtteranceProgressListener() {
        override fun onStart(utteranceId: String?) = Unit

        override fun onDone(utteranceId: String?) = utteranceFinished()

        @Deprecated("Deprecated in Java")
        override fun onError(utteranceId: String?) = utteranceFinished()

        override fun onError(utteranceId: String?, errorCode: Int) = utteranceFinished()

        override fun onStop(utteranceId: String?, interrupted: Boolean) = utteranceFinished()
    }

    override fun onCreate() {
        super.onCreate()
        VoiceSettings.init(applicationContext)
        NotificationHelper.createChannels(this)
        acquireWakeLock()
        engine = TextToSpeech(applicationContext) { status ->
            mainHandler.post {
                if (status == TextToSpeech.SUCCESS) {
                    engine?.setOnUtteranceProgressListener(listener)
                    ready = true
                    flush()
                } else if (!humanBusy && humanQueue.isEmpty()) {
                    finish()
                }
            }
        }
        // Safety net: never keep the foreground service alive forever.
        mainHandler.postDelayed({ finish() }, MAX_LIFETIME_MS)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val text = intent?.getStringExtra(EXTRA_TEXT).orEmpty()
        val alarm = intent?.getBooleanExtra(EXTRA_ALARM, false) ?: false

        // Must be called within a few seconds of startForegroundService().
        try {
            val type = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PLAYBACK
            } else {
                0
            }
            ServiceCompat.startForeground(this, FOREGROUND_ID, buildNotification(text), type)
        } catch (e: Exception) {
            stopSelf()
            return START_NOT_STICKY
        }

        if (text.isNotBlank()) {
            if (VoiceSettings.canUseHuman(applicationContext)) {
                humanQueue.add(text to alarm)
            } else {
                pending.add(text to alarm)
            }
            active++
        }
        if (ready) flush()
        drainHuman()
        if (active <= 0 && ready) finish()
        return START_NOT_STICKY
    }

    private fun flush() {
        while (pending.isNotEmpty()) {
            val (text, alarm) = pending.poll() ?: break
            speakWithEngine(text, alarm)
        }
    }

    /** The phone's own voice. Always ends in exactly one [utteranceFinished] for this text. */
    private fun speakWithEngine(text: String, alarm: Boolean) {
        val tts = engine
        if (tts == null) {
            utteranceFinished()
            return
        }
        val lang = AppLanguage.detect(text)
        val result = tts.setLanguage(lang.locale)
        if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
            tts.setLanguage(Locale.getDefault())
        }
        tts.setAudioAttributes(
            AudioAttributes.Builder()
                .setUsage(if (alarm) AudioAttributes.USAGE_ALARM else AudioAttributes.USAGE_ASSISTANT)
                .setContentType(AudioAttributes.CONTENT_TYPE_SPEECH)
                .build()
        )
        counter++
        val safe = text.take(TextToSpeech.getMaxSpeechInputLength() - 1)
        val code = tts.speak(safe, TextToSpeech.QUEUE_ADD, null, "va-svc-" + counter)
        if (code != TextToSpeech.SUCCESS) utteranceFinished()
    }

    /** Human voice: one text at a time; whatever it could not say falls back to the phone's voice. */
    private fun drainHuman() {
        if (humanBusy) return
        val next = humanQueue.poll() ?: return
        humanBusy = true
        val player = human ?: HumanVoicePlayer().also { human = it }
        player.speak(
            text = next.first,
            voiceId = VoiceSettings.voiceId(),
            alarm = next.second,
            onStarted = {},
            onFinished = { remaining ->
                humanBusy = false
                if (remaining.isNotBlank() && ready) {
                    speakWithEngine(remaining, next.second)
                } else {
                    utteranceFinished()
                }
                drainHuman()
            }
        )
    }

    private fun utteranceFinished() {
        mainHandler.post {
            active--
            if (active <= 0 && pending.isEmpty() && humanQueue.isEmpty() && !humanBusy) finish()
        }
    }

    private fun finish() {
        ServiceCompat.stopForeground(this, ServiceCompat.STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    private fun buildNotification(text: String): Notification {
        val lang = AppLanguage.detect(text)
        return NotificationCompat.Builder(this, NotificationHelper.CHANNEL_SPEAKING)
            .setSmallIcon(android.R.drawable.ic_btn_speak_now)
            .setContentTitle(lang.tr("Zevorix AI", "Zevorix AI"))
            .setContentText(text.ifBlank { lang.tr("جارٍ النطق…", "Speaking…") })
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .build()
    }

    private fun acquireWakeLock() {
        try {
            val pm = getSystemService(PowerManager::class.java)
            wakeLock = pm?.newWakeLock(PowerManager.PARTIAL_WAKE_LOCK, "voiceassistant:speaking")
                ?.apply { acquire(MAX_LIFETIME_MS) }
        } catch (e: Exception) {
            wakeLock = null
        }
    }

    override fun onDestroy() {
        mainHandler.removeCallbacksAndMessages(null)
        human?.stop()
        engine?.stop()
        engine?.shutdown()
        engine = null
        try {
            if (wakeLock?.isHeld == true) wakeLock?.release()
        } catch (e: Exception) {
            // already released
        }
        super.onDestroy()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
''')

# ------------------------------------------------------------------ 5. شاشة اختيار الصوت (الإعدادات)
write_file(_PKG + "/ui/components/VoiceSettingsSheet.kt", r'''package com.example.voiceassistant.ui.components

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PlayArrow
import androidx.compose.material.icons.filled.Stop
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.RadioButton
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.example.voiceassistant.data.AiProvider
import com.example.voiceassistant.data.AiSettings
import com.example.voiceassistant.speech.HumanVoice
import com.example.voiceassistant.speech.HumanVoicePlayer
import com.example.voiceassistant.speech.HumanVoices
import com.example.voiceassistant.speech.VoiceSettings
import com.example.voiceassistant.viewmodel.AppLanguage

/**
 * Voice settings: switch between real human voices (Gemini) and the phone's built-in voice,
 * and pick a female or male voice. Tapping a voice selects it and plays a short sample.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun VoiceSettingsSheet(language: AppLanguage, onDismiss: () -> Unit) {
    val context = LocalContext.current
    val settings by VoiceSettings.state.collectAsState()
    val ai by AiSettings.state.collectAsState()
    val hasKey = ai.hasUserKey[AiProvider.GEMINI] == true || ai.hasBuildKey[AiProvider.GEMINI] == true
    val player = remember { HumanVoicePlayer() }
    var previewId by remember { mutableStateOf<String?>(null) }
    var previewLoading by remember { mutableStateOf(false) }
    var previewFailed by remember { mutableStateOf(false) }

    LaunchedEffect(Unit) { VoiceSettings.init(context) }
    DisposableEffect(player) { onDispose { player.stop() } }

    val sample = language.tr(
        "مرحباً، أنا مساعدك الصوتي. هذا هو صوتي، هل يعجبك؟",
        "Hello, I'm your voice assistant. This is my voice. Do you like it?"
    )

    val stopPreview: () -> Unit = {
        player.stop()
        previewId = null
        previewLoading = false
    }
    val startPreview: (HumanVoice) -> Unit = { voice ->
        player.stop()
        previewFailed = false
        previewId = voice.id
        previewLoading = true
        player.speak(
            text = sample,
            voiceId = voice.id,
            alarm = false,
            onStarted = { previewLoading = false },
            onFinished = { remaining ->
                previewLoading = false
                if (previewId == voice.id) previewId = null
                if (remaining.isNotBlank()) previewFailed = true
            }
        )
    }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp)
                .navigationBarsPadding()
                .padding(bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = language.tr("الصوت", "Voice"),
                style = MaterialTheme.typography.titleLarge
            )
            Text(
                text = language.tr(
                    "اختر صوتاً بشرياً (نسائياً أو رجالياً) ينطق به المساعد. هذه الأصوات تحتاج إنترنت ومفتاح Gemini، ويُرسل نص الرد إلى Google لتحويله إلى صوت. وعند تعذّر ذلك يُستخدم صوت الهاتف تلقائياً.",
                    "Pick the human voice (female or male) the assistant speaks with. These voices need internet and a Gemini key, and the reply text is sent to Google to be turned into speech. If that isn't possible, the phone's own voice is used automatically."
                ),
                style = MaterialTheme.typography.bodySmall
            )
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text(
                    text = language.tr("أصوات بشرية حقيقية", "Real human voices"),
                    modifier = Modifier.weight(1f),
                    style = MaterialTheme.typography.bodyLarge
                )
                Switch(
                    checked = settings.humanEnabled,
                    onCheckedChange = { on ->
                        VoiceSettings.setHumanEnabled(on)
                        if (!on) stopPreview()
                    }
                )
            }
            if (settings.humanEnabled && !hasKey) {
                Text(
                    text = language.tr(
                        "لا يوجد مفتاح Gemini. أضفه من «نماذج الذكاء الاصطناعي» ليعمل الصوت البشري، وإلا يُستخدم صوت الهاتف.",
                        "No Gemini key. Add it in \"AI models\" to enable the human voice, otherwise the phone's voice is used."
                    ),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error
                )
            }
            if (previewFailed) {
                Text(
                    text = language.tr(
                        "تعذّر تشغيل الصوت. تحقق من الإنترنت ومن مفتاح Gemini.",
                        "Couldn't play the voice. Check the internet and your Gemini key."
                    ),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.error
                )
            }
            if (settings.humanEnabled) {
                VoiceGroup(
                    title = language.tr("أصوات نسائية", "Female voices"),
                    voices = HumanVoices.females,
                    language = language,
                    selectedId = settings.voiceId,
                    previewId = previewId,
                    previewLoading = previewLoading,
                    canPlay = hasKey,
                    onSelect = { voice ->
                        VoiceSettings.setVoice(voice.id)
                        if (hasKey) startPreview(voice)
                    },
                    onPreview = { voice ->
                        if (previewId == voice.id) stopPreview() else startPreview(voice)
                    }
                )
                VoiceGroup(
                    title = language.tr("أصوات رجالية", "Male voices"),
                    voices = HumanVoices.males,
                    language = language,
                    selectedId = settings.voiceId,
                    previewId = previewId,
                    previewLoading = previewLoading,
                    canPlay = hasKey,
                    onSelect = { voice ->
                        VoiceSettings.setVoice(voice.id)
                        if (hasKey) startPreview(voice)
                    },
                    onPreview = { voice ->
                        if (previewId == voice.id) stopPreview() else startPreview(voice)
                    }
                )
            } else {
                Text(
                    text = language.tr(
                        "الصوت الحالي: صوت الهاتف المدمج.",
                        "Current voice: the phone's built-in voice."
                    ),
                    style = MaterialTheme.typography.bodyMedium
                )
            }
        }
    }
}

@Composable
private fun VoiceGroup(
    title: String,
    voices: List<HumanVoice>,
    language: AppLanguage,
    selectedId: String,
    previewId: String?,
    previewLoading: Boolean,
    canPlay: Boolean,
    onSelect: (HumanVoice) -> Unit,
    onPreview: (HumanVoice) -> Unit
) {
    Card(modifier = Modifier.fillMaxWidth()) {
        Column(modifier = Modifier.padding(vertical = 8.dp)) {
            Text(
                text = title,
                style = MaterialTheme.typography.titleMedium,
                modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp)
            )
            voices.forEach { voice ->
                val active = previewId == voice.id
                Row(
                    modifier = Modifier
                        .fillMaxWidth()
                        .clickable { onSelect(voice) }
                        .padding(horizontal = 8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    RadioButton(
                        selected = voice.id == selectedId,
                        onClick = { onSelect(voice) }
                    )
                    Column(modifier = Modifier.weight(1f)) {
                        Text(
                            text = language.tr(voice.nameAr, voice.nameEn),
                            style = MaterialTheme.typography.bodyLarge
                        )
                        Text(
                            text = language.tr(voice.styleAr, voice.styleEn),
                            style = MaterialTheme.typography.bodySmall,
                            color = MaterialTheme.colorScheme.onSurfaceVariant
                        )
                    }
                    IconButton(onClick = { onPreview(voice) }, enabled = canPlay) {
                        if (active && previewLoading) {
                            CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp)
                        } else {
                            Icon(
                                imageVector = if (active) Icons.Filled.Stop else Icons.Filled.PlayArrow,
                                contentDescription = language.tr("تجربة الصوت", "Preview voice")
                            )
                        }
                    }
                }
            }
        }
    }
}
''')

# ------------------------------------------------------------------ 6. MainScreen: زر «الصوت» داخل قائمة الإعدادات (الترس)
_voice_screen_path = _PKG + "/ui/MainScreen.kt"

insert_before(
    _voice_screen_path,
    "import androidx.compose.material.icons.filled.Psychology\n",
    "import androidx.compose.material.icons.filled.GraphicEq\n"
)
insert_before(
    _voice_screen_path,
    "import com.example.voiceassistant.ui.components.LanguageToggle\n",
    "import com.example.voiceassistant.ui.components.VoiceSettingsSheet\n"
)
insert_before(
    _voice_screen_path,
    "    var showSettingsMenu by remember { mutableStateOf(false) }\n",
    "    var showVoiceSettings by remember { mutableStateOf(false) }\n"
)
insert_before(
    _voice_screen_path,
    "        if (showAiSettings) {\n",
    '''        if (showVoiceSettings) {
            VoiceSettingsSheet(
                language = state.language,
                onDismiss = { showVoiceSettings = false }
            )
        }
''')
insert_before(
    _voice_screen_path,
    "                                DropdownMenuItem(\n"
    "                                    text = { Text(state.language.tr(\"الذاكرة\", \"Memory\")) },\n",
    '''                                DropdownMenuItem(
                                    text = { Text(state.language.tr("الصوت", "Voice")) },
                                    leadingIcon = { Icon(Icons.Filled.GraphicEq, contentDescription = null) },
                                    onClick = {
                                        showSettingsMenu = false
                                        showVoiceSettings = true
                                    }
                                )
''')
print(">> Human voices (male / female) + voice settings sheet injected.")


# ==============================================================================
# الميزة 20: الربط الخارجي بالبلوتوث والواي فاي (زر في قائمة الإعدادات)
#   - زر «البلوتوث والواي فاي» في قائمة الترس يفتح شاشة NearbyLinkSheet.
#   - التقاط (بحث عن) أجهزة البلوتوث القريبة + عرض الأجهزة المقترنة + اقتران بلمسة واحدة.
#   - التقاط شبكات الواي فاي القريبة + الاتصال بها (مع كلمة المرور للشبكات المحمية).
#   - زر «اجعل جهازي مرئياً» ليتمكن جهاز آخر من العثور على هذا الهاتف عبر البلوتوث.
#   - لا مكتبات خارجية: إطار أندرويد فقط (BluetoothAdapter / WifiManager / ConnectivityManager).
# ==============================================================================

# ------------------------------------------------------------------ 1. المنطق: NearbyLink
write_file(_PKG + "/connectivity/NearbyLink.kt", r'''package com.example.voiceassistant.connectivity

import android.Manifest
import android.annotation.SuppressLint
import android.bluetooth.BluetoothAdapter
import android.bluetooth.BluetoothDevice
import android.bluetooth.BluetoothManager
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.content.pm.PackageManager
import android.location.LocationManager
import android.net.ConnectivityManager
import android.net.Network
import android.net.NetworkCapabilities
import android.net.NetworkRequest
import android.net.wifi.ScanResult
import android.net.wifi.WifiConfiguration
import android.net.wifi.WifiManager
import android.net.wifi.WifiNetworkSpecifier
import android.os.Build
import android.os.Handler
import android.os.Looper
import androidx.core.content.ContextCompat
import androidx.core.location.LocationManagerCompat
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

/** A Bluetooth device found nearby (or already paired). */
data class BtDevice(
    val address: String,
    val name: String?,
    val bonded: Boolean,
    val bonding: Boolean,
    val rssi: Int?
)

enum class WifiSecurity { OPEN, WPA2, WPA3, OTHER }

/** A Wi-Fi network found nearby. [level] is the signal strength in dBm. */
data class WifiNet(
    val ssid: String,
    val level: Int,
    val security: WifiSecurity
)

/** Short messages the settings sheet shows (the sheet translates them). */
enum class LinkNotice(val error: Boolean) {
    NO_BLUETOOTH(true),
    NO_WIFI(true),
    WIFI_OFF(true),
    LOCATION_OFF(true),
    PERMISSION_DENIED(true),
    BT_SCAN_FAILED(true),
    WIFI_THROTTLED(false),
    PAIR_STARTED(false),
    PAIR_DONE(false),
    PAIR_FAILED(true),
    ALREADY_PAIRED(false),
    WIFI_CONNECTING(false),
    WIFI_CONNECTED(false),
    WIFI_FAILED(true),
    WIFI_BAD_PASSWORD(true),
    WIFI_UNSUPPORTED(true)
}

/**
 * Scans for nearby Bluetooth devices and Wi-Fi networks and links with them.
 * Uses only the Android framework APIs. Lives as an object so a Wi-Fi link made from the
 * settings sheet stays alive after the sheet is closed.
 */
@SuppressLint("MissingPermission")
object NearbyLink {
    private const val WIFI_SCAN_TIMEOUT_MS = 12_000L
    private const val WIFI_CONNECT_TIMEOUT_MS = 30_000

    private var app: Context? = null
    private val handler = Handler(Looper.getMainLooper())
    private val btFound = linkedMapOf<String, BtDevice>()
    private var attached = false
    private var networkCallback: ConnectivityManager.NetworkCallback? = null

    /** The Wi-Fi network linked from this app (use its socketFactory to talk to the other device). */
    @Volatile
    var activeNetwork: Network? = null
        private set

    private val _bluetooth = MutableStateFlow<List<BtDevice>>(emptyList())
    val bluetooth: StateFlow<List<BtDevice>> = _bluetooth.asStateFlow()

    private val _wifi = MutableStateFlow<List<WifiNet>>(emptyList())
    val wifi: StateFlow<List<WifiNet>> = _wifi.asStateFlow()

    private val _bluetoothScanning = MutableStateFlow(false)
    val bluetoothScanning: StateFlow<Boolean> = _bluetoothScanning.asStateFlow()

    private val _wifiScanning = MutableStateFlow(false)
    val wifiScanning: StateFlow<Boolean> = _wifiScanning.asStateFlow()

    private val _connectedSsid = MutableStateFlow<String?>(null)
    val connectedSsid: StateFlow<String?> = _connectedSsid.asStateFlow()

    private val _notice = MutableStateFlow<LinkNotice?>(null)
    val notice: StateFlow<LinkNotice?> = _notice.asStateFlow()

    fun init(context: Context) {
        if (app == null) app = context.applicationContext
    }

    // ------------------------------------------------------------ permissions
    /** Runtime permissions needed for scanning (and for being visible when [advertise] is true). */
    fun permissions(advertise: Boolean): Array<String> {
        val list = mutableListOf<String>()
        if (Build.VERSION.SDK_INT >= 31) {
            list.add(Manifest.permission.BLUETOOTH_SCAN)
            list.add(Manifest.permission.BLUETOOTH_CONNECT)
            if (advertise) list.add(Manifest.permission.BLUETOOTH_ADVERTISE)
        }
        if (Build.VERSION.SDK_INT >= 33) {
            list.add(Manifest.permission.NEARBY_WIFI_DEVICES)
        } else {
            list.add(Manifest.permission.ACCESS_FINE_LOCATION)
        }
        return list.toTypedArray()
    }

    fun hasPermissions(context: Context, advertise: Boolean): Boolean =
        permissions(advertise).all {
            ContextCompat.checkSelfPermission(context, it) == PackageManager.PERMISSION_GRANTED
        }

    fun report(notice: LinkNotice) {
        _notice.value = notice
    }

    fun dismissNotice() {
        _notice.value = null
    }

    // ------------------------------------------------------------ helpers
    private fun adapter(): BluetoothAdapter? {
        val manager = app?.getSystemService(Context.BLUETOOTH_SERVICE) as? BluetoothManager
        return manager?.adapter
    }

    private fun wifiManager(): WifiManager? = app?.getSystemService(Context.WIFI_SERVICE) as? WifiManager

    private fun connectivity(): ConnectivityManager? =
        app?.getSystemService(Context.CONNECTIVITY_SERVICE) as? ConnectivityManager

    private fun locationOn(): Boolean {
        val manager = app?.getSystemService(Context.LOCATION_SERVICE) as? LocationManager ?: return true
        return LocationManagerCompat.isLocationEnabled(manager)
    }

    private fun quoted(text: String): String = "\"" + text + "\""

    /** True when Bluetooth exists but is switched off (the sheet then asks the system to turn it on). */
    fun needsBluetoothEnable(): Boolean {
        val adapter = adapter() ?: return false
        return try {
            !adapter.isEnabled
        } catch (e: SecurityException) {
            false
        }
    }

    // ------------------------------------------------------------ attach / detach
    private val receiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            if (intent == null) return
            val action = intent.action ?: return
            when (action) {
                BluetoothDevice.ACTION_FOUND -> onBluetoothFound(intent)
                BluetoothAdapter.ACTION_DISCOVERY_FINISHED -> _bluetoothScanning.value = false
                BluetoothDevice.ACTION_BOND_STATE_CHANGED -> onBondChanged(intent)
                WifiManager.SCAN_RESULTS_AVAILABLE_ACTION -> onWifiResults()
            }
        }
    }

    private val wifiTimeout = Runnable {
        _wifiScanning.value = false
        publishWifi()
    }

    private fun attach() {
        val context = app ?: return
        if (attached) return
        val filter = IntentFilter()
        filter.addAction(BluetoothDevice.ACTION_FOUND)
        filter.addAction(BluetoothAdapter.ACTION_DISCOVERY_FINISHED)
        filter.addAction(BluetoothDevice.ACTION_BOND_STATE_CHANGED)
        filter.addAction(WifiManager.SCAN_RESULTS_AVAILABLE_ACTION)
        ContextCompat.registerReceiver(context, receiver, filter, ContextCompat.RECEIVER_NOT_EXPORTED)
        attached = true
    }

    /** Stops scanning and the broadcast listener (called when the settings sheet closes). */
    fun detach() {
        handler.removeCallbacks(wifiTimeout)
        val context = app
        if (attached && context != null) {
            try {
                context.unregisterReceiver(receiver)
            } catch (e: IllegalArgumentException) {
                // not registered
            }
            attached = false
        }
        try {
            adapter()?.cancelDiscovery()
        } catch (e: SecurityException) {
            // permission missing: nothing to cancel
        }
        _bluetoothScanning.value = false
        _wifiScanning.value = false
    }

    /** Shows the already paired devices, the last Wi-Fi results and the current Wi-Fi name. */
    fun refresh() {
        loadBonded()
        publishWifi()
    }

    // ------------------------------------------------------------ Bluetooth
    @Suppress("DEPRECATION")
    private fun deviceFrom(intent: Intent): BluetoothDevice? =
        if (Build.VERSION.SDK_INT >= 33) {
            intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE, BluetoothDevice::class.java)
        } else {
            intent.getParcelableExtra(BluetoothDevice.EXTRA_DEVICE)
        }

    private fun nameOf(device: BluetoothDevice): String? = try {
        device.name
    } catch (e: SecurityException) {
        null
    }

    private fun bondOf(device: BluetoothDevice): Int = try {
        device.bondState
    } catch (e: SecurityException) {
        BluetoothDevice.BOND_NONE
    }

    private fun publishBluetooth() {
        _bluetooth.value = btFound.values.sortedWith(
            compareByDescending<BtDevice> { it.bonded || it.bonding }
                .thenByDescending { it.rssi ?: Int.MIN_VALUE }
        )
    }

    private fun loadBonded() {
        val adapter = adapter() ?: return
        try {
            adapter.bondedDevices?.forEach { device ->
                val old = btFound[device.address]
                btFound[device.address] = BtDevice(
                    address = device.address,
                    name = nameOf(device) ?: old?.name,
                    bonded = true,
                    bonding = false,
                    rssi = old?.rssi
                )
            }
        } catch (e: SecurityException) {
            // permission missing: the sheet asks for it before calling this
        }
        publishBluetooth()
    }

    private fun onBluetoothFound(intent: Intent) {
        val device = deviceFrom(intent) ?: return
        val rawRssi = intent.getShortExtra(BluetoothDevice.EXTRA_RSSI, Short.MIN_VALUE).toInt()
        val old = btFound[device.address]
        val state = bondOf(device)
        btFound[device.address] = BtDevice(
            address = device.address,
            name = nameOf(device) ?: old?.name,
            bonded = state == BluetoothDevice.BOND_BONDED,
            bonding = state == BluetoothDevice.BOND_BONDING,
            rssi = if (rawRssi == Short.MIN_VALUE.toInt()) old?.rssi else rawRssi
        )
        publishBluetooth()
    }

    private fun onBondChanged(intent: Intent) {
        val device = deviceFrom(intent) ?: return
        val state = intent.getIntExtra(BluetoothDevice.EXTRA_BOND_STATE, BluetoothDevice.BOND_NONE)
        val old = btFound[device.address]
        btFound[device.address] = BtDevice(
            address = device.address,
            name = nameOf(device) ?: old?.name,
            bonded = state == BluetoothDevice.BOND_BONDED,
            bonding = state == BluetoothDevice.BOND_BONDING,
            rssi = old?.rssi
        )
        publishBluetooth()
        if (state == BluetoothDevice.BOND_BONDED) {
            report(LinkNotice.PAIR_DONE)
        } else if (state == BluetoothDevice.BOND_NONE && old?.bonding == true) {
            report(LinkNotice.PAIR_FAILED)
        }
    }

    /** Starts looking for nearby Bluetooth devices (about 12 seconds). */
    fun startBluetoothScan() {
        val adapter = adapter()
        if (adapter == null) {
            report(LinkNotice.NO_BLUETOOTH)
            return
        }
        if (Build.VERSION.SDK_INT < 31 && !locationOn()) {
            report(LinkNotice.LOCATION_OFF)
            return
        }
        dismissNotice()
        attach()
        btFound.values.removeAll { !it.bonded }
        loadBonded()
        try {
            if (adapter.isDiscovering) adapter.cancelDiscovery()
            val started = adapter.startDiscovery()
            _bluetoothScanning.value = started
            if (!started) report(LinkNotice.BT_SCAN_FAILED)
        } catch (e: SecurityException) {
            _bluetoothScanning.value = false
            report(LinkNotice.PERMISSION_DENIED)
        }
    }

    /** Pairs with a found device (the system shows its own confirmation / PIN dialog). */
    fun pair(address: String) {
        val adapter = adapter()
        if (adapter == null) {
            report(LinkNotice.NO_BLUETOOTH)
            return
        }
        try {
            val remote = adapter.getRemoteDevice(address)
            if (adapter.isDiscovering) adapter.cancelDiscovery()
            if (remote.bondState == BluetoothDevice.BOND_BONDED) {
                report(LinkNotice.ALREADY_PAIRED)
            } else if (remote.createBond()) {
                report(LinkNotice.PAIR_STARTED)
            } else {
                report(LinkNotice.PAIR_FAILED)
            }
        } catch (e: SecurityException) {
            report(LinkNotice.PERMISSION_DENIED)
        } catch (e: IllegalArgumentException) {
            report(LinkNotice.PAIR_FAILED)
        }
    }

    // ------------------------------------------------------------ Wi-Fi
    @Suppress("DEPRECATION")
    private fun toNet(result: ScanResult): WifiNet? {
        val ssid = (result.SSID ?: "").trim().trim('"')
        if (ssid.isEmpty()) return null
        val caps = result.capabilities ?: ""
        val security = when {
            caps.contains("SAE") && !caps.contains("PSK") -> WifiSecurity.WPA3
            caps.contains("PSK") -> WifiSecurity.WPA2
            caps.contains("WEP") || caps.contains("EAP") -> WifiSecurity.OTHER
            else -> WifiSecurity.OPEN
        }
        return WifiNet(ssid, result.level, security)
    }

    @Suppress("DEPRECATION")
    private fun currentSsid(): String? {
        val info = try {
            wifiManager()?.connectionInfo
        } catch (e: SecurityException) {
            null
        }
        val ssid = info?.ssid?.trim('"') ?: return null
        return if (ssid.isEmpty() || ssid == "<unknown ssid>") null else ssid
    }

    private fun publishWifi() {
        val manager = wifiManager() ?: return
        val results: List<ScanResult> = try {
            manager.scanResults ?: emptyList()
        } catch (e: SecurityException) {
            emptyList()
        }
        _wifi.value = results
            .mapNotNull { toNet(it) }
            .groupBy { it.ssid }
            .values
            .mapNotNull { group -> group.maxByOrNull { it.level } }
            .sortedByDescending { it.level }
        if (_connectedSsid.value == null || activeNetwork == null) {
            _connectedSsid.value = currentSsid()
        }
    }

    private fun onWifiResults() {
        handler.removeCallbacks(wifiTimeout)
        _wifiScanning.value = false
        publishWifi()
    }

    /** Starts looking for nearby Wi-Fi networks (Android limits how often this may run). */
    fun startWifiScan() {
        val manager = wifiManager()
        if (manager == null) {
            report(LinkNotice.NO_WIFI)
            return
        }
        if (!manager.isWifiEnabled) {
            report(LinkNotice.WIFI_OFF)
            return
        }
        if (Build.VERSION.SDK_INT < 33 && !locationOn()) {
            report(LinkNotice.LOCATION_OFF)
            return
        }
        dismissNotice()
        attach()
        _wifiScanning.value = true
        @Suppress("DEPRECATION")
        val started = manager.startScan()
        if (started) {
            handler.removeCallbacks(wifiTimeout)
            handler.postDelayed(wifiTimeout, WIFI_SCAN_TIMEOUT_MS)
        } else {
            _wifiScanning.value = false
            publishWifi()
            report(LinkNotice.WIFI_THROTTLED)
        }
    }

    /** Links with a network. [password] is ignored for open networks. */
    fun connectWifi(net: WifiNet, password: String) {
        when {
            net.security == WifiSecurity.OTHER -> report(LinkNotice.WIFI_UNSUPPORTED)
            Build.VERSION.SDK_INT >= 29 -> connectModern(net, password)
            else -> connectLegacy(net, password)
        }
    }

    @SuppressLint("NewApi")
    private fun connectModern(net: WifiNet, password: String) {
        val manager = connectivity()
        if (manager == null) {
            report(LinkNotice.WIFI_FAILED)
            return
        }
        disconnectWifi()
        val request = try {
            val builder = WifiNetworkSpecifier.Builder().setSsid(net.ssid)
            when (net.security) {
                WifiSecurity.WPA2 -> builder.setWpa2Passphrase(password)
                WifiSecurity.WPA3 -> builder.setWpa3Passphrase(password)
                else -> Unit
            }
            NetworkRequest.Builder()
                .addTransportType(NetworkCapabilities.TRANSPORT_WIFI)
                .removeCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
                .setNetworkSpecifier(builder.build())
                .build()
        } catch (e: IllegalArgumentException) {
            report(LinkNotice.WIFI_BAD_PASSWORD)
            return
        }
        val callback = object : ConnectivityManager.NetworkCallback() {
            override fun onAvailable(network: Network) {
                activeNetwork = network
                _connectedSsid.value = net.ssid
                report(LinkNotice.WIFI_CONNECTED)
            }

            override fun onUnavailable() {
                networkCallback = null
                report(LinkNotice.WIFI_FAILED)
            }

            override fun onLost(network: Network) {
                activeNetwork = null
                _connectedSsid.value = currentSsid()
            }
        }
        networkCallback = callback
        report(LinkNotice.WIFI_CONNECTING)
        try {
            manager.requestNetwork(request, callback, handler, WIFI_CONNECT_TIMEOUT_MS)
        } catch (e: Exception) {
            networkCallback = null
            report(LinkNotice.WIFI_FAILED)
        }
    }

    @Suppress("DEPRECATION")
    private fun connectLegacy(net: WifiNet, password: String) {
        val manager = wifiManager()
        if (manager == null) {
            report(LinkNotice.WIFI_FAILED)
            return
        }
        val config = WifiConfiguration()
        config.SSID = quoted(net.ssid)
        if (net.security == WifiSecurity.OPEN) {
            config.allowedKeyManagement.set(WifiConfiguration.KeyMgmt.NONE)
        } else {
            config.preSharedKey = quoted(password)
        }
        val id = manager.addNetwork(config)
        if (id == -1) {
            report(LinkNotice.WIFI_FAILED)
            return
        }
        manager.disconnect()
        if (manager.enableNetwork(id, true) && manager.reconnect()) {
            _connectedSsid.value = net.ssid
            report(LinkNotice.WIFI_CONNECTING)
        } else {
            report(LinkNotice.WIFI_FAILED)
        }
    }

    /** Drops the Wi-Fi link that was made from this app. */
    fun disconnectWifi() {
        val callback = networkCallback
        if (callback != null) {
            try {
                connectivity()?.unregisterNetworkCallback(callback)
            } catch (e: IllegalArgumentException) {
                // already unregistered
            }
        }
        networkCallback = null
        activeNetwork = null
        _connectedSsid.value = currentSsid()
    }

    /** True when the link was made by this app (so the sheet can offer a disconnect button). */
    fun hasAppLink(): Boolean = activeNetwork != null
}
''')

# ------------------------------------------------------------------ 2. الواجهة: NearbyLinkSheet
write_file(_PKG + "/ui/components/NearbyLinkSheet.kt", r'''package com.example.voiceassistant.ui.components

import android.app.Activity
import android.bluetooth.BluetoothAdapter
import android.content.Intent
import android.provider.Settings
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Bluetooth
import androidx.compose.material.icons.filled.Lock
import androidx.compose.material.icons.filled.Search
import androidx.compose.material.icons.filled.Visibility
import androidx.compose.material.icons.filled.Wifi
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.HorizontalDivider
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import com.example.voiceassistant.connectivity.BtDevice
import com.example.voiceassistant.connectivity.LinkNotice
import com.example.voiceassistant.connectivity.NearbyLink
import com.example.voiceassistant.connectivity.WifiNet
import com.example.voiceassistant.connectivity.WifiSecurity
import com.example.voiceassistant.viewmodel.AppLanguage

/**
 * Bluetooth & Wi-Fi settings: scan for nearby devices and networks, pair with a Bluetooth
 * device, join a Wi-Fi network, and make this phone visible so other devices can find it.
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun NearbyLinkSheet(language: AppLanguage, onDismiss: () -> Unit) {
    val context = LocalContext.current
    val bluetooth by NearbyLink.bluetooth.collectAsState()
    val wifi by NearbyLink.wifi.collectAsState()
    val btScanning by NearbyLink.bluetoothScanning.collectAsState()
    val wifiScanning by NearbyLink.wifiScanning.collectAsState()
    val connectedSsid by NearbyLink.connectedSsid.collectAsState()
    val notice by NearbyLink.notice.collectAsState()

    var pendingAction by remember { mutableStateOf<(() -> Unit)?>(null) }
    var pendingAdvertise by remember { mutableStateOf(false) }
    var passwordFor by remember { mutableStateOf<WifiNet?>(null) }
    var password by remember { mutableStateOf("") }

    LaunchedEffect(Unit) {
        NearbyLink.init(context)
        NearbyLink.dismissNotice()
        if (NearbyLink.hasPermissions(context, false)) NearbyLink.refresh()
    }
    DisposableEffect(Unit) { onDispose { NearbyLink.detach() } }

    val permissionLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { _ ->
        val action = pendingAction
        pendingAction = null
        if (action != null && NearbyLink.hasPermissions(context, pendingAdvertise)) {
            action()
        } else {
            NearbyLink.report(LinkNotice.PERMISSION_DENIED)
        }
    }

    val enableBluetoothLauncher = rememberLauncherForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == Activity.RESULT_OK) NearbyLink.startBluetoothScan()
    }

    val withPermissions: (Boolean, () -> Unit) -> Unit = { advertise, action ->
        NearbyLink.init(context)
        if (NearbyLink.hasPermissions(context, advertise)) {
            action()
        } else {
            pendingAction = action
            pendingAdvertise = advertise
            permissionLauncher.launch(NearbyLink.permissions(advertise))
        }
    }

    val scanBluetooth: () -> Unit = {
        withPermissions(false) {
            if (NearbyLink.needsBluetoothEnable()) {
                enableBluetoothLauncher.launch(Intent(BluetoothAdapter.ACTION_REQUEST_ENABLE))
            } else {
                NearbyLink.startBluetoothScan()
            }
        }
    }
    val scanWifi: () -> Unit = {
        withPermissions(false) { NearbyLink.startWifiScan() }
    }
    val makeVisible: () -> Unit = {
        withPermissions(true) {
            try {
                val intent = Intent(BluetoothAdapter.ACTION_REQUEST_DISCOVERABLE)
                intent.putExtra(BluetoothAdapter.EXTRA_DISCOVERABLE_DURATION, 300)
                context.startActivity(intent)
            } catch (e: Exception) {
                NearbyLink.report(LinkNotice.NO_BLUETOOTH)
            }
        }
    }
    val openSystemSettings: (String) -> Unit = { action ->
        try {
            val intent = Intent(action)
            intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            context.startActivity(intent)
        } catch (e: Exception) {
            // no settings screen available on this device
        }
    }
    val connect: (WifiNet) -> Unit = { net ->
        if (net.security == WifiSecurity.OPEN) {
            NearbyLink.connectWifi(net, "")
        } else if (net.security == WifiSecurity.OTHER) {
            NearbyLink.report(LinkNotice.WIFI_UNSUPPORTED)
        } else {
            password = ""
            passwordFor = net
        }
    }

    ModalBottomSheet(
        onDismissRequest = onDismiss,
        sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 16.dp)
                .navigationBarsPadding()
                .padding(bottom = 24.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = language.tr("البلوتوث والواي فاي", "Bluetooth & Wi-Fi"),
                style = MaterialTheme.typography.titleLarge
            )
            Text(
                text = language.tr(
                    "التقط الأجهزة وشبكات الواي فاي القريبة واربط هاتفك بها. يطلب الأندرويد منك الأذونات اللازمة عند أول بحث.",
                    "Find nearby devices and Wi-Fi networks and link your phone with them. Android asks for the needed permissions on the first scan."
                ),
                style = MaterialTheme.typography.bodySmall
            )
            notice?.let { current ->
                Text(
                    text = noticeText(current, language),
                    style = MaterialTheme.typography.bodyMedium,
                    color = if (current.error) MaterialTheme.colorScheme.error else MaterialTheme.colorScheme.primary
                )
            }

            // ---------------- Bluetooth
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Filled.Bluetooth, contentDescription = null)
                        Text(
                            text = language.tr("البلوتوث", "Bluetooth"),
                            style = MaterialTheme.typography.titleMedium,
                            modifier = Modifier
                                .weight(1f)
                                .padding(horizontal = 8.dp)
                        )
                        if (btScanning) {
                            CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp)
                        }
                    }
                    Button(
                        onClick = scanBluetooth,
                        enabled = !btScanning,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(Icons.Filled.Search, contentDescription = null, modifier = Modifier.size(18.dp))
                        Text(
                            text = language.tr("التقاط أجهزة البلوتوث", "Scan for Bluetooth devices"),
                            modifier = Modifier.padding(start = 8.dp)
                        )
                    }
                    OutlinedButton(onClick = makeVisible, modifier = Modifier.fillMaxWidth()) {
                        Icon(Icons.Filled.Visibility, contentDescription = null, modifier = Modifier.size(18.dp))
                        Text(
                            text = language.tr("اجعل جهازي مرئياً (5 دقائق)", "Make my phone visible (5 min)"),
                            modifier = Modifier.padding(start = 8.dp)
                        )
                    }
                    if (bluetooth.isEmpty()) {
                        Text(
                            text = if (btScanning) {
                                language.tr("جارٍ البحث…", "Searching…")
                            } else {
                                language.tr(
                                    "لا توجد أجهزة بعد. اضغط «التقاط» وتأكد أن الجهاز الآخر مرئي.",
                                    "No devices yet. Tap Scan and make sure the other device is visible."
                                )
                            },
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                    bluetooth.forEach { device ->
                        BluetoothRow(
                            device = device,
                            language = language,
                            onPair = { withPermissions(false) { NearbyLink.pair(device.address) } }
                        )
                    }
                    TextButton(onClick = { openSystemSettings(Settings.ACTION_BLUETOOTH_SETTINGS) }) {
                        Text(language.tr("إعدادات البلوتوث في النظام", "System Bluetooth settings"))
                    }
                }
            }

            // ---------------- Wi-Fi
            Card(modifier = Modifier.fillMaxWidth()) {
                Column(
                    modifier = Modifier.padding(16.dp),
                    verticalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(Icons.Filled.Wifi, contentDescription = null)
                        Text(
                            text = language.tr("الواي فاي", "Wi-Fi"),
                            style = MaterialTheme.typography.titleMedium,
                            modifier = Modifier
                                .weight(1f)
                                .padding(horizontal = 8.dp)
                        )
                        if (wifiScanning) {
                            CircularProgressIndicator(modifier = Modifier.size(20.dp), strokeWidth = 2.dp)
                        }
                    }
                    Button(
                        onClick = scanWifi,
                        enabled = !wifiScanning,
                        modifier = Modifier.fillMaxWidth()
                    ) {
                        Icon(Icons.Filled.Search, contentDescription = null, modifier = Modifier.size(18.dp))
                        Text(
                            text = language.tr("التقاط شبكات الواي فاي", "Scan for Wi-Fi networks"),
                            modifier = Modifier.padding(start = 8.dp)
                        )
                    }
                    if (wifi.isEmpty()) {
                        Text(
                            text = if (wifiScanning) {
                                language.tr("جارٍ البحث…", "Searching…")
                            } else {
                                language.tr("لا توجد شبكات بعد. اضغط «التقاط».", "No networks yet. Tap Scan.")
                            },
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                    wifi.forEach { net ->
                        WifiRow(
                            net = net,
                            connected = net.ssid == connectedSsid,
                            language = language,
                            onClick = { connect(net) }
                        )
                    }
                    if (NearbyLink.hasAppLink()) {
                        TextButton(onClick = { NearbyLink.disconnectWifi() }) {
                            Text(language.tr("قطع الاتصال الذي أنشأه التطبيق", "Disconnect the link made by this app"))
                        }
                    }
                    TextButton(onClick = { openSystemSettings(Settings.ACTION_WIFI_SETTINGS) }) {
                        Text(language.tr("إعدادات الواي فاي في النظام", "System Wi-Fi settings"))
                    }
                }
            }
        }
    }

    passwordFor?.let { net ->
        AlertDialog(
            onDismissRequest = {
                passwordFor = null
                password = ""
            },
            title = { Text(net.ssid) },
            text = {
                OutlinedTextField(
                    value = password,
                    onValueChange = { password = it },
                    singleLine = true,
                    label = { Text(language.tr("كلمة المرور", "Password")) },
                    visualTransformation = PasswordVisualTransformation()
                )
            },
            confirmButton = {
                TextButton(
                    enabled = password.length >= 8,
                    onClick = {
                        NearbyLink.connectWifi(net, password)
                        passwordFor = null
                        password = ""
                    }
                ) { Text(language.tr("اتصال", "Connect")) }
            },
            dismissButton = {
                TextButton(onClick = {
                    passwordFor = null
                    password = ""
                }) { Text(language.tr("إلغاء", "Cancel")) }
            }
        )
    }
}

@Composable
private fun BluetoothRow(device: BtDevice, language: AppLanguage, onPair: () -> Unit) {
    Column {
        HorizontalDivider()
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(vertical = 6.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = device.name ?: language.tr("جهاز غير معروف", "Unknown device"),
                    style = MaterialTheme.typography.bodyLarge
                )
                Text(
                    text = device.address + (device.rssi?.let { "  ·  " + it + " dBm" } ?: ""),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            when {
                device.bonding -> Text(
                    text = language.tr("جارٍ الاقتران…", "Pairing…"),
                    style = MaterialTheme.typography.bodySmall
                )
                device.bonded -> Text(
                    text = language.tr("مقترن", "Paired"),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.primary
                )
                else -> TextButton(onClick = onPair) {
                    Text(language.tr("اقتران", "Pair"))
                }
            }
        }
    }
}

@Composable
private fun WifiRow(net: WifiNet, connected: Boolean, language: AppLanguage, onClick: () -> Unit) {
    val percent = ((net.level + 100) * 100 / 60).coerceIn(0, 100)
    Column {
        HorizontalDivider()
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .clickable(enabled = !connected) { onClick() }
                .padding(vertical = 10.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Column(modifier = Modifier.weight(1f)) {
                Text(text = net.ssid, style = MaterialTheme.typography.bodyLarge)
                Text(
                    text = language.tr("الإشارة ", "Signal ") + percent + "%",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            if (connected) {
                Text(
                    text = language.tr("متصل", "Connected"),
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.primary
                )
            } else if (net.security != WifiSecurity.OPEN) {
                Icon(
                    imageVector = Icons.Filled.Lock,
                    contentDescription = language.tr("شبكة محمية", "Secured network"),
                    modifier = Modifier.size(18.dp)
                )
            }
        }
    }
}

private fun noticeText(notice: LinkNotice, language: AppLanguage): String = when (notice) {
    LinkNotice.NO_BLUETOOTH -> language.tr("هذا الجهاز لا يدعم البلوتوث.", "This device has no Bluetooth.")
    LinkNotice.NO_WIFI -> language.tr("هذا الجهاز لا يدعم الواي فاي.", "This device has no Wi-Fi.")
    LinkNotice.WIFI_OFF -> language.tr(
        "الواي فاي مطفأ. شغّله من إعدادات النظام ثم أعد البحث.",
        "Wi-Fi is off. Turn it on in system settings, then scan again."
    )
    LinkNotice.LOCATION_OFF -> language.tr(
        "فعّل خدمة الموقع في الهاتف، فأندرويد يشترطها لعرض نتائج البحث.",
        "Turn on Location in the phone: Android requires it to show scan results."
    )
    LinkNotice.PERMISSION_DENIED -> language.tr(
        "لم تُمنح الأذونات المطلوبة. اسمح بها من إعدادات التطبيق ثم أعد المحاولة.",
        "The required permissions were not granted. Allow them in the app settings and try again."
    )
    LinkNotice.BT_SCAN_FAILED -> language.tr("تعذّر بدء البحث عن أجهزة البلوتوث.", "Couldn't start the Bluetooth scan.")
    LinkNotice.WIFI_THROTTLED -> language.tr(
        "أندرويد يحدّ من عدد مرات البحث. أعرض آخر النتائج، حاول بعد دقيقة.",
        "Android limits how often Wi-Fi can be scanned. Showing the last results; try again in a minute."
    )
    LinkNotice.PAIR_STARTED -> language.tr("بدأ الاقتران. أكّد الطلب على الجهازين.", "Pairing started. Confirm the request on both devices.")
    LinkNotice.PAIR_DONE -> language.tr("تم الاقتران بنجاح.", "Paired successfully.")
    LinkNotice.PAIR_FAILED -> language.tr("فشل الاقتران.", "Pairing failed.")
    LinkNotice.ALREADY_PAIRED -> language.tr("الجهاز مقترن بالفعل.", "Already paired.")
    LinkNotice.WIFI_CONNECTING -> language.tr("جارٍ الاتصال بالشبكة…", "Connecting to the network…")
    LinkNotice.WIFI_CONNECTED -> language.tr("تم الاتصال بالشبكة.", "Connected to the network.")
    LinkNotice.WIFI_FAILED -> language.tr(
        "تعذّر الاتصال. تأكد من كلمة المرور وأن الشبكة في المدى.",
        "Couldn't connect. Check the password and that the network is in range."
    )
    LinkNotice.WIFI_BAD_PASSWORD -> language.tr(
        "كلمة المرور غير صالحة (8 أحرف على الأقل).",
        "Invalid password (at least 8 characters)."
    )
    LinkNotice.WIFI_UNSUPPORTED -> language.tr(
        "هذا النوع من الشبكات (WEP / مؤسسية) غير مدعوم هنا. استخدم إعدادات النظام.",
        "This network type (WEP / enterprise) isn't supported here. Use the system settings."
    )
}
''')

# ------------------------------------------------------------------ 3. المانيفست: الأذونات
_replace_once(
    "app/src/main/AndroidManifest.xml",
    '    <uses-permission android:name="android.permission.WAKE_LOCK" />\n',
    '''    <uses-permission android:name="android.permission.WAKE_LOCK" />

    <!-- Bluetooth & Wi-Fi scanning / linking (NearbyLink) -->
    <uses-permission android:name="android.permission.ACCESS_WIFI_STATE" />
    <uses-permission android:name="android.permission.CHANGE_WIFI_STATE" />
    <uses-permission android:name="android.permission.CHANGE_NETWORK_STATE" />
    <uses-permission android:name="android.permission.BLUETOOTH" android:maxSdkVersion="30" />
    <uses-permission android:name="android.permission.BLUETOOTH_ADMIN" android:maxSdkVersion="30" />
    <uses-permission
        android:name="android.permission.BLUETOOTH_SCAN"
        android:usesPermissionFlags="neverForLocation" />
    <uses-permission android:name="android.permission.BLUETOOTH_CONNECT" />
    <uses-permission android:name="android.permission.BLUETOOTH_ADVERTISE" />
    <uses-permission
        android:name="android.permission.NEARBY_WIFI_DEVICES"
        android:usesPermissionFlags="neverForLocation" />
    <uses-feature android:name="android.hardware.bluetooth" android:required="false" />
    <uses-feature android:name="android.hardware.wifi" android:required="false" />
'''
)

# ------------------------------------------------------------------ 4. MainScreen: زر في قائمة الإعدادات (الترس)
_nl_screen = _PKG + "/ui/MainScreen.kt"

insert_before(
    _nl_screen,
    "import androidx.compose.material.icons.filled.GraphicEq\n",
    "import androidx.compose.material.icons.filled.Bluetooth\n"
)
insert_before(
    _nl_screen,
    "import com.example.voiceassistant.ui.components.VoiceSettingsSheet\n",
    "import com.example.voiceassistant.ui.components.NearbyLinkSheet\n"
)
insert_before(
    _nl_screen,
    "    var showVoiceSettings by remember { mutableStateOf(false) }\n",
    "    var showNearbyLink by remember { mutableStateOf(false) }\n"
)
insert_before(
    _nl_screen,
    "        if (showVoiceSettings) {\n",
    '''        if (showNearbyLink) {
            NearbyLinkSheet(
                language = state.language,
                onDismiss = { showNearbyLink = false }
            )
        }
'''
)
insert_before(
    _nl_screen,
    "                                DropdownMenuItem(\n"
    "                                    text = { Text(state.language.tr(\"الصوت\", \"Voice\")) },\n",
    '''                                DropdownMenuItem(
                                    text = { Text(state.language.tr("البلوتوث والواي فاي", "Bluetooth & Wi-Fi")) },
                                    leadingIcon = { Icon(Icons.Filled.Bluetooth, contentDescription = null) },
                                    onClick = {
                                        showSettingsMenu = false
                                        showNearbyLink = true
                                    }
                                )
'''
)
print(">> Bluetooth & Wi-Fi scan/link sheet (settings menu button) injected.")


# ==============================================================================
# تسجيل الشاشة بالفيديو (يعمل بدون إنترنت): MediaProjection + MediaRecorder (H.264/MP4)
#  - يبدأ من قائمة الترس («تسجيل الشاشة بالفيديو») أو بالصوت («سجل الشاشة») وبعد عدّ تنازلي 3 ثوانٍ.
#  - الإيقاف / الإيقاف المؤقت من إشعار التسجيل، أو بالصوت («أوقف التسجيل»).
#  - يُحفظ تلقائياً في المعرض (Movies/VoiceAssistant)، وتظهر نافذة: مشاركة / فتح / حذف (وإشعار بنفس الأزرار).
#  - خيار صوت الميكروفون (مفتاح في قائمة الترس) يوقف الاستدعاء الصوتي مؤقتاً أثناء التسجيل.
# ==============================================================================
_REC_PKG = "app/src/main/java/com/example/voiceassistant"

write_file(_REC_PKG + "/service/ScreenRecordBridge.kt", r'''package com.example.voiceassistant.service

import android.content.ClipData
import android.content.Context
import android.content.Intent
import android.net.Uri
import com.example.voiceassistant.ScreenRecordActivity
import java.io.File
import java.util.Locale
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow

enum class RecState { IDLE, COUNTDOWN, RECORDING, PAUSED }

/** A finished recording. [uri] is a content:// Uri that can be played and shared. */
class SavedRecording(
    val uri: String,
    /** Real file path when the video is in the app folder (Android 8/9); null when it is in the gallery. */
    val filePath: String?,
    val name: String,
    val durationMs: Long,
    val sizeBytes: Long,
    val inGallery: Boolean
)

/** Shared state between [ScreenRecordService] and the UI (same process). */
object ScreenRecordBridge {
    private const val PREFS = "screen_record"
    private const val KEY_MIC = "mic"

    private val _state = MutableStateFlow(RecState.IDLE)
    val state: StateFlow<RecState> = _state.asStateFlow()

    private val _saved = MutableStateFlow<SavedRecording?>(null)

    /** The last finished recording, shown in a dialog until the user closes it. */
    val saved: StateFlow<SavedRecording?> = _saved.asStateFlow()

    internal fun setState(value: RecState) {
        _state.value = value
    }

    internal fun publishSaved(recording: SavedRecording) {
        _saved.value = recording
    }

    fun dismissSaved() {
        _saved.value = null
    }

    fun isMicEnabled(context: Context): Boolean =
        context.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE).getBoolean(KEY_MIC, false)

    fun setMicEnabled(context: Context, enabled: Boolean) {
        context.applicationContext.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit().putBoolean(KEY_MIC, enabled).apply()
    }

    /** Opens the (transparent) permission screen; recording starts after the user taps "Start now". */
    fun requestStart(context: Context) {
        try {
            context.startActivity(
                Intent(context, ScreenRecordActivity::class.java).addFlags(Intent.FLAG_ACTIVITY_NEW_TASK)
            )
        } catch (e: Exception) {
            // ignored
        }
    }

    fun viewIntent(recording: SavedRecording): Intent =
        Intent(Intent.ACTION_VIEW)
            .setDataAndType(Uri.parse(recording.uri), "video/mp4")
            .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION or Intent.FLAG_ACTIVITY_NEW_TASK)

    fun shareIntent(recording: SavedRecording, title: String): Intent {
        val uri = Uri.parse(recording.uri)
        val send = Intent(Intent.ACTION_SEND)
            .setType("video/mp4")
            .putExtra(Intent.EXTRA_STREAM, uri)
            .addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        send.clipData = ClipData.newRawUri("", uri)
        return Intent.createChooser(send, title)
            .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_GRANT_READ_URI_PERMISSION)
    }

    fun delete(context: Context, recording: SavedRecording): Boolean {
        return try {
            val path = recording.filePath
            if (path != null) {
                File(path).delete()
            } else {
                context.contentResolver.delete(Uri.parse(recording.uri), null, null) > 0
            }
        } catch (e: Exception) {
            false
        }
    }

    fun formatDuration(ms: Long): String {
        val total = ms / 1000
        val h = total / 3600
        val m = (total % 3600) / 60
        val s = total % 60
        return if (h > 0) String.format(Locale.US, "%d:%02d:%02d", h, m, s)
        else String.format(Locale.US, "%02d:%02d", m, s)
    }

    fun formatSize(bytes: Long): String =
        if (bytes >= 1024L * 1024L) String.format(Locale.US, "%.1f MB", bytes / 1048576.0)
        else String.format(Locale.US, "%d KB", bytes / 1024)
}
''')

write_file(_REC_PKG + "/service/ScreenRecordService.kt", r'''package com.example.voiceassistant.service

import android.Manifest
import android.app.Activity
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.ContentValues
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.content.pm.ServiceInfo
import android.hardware.display.DisplayManager
import android.hardware.display.VirtualDisplay
import android.media.MediaCodecInfo
import android.media.MediaCodecList
import android.media.MediaRecorder
import android.media.projection.MediaProjection
import android.media.projection.MediaProjectionManager
import android.net.Uri
import android.os.Build
import android.os.Environment
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.os.ParcelFileDescriptor
import android.os.StatFs
import android.os.SystemClock
import android.provider.MediaStore
import android.provider.OpenableColumns
import android.view.WindowManager
import android.widget.Toast
import androidx.core.app.NotificationCompat
import androidx.core.app.ServiceCompat
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import com.example.voiceassistant.MainActivity
import java.io.File
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale
import kotlin.math.min

/**
 * Records the screen to an MP4 file (H.264 + optional microphone audio). Works completely offline.
 * The video is saved in the gallery (Movies/VoiceAssistant) and offered for sharing when it ends.
 */
class ScreenRecordService : Service() {

    companion object {
        const val ACTION_STOP = "com.example.voiceassistant.action.RECORD_STOP"
        const val ACTION_PAUSE_RESUME = "com.example.voiceassistant.action.RECORD_PAUSE_RESUME"

        private const val EXTRA_RESULT_CODE = "result_code"
        private const val EXTRA_DATA = "projection_data"
        private const val EXTRA_MIC = "with_mic"

        private const val CHANNEL_ID = "va_screen_record"
        private const val RESULT_CHANNEL_ID = "va_screen_record_done"
        private const val NOTIFICATION_ID = 7431
        private const val RESULT_NOTIFICATION_ID = 7432

        /** Time to move to the screen you want to record (shown in the notification). */
        private const val COUNTDOWN_SECONDS = 3
        private const val MAX_SHORT_SIDE = 1080
        private const val FRAME_RATE = 30
        private const val MIN_FREE_BYTES = 150L * 1024L * 1024L

        fun start(context: Context, resultCode: Int, data: Intent, withMic: Boolean) {
            val intent = Intent(context, ScreenRecordService::class.java)
                .putExtra(EXTRA_RESULT_CODE, resultCode)
                .putExtra(EXTRA_DATA, data)
                .putExtra(EXTRA_MIC, withMic)
            ContextCompat.startForegroundService(context, intent)
        }

        fun stop(context: Context) = send(context, ACTION_STOP)

        fun togglePause(context: Context) = send(context, ACTION_PAUSE_RESUME)

        private fun send(context: Context, action: String) {
            if (ScreenRecordBridge.state.value == RecState.IDLE) return
            try {
                context.startService(Intent(context, ScreenRecordService::class.java).setAction(action))
            } catch (e: Exception) {
                // ignored
            }
        }
    }

    private class Output(val name: String, val uri: Uri?, val file: File?, val pfd: ParcelFileDescriptor?)

    private val mainHandler = Handler(Looper.getMainLooper())
    private var projection: MediaProjection? = null
    private var recorder: MediaRecorder? = null
    private var virtualDisplay: VirtualDisplay? = null
    private var output: Output? = null

    private var resultCode = Activity.RESULT_CANCELED
    private var projectionData: Intent? = null
    private var withMic = false

    private var active = false
    private var recording = false
    private var paused = false
    private var countdownLeft = 0
    private var accumulatedMs = 0L
    private var segmentStart = 0L

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_STOP -> {
                if (active) finishRecording() else stopSelf()
                return START_NOT_STICKY
            }
            ACTION_PAUSE_RESUME -> {
                togglePause()
                return START_NOT_STICKY
            }
        }
        if (active) return START_NOT_STICKY

        resultCode = intent?.getIntExtra(EXTRA_RESULT_CODE, Activity.RESULT_CANCELED) ?: Activity.RESULT_CANCELED
        @Suppress("DEPRECATION")
        projectionData = if (Build.VERSION.SDK_INT >= 33) {
            intent?.getParcelableExtra(EXTRA_DATA, Intent::class.java)
        } else {
            intent?.getParcelableExtra(EXTRA_DATA)
        }
        if (projectionData == null || resultCode != Activity.RESULT_OK) {
            stopSelf()
            return START_NOT_STICKY
        }
        withMic = (intent?.getBooleanExtra(EXTRA_MIC, false) ?: false) &&
            ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) ==
            PackageManager.PERMISSION_GRANTED

        countdownLeft = COUNTDOWN_SECONDS
        // Must be a foreground service BEFORE the projection is created (required on Android 14+).
        if (!enterForeground(withMic)) {
            withMic = false
            if (!enterForeground(false)) {
                fail(ProactiveScheduler.language(this).tr("تعذّر بدء تسجيل الشاشة.", "Could not start screen recording."))
                return START_NOT_STICKY
            }
        }
        active = true
        ScreenRecordBridge.setState(RecState.COUNTDOWN)
        // Release the microphone from the wake-word listener while the recorder uses it.
        if (withMic) WakeWordService.setMicBusy(true)
        runCountdown(COUNTDOWN_SECONDS)
        return START_NOT_STICKY
    }

    private fun enterForeground(mic: Boolean): Boolean {
        return try {
            var type = ServiceInfo.FOREGROUND_SERVICE_TYPE_MEDIA_PROJECTION
            if (mic) type = type or ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE
            ServiceCompat.startForeground(this, NOTIFICATION_ID, buildNotification(), type)
            true
        } catch (e: Exception) {
            false
        }
    }

    private fun runCountdown(left: Int) {
        if (!active) return
        if (left <= 0) {
            beginRecording()
            return
        }
        countdownLeft = left
        updateNotification()
        mainHandler.postDelayed({ runCountdown(left - 1) }, 1000L)
    }

    private fun beginRecording() {
        if (!active) return
        val lang = ProactiveScheduler.language(this)
        try {
            if (freeBytes() < MIN_FREE_BYTES) {
                fail(lang.tr("المساحة المتاحة غير كافية لبدء التسجيل.", "Not enough free storage to start recording."))
                return
            }
            val data = projectionData ?: run { fail(lang.tr("تعذّر بدء تسجيل الشاشة.", "Could not start screen recording.")); return }
            val mp = getSystemService(MediaProjectionManager::class.java).getMediaProjection(resultCode, data)
            projection = mp
            projectionData = null
            // Android 14+: a callback must be registered before the virtual display is created.
            mp.registerCallback(object : MediaProjection.Callback() {
                override fun onStop() {
                    // The user stopped the capture from the system (status bar chip / revoked).
                    mainHandler.post { if (active) finishRecording() }
                }
            }, mainHandler)

            val caps = avcCaps()
            val (width, height) = chooseSize(caps)
            var bitrate = (width.toLong() * height * FRAME_RATE * 0.08).toLong()
                .coerceIn(1_500_000L, 10_000_000L).toInt()
            val range = caps?.bitrateRange
            if (range != null) bitrate = bitrate.coerceIn(range.lower, range.upper)

            val out = openOutput()
            output = out

            @Suppress("DEPRECATION")
            val rec = if (Build.VERSION.SDK_INT >= 31) MediaRecorder(this) else MediaRecorder()
            recorder = rec
            if (withMic) rec.setAudioSource(MediaRecorder.AudioSource.MIC)
            rec.setVideoSource(MediaRecorder.VideoSource.SURFACE)
            rec.setOutputFormat(MediaRecorder.OutputFormat.MPEG_4)
            val pfd = out.pfd
            val file = out.file
            if (pfd != null) rec.setOutputFile(pfd.fileDescriptor) else rec.setOutputFile(file!!.absolutePath)
            rec.setVideoEncoder(MediaRecorder.VideoEncoder.H264)
            if (withMic) {
                rec.setAudioEncoder(MediaRecorder.AudioEncoder.AAC)
                rec.setAudioEncodingBitRate(128_000)
                rec.setAudioSamplingRate(44_100)
            }
            rec.setVideoSize(width, height)
            rec.setVideoFrameRate(FRAME_RATE)
            rec.setVideoEncodingBitRate(bitrate)
            rec.prepare()

            virtualDisplay = mp.createVirtualDisplay(
                "va-record",
                width,
                height,
                resources.displayMetrics.densityDpi,
                DisplayManager.VIRTUAL_DISPLAY_FLAG_AUTO_MIRROR,
                rec.surface,
                null,
                mainHandler
            )
            rec.start()
            recording = true
            accumulatedMs = 0L
            segmentStart = SystemClock.elapsedRealtime()
            ScreenRecordBridge.setState(RecState.RECORDING)
            updateNotification()
        } catch (e: Exception) {
            fail(lang.tr("تعذّر بدء تسجيل الشاشة.", "Could not start screen recording."))
        }
    }

    // ---------------- Pause / resume / stop ----------------

    private fun togglePause() {
        val rec = recorder ?: return
        if (!recording) return
        try {
            if (!paused) {
                rec.pause()
                accumulatedMs += SystemClock.elapsedRealtime() - segmentStart
                paused = true
                ScreenRecordBridge.setState(RecState.PAUSED)
            } else {
                rec.resume()
                segmentStart = SystemClock.elapsedRealtime()
                paused = false
                ScreenRecordBridge.setState(RecState.RECORDING)
            }
            updateNotification()
        } catch (e: Exception) {
            // ignored
        }
    }

    private fun elapsedMs(): Long =
        accumulatedMs + if (recording && !paused) SystemClock.elapsedRealtime() - segmentStart else 0L

    private fun finishRecording() {
        if (!active) return
        val lang = ProactiveScheduler.language(this)
        val wasRecording = recording
        val duration = elapsedMs()
        var stopped = false
        if (wasRecording) {
            try {
                recorder?.stop()
                stopped = true
            } catch (e: RuntimeException) {
                // stop() fails when no frame was recorded yet: the file is useless.
            }
        }
        teardown()
        val out = output
        output = null
        val saved = if (out != null) commitOutput(out, stopped && duration >= 1000L, duration) else null
        if (saved != null) {
            ScreenRecordBridge.publishSaved(saved)
            showResultNotification(saved)
        } else if (wasRecording) {
            Toast.makeText(
                this,
                lang.tr("التسجيل قصير جداً ولم يُحفظ.", "The recording was too short and was not saved."),
                Toast.LENGTH_LONG
            ).show()
        }
        stopSelf()
    }

    private fun fail(message: String) {
        val out = output
        output = null
        teardown()
        if (out != null) discard(out)
        Toast.makeText(this, message, Toast.LENGTH_LONG).show()
        stopSelf()
    }

    /** Frees everything (the recorder, the virtual display, the projection) and resets the state. */
    private fun teardown() {
        active = false
        recording = false
        paused = false
        mainHandler.removeCallbacksAndMessages(null)
        try { virtualDisplay?.release() } catch (_: Exception) { }
        virtualDisplay = null
        try { recorder?.reset() } catch (_: Exception) { }
        try { recorder?.release() } catch (_: Exception) { }
        recorder = null
        try { projection?.stop() } catch (_: Exception) { }
        projection = null
        projectionData = null
        if (withMic) WakeWordService.setMicBusy(false)
        ScreenRecordBridge.setState(RecState.IDLE)
        stopForeground(STOP_FOREGROUND_REMOVE)
    }

    override fun onDestroy() {
        if (active) finishRecording()
        super.onDestroy()
    }

    // ---------------- Output file ----------------

    private fun openOutput(): Output {
        val stamp = SimpleDateFormat("yyyyMMdd_HHmmss", Locale.US).format(Date())
        val name = "ScreenRecord_$stamp.mp4"
        if (Build.VERSION.SDK_INT >= 29) {
            val values = ContentValues().apply {
                put(MediaStore.Video.Media.DISPLAY_NAME, name)
                put(MediaStore.Video.Media.MIME_TYPE, "video/mp4")
                put(MediaStore.Video.Media.RELATIVE_PATH, Environment.DIRECTORY_MOVIES + "/VoiceAssistant")
                put(MediaStore.Video.Media.IS_PENDING, 1)
            }
            val uri = contentResolver.insert(
                MediaStore.Video.Media.getContentUri(MediaStore.VOLUME_EXTERNAL_PRIMARY),
                values
            ) ?: throw IllegalStateException("Could not create the video entry")
            val pfd = contentResolver.openFileDescriptor(uri, "rw")
                ?: throw IllegalStateException("Could not open the video entry")
            return Output(name, uri, null, pfd)
        }
        // Android 8/9: app folder (Android/data/<app>/files/Movies), no storage permission needed.
        val dir = getExternalFilesDir(Environment.DIRECTORY_MOVIES) ?: File(filesDir, "recordings")
        dir.mkdirs()
        return Output(name, null, File(dir, name), null)
    }

    private fun commitOutput(out: Output, keep: Boolean, durationMs: Long): SavedRecording? {
        try { out.pfd?.close() } catch (_: Exception) { }
        if (!keep) {
            discard(out)
            return null
        }
        return try {
            val uri = out.uri
            val file = out.file
            if (uri != null) {
                val values = ContentValues().apply { put(MediaStore.Video.Media.IS_PENDING, 0) }
                contentResolver.update(uri, values, null, null)
                SavedRecording(uri.toString(), null, out.name, durationMs, querySize(uri), true)
            } else {
                val shareUri = FileProvider.getUriForFile(this, "$packageName.fileprovider", file!!)
                SavedRecording(shareUri.toString(), file.absolutePath, out.name, durationMs, file.length(), false)
            }
        } catch (e: Exception) {
            discard(out)
            null
        }
    }

    private fun discard(out: Output) {
        try { out.pfd?.close() } catch (_: Exception) { }
        try {
            val uri = out.uri
            if (uri != null) contentResolver.delete(uri, null, null) else out.file?.delete()
        } catch (_: Exception) { }
    }

    private fun querySize(uri: Uri): Long {
        return try {
            contentResolver.query(uri, arrayOf(OpenableColumns.SIZE), null, null, null)?.use { c ->
                if (c.moveToFirst()) c.getLong(0) else 0L
            } ?: 0L
        } catch (e: Exception) {
            0L
        }
    }

    private fun freeBytes(): Long {
        return try {
            val dir = getExternalFilesDir(null) ?: filesDir
            StatFs(dir.path).availableBytes
        } catch (e: Exception) {
            Long.MAX_VALUE
        }
    }

    // ---------------- Video size (what the phone's H.264 encoder really supports) ----------------

    private fun avcCaps(): MediaCodecInfo.VideoCapabilities? {
        return try {
            val infos = MediaCodecList(MediaCodecList.REGULAR_CODECS).codecInfos.filter { info ->
                info.isEncoder && info.supportedTypes.any { it.equals("video/avc", ignoreCase = true) }
            }
            // Prefer the hardware encoder (the one MediaRecorder normally uses).
            val preferred = infos.firstOrNull { !it.name.startsWith("OMX.google") && !it.name.startsWith("c2.android") }
                ?: infos.firstOrNull()
            preferred?.getCapabilitiesForType("video/avc")?.videoCapabilities
        } catch (e: Exception) {
            null
        }
    }

    private fun chooseSize(caps: MediaCodecInfo.VideoCapabilities?): Pair<Int, Int> {
        val screen = screenSize()
        val sw = screen.first
        val sh = screen.second
        val wAlign = maxOf(2, caps?.widthAlignment ?: 2)
        val hAlign = maxOf(2, caps?.heightAlignment ?: 2)
        var scale = min(1f, MAX_SHORT_SIDE.toFloat() / min(sw, sh))
        repeat(12) {
            val w = (sw * scale).toInt() / wAlign * wAlign
            val h = (sh * scale).toInt() / hAlign * hAlign
            if (w >= 2 && h >= 2 && (caps == null || caps.isSizeSupported(w, h))) return w to h
            scale *= 0.9f
        }
        return if (sw < sh) 720 to 1280 else 1280 to 720
    }

    /** Real screen size in pixels (width, height). */
    private fun screenSize(): Pair<Int, Int> {
        val wm = getSystemService(WindowManager::class.java)
        return if (Build.VERSION.SDK_INT >= 30) {
            val b = wm.maximumWindowMetrics.bounds
            b.width() to b.height()
        } else {
            val m = resources.displayMetrics
            m.widthPixels to m.heightPixels
        }
    }

    // ---------------- Notifications ----------------

    private fun ensureChannels() {
        val manager = getSystemService(NotificationManager::class.java)
        val lang = ProactiveScheduler.language(this)
        if (manager.getNotificationChannel(CHANNEL_ID) == null) {
            manager.createNotificationChannel(
                NotificationChannel(CHANNEL_ID, lang.tr("تسجيل الشاشة", "Screen recording"), NotificationManager.IMPORTANCE_LOW)
            )
        }
        if (manager.getNotificationChannel(RESULT_CHANNEL_ID) == null) {
            manager.createNotificationChannel(
                NotificationChannel(
                    RESULT_CHANNEL_ID,
                    lang.tr("تسجيلات الشاشة المحفوظة", "Saved screen recordings"),
                    NotificationManager.IMPORTANCE_DEFAULT
                )
            )
        }
    }

    private fun servicePendingIntent(code: Int, action: String): PendingIntent =
        PendingIntent.getService(
            this,
            code,
            Intent(this, ScreenRecordService::class.java).setAction(action),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )

    private fun buildNotification(): Notification {
        ensureChannels()
        val lang = ProactiveScheduler.language(this)
        val open = PendingIntent.getActivity(
            this,
            0,
            Intent(this, MainActivity::class.java)
                .addFlags(Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_SINGLE_TOP),
            PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
        )
        val state = ScreenRecordBridge.state.value
        val builder = NotificationCompat.Builder(this, CHANNEL_ID)
            .setSmallIcon(android.R.drawable.presence_video_busy)
            .setContentIntent(open)
            .setOngoing(true)
            .setOnlyAlertOnce(true)
            .setCategory(NotificationCompat.CATEGORY_SERVICE)
            .setPriority(NotificationCompat.PRIORITY_LOW)

        when (state) {
            RecState.RECORDING -> builder
                .setContentTitle(lang.tr("جارٍ تسجيل الشاشة", "Recording the screen"))
                .setContentText(lang.tr("اضغط «إيقاف» لحفظ الفيديو.", "Tap Stop to save the video."))
                .setUsesChronometer(true)
                .setShowWhen(true)
                .setWhen(System.currentTimeMillis() - elapsedMs())
            RecState.PAUSED -> builder
                .setContentTitle(lang.tr("التسجيل متوقف مؤقتاً", "Recording paused"))
                .setContentText(ScreenRecordBridge.formatDuration(elapsedMs()))
            else -> builder
                .setContentTitle(lang.tr("المساعد الصوتي", "Voice Assistant"))
                .setContentText(
                    lang.tr(
                        "يبدأ تسجيل الشاشة بعد $countdownLeft…",
                        "Screen recording starts in $countdownLeft…"
                    )
                )
        }

        if (state == RecState.RECORDING || state == RecState.PAUSED) {
            val paused = state == RecState.PAUSED
            builder.addAction(
                if (paused) android.R.drawable.ic_media_play else android.R.drawable.ic_media_pause,
                if (paused) lang.tr("متابعة", "Resume") else lang.tr("إيقاف مؤقت", "Pause"),
                servicePendingIntent(11, ACTION_PAUSE_RESUME)
            )
        }
        builder.addAction(
            android.R.drawable.ic_menu_close_clear_cancel,
            lang.tr("إيقاف وحفظ", "Stop & save"),
            servicePendingIntent(12, ACTION_STOP)
        )
        return builder.build()
    }

    private fun updateNotification() {
        try {
            getSystemService(NotificationManager::class.java).notify(NOTIFICATION_ID, buildNotification())
        } catch (e: Exception) {
            // ignored
        }
    }

    private fun showResultNotification(saved: SavedRecording) {
        try {
            ensureChannels()
            val lang = ProactiveScheduler.language(this)
            val flags = PendingIntent.FLAG_IMMUTABLE or PendingIntent.FLAG_UPDATE_CURRENT
            val viewPi = PendingIntent.getActivity(this, 21, ScreenRecordBridge.viewIntent(saved), flags)
            val sharePi = PendingIntent.getActivity(
                this,
                22,
                ScreenRecordBridge.shareIntent(saved, lang.tr("مشاركة التسجيل", "Share recording")),
                flags
            )
            val where = if (saved.inGallery) {
                lang.tr("محفوظ في المعرض (Movies/VoiceAssistant)", "Saved in your gallery (Movies/VoiceAssistant)")
            } else {
                lang.tr("محفوظ في: ", "Saved in: ") + (saved.filePath ?: "")
            }
            val text = ScreenRecordBridge.formatDuration(saved.durationMs) + " • " + ScreenRecordBridge.formatSize(saved.sizeBytes)
            val notification = NotificationCompat.Builder(this, RESULT_CHANNEL_ID)
                .setSmallIcon(android.R.drawable.ic_menu_gallery)
                .setContentTitle(lang.tr("تم حفظ تسجيل الشاشة", "Screen recording saved"))
                .setContentText(text)
                .setStyle(NotificationCompat.BigTextStyle().bigText(text + "\n" + where))
                .setContentIntent(viewPi)
                .setAutoCancel(true)
                .addAction(android.R.drawable.ic_menu_share, lang.tr("مشاركة", "Share"), sharePi)
                .addAction(android.R.drawable.ic_media_play, lang.tr("فتح", "Open"), viewPi)
                .build()
            getSystemService(NotificationManager::class.java).notify(RESULT_NOTIFICATION_ID, notification)
        } catch (e: Exception) {
            // ignored
        }
    }
}
''')

write_file(_REC_PKG + "/ScreenRecordActivity.kt", r'''package com.example.voiceassistant

import android.Manifest
import android.app.Activity
import android.content.pm.PackageManager
import android.media.projection.MediaProjectionManager
import android.os.Build
import android.os.Bundle
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.result.contract.ActivityResultContracts
import androidx.core.content.ContextCompat
import com.example.voiceassistant.service.ProactiveScheduler
import com.example.voiceassistant.service.RecState
import com.example.voiceassistant.service.ScreenRecordBridge
import com.example.voiceassistant.service.ScreenRecordService

/**
 * Transparent screen that asks for the permissions (microphone if chosen, notifications, screen capture)
 * and starts [ScreenRecordService]. Opened again while recording, it stops the recording instead.
 */
class ScreenRecordActivity : ComponentActivity() {

    private var wantMic = false

    private val notificationPermission =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { askProjection() }

    private val micPermission =
        registerForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
            wantMic = granted
            if (!granted) {
                Toast.makeText(
                    this,
                    ProactiveScheduler.language(this).tr(
                        "لم يُمنح إذن الميكروفون: سيُسجَّل الفيديو بدون صوت.",
                        "Microphone permission denied: the video will have no sound."
                    ),
                    Toast.LENGTH_LONG
                ).show()
            }
            askNotificationThenProjection()
        }

    private val projectionLauncher =
        registerForActivityResult(ActivityResultContracts.StartActivityForResult()) { result ->
            val data = result.data
            if (result.resultCode == Activity.RESULT_OK && data != null) {
                ScreenRecordService.start(this, result.resultCode, data, wantMic)
                // Hide the app so the recording shows the phone, not this assistant.
                moveTaskToBack(true)
            }
            finish()
        }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        if (ScreenRecordBridge.state.value != RecState.IDLE) {
            ScreenRecordService.stop(this)
            finish()
            return
        }
        wantMic = ScreenRecordBridge.isMicEnabled(this)
        if (wantMic && ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) !=
            PackageManager.PERMISSION_GRANTED
        ) {
            micPermission.launch(Manifest.permission.RECORD_AUDIO)
        } else {
            askNotificationThenProjection()
        }
    }

    private fun askNotificationThenProjection() {
        if (Build.VERSION.SDK_INT >= 33 &&
            ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) !=
            PackageManager.PERMISSION_GRANTED
        ) {
            // The Stop button of the recording lives in its notification.
            notificationPermission.launch(Manifest.permission.POST_NOTIFICATIONS)
        } else {
            askProjection()
        }
    }

    private fun askProjection() {
        try {
            val manager = getSystemService(MediaProjectionManager::class.java)
            projectionLauncher.launch(manager.createScreenCaptureIntent())
        } catch (e: Exception) {
            Toast.makeText(
                this,
                ProactiveScheduler.language(this).tr("تعذّر طلب إذن تسجيل الشاشة.", "Could not request screen recording permission."),
                Toast.LENGTH_SHORT
            ).show()
            finish()
        }
    }
}
''')

write_file(_REC_PKG + "/ui/components/ScreenRecordResultDialog.kt", r'''package com.example.voiceassistant.ui.components

import android.widget.Toast
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import com.example.voiceassistant.service.SavedRecording
import com.example.voiceassistant.service.ScreenRecordBridge
import com.example.voiceassistant.viewmodel.AppLanguage

/** Shown when a screen recording is finished: share it directly, open it, or delete it. */
@Composable
fun ScreenRecordResultDialog(
    language: AppLanguage,
    rec: SavedRecording,
    onDismiss: () -> Unit
) {
    val context = LocalContext.current
    AlertDialog(
        onDismissRequest = onDismiss,
        title = { Text(language.tr("تم حفظ تسجيل الشاشة", "Screen recording saved")) },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(rec.name, style = MaterialTheme.typography.bodyMedium)
                Text(
                    language.tr("المدة", "Duration") + ": " + ScreenRecordBridge.formatDuration(rec.durationMs) +
                        "  •  " + ScreenRecordBridge.formatSize(rec.sizeBytes),
                    style = MaterialTheme.typography.bodySmall
                )
                Text(
                    if (rec.inGallery) {
                        language.tr("محفوظ في المعرض: Movies/VoiceAssistant", "Saved in your gallery: Movies/VoiceAssistant")
                    } else {
                        language.tr("محفوظ في: ", "Saved in: ") + (rec.filePath ?: "")
                    },
                    style = MaterialTheme.typography.bodySmall
                )
                Row(horizontalArrangement = Arrangement.spacedBy(4.dp), modifier = Modifier) {
                    TextButton(onClick = {
                        try {
                            context.startActivity(ScreenRecordBridge.viewIntent(rec))
                        } catch (e: Exception) {
                            Toast.makeText(
                                context,
                                language.tr("لا يوجد تطبيق لتشغيل الفيديو.", "No app can play the video."),
                                Toast.LENGTH_SHORT
                            ).show()
                        }
                    }) { Text(language.tr("فتح", "Open")) }
                    TextButton(onClick = {
                        ScreenRecordBridge.delete(context, rec)
                        onDismiss()
                    }) {
                        Text(language.tr("حذف", "Delete"), color = MaterialTheme.colorScheme.error)
                    }
                }
            }
        },
        confirmButton = {
            TextButton(onClick = {
                try {
                    context.startActivity(
                        ScreenRecordBridge.shareIntent(rec, language.tr("مشاركة التسجيل", "Share recording"))
                    )
                } catch (e: Exception) {
                    Toast.makeText(
                        context,
                        language.tr("تعذّرت المشاركة.", "Could not share."),
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }) { Text(language.tr("مشاركة", "Share")) }
        },
        dismissButton = {
            TextButton(onClick = onDismiss) { Text(language.tr("إغلاق", "Close")) }
        }
    )
}
''')

# --- AndroidManifest: الخدمة + الشاشة الشفافة ---
insert_before(
    "app/src/main/AndroidManifest.xml",
    "        <!-- FileProvider: gives the camera app a content:// Uri inside our cache folder (Android 7+) -->\n",
    '''        <!-- Screen recording (video, works offline): foreground service + transparent permission screen -->
        <service
            android:name=".service.ScreenRecordService"
            android:exported="false"
            android:foregroundServiceType="mediaProjection|microphone" />

        <activity
            android:name=".ScreenRecordActivity"
            android:exported="false"
            android:excludeFromRecents="true"
            android:theme="@android:style/Theme.Translucent.NoTitleBar" />

''')

# --- FileProvider: مجلدات التسجيل (أندرويد 8/9 فقط؛ من 10 يُحفظ في المعرض عبر MediaStore) ---
_replace_once(
    "app/src/main/res/xml/file_paths.xml",
    '    <cache-path name="camera" path="camera/" />\n',
    '    <cache-path name="camera" path="camera/" />\n'
    '    <!-- Screen recordings on Android 8/9 -->\n'
    '    <external-files-path name="recordings" path="Movies/" />\n'
    '    <files-path name="recordings_internal" path="recordings/" />\n'
)

# --- الاستدعاء الصوتي: تحرير الميكروفون أثناء تسجيل الشاشة بصوت ---
_ww_path = _REC_PKG + "/service/WakeWordService.kt"
_replace_once(
    _ww_path,
    "        private var visibleActivities = 0\n",
    "        private var visibleActivities = 0\n\n"
    "        /** True while the screen recorder is using the microphone (the two must not fight over it). */\n"
    "        @Volatile\n"
    "        private var micBusy = false\n\n"
    "        fun setMicBusy(busy: Boolean) {\n"
    "            micBusy = busy\n"
    "            instance?.onVisibilityChanged()\n"
    "        }\n"
)
_replace_once(
    _ww_path,
    "        if (visibleActivities > 0) pauseListening() else resumeListening()\n",
    "        if (visibleActivities > 0 || micBusy) pauseListening() else resumeListening()\n"
)
_replace_once(
    _ww_path,
    "        if (destroyed || visibleActivities > 0) return\n",
    "        if (destroyed || visibleActivities > 0 || micBusy) return\n"
)
_replace_once(
    _ww_path,
    "        if (visibleActivities == 0) resumeListening() else pauseListening()\n",
    "        if (visibleActivities == 0 && !micBusy) resumeListening() else pauseListening()\n"
)

# --- الأوامر الصوتية: «سجل الشاشة» / «أوقف التسجيل» / «إيقاف مؤقت للتسجيل» ---
_rec_vm_path = _REC_PKG + "/viewmodel/MainViewModel.kt"
insert_before(
    _rec_vm_path,
    "    private fun process(text: String, speak: Boolean = true) {\n",
    r'''    // ---------------- Screen recording by voice ----------------
    /**
     * "سجل الشاشة" / "record my screen" starts, "أوقف التسجيل" / "stop recording" stops (and saves),
     * "إيقاف مؤقت للتسجيل" pauses, "كمّل التسجيل" resumes. Returns true when the text was a recording command.
     */
    private fun handleRecordingCommand(text: String, lang: AppLanguage, speak: Boolean): Boolean {
        val t = WakeWordService.normalize(text)
        // Questions ("كيف أسجل الشاشة؟") go to the normal conversation.
        if (t.startsWith("كيف") || t.startsWith("how") || t.startsWith("ماذا") || t.startsWith("what") ||
            t.endsWith("?") || t.endsWith("؟")
        ) return false

        val app = getApplication<Application>()
        val bridge = com.example.voiceassistant.service.ScreenRecordBridge
        val service = com.example.voiceassistant.service.ScreenRecordService
        val idle = bridge.state.value == com.example.voiceassistant.service.RecState.IDLE

        val mentionsScreen = t.contains("الشاشه") || t.contains("شاشتي") || t.contains("screen")
        val aboutRecording = t.contains("تسجيل") || t.contains("recording") || t.contains("record")
        val startVerb = t.contains("سجل") || t.contains("تسجيل") || t.contains("record")
        val stopVerb = listOf("اوقف", "وقف", "ايقاف", "انهي", "انهاء", "stop", "finish").any { t.contains(it) }
        val pauseVerb = t.contains("مؤقت") || t.contains("pause")
        val resumeVerb = listOf("استانف", "كمل", "استمر", "متابعه", "resume", "continue").any { t.contains(it) }

        when {
            // pause / resume (only while recording)
            !idle && aboutRecording && pauseVerb -> {
                service.togglePause(app)
                reply(lang.tr("تم إيقاف التسجيل مؤقتاً.", "Recording paused."), lang, speak = speak)
                return true
            }
            !idle && aboutRecording && resumeVerb -> {
                service.togglePause(app)
                reply(lang.tr("تابعت التسجيل.", "Recording resumed."), lang, speak = speak)
                return true
            }
            // stop
            aboutRecording && stopVerb && (mentionsScreen || !idle) -> {
                if (idle) {
                    reply(lang.tr("لا يوجد تسجيل جارٍ حالياً.", "No recording is running right now."), lang, speak = speak)
                } else {
                    service.stop(app)
                    reply(
                        lang.tr("أوقفت التسجيل وجارٍ حفظه.", "Stopped the recording and saving it."),
                        lang,
                        speak = speak
                    )
                }
                return true
            }
            // start
            mentionsScreen && startVerb && !stopVerb -> {
                if (!idle) {
                    reply(lang.tr("التسجيل يعمل بالفعل.", "A recording is already running."), lang, speak = speak)
                } else {
                    bridge.requestStart(app)
                    reply(
                        lang.tr(
                            "سأطلب إذن تسجيل الشاشة. اضغط «ابدأ الآن» وسيبدأ التسجيل بعد 3 ثوانٍ.",
                            "I'll ask for screen recording permission. Tap Start now and recording begins after 3 seconds."
                        ),
                        lang,
                        speak = speak
                    )
                }
                return true
            }
        }
        return false
    }

''')
insert_before(
    _rec_vm_path,
    "            val parsed = parser.parse(text)\n",
    "            if (handleRecordingCommand(text, lang, speak)) return@launch\n"
)

# --- الواجهة: قائمة الترس + نافذة نتيجة التسجيل ---
_rec_screen_path = _REC_PKG + "/ui/MainScreen.kt"
insert_before(
    _rec_screen_path,
    "import androidx.compose.material.icons.filled.Psychology\n",
    "import androidx.compose.material.icons.filled.Videocam\n"
    "import androidx.compose.material.icons.filled.Stop\n"
    "import androidx.compose.material.icons.filled.Mic\n"
    "import com.example.voiceassistant.service.RecState\n"
    "import com.example.voiceassistant.service.ScreenRecordBridge\n"
    "import com.example.voiceassistant.service.ScreenRecordService\n"
    "import com.example.voiceassistant.ui.components.ScreenRecordResultDialog\n"
)
insert_before(
    _rec_screen_path,
    "        if (showAiSettings) {\n",
    '''        val recState by ScreenRecordBridge.state.collectAsStateWithLifecycle()
        val savedRecording by ScreenRecordBridge.saved.collectAsStateWithLifecycle()
        var recordMic by remember { mutableStateOf(ScreenRecordBridge.isMicEnabled(context)) }
        savedRecording?.let { rec ->
            ScreenRecordResultDialog(
                language = state.language,
                rec = rec,
                onDismiss = { ScreenRecordBridge.dismissSaved() }
            )
        }
''')
insert_before(
    _rec_screen_path,
    "                                DropdownMenuItem(\n"
    "                                    text = { Text(state.language.tr(\"السيناريوهات\", \"Routines\")) },\n",
    '''                                DropdownMenuItem(
                                    text = {
                                        Text(
                                            if (recState == RecState.IDLE) {
                                                state.language.tr("تسجيل الشاشة بالفيديو", "Record screen")
                                            } else {
                                                state.language.tr("إيقاف تسجيل الشاشة", "Stop screen recording")
                                            }
                                        )
                                    },
                                    leadingIcon = {
                                        Icon(
                                            if (recState == RecState.IDLE) Icons.Filled.Videocam else Icons.Filled.Stop,
                                            contentDescription = null,
                                            tint = if (recState == RecState.IDLE) {
                                                LocalContentColor.current
                                            } else {
                                                MaterialTheme.colorScheme.error
                                            }
                                        )
                                    },
                                    onClick = {
                                        showSettingsMenu = false
                                        if (recState == RecState.IDLE) {
                                            ScreenRecordBridge.requestStart(context)
                                        } else {
                                            ScreenRecordService.stop(context)
                                        }
                                    }
                                )
                                DropdownMenuItem(
                                    text = { Text(state.language.tr("صوت الميكروفون في التسجيل", "Microphone audio in recording")) },
                                    leadingIcon = { Icon(Icons.Filled.Mic, contentDescription = null) },
                                    onClick = {
                                        recordMic = !recordMic
                                        ScreenRecordBridge.setMicEnabled(context, recordMic)
                                    },
                                    trailingIcon = {
                                        Switch(
                                            checked = recordMic,
                                            onCheckedChange = { on ->
                                                recordMic = on
                                                ScreenRecordBridge.setMicEnabled(context, on)
                                            }
                                        )
                                    }
                                )
''')
print(">> Screen video recording injected (ScreenRecordService + ScreenRecordActivity + menu + voice commands).")


# ==============================================================================
# زر تسجيل الشاشة بالفيديو في شريط الإدخال، بجانب زر لقطة الشاشة (لقطة الشاشة لم تتغير).
# يتحول إلى زر إيقاف أحمر أثناء التسجيل. مفتاح صوت الميكروفون يبقى في قائمة الترس.
# ==============================================================================
_rec_bar_path = _REC_PKG + "/ui/components/ChatInputBar.kt"
insert_before(
    _rec_bar_path,
    "import androidx.compose.material.icons.filled.PhotoCamera\n",
    "import androidx.compose.material.icons.filled.Videocam\n"
    "import androidx.compose.material.icons.filled.Stop\n"
    "import androidx.compose.runtime.collectAsState\n"
    "import com.example.voiceassistant.service.RecState\n"
    "import com.example.voiceassistant.service.ScreenRecordBridge\n"
    "import com.example.voiceassistant.service.ScreenRecordService\n"
)
insert_before(
    _rec_bar_path,
    "    // The screenshot is analysed when the app is visible again (so the request is not lost in the background).\n",
    "    val recState by ScreenRecordBridge.state.collectAsState()\n\n"
)
insert_before(
    _rec_bar_path,
    "            MicButton(\n                status = micStatus,\n",
    '''            IconButton(
                onClick = {
                    if (recState == RecState.IDLE) {
                        ScreenRecordBridge.requestStart(context)
                    } else {
                        ScreenRecordService.stop(context)
                    }
                },
                modifier = Modifier.size(40.dp)
            ) {
                Icon(
                    imageVector = if (recState == RecState.IDLE) Icons.Filled.Videocam else Icons.Filled.Stop,
                    contentDescription = if (recState == RecState.IDLE) {
                        language.tr("تسجيل الشاشة بالفيديو", "Record screen")
                    } else {
                        language.tr("إيقاف التسجيل", "Stop recording")
                    },
                    tint = if (recState == RecState.IDLE) {
                        androidx.compose.material3.LocalContentColor.current
                    } else {
                        MaterialTheme.colorScheme.error
                    }
                )
            }
''')
print(">> Screen recording button added next to the screenshot button.")


# ==============================================================================
# نظام الترخيص والحصة اليومية (الدفعة 1: ملفات مستقلة فقط):
#   - CreditsManager: حصة يومية مجانية (5 طلبات) بحماية رجوع الساعة.
#   - LicenseManager: أكواد تفعيل HMAC (ترخيص دائم) + حالة الاشتراك.
#   - PaywallSheet: واجهة «حصة اليوم انتهت» + تفعيل الكود + شراء/اشتراك.
# لا يلمس هذا القسم أي جزء سابق؛ يستخدم _replace_once / insert_before المعرّفتين أعلاه.
# سرّ التوقيع LICENSE_SECRET يأتي من GitHub Secrets أو keys.properties (مثل مفاتيح API).
# ==============================================================================
write_file(_PKG + "/data/CreditsManager.kt", r'''package com.example.voiceassistant.data

import android.content.Context
import android.content.SharedPreferences
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import java.util.TimeZone

/**
 * عدّاد الحصة اليومية المجانية.
 *
 * - من يملك ترخيصاً دائماً أو اشتراكاً نشطاً (LicenseManager.isUnlocked) => بلا حدود.
 * - غير ذلك => DAILY_FREE_MESSAGES طلبات نصية يومياً.
 * - الخصم بعد النجاح فقط: استدعِ canSend() قبل الطلب و recordSuccess() بعد نجاحه.
 *   عند الفشل لا تستدعِ شيئاً فلا تُستهلك الحصة.
 * - حماية الساعة: يُصفَّر العدّاد فقط حين يتحرك اليوم إلى الأمام.
 *
 * ملاحظة: الحالة محلية، ومسح بيانات التطبيق يعيد الحصة.
 */
object CreditsManager {
    const val DAILY_FREE_MESSAGES = 5

    private const val PREFS = "credits_prefs"
    private const val KEY_FREE_USED = "free_used"
    private const val KEY_SAVED_DAY = "saved_day"

    data class CreditsState(
        val freeUsed: Int = 0,
        val freeLimit: Int = DAILY_FREE_MESSAGES,
        val remaining: Int = DAILY_FREE_MESSAGES,
        val unlimited: Boolean = false
    )

    private val lock = Any()
    private var prefs: SharedPreferences? = null

    private val _state = MutableStateFlow(CreditsState())
    val state: StateFlow<CreditsState> = _state.asStateFlow()

    /** يُستدعى من Application.onCreate (وهو آمن عند تكراره). */
    fun init(context: Context) {
        synchronized(lock) {
            if (prefs == null) {
                prefs = context.applicationContext
                    .getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            }
        }
        LicenseManager.init(context)
        synchronized(lock) {
            rollDayIfNeeded()
            publish()
        }
    }

    /** هل يُسمح بإرسال طلب نصي الآن؟ */
    fun canSend(): Boolean = synchronized(lock) {
        if (LicenseManager.isUnlocked()) return true
        rollDayIfNeeded()
        freeUsedToday() < DAILY_FREE_MESSAGES
    }

    /** يُستدعى بعد نجاح الطلب فقط. */
    fun recordSuccess() {
        synchronized(lock) {
            if (LicenseManager.isUnlocked()) { publish(); return }
            rollDayIfNeeded()
            val used = (freeUsedToday() + 1).coerceAtMost(DAILY_FREE_MESSAGES)
            prefs?.edit()?.putInt(KEY_FREE_USED, used)?.apply()
            publish()
        }
    }

    fun freeLeft(): Int = synchronized(lock) {
        rollDayIfNeeded()
        (DAILY_FREE_MESSAGES - freeUsedToday()).coerceAtLeast(0)
    }

    /** تُستدعى من LicenseManager عند تغيّر الترخيص/الاشتراك لتحديث الواجهة. */
    fun refresh() {
        synchronized(lock) { publish() }
    }

    // ---- داخلي ----

    private fun freeUsedToday(): Int = prefs?.getInt(KEY_FREE_USED, 0) ?: 0

    private fun currentDay(): Long {
        val now = System.currentTimeMillis()
        val offset = TimeZone.getDefault().getOffset(now)
        return (now + offset) / 86_400_000L
    }

    /** يصفّر فقط إذا تحرك التاريخ للأمام. إرجاع الساعة للخلف لا يمنح حصة. */
    private fun rollDayIfNeeded() {
        val p = prefs ?: return
        val today = currentDay()
        val saved = p.getLong(KEY_SAVED_DAY, -1L)
        if (saved == -1L || today > saved) {
            p.edit()
                .putInt(KEY_FREE_USED, 0)
                .putLong(KEY_SAVED_DAY, today)
                .apply()
        }
    }

    private fun publish() {
        val used = freeUsedToday()
        _state.value = CreditsState(
            freeUsed = used,
            freeLimit = DAILY_FREE_MESSAGES,
            remaining = (DAILY_FREE_MESSAGES - used).coerceAtLeast(0),
            unlimited = LicenseManager.isUnlocked()
        )
    }
}
''')

write_file(_PKG + "/data/LicenseManager.kt", r'''package com.example.voiceassistant.data

import android.content.Context
import android.content.SharedPreferences
import com.example.voiceassistant.BuildConfig
import java.security.MessageDigest
import javax.crypto.Mac
import javax.crypto.spec.SecretKeySpec

/**
 * ملاحظات أمنية مهمة:
 *
 * 1) LICENSE_SECRET مدمج داخل APK، فيمكن استخراجه بـ apktool/jadx. من يستخرجه
 *    يستطيع توليد أكواد صالحة. هذا مقبول لبيع صغير (حتى مئات المستخدمين).
 * 2) للتوسع استخدم توقيعاً غير متماثل: Ed25519 (RFC 8032) أو RSA-PSS، بحيث
 *    يبقى المفتاح الخاص عند المطوّر ويحمل التطبيق المفتاح العام فقط.
 * 3) الحالة محلية: مسح بيانات التطبيق يزيل الترخيص والـ nonces المستخدمة
 *    (أعد الكود نفسه للتفعيل من جديد)، ويعيد الحصة اليومية.
 * 4) حالة الاشتراك تُكتب من طبقة Billing (لاحقاً) ويجب إعادة التحقق منها
 *    عند كل تشغيل؛ لا تعتمد على التخزين المحلي وحده.
 *
 * صيغة الكود: ZEV-<nonce>-<signature>
 *   nonce     : 6 أحرف من ABCDEFGHIJKLMNOPQRSTUVWXYZ234567
 *   signature : أول 8 أحرف (hex كبيرة) من HMAC-SHA256 للرسالة "ZEV|<nonce>"
 *               بمفتاح BuildConfig.LICENSE_SECRET
 * الكود = ترخيص دائم لمرة واحدة، وكل nonce يُستخدم مرة واحدة.
 */
object LicenseManager {

    sealed class RedeemResult {
        object Success : RedeemResult()
        object Invalid : RedeemResult()
        object AlreadyUsed : RedeemResult()
        object NotConfigured : RedeemResult()
        data class Locked(val minutes: Int) : RedeemResult()
    }

    data class RedeemHistoryEntry(val codeShort: String, val timestamp: Long)

    private const val PREFS = "license_prefs"
    private const val KEY_LIFETIME = "lifetime"
    private const val KEY_USED_NONCES = "used_nonces"
    private const val KEY_HISTORY = "history"
    private const val KEY_FAILS = "fails"
    private const val KEY_LOCK_UNTIL = "lock_until"
    private const val KEY_SUB_ACTIVE = "sub_active"
    private const val KEY_SUB_EXPIRY = "sub_expiry"

    private const val PREFIX = "ZEV"
    private const val ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567"
    private const val NONCE_LEN = 6
    private const val SIG_LEN = 8
    private const val MAX_FAILS = 5
    private const val LOCK_MINUTES = 10
    private const val MAX_HISTORY = 20

    private val lock = Any()
    private var prefs: SharedPreferences? = null

    fun init(context: Context) {
        synchronized(lock) {
            if (prefs == null) {
                prefs = context.applicationContext
                    .getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            }
        }
    }

    // ---------------- الحالة ----------------

    fun hasLifetime(): Boolean = prefs?.getBoolean(KEY_LIFETIME, false) ?: false

    /** expiry = 0 يعني بلا تاريخ انتهاء معروف (يعتمد على Billing). */
    fun subscriptionActive(): Boolean {
        val p = prefs ?: return false
        if (!p.getBoolean(KEY_SUB_ACTIVE, false)) return false
        val expiry = p.getLong(KEY_SUB_EXPIRY, 0L)
        return expiry == 0L || expiry > System.currentTimeMillis()
    }

    /** هل التطبيق مفتوح بلا حدود (ترخيص دائم أو اشتراك نشط)؟ */
    fun isUnlocked(): Boolean = hasLifetime() || subscriptionActive()

    /** تُستدعى من طبقة Billing بعد التحقق من حالة الاشتراك. */
    fun setSubscription(active: Boolean, expiryMillis: Long = 0L) {
        synchronized(lock) {
            prefs?.edit()
                ?.putBoolean(KEY_SUB_ACTIVE, active)
                ?.putLong(KEY_SUB_EXPIRY, expiryMillis)
                ?.apply()
        }
        CreditsManager.refresh()
    }

    // ---------------- التفعيل ----------------

    fun redeem(context: Context, rawCode: String): RedeemResult {
        init(context)
        synchronized(lock) {
            val p = prefs ?: return RedeemResult.Invalid

            val secret = BuildConfig.LICENSE_SECRET
            if (secret.isBlank()) return RedeemResult.NotConfigured

            val now = System.currentTimeMillis()
            val lockUntil = p.getLong(KEY_LOCK_UNTIL, 0L)
            if (lockUntil > now) {
                val mins = (((lockUntil - now) + 59_999L) / 60_000L).toInt().coerceAtLeast(1)
                return RedeemResult.Locked(mins)
            }

            val code = rawCode.trim().uppercase().replace(" ", "")
            val parts = code.split("-")
            val valid = parts.size == 3 &&
                parts[0] == PREFIX &&
                parts[1].length == NONCE_LEN && parts[1].all { it in ALPHABET } &&
                parts[2].length == SIG_LEN &&
                signatureMatches(secret, parts[1], parts[2])

            if (!valid) return registerFailure(p, now)

            val nonce = parts[1]
            val used = p.getStringSet(KEY_USED_NONCES, emptySet())!!.toMutableSet()
            if (nonce in used) return RedeemResult.AlreadyUsed

            used.add(nonce)
            p.edit()
                .putStringSet(KEY_USED_NONCES, used)
                .putBoolean(KEY_LIFETIME, true)
                .putInt(KEY_FAILS, 0)
                .putLong(KEY_LOCK_UNTIL, 0L)
                .apply()
            recordHistory(p, "$PREFIX-${nonce.take(3)}…", now)
            CreditsManager.refresh()
            return RedeemResult.Success
        }
    }

    fun history(context: Context): List<RedeemHistoryEntry> {
        init(context)
        val raw = prefs?.getString(KEY_HISTORY, "") ?: ""
        if (raw.isEmpty()) return emptyList()
        return raw.split("\n").mapNotNull { line ->
            val i = line.indexOf('|')
            if (i <= 0) return@mapNotNull null
            val ts = line.substring(0, i).toLongOrNull() ?: return@mapNotNull null
            RedeemHistoryEntry(codeShort = line.substring(i + 1), timestamp = ts)
        }
    }

    // ---------------- داخلي ----------------

    private fun registerFailure(p: SharedPreferences, now: Long): RedeemResult {
        val fails = p.getInt(KEY_FAILS, 0) + 1
        return if (fails >= MAX_FAILS) {
            p.edit()
                .putInt(KEY_FAILS, 0)
                .putLong(KEY_LOCK_UNTIL, now + LOCK_MINUTES * 60_000L)
                .apply()
            RedeemResult.Locked(LOCK_MINUTES)
        } else {
            p.edit().putInt(KEY_FAILS, fails).apply()
            RedeemResult.Invalid
        }
    }

    private fun recordHistory(p: SharedPreferences, codeShort: String, ts: Long) {
        val old = history(p)
        val entries = (listOf("$ts|$codeShort") + old).take(MAX_HISTORY)
        p.edit().putString(KEY_HISTORY, entries.joinToString("\n")).apply()
    }

    private fun history(p: SharedPreferences): List<String> {
        val raw = p.getString(KEY_HISTORY, "") ?: ""
        return if (raw.isEmpty()) emptyList() else raw.split("\n")
    }

    private fun signatureMatches(secret: String, nonce: String, given: String): Boolean {
        val expected = sign(secret, nonce)
        // مقارنة آمنة زمنياً
        return MessageDigest.isEqual(
            expected.toByteArray(Charsets.UTF_8),
            given.toByteArray(Charsets.UTF_8)
        )
    }

    private fun sign(secret: String, nonce: String): String {
        val mac = Mac.getInstance("HmacSHA256")
        mac.init(SecretKeySpec(secret.toByteArray(Charsets.UTF_8), "HmacSHA256"))
        val bytes = mac.doFinal("$PREFIX|$nonce".toByteArray(Charsets.UTF_8))
        return bytes.joinToString("") { "%02X".format(it) }.take(SIG_LEN)
    }
}
''')

write_file(_PKG + "/ui/components/PaywallSheet.kt", r'''package com.example.voiceassistant.ui.components

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.ModalBottomSheet
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Text
import androidx.compose.material3.rememberModalBottomSheetState
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.unit.dp
import com.example.voiceassistant.data.CreditsManager
import com.example.voiceassistant.data.LicenseManager
import java.text.SimpleDateFormat
import java.util.Date
import java.util.Locale

/**
 * @param onBuyLicense  يفتح شراء الترخيص الدائم (رابط المتجر أو تدفق الدفع)
 * @param onSubscribe   يبدأ تدفق الاشتراك (Billing، يُربط لاحقاً)
 * @param initialCode   كود يُملأ مسبقاً في الحقل (مثلاً من رابط عميق)
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PaywallSheet(
    onDismiss: () -> Unit,
    onBuyLicense: () -> Unit,
    onSubscribe: () -> Unit,
    initialCode: String? = null
) {
    val context = LocalContext.current
    val sheetState = rememberModalBottomSheetState(skipPartiallyExpanded = true)
    val credits by CreditsManager.state.collectAsState()

    var code by remember { mutableStateOf("") }
    var message by remember { mutableStateOf<String?>(null) }
    var success by remember { mutableStateOf(false) }
    var history by remember { mutableStateOf(LicenseManager.history(context)) }

    LaunchedEffect(initialCode) {
        if (!initialCode.isNullOrBlank()) code = initialCode
    }

    val dateFmt = remember { SimpleDateFormat("dd/MM HH:mm", Locale.US) }

    ModalBottomSheet(onDismissRequest = onDismiss, sheetState = sheetState) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .verticalScroll(rememberScrollState())
                .padding(horizontal = 20.dp, vertical = 8.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = if (credits.unlimited) "التطبيق مفتوح بلا حدود"
                else if (credits.remaining == 0) "حصة اليوم انتهت"
                else "حصتك اليومية",
                style = MaterialTheme.typography.titleLarge
            )

            // بطاقة الحصة
            Card(
                modifier = Modifier.fillMaxWidth(),
                colors = CardDefaults.cardColors(
                    containerColor = MaterialTheme.colorScheme.surfaceVariant
                )
            ) {
                Column(Modifier.padding(16.dp)) {
                    Text(
                        text = if (credits.unlimited) "بلا حدود"
                        else "${credits.remaining} / ${credits.freeLimit}",
                        style = MaterialTheme.typography.headlineMedium
                    )
                    Text(
                        text = if (credits.unlimited) "ترخيص دائم أو اشتراك نشط"
                        else "الطلبات المجانية المتبقية اليوم",
                        style = MaterialTheme.typography.bodyMedium
                    )
                }
            }

            // إدخال الكود
            OutlinedTextField(
                value = code,
                onValueChange = { code = it; message = null },
                modifier = Modifier.fillMaxWidth(),
                label = { Text("كود التفعيل") },
                placeholder = { Text("ZEV-XXXXXX-XXXXXXXX") },
                singleLine = true
            )
            Button(
                onClick = {
                    val result = LicenseManager.redeem(context, code)
                    success = result is LicenseManager.RedeemResult.Success
                    message = when (result) {
                        is LicenseManager.RedeemResult.Success -> {
                            code = ""
                            history = LicenseManager.history(context)
                            "تم التفعيل: ترخيص دائم"
                        }
                        is LicenseManager.RedeemResult.Invalid -> "الكود غير صحيح"
                        is LicenseManager.RedeemResult.AlreadyUsed -> "هذا الكود مستخدم سابقاً"
                        is LicenseManager.RedeemResult.NotConfigured -> "التفعيل غير مُهيّأ في هذه النسخة"
                        is LicenseManager.RedeemResult.Locked ->
                            "محاولات كثيرة. حاول بعد ${result.minutes} دقيقة"
                    }
                },
                enabled = code.isNotBlank(),
                modifier = Modifier.fillMaxWidth()
            ) { Text("تفعيل") }

            message?.let {
                Text(
                    text = it,
                    color = if (success) Color(0xFF2E7D32) else MaterialTheme.colorScheme.error,
                    style = MaterialTheme.typography.bodyMedium
                )
            }

            // الشراء والاشتراك
            if (!credits.unlimited) {
                Spacer(Modifier.height(4.dp))
                Button(onClick = onBuyLicense, modifier = Modifier.fillMaxWidth()) {
                    Text("شراء ترخيص دائم")
                }
                OutlinedButton(onClick = onSubscribe, modifier = Modifier.fillMaxWidth()) {
                    Text("اشتراك")
                }
            }

            // آخر عمليات التفعيل
            if (history.isNotEmpty()) {
                Spacer(Modifier.height(4.dp))
                Text("آخر عمليات التفعيل", style = MaterialTheme.typography.titleSmall)
                history.forEach { e ->
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.spacedBy(12.dp)
                    ) {
                        Text(
                            text = dateFmt.format(Date(e.timestamp)),
                            fontFamily = FontFamily.Monospace,
                            style = MaterialTheme.typography.bodySmall
                        )
                        Text(
                            text = "ترخيص دائم  (${e.codeShort})",
                            fontFamily = FontFamily.Monospace,
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            }
            Spacer(Modifier.height(24.dp))
        }
    }
}
''')

# LICENSE_SECRET في BuildConfig (مطلوب لـ LicenseManager)
_replace_once(
    "app/build.gradle.kts",
    '        buildConfigField("String", "CLAUDE_API_KEY", "\\"${buildKey("CLAUDE_API_KEY")}\\"")\n',
    '        buildConfigField("String", "CLAUDE_API_KEY", "\\"${buildKey("CLAUDE_API_KEY")}\\"")\n'
    '        buildConfigField("String", "LICENSE_SECRET", "\\"${buildKey("LICENSE_SECRET")}\\"")\n'
)

# تمرير السر من GitHub Secrets إلى خطوة البناء فقط
_replace_once(
    ".github/workflows/build.yml",
    "      - name: Build debug APK\n        run: ./gradlew assembleDebug --stacktrace\n        env:\n",
    "      - name: Build debug APK\n        run: ./gradlew assembleDebug --stacktrace\n        env:\n"
    "          LICENSE_SECRET: ${{ secrets.LICENSE_SECRET }}\n"
)
print(">> Credits + License + Paywall files injected (LICENSE_SECRET added to BuildConfig).")


# ==============================================================================
# الدفعة 2: ربط الحصة اليومية بمنطق الإرسال.
#   - VoiceAssistantApp: CreditsManager.init بعد AiSettings.init.
#   - MainViewModel: بوابة واحدة ensureQuota (دالة منطقية) + recordSuccess بعد نجاح كل طلب ذكاء اصطناعي.
#   - MainUiState.showPaywall + openPaywall/dismissPaywall.
#   - MainScreen: زر الحصة في الشريط العلوي قبل الترس + PaywallSheet.
# كل نقطة تُدرج/تُستبدل مرة واحدة بالضبط (insert_before / _replace_once ترميان RuntimeError واضحاً).
# handleRecordingCommand ليست ذكاءً اصطناعياً ولا تُلمس.
# ==============================================================================
_Q_APP = _PKG + "/VoiceAssistantApp.kt"
_Q_STATE = _PKG + "/viewmodel/MainUiState.kt"
_Q_VM = _PKG + "/viewmodel/MainViewModel.kt"
_Q_SCREEN = _PKG + "/ui/MainScreen.kt"

# ---- 1) VoiceAssistantApp.kt ----
insert_before(
    _Q_APP,
    "import com.example.voiceassistant.data.ConversationRepository\n",
    "import com.example.voiceassistant.data.CreditsManager\n"
)
_replace_once(
    _Q_APP,
    "        AiSettings.init(this)\n",
    "        AiSettings.init(this)\n"
    "        // Daily free quota + license state (the license reads BuildConfig.LICENSE_SECRET).\n"
    "        CreditsManager.init(this)\n"
)

# ---- 2) MainUiState.kt ----
_replace_once(
    _Q_STATE,
    "    val recentProjects: List<MemoryEntry> = emptyList()\n)",
    "    val recentProjects: List<MemoryEntry> = emptyList(),\n"
    "    /** The quota / license sheet is open (quota button, or the free quota ran out). */\n"
    "    val showPaywall: Boolean = false\n)"
)

# ---- 3) MainViewModel.kt: import + البوابة + openPaywall/dismissPaywall ----
insert_before(
    _Q_VM,
    "import com.example.voiceassistant.data.ChatHistoryManager\n",
    "import com.example.voiceassistant.data.CreditsManager\n"
)
insert_before(
    _Q_VM,
    "    private suspend fun askAi(text: String, lang: AppLanguage, speak: Boolean = true) {\n",
    r'''    fun openPaywall() {
        _uiState.update { it.copy(showPaywall = true) }
    }

    fun dismissPaywall() {
        _uiState.update { it.copy(showPaywall = false) }
    }

    /**
     * يفحص الحصة، ويعرض رسالة + يفتح شاشة الدفع إن نفدت، ويوقف المحادثة المستمرة.
     * @return true إذا كان مسموحاً بالمتابعة.
     */
    private fun ensureQuota(lang: AppLanguage, speak: Boolean): Boolean {
        if (CreditsManager.canSend()) return true
        reply(
            lang.tr(
                "انتهت حصتك اليومية المجانية. افتح «الحصة» للترقية.",
                "Your free daily quota is used up. Open \"Quota\" to upgrade."
            ),
            lang,
            speak = speak
        )
        conversationActive = false
        _uiState.update { it.copy(showPaywall = true) }
        return false
    }

'''
)

# ---- 3-1) askAi(): بوابة في البداية + recordSuccess بعد reply() ----
_replace_once(
    _Q_VM,
    r'''    private suspend fun askAi(text: String, lang: AppLanguage, speak: Boolean = true) {
        when (val result = ai.ask(text, lang)) {
            is AiResult.Success -> reply(result.text, lang, result.code, speak = speak)
''',
    r'''    private suspend fun askAi(text: String, lang: AppLanguage, speak: Boolean = true) {
        if (!ensureQuota(lang, speak)) return
        when (val result = ai.ask(text, lang)) {
            is AiResult.Success -> {
                reply(result.text, lang, result.code, speak = speak)
                CreditsManager.recordSuccess()
            }
'''
)

# ---- 3-2) generateImage(): بوابة في البداية + recordSuccess بعد reply() (وليس عند فشل الحفظ) ----
_replace_once(
    _Q_VM,
    r'''    private suspend fun generateImage(prompt: String, lang: AppLanguage, speak: Boolean = true) {
        when (val result = ai.generateImage(prompt)) {
''',
    r'''    private suspend fun generateImage(prompt: String, lang: AppLanguage, speak: Boolean = true) {
        if (!ensureQuota(lang, speak)) return
        when (val result = ai.generateImage(prompt)) {
'''
)
_replace_once(
    _Q_VM,
    r'''                    reply(lang.tr("تفضل، هذه هي الصورة.", "Here is your image."), lang, imagePath = path, speak = speak)
''',
    r'''                    reply(lang.tr("تفضل، هذه هي الصورة.", "Here is your image."), lang, imagePath = path, speak = speak)
                    CreditsManager.recordSuccess()
'''
)

# ---- 3-3) handleTranslation(): بوابة قبل ai.ask() + recordSuccess بعد reply() في المسارين ----
_replace_once(
    _Q_VM,
    r'''        _uiState.update { it.copy(status = AssistantStatus.PROCESSING, partialText = "") }
        when (val result = ai.ask(prompt, target)) {
''',
    r'''        if (!ensureQuota(lang, speak)) return
        _uiState.update { it.copy(status = AssistantStatus.PROCESSING, partialText = "") }
        when (val result = ai.ask(prompt, target)) {
'''
)
_replace_once(
    _Q_VM,
    r'''                    reply(translated, target, speak = speak)
                    return
''',
    r'''                    reply(translated, target, speak = speak)
                    CreditsManager.recordSuccess()
                    return
'''
)
_replace_once(
    _Q_VM,
    r'''                    speak = speak
                )
            }
            is AiResult.Error -> replyAiError(result.kind, result.detail, lang, speak)
        }
    }

    // ---------------- Screen recording by voice''',
    r'''                    speak = speak
                )
                CreditsManager.recordSuccess()
            }
            is AiResult.Error -> replyAiError(result.kind, result.detail, lang, speak)
        }
    }

    // ---------------- Screen recording by voice'''
)

# ---- 3-4) TypeText (process): بوابة قبل ai.generateTextToType() + recordSuccess داخل Success ----
_replace_once(
    _Q_VM,
    r'''            if (parsed is ParsedCommand.TypeText) {
                _uiState.update { it.copy(status = AssistantStatus.PROCESSING, partialText = "") }
''',
    r'''            if (parsed is ParsedCommand.TypeText) {
                if (!ensureQuota(lang, speak)) return@launch
                _uiState.update { it.copy(status = AssistantStatus.PROCESSING, partialText = "") }
'''
)
_replace_once(
    _Q_VM,
    r'''                    }
                } else {
                    val errDetails = (result as? AiResult.Error)?.detail ?: "Unknown Error"
''',
    r'''                    }
                    CreditsManager.recordSuccess()
                } else {
                    val errDetails = (result as? AiResult.Error)?.detail ?: "Unknown Error"
'''
)

# ---- 3-5) handleClipboardShare(): بوابة فقط عند summarize + recordSuccess داخل Success ----
_replace_once(
    _Q_VM,
    r'''        val message = if (command.summarize) {
            _uiState.update { it.copy(status = AssistantStatus.PROCESSING, partialText = "") }
''',
    r'''        val message = if (command.summarize) {
            if (!ensureQuota(lang, speak)) return
            _uiState.update { it.copy(status = AssistantStatus.PROCESSING, partialText = "") }
'''
)
_replace_once(
    _Q_VM,
    r'''                is AiResult.Success -> result.text.trim()
''',
    r'''                is AiResult.Success -> {
                    CreditsManager.recordSuccess()
                    result.text.trim()
                }
'''
)

# ---- 3-6) sendTyped(): مسار الصور/PDF فقط (النص وملفات الكود تمر عبر askAi) ----
_replace_once(
    _Q_VM,
    r'''            when (val result = ai.askWithFile(askPrompt, lang, attachment.mime, attachment.name, attachment.bytes)) {
                is AiResult.Success -> reply(result.text, lang, result.code, speak = attachment.speakReply)
''',
    r'''            if (!ensureQuota(lang, attachment.speakReply)) return@launch
            when (val result = ai.askWithFile(askPrompt, lang, attachment.mime, attachment.name, attachment.bytes)) {
                is AiResult.Success -> {
                    reply(result.text, lang, result.code, speak = attachment.speakReply)
                    CreditsManager.recordSuccess()
                }
'''
)

# ---- 4) MainScreen.kt: زر الحصة قبل الترس + PaywallSheet ----
insert_before(
    _Q_SCREEN,
    "import com.example.voiceassistant.ui.components.AiSettingsSheet\n",
    "import com.example.voiceassistant.ui.components.PaywallSheet\n"
)
insert_before(
    _Q_SCREEN,
    "import com.example.voiceassistant.data.SavedSession\n",
    "import com.example.voiceassistant.data.CreditsManager\n"
)
insert_before(
    _Q_SCREEN,
    "    val routines by viewModel.routines.collectAsStateWithLifecycle()\n",
    "    val credits by CreditsManager.state.collectAsStateWithLifecycle()\n"
)
insert_before(
    _Q_SCREEN,
    "        if (showAiSettings) {\n            AiSettingsSheet(\n",
    r'''        if (state.showPaywall) {
            PaywallSheet(
                onDismiss = viewModel::dismissPaywall,
                onBuyLicense = {},
                onSubscribe = {}
            )
        }
'''
)
_replace_once(
    _Q_SCREEN,
    "                    actions = {\n                        Box {\n                            IconButton(onClick = { showSettingsMenu = true }) {\n",
    r'''                    actions = {
                        TextButton(onClick = viewModel::openPaywall) {
                            Text(
                                text = if (credits.unlimited) {
                                    state.language.tr("بلا حدود", "Unlimited")
                                } else {
                                    state.language.tr(
                                        "حصة ${credits.remaining}/${credits.freeLimit}",
                                        "Quota ${credits.remaining}/${credits.freeLimit}"
                                    )
                                },
                                maxLines = 1
                            )
                        }
                        Box {
                            IconButton(onClick = { showSettingsMenu = true }) {
'''
)
print(">> Quota gate wired: App.init, MainViewModel (6 AI call sites), MainUiState.showPaywall, MainScreen quota button + PaywallSheet.")


# ==============================================================================
# الدفعة 3: طبقة Billing (Google Play Billing 7.1.1) مع محاكاة debug فقط.
#   - build.gradle.kts: اعتمادية billing-ktx + معرّفا المنتجين في BuildConfig.
#   - billing/BillingManager.kt: الاتصال + الشراء/الاشتراك + queryPurchasesAsync عند كل تشغيل و24 ساعة.
#   - billing/DebugPurchaseSimulator.kt: محاكاة شراء تعمل فقط حين BuildConfig.DEBUG (ملف منفصل).
#   - LicenseManager.grantLifetime، VoiceAssistantApp، MainActivity، MainScreen، PaywallSheet، ProGuard.
# build.yml لا يُلمس في هذه الدفعة. كل نقطة تُدرج/تُستبدل مرة واحدة بالضبط.
# ملاحظة: على APK مثبّت خارج Google Play يصبح BillingState.Unavailable (متوقع)، وتبقى الأكواد قناة البيع.
# ==============================================================================
_B_GRADLE = "app/build.gradle.kts"
_B_APP = _PKG + "/VoiceAssistantApp.kt"
_B_ACT = _PKG + "/MainActivity.kt"
_B_SCREEN = _PKG + "/ui/MainScreen.kt"
_B_PAYWALL = _PKG + "/ui/components/PaywallSheet.kt"
_B_LICENSE = _PKG + "/data/LicenseManager.kt"

# ---- 1) app/build.gradle.kts ----
insert_before(
    _B_GRADLE,
    "    // HTTP client for the conversational AI service\n",
    '    // Google Play Billing (license + subscription). Unavailable on APKs installed outside Google Play.\n'
    '    implementation("com.android.billingclient:billing-ktx:7.1.1")\n\n'
)
_replace_once(
    _B_GRADLE,
    '        buildConfigField("String", "LICENSE_SECRET", "\\"${buildKey("LICENSE_SECRET")}\\"")\n',
    '        buildConfigField("String", "LICENSE_SECRET", "\\"${buildKey("LICENSE_SECRET")}\\"")\n'
    '        buildConfigField("String", "BILLING_LIFETIME_SKU", "\\"premium_lifetime\\"")\n'
    '        buildConfigField("String", "BILLING_MONTHLY_SKU", "\\"premium_monthly\\"")\n'
)

# ---- 2) billing/BillingManager.kt ----
write_file(_PKG + "/billing/BillingManager.kt", r'''package com.example.voiceassistant.billing

import android.app.Activity
import android.content.Context
import android.content.SharedPreferences
import android.util.Log
import com.android.billingclient.api.AcknowledgePurchaseParams
import com.android.billingclient.api.BillingClient
import com.android.billingclient.api.BillingClientStateListener
import com.android.billingclient.api.BillingFlowParams
import com.android.billingclient.api.BillingResult
import com.android.billingclient.api.PendingPurchasesParams
import com.android.billingclient.api.Purchase
import com.android.billingclient.api.PurchasesUpdatedListener
import com.android.billingclient.api.QueryProductDetailsParams
import com.android.billingclient.api.QueryPurchasesParams
import com.android.billingclient.api.acknowledgePurchase
import com.android.billingclient.api.queryProductDetails
import com.android.billingclient.api.queryPurchasesAsync
import com.example.voiceassistant.BuildConfig
import com.example.voiceassistant.data.LicenseManager
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

enum class BillingState { Idle, Connecting, Ready, Purchasing, Unavailable, Error }

/**
 * طبقة Google Play Billing.
 *
 * - على APK مثبّت خارج Google Play يصبح الوضع Unavailable (متوقع)؛ أكواد التفعيل تبقى قناة البيع.
 * - التحقق داخل التطبيق فقط: queryPurchasesAsync عند كل اتصال + مرة كل 24 ساعة على الأقل
 *   (resumeChecking). لا خادم ولا Play Developer API. قابل للتجاوز على أجهزة معدّلة.
 * - لا يوجد تاريخ انتهاء في Purchase (billing-ktx 7.1.1): Google Play لا يعيد في الاستعلام إلا
 *   الاشتراكات النشطة، فغياب الاشتراك في نتيجة ناجحة يعني إلغاء تفعيله محلياً.
 * - لا محاكاة هنا: انظر DebugPurchaseSimulator (ملف منفصل، DEBUG فقط).
 */
object BillingManager {
    private const val TAG = "Billing"
    private const val PREFS = "billing_prefs"
    private const val KEY_LAST_CHECK = "last_check"
    private const val CHECK_INTERVAL_MS = 24L * 60L * 60L * 1000L
    private const val CONNECT_TIMEOUT_MS = 15_000L

    private val _state = MutableStateFlow(BillingState.Idle)
    val state: StateFlow<BillingState> = _state.asStateFlow()

    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.Main.immediate)
    private var appContext: Context? = null
    private var prefs: SharedPreferences? = null
    private var client: BillingClient? = null

    private val purchasesListener = PurchasesUpdatedListener { result, purchases ->
        onPurchasesUpdated(result, purchases)
    }

    /** يُستدعى من VoiceAssistantApp.onCreate بعد CreditsManager.init. */
    fun init(context: Context) {
        if (appContext != null) return
        val app = context.applicationContext
        appContext = app
        prefs = app.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        startConnection()
    }

    fun startConnection() {
        val ctx = appContext ?: return
        try {
            if (_state.value == BillingState.Connecting) return
            val existing = client
            if (existing != null && existing.isReady) {
                if (_state.value == BillingState.Idle || _state.value == BillingState.Unavailable) {
                    _state.value = BillingState.Ready
                }
                return
            }
            _state.value = BillingState.Connecting
            val c = existing ?: BillingClient.newBuilder(ctx)
                .setListener(purchasesListener)
                .enablePendingPurchases(
                    PendingPurchasesParams.newBuilder().enableOneTimeProducts().build()
                )
                .build()
                .also { client = it }
            c.startConnection(object : BillingClientStateListener {
                override fun onBillingSetupFinished(result: BillingResult) {
                    try {
                        if (result.responseCode == BillingClient.BillingResponseCode.OK) {
                            _state.value = BillingState.Ready
                            scope.launch { querySync() }
                        } else {
                            // متوقع على APK خارج Google Play.
                            Log.w(TAG, "Billing unavailable: ${result.responseCode} ${result.debugMessage}")
                            _state.value = BillingState.Unavailable
                        }
                    } catch (e: Exception) {
                        Log.w(TAG, "onBillingSetupFinished failed", e)
                        _state.value = BillingState.Error
                    }
                }

                override fun onBillingServiceDisconnected() {
                    Log.w(TAG, "Billing service disconnected")
                    _state.value = BillingState.Unavailable
                }
            })
            // بعض الأجهزة بلا Google Play لا تستدعي أي callback: لا نبقى في Connecting إلى الأبد.
            scope.launch {
                delay(CONNECT_TIMEOUT_MS)
                if (_state.value == BillingState.Connecting) _state.value = BillingState.Unavailable
            }
        } catch (e: Exception) {
            Log.w(TAG, "startConnection failed", e)
            _state.value = BillingState.Error
        }
    }

    /** شراء الترخيص الدائم (منتج لمرة واحدة). يحتاج Activity لا Context. */
    fun launchPurchase(activity: Activity, sku: String) =
        launchFlow(activity, sku, BillingClient.ProductType.INAPP)

    /** بدء الاشتراك. يحتاج Activity لا Context. */
    fun launchSubscribe(activity: Activity, sku: String) =
        launchFlow(activity, sku, BillingClient.ProductType.SUBS)

    private fun launchFlow(activity: Activity, sku: String, productType: String) {
        val c = client
        if (c == null || !c.isReady) {
            Log.w(TAG, "Billing client not ready; reconnecting")
            startConnection()
            return
        }
        scope.launch {
            try {
                _state.value = BillingState.Purchasing
                val query = QueryProductDetailsParams.newBuilder()
                    .setProductList(
                        listOf(
                            QueryProductDetailsParams.Product.newBuilder()
                                .setProductId(sku)
                                .setProductType(productType)
                                .build()
                        )
                    )
                    .build()
                val result = c.queryProductDetails(query)
                val details = result.productDetailsList?.firstOrNull()
                if (result.billingResult.responseCode != BillingClient.BillingResponseCode.OK || details == null) {
                    Log.w(TAG, "Product not found: $sku (${result.billingResult.responseCode})")
                    _state.value = BillingState.Error
                    return@launch
                }
                val productParams = BillingFlowParams.ProductDetailsParams.newBuilder()
                    .setProductDetails(details)
                if (productType == BillingClient.ProductType.SUBS) {
                    val offerToken = details.subscriptionOfferDetails?.firstOrNull()?.offerToken
                    if (offerToken == null) {
                        Log.w(TAG, "No subscription offer for $sku")
                        _state.value = BillingState.Error
                        return@launch
                    }
                    productParams.setOfferToken(offerToken)
                }
                val flow = BillingFlowParams.newBuilder()
                    .setProductDetailsParamsList(listOf(productParams.build()))
                    .build()
                val launched = c.launchBillingFlow(activity, flow)
                if (launched.responseCode != BillingClient.BillingResponseCode.OK) {
                    Log.w(TAG, "launchBillingFlow failed: ${launched.responseCode} ${launched.debugMessage}")
                    _state.value = BillingState.Error
                }
            } catch (e: Exception) {
                Log.w(TAG, "launchFlow failed", e)
                _state.value = BillingState.Error
            }
        }
    }

    private fun onPurchasesUpdated(result: BillingResult, purchases: List<Purchase>?) {
        try {
            when (result.responseCode) {
                BillingClient.BillingResponseCode.OK -> {
                    _state.value = BillingState.Ready
                    purchases?.forEach { syncPurchase(it) }
                }
                BillingClient.BillingResponseCode.USER_CANCELED -> _state.value = BillingState.Ready
                BillingClient.BillingResponseCode.ITEM_ALREADY_OWNED -> {
                    _state.value = BillingState.Ready
                    scope.launch { querySync() }
                }
                else -> {
                    Log.w(TAG, "Purchase failed: ${result.responseCode} ${result.debugMessage}")
                    _state.value = BillingState.Error
                }
            }
        } catch (e: Exception) {
            Log.w(TAG, "onPurchasesUpdated failed", e)
        }
    }

    /** تضبط LicenseManager حسب حالة الشراء. تُستدعى من onPurchasesUpdated ومن queryPurchasesAsync. */
    fun syncPurchase(purchase: Purchase) {
        try {
            when (purchase.purchaseState) {
                Purchase.PurchaseState.PURCHASED -> {
                    if (BuildConfig.BILLING_LIFETIME_SKU in purchase.products) {
                        LicenseManager.grantLifetime()
                    } else {
                        LicenseManager.setSubscription(true, 0L)
                    }
                    acknowledgeIfNeeded(purchase)
                    if (_state.value == BillingState.Purchasing) _state.value = BillingState.Ready
                }
                // معلّق (مثلاً دفع نقدي): لا تُمنح الميزة بعد.
                Purchase.PurchaseState.PENDING -> _state.value = BillingState.Purchasing
                else -> Unit // UNSPECIFIED_STATE
            }
        } catch (e: Exception) {
            Log.w(TAG, "syncPurchase failed", e)
        }
    }

    /** Google تُرجع المبلغ تلقائياً إن لم يُؤكَّد الشراء خلال 3 أيام. */
    private fun acknowledgeIfNeeded(purchase: Purchase) {
        if (purchase.isAcknowledged) return
        val c = client ?: return
        scope.launch {
            try {
                val r = c.acknowledgePurchase(
                    AcknowledgePurchaseParams.newBuilder()
                        .setPurchaseToken(purchase.purchaseToken)
                        .build()
                )
                if (r.responseCode != BillingClient.BillingResponseCode.OK) {
                    Log.w(TAG, "acknowledge failed: ${r.responseCode} ${r.debugMessage}")
                }
            } catch (e: Exception) {
                Log.w(TAG, "acknowledge error", e)
            }
        }
    }

    private suspend fun querySync() {
        val c = client ?: return
        if (!c.isReady) return
        try {
            val inapp = c.queryPurchasesAsync(
                QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.INAPP).build()
            )
            if (inapp.billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                inapp.purchasesList.forEach { syncPurchase(it) }
            }

            val subs = c.queryPurchasesAsync(
                QueryPurchasesParams.newBuilder().setProductType(BillingClient.ProductType.SUBS).build()
            )
            if (subs.billingResult.responseCode == BillingClient.BillingResponseCode.OK) {
                var activeSub = false
                subs.purchasesList.forEach {
                    syncPurchase(it)
                    if (it.purchaseState == Purchase.PurchaseState.PURCHASED) activeSub = true
                }
                // نتيجة ناجحة بلا اشتراك نشط = انتهى أو أُلغي. (الترخيص الدائم لا يتأثر.)
                if (!activeSub) LicenseManager.setSubscription(false, 0L)
                prefs?.edit()?.putLong(KEY_LAST_CHECK, System.currentTimeMillis())?.apply()
            } else {
                Log.w(TAG, "subs query failed: ${subs.billingResult.responseCode}")
            }
        } catch (e: Exception) {
            Log.w(TAG, "querySync failed", e)
        }
    }

    /** من MainActivity.onResume: إعادة تحقق فقط إن مرّت 24 ساعة على آخر فحص ناجح. */
    fun resumeChecking() {
        try {
            val c = client
            if (c == null || !c.isReady) {
                startConnection() // الاتصال يُجري الاستعلام عند نجاحه
                return
            }
            val last = prefs?.getLong(KEY_LAST_CHECK, 0L) ?: 0L
            val now = System.currentTimeMillis()
            // رجوع الساعة للخلف لا يؤجل الفحص.
            if (now >= last && now - last < CHECK_INTERVAL_MS) return
            scope.launch { querySync() }
        } catch (e: Exception) {
            Log.w(TAG, "resumeChecking failed", e)
        }
    }

    /** من MainActivity.onDestroy. */
    fun disconnect() {
        try {
            client?.endConnection()
        } catch (e: Exception) {
            Log.w(TAG, "disconnect failed", e)
        } finally {
            client = null
            _state.value = BillingState.Idle
        }
    }
}
''')

# ---- 2-ب) billing/DebugPurchaseSimulator.kt (ملف منفصل؛ لا يعمل إلا مع BuildConfig.DEBUG) ----
write_file(_PKG + "/billing/DebugPurchaseSimulator.kt", r'''package com.example.voiceassistant.billing

import android.app.Activity
import android.app.AlertDialog
import android.util.Log
import com.example.voiceassistant.BuildConfig
import com.example.voiceassistant.data.LicenseManager

/**
 * محاكاة شراء لنسخ debug فقط (APK خارج Google Play حيث BillingState.Unavailable).
 * الاستدعاء الوحيد من MainScreen خلف الشرط:
 *   BuildConfig.DEBUG && BillingManager.state.value == BillingState.Unavailable
 * وفي الدالة نفسها حارس ثانٍ: في release لا تفعل شيئاً.
 */
object DebugPurchaseSimulator {

    fun simulate(activity: Activity, sku: String) {
        if (!BuildConfig.DEBUG) return
        try {
            AlertDialog.Builder(activity)
                .setMessage("وضع debug — محاكاة شراء $sku؟")
                .setPositiveButton("محاكاة") { _, _ -> apply(sku) }
                .setNegativeButton("إلغاء", null)
                .show()
        } catch (e: Exception) {
            Log.w("Billing", "simulate failed", e)
        }
    }

    private fun apply(sku: String) {
        if (!BuildConfig.DEBUG) return
        if (sku == BuildConfig.BILLING_LIFETIME_SKU) {
            LicenseManager.grantLifetime()
        } else {
            LicenseManager.setSubscription(true, 0L)
        }
    }
}
''')

# ---- 3) LicenseManager.grantLifetime() (redeem لا يُلمس) ----
insert_before(
    _B_LICENSE,
    "    // ---------------- التفعيل ----------------\n",
    r'''    /** يمنح الترخيص الدائم بعد تأكيد الشراء من المتجر (BillingManager). لا علاقة له بـ redeem. */
    fun grantLifetime() {
        synchronized(lock) {
            prefs?.edit()?.putBoolean(KEY_LIFETIME, true)?.apply()
        }
        CreditsManager.refresh()
    }

'''
)

# ---- 4) VoiceAssistantApp: BillingManager.init بعد CreditsManager.init ----
insert_before(
    _B_APP,
    "import com.example.voiceassistant.data.AiSettings\n",
    "import com.example.voiceassistant.billing.BillingManager\n"
)
_replace_once(
    _B_APP,
    "        CreditsManager.init(this)\n",
    "        CreditsManager.init(this)\n"
    "        // Google Play Billing (Unavailable on APKs installed outside Google Play: expected).\n"
    "        BillingManager.init(this)\n"
)

# ---- 5) MainActivity: onResume / onDestroy ----
insert_before(
    _B_ACT,
    "import com.example.voiceassistant.ui.MainScreen\n",
    "import com.example.voiceassistant.billing.BillingManager\n"
)
insert_before(
    _B_ACT,
    "    private fun requestNotificationPermissionIfNeeded() {\n",
    r'''    override fun onResume() {
        super.onResume()
        // Purchase / subscription re-check (at most once every 24 hours; reconnects if needed).
        BillingManager.resumeChecking()
    }

    override fun onDestroy() {
        BillingManager.disconnect()
        super.onDestroy()
    }

'''
)

# ---- 6) MainScreen: تدفق شراء حقيقي (+ محاكاة debug عند Unavailable) ----
insert_before(
    _B_SCREEN,
    "import com.example.voiceassistant.ui.components.PaywallSheet\n",
    "import com.example.voiceassistant.BuildConfig\n"
    "import com.example.voiceassistant.billing.BillingManager\n"
    "import com.example.voiceassistant.billing.BillingState\n"
    "import com.example.voiceassistant.billing.DebugPurchaseSimulator\n"
)
_replace_once(
    _B_SCREEN,
    r'''        if (state.showPaywall) {
            PaywallSheet(
                onDismiss = viewModel::dismissPaywall,
                onBuyLicense = {},
                onSubscribe = {}
            )
        }
''',
    r'''        if (state.showPaywall) {
            val activity = context as? Activity
            PaywallSheet(
                onDismiss = viewModel::dismissPaywall,
                onBuyLicense = {
                    if (BuildConfig.DEBUG && BillingManager.state.value == BillingState.Unavailable) {
                        activity?.let { DebugPurchaseSimulator.simulate(it, BuildConfig.BILLING_LIFETIME_SKU) }
                    } else if (activity != null) {
                        BillingManager.launchPurchase(activity, BuildConfig.BILLING_LIFETIME_SKU)
                    }
                },
                onSubscribe = {
                    if (BuildConfig.DEBUG && BillingManager.state.value == BillingState.Unavailable) {
                        activity?.let { DebugPurchaseSimulator.simulate(it, BuildConfig.BILLING_MONTHLY_SKU) }
                    } else if (activity != null) {
                        BillingManager.launchSubscribe(activity, BuildConfig.BILLING_MONTHLY_SKU)
                    }
                }
            )
        }
'''
)

# ---- 6-ب) PaywallSheet: حالة BillingManager + زر «إعادة المحاولة» عند Unavailable ----
insert_before(
    _B_PAYWALL,
    "import com.example.voiceassistant.data.CreditsManager\n",
    "import com.example.voiceassistant.billing.BillingManager\n"
    "import com.example.voiceassistant.billing.BillingState\n"
)
insert_before(
    _B_PAYWALL,
    "    val credits by CreditsManager.state.collectAsState()\n",
    "    val billing by BillingManager.state.collectAsState()\n"
)
insert_before(
    _B_PAYWALL,
    "            // آخر عمليات التفعيل\n",
    r'''            // حالة خدمة الدفع (Google Play)
            if (!credits.unlimited) {
                Text(
                    text = when (billing) {
                        BillingState.Idle -> "خدمة الدفع: غير متصلة"
                        BillingState.Connecting -> "خدمة الدفع: جارٍ الاتصال..."
                        BillingState.Ready -> "خدمة الدفع: جاهزة"
                        BillingState.Purchasing -> "عملية الشراء قيد المعالجة..."
                        BillingState.Unavailable ->
                            "الدفع عبر Google Play غير متاح في هذه النسخة. استخدم كود التفعيل."
                        BillingState.Error -> "حدث خطأ في خدمة الدفع"
                    },
                    style = MaterialTheme.typography.bodySmall
                )
                if (billing == BillingState.Unavailable) {
                    OutlinedButton(
                        onClick = { BillingManager.startConnection() },
                        modifier = Modifier.fillMaxWidth()
                    ) { Text("إعادة المحاولة") }
                }
            }

'''
)

# ---- 7) proguard-rules.pro ----
insert_before(
    "proguard-rules.pro",
    "# Keep line numbers for readable crash reports\n",
    "# Google Play Billing + our billing layer\n"
    "-keep class com.android.billingclient.** { *; }\n"
    "-keep class com.example.voiceassistant.billing.** { *; }\n\n"
)
print(">> Billing layer injected (BillingManager + DebugPurchaseSimulator + wiring). build.yml untouched.")
