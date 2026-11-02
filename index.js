// ══════════════════════════════════════════════════════════════════════════════
// Zevorix AI & Gradiometer — Backend (v5, Master IPN)
// ══════════════════════════════════════════════════════════════════════════════

const express = require('express');
const sgMail = require('@sendgrid/mail');
const crypto = require('crypto');
const admin = require('firebase-admin');
const multer = require('multer');
const fs = require('fs');
const nacl = require('tweetnacl');

process.on('uncaughtException', (err) => console.error('❌ CRITICAL CRASH:', err.message, err.stack));
process.on('unhandledRejection', (reason) => console.error('❌ UNHANDLED REJECTION:', reason));

const app = express();
app.use(express.json({ limit: '25mb' }));

const upload = multer({
    storage: multer.memoryStorage(),
    limits: { fileSize: 100 * 1024 * 1024 }
});

// ============================================================================
// 1. Environment
// ============================================================================
const LICENSE_SECRET           = process.env.LICENSE_SECRET;
const ED25519_PRIVATE_KEY_RAW  = (process.env.ED25519_PRIVATE_KEY || '').trim();
const SENDGRID_KEY             = process.env.SENDGRID_KEY;
const NOWPAYMENTS_IPN_SECRET   = process.env.NOWPAYMENTS_IPN_SECRET;
const FIREBASE_SERVICE_ACCOUNT = process.env.FIREBASE_SERVICE_ACCOUNT;
const FIREBASE_STORAGE_BUCKET  = process.env.FIREBASE_STORAGE_BUCKET;
const REPLICATE_TOKEN          = process.env.REPLICATE_TOKEN;
const BASE_URL                 = (process.env.BASE_URL || '').replace(/\/+$/, '');

const REPLICATE_VIDEO_VERSION      = process.env.REPLICATE_VIDEO_VERSION;
const REPLICATE_MUSIC_VERSION      = process.env.REPLICATE_MUSIC_VERSION;
const REPLICATE_EDIT_VIDEO_VERSION = process.env.REPLICATE_EDIT_VIDEO_VERSION;

const GEMINI_API_KEY = (process.env.GEMINI_API_KEY || '').trim();
const OPENAI_API_KEY = (process.env.OPENAI_API_KEY || '').trim();
const CLAUDE_API_KEY = (process.env.CLAUDE_API_KEY || '').trim();

if (!LICENSE_SECRET) { console.error("FATAL: LICENSE_SECRET is missing!"); process.exit(1); }

const ED25519_PRIVATE_KEY = (() => {
    if (!ED25519_PRIVATE_KEY_RAW) { console.error("FATAL: ED25519_PRIVATE_KEY missing!"); process.exit(1); }
    let bytes;
    try {
        bytes = /^[0-9a-fA-F]{128}$/.test(ED25519_PRIVATE_KEY_RAW)
            ? Buffer.from(ED25519_PRIVATE_KEY_RAW, 'hex')
            : Buffer.from(ED25519_PRIVATE_KEY_RAW, 'base64');
    } catch (e) { console.error("FATAL: ED25519_PRIVATE_KEY decode failed:", e.message); process.exit(1); }
    if (!bytes || bytes.length !== 64) { console.error("FATAL: ED25519_PRIVATE_KEY must be 64 bytes"); process.exit(1); }
    return bytes;
})();
const ED25519_PUBLIC_KEY = nacl.sign.keyPair.fromSecretKey(ED25519_PRIVATE_KEY).publicKey;

if (SENDGRID_KEY) sgMail.setApiKey(SENDGRID_KEY);
console.log("🔐 Ed25519 loaded (pub: " + Buffer.from(ED25519_PUBLIC_KEY).toString('hex').substring(0, 16) + "…)");
console.log("🤖 AI keys: Gemini=" + (GEMINI_API_KEY ? "✓" : "✗") + " OpenAI=" + (OPENAI_API_KEY ? "✓" : "✗") + " Claude=" + (CLAUDE_API_KEY ? "✓" : "✗"));

// ============================================================================
// 2. Firebase Admin (Zevorix + Gradiometer)
// ============================================================================
let firebaseReady = false;
let db, bucket;

try {
    let sa = null;
    if (process.env.FIREBASE_KEY_BASE64) {
        sa = JSON.parse(Buffer.from(process.env.FIREBASE_KEY_BASE64, 'base64').toString('utf8'));
    } else if (fs.existsSync('/etc/secrets/firebase-key.json')) {
        sa = JSON.parse(fs.readFileSync('/etc/secrets/firebase-key.json', 'utf8'));
    } else if (FIREBASE_SERVICE_ACCOUNT) {
        sa = JSON.parse(FIREBASE_SERVICE_ACCOUNT);
        if (sa.private_key) sa.private_key = sa.private_key.replace(/\\n/g, '\n');
    }
    if (sa) {
        admin.initializeApp({
            credential: admin.credential.cert(sa),
            storageBucket: FIREBASE_STORAGE_BUCKET || `${sa.project_id}.appspot.com`
        });
        db = admin.firestore();
        bucket = admin.storage().bucket();
        firebaseReady = true;
        console.log("🔥 Zevorix Firebase ready.");
    } else { console.warn("⚠️ Zevorix Firebase key missing."); }
} catch (e) { console.error("❌ Zevorix Firebase init failed:", e.message); }

// --- Gradiometer Firebase Init ---
let gradDb = null;
try {
    const gradKeyB64 = process.env.GRADIOMETER_FIREBASE_KEY_BASE64;
    if (gradKeyB64) {
        const gradSA = JSON.parse(Buffer.from(gradKeyB64, 'base64').toString('utf8'));
        if (gradSA.private_key) gradSA.private_key = gradSA.private_key.replace(/\\n/g, '\n');
        const gradApp = admin.initializeApp(
            { credential: admin.credential.cert(gradSA) },
            'gradiometer'
        );
        gradDb = admin.firestore(gradApp);
        console.log('🔥 Gradiometer Firebase ready.');
    } else {
        console.warn('⚠️ GRADIOMETER_FIREBASE_KEY_BASE64 not set.');
    }
} catch (e) {
    console.error('❌ Gradiometer Firebase init failed:', e.message);
}

// ============================================================================
// 3. Helpers
// ============================================================================
function deepSort(obj) {
    if (Array.isArray(obj)) return obj.map(deepSort);
    if (obj !== null && typeof obj === 'object') {
        return Object.keys(obj).sort().reduce((r, k) => { r[k] = deepSort(obj[k]); return r; }, {});
    }
    return obj;
}
function safeEqual(a, b) {
    const x = Buffer.from(String(a || '')); const y = Buffer.from(String(b || ''));
    return x.length === y.length && crypto.timingSafeEqual(x, y);
}

const BASE58_ALPHABET = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz";
const NONCE_ALPHABET  = "ABCDEFGHIJKLMNOPQRSTUVWXYZ234567";
const NONCE_LEN = 8, SIGNATURE_BYTES = 64, MAX_CODE_LENGTH = 160;

function base58Encode(bytes) {
    let n = 0n; for (const b of bytes) n = n * 256n + BigInt(b);
    let out = ""; while (n > 0n) { const r = Number(n % 58n); out = BASE58_ALPHABET[r] + out; n /= 58n; }
    for (const b of bytes) { if (b === 0) out = "1" + out; else break; }
    return out;
}
function base58Decode(str) {
    if (!str || str.length === 0 || str.length > 100) return null;
    let n = 0n; for (const ch of str) { const i = BASE58_ALPHABET.indexOf(ch); if (i < 0) return null; n = n * 58n + BigInt(i); }
    const bytes = []; while (n > 0n) { bytes.unshift(Number(n % 256n)); n /= 256n; }
    let lead = 0; for (const ch of str) { if (ch === '1') lead++; else break; }
    const r = Buffer.alloc(lead + bytes.length);
    for (let i = 0; i < bytes.length; i++) r[lead + i] = bytes[i];
    return r;
}
function generateLicenseKey() {
    let nonce = ""; const bytes = crypto.randomBytes(NONCE_LEN);
    for (let i = 0; i < NONCE_LEN; i++) nonce += NONCE_ALPHABET.charAt(bytes[i] % NONCE_ALPHABET.length);
    const sig = nacl.sign.detached(Buffer.from(nonce, 'utf-8'), ED25519_PRIVATE_KEY);
    return `ZEV-${nonce}-${base58Encode(sig)}`;
}
function isValidLicenseKey(key) {
    if (!key || typeof key !== 'string') return false;
    const t = key.trim();
    if (t.length > MAX_CODE_LENGTH) return false;
    const p = t.split('-'); if (p.length !== 3 || p[0].toUpperCase() !== 'ZEV') return false;
    const nonce = p[1].toUpperCase(), sig = p[2];
    if (nonce.length !== NONCE_LEN || !/^[A-Z2-7]+$/.test(nonce)) return false;
    if (sig.length < 80 || sig.length > 90) return false;
    const sb = base58Decode(sig);
    if (!sb || sb.length !== SIGNATURE_BYTES) return false;
    try { return nacl.sign.detached.verify(Buffer.from(nonce, 'utf-8'), sb, ED25519_PUBLIC_KEY); }
    catch { return false; }
}
const isValidDeviceId = (id) => typeof id === 'string' && /^[A-Za-z0-9_-]{6,64}$/.test(id);
const isValidJobId = (id) => typeof id === 'string' && /^[A-Za-z0-9]{10,40}$/.test(id);
const webhookToken = (d, t, j) => crypto.createHmac('sha256', LICENSE_SECRET).update(`WH|${d}|${t}|${j || ''}`).digest('hex').substring(0, 32);

// ============================================================================
// 4. Credits
// ============================================================================
async function deductCredits(licenseKey, deviceId, cost, type, prompt) {
    if (!firebaseReady) throw new Error("DB_NOT_READY");
    const ref = db.collection('licenses').doc(licenseKey);
    const jobRef = db.collection('jobs').doc();
    const remaining = await db.runTransaction(async (tx) => {
        const doc = await tx.get(ref);
        if (!doc.exists) throw new Error('INVALID_LICENSE');
        const data = doc.data();
        if (data.deviceId && data.deviceId !== deviceId) throw new Error('LICENSE_BOUND_TO_OTHER_DEVICE');
        const cur = data.credits || 0;
        if (cur < cost) throw new Error('INSUFFICIENT_CREDITS');
        tx.update(ref, {
            deviceId,
            credits: admin.firestore.FieldValue.increment(-cost),
            lastUsedAt: admin.firestore.FieldValue.serverTimestamp()
        });
        tx.set(jobRef, {
            licenseKey, deviceId, type, cost, prompt,
            status: 'pending', refunded: false,
            createdAt: admin.firestore.FieldValue.serverTimestamp()
        });
        return cur - cost;
    });
    return { remaining, jobId: jobRef.id };
}
async function failJob(jobId, reason) {
    if (!firebaseReady || !jobId) return { refunded: false };
    const jobRef = db.collection('jobs').doc(jobId);
    const failureRef = db.collection('failures').doc();
    return await db.runTransaction(async (tx) => {
        const jd = await tx.get(jobRef);
        if (!jd.exists) return { refunded: false };
        const job = jd.data();
        if (job.status === 'failed') return { refunded: !!job.refunded };
        let licRef = null;
        if (job.licenseKey && job.cost > 0) licRef = db.collection('licenses').doc(job.licenseKey);
        if (licRef) tx.update(licRef, { credits: admin.firestore.FieldValue.increment(job.cost) });
        tx.update(jobRef, {
            status: 'failed', refunded: !!licRef,
            failReason: String(reason).substring(0, 500),
            failedAt: admin.firestore.FieldValue.serverTimestamp()
        });
        tx.set(failureRef, {
            jobId, deviceId: job.deviceId, licenseKey: job.licenseKey || null,
            type: job.type, cost: job.cost, prompt: job.prompt || '',
            reason: String(reason).substring(0, 500), refunded: !!licRef,
            createdAt: admin.firestore.FieldValue.serverTimestamp()
        });
        return { refunded: !!licRef };
    });
}

// ============================================================================
// 5. AI providers (Zevorix)
// ============================================================================
const GEMINI_MODELS = ["gemini-3.8-flash", "gemini-3.1-flash-lite"];
const OPENAI_MODEL = "gpt-4o-mini";
const CLAUDE_MODEL = "claude-3-5-sonnet-20241022";
const GEMINI_IMAGE_MODEL = "gemini-3.1-flash-image";
const GEMINI_TTS_MODEL = "gemini-3.8-flash-lite-tts";

const DEFAULT_TIMEOUT_MS = 60_000;

async function fetchWithTimeout(url, options = {}, timeoutMs = DEFAULT_TIMEOUT_MS) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
        return await fetch(url, { ...options, signal: controller.signal });
    } finally { clearTimeout(timer); }
}

function toGeminiParts(messages, attachments, systemPrompt) {
    const parts = [];
    if (attachments) {
        for (const a of attachments) {
            if (a.mime && a.mime.startsWith('image/')) {
                parts.push({ inline_data: { mime_type: a.mime, data: a.data } });
            } else if (a.mime === 'application/pdf') {
                parts.push({ inline_data: { mime_type: 'application/pdf', data: a.data } });
            } else {
                try {
                    const text = Buffer.from(a.data, 'base64').toString('utf8');
                    parts.push({ text: `\n--- FILE: ${a.name} ---\n${text}\n--- END FILE ---\n` });
                } catch { /* skip invalid base64 */ }
            }
        }
    }
    parts.push({ text: messages[messages.length - 1].content });
    return parts;
}

async function callGemini(apiKey, model, messages, systemPrompt, attachments) {
    const url = `https://generativelanguage.googleapis.com/v1beta/models/${model}:generateContent`;
    const body = {
        system_instruction: { parts: [{ text: systemPrompt }] },
        contents: [
            ...messages.slice(0, -1).map(m => ({
                role: m.role === 'assistant' ? 'model' : 'user',
                parts: [{ text: m.content }]
            })),
            { role: 'user', parts: toGeminiParts(messages, attachments, systemPrompt) }
        ],
        generationConfig: { maxOutputTokens: 16384 }
    };
    const res = await fetchWithTimeout(url, {
        method: 'POST',
        headers: { 'x-goog-api-key': apiKey, 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    const raw = await res.text();
    if (!res.ok) throw new Error(`gemini ${res.status}: ${raw.slice(0, 200)}`);
    const json = JSON.parse(raw);
    const parts = json.candidates?.[0]?.content?.parts || [];
    const text = parts.map(p => p.text || '').join('').trim();
    if (!text) throw new Error('gemini: empty response');
    return { text, provider: 'gemini', model };
}

async function callOpenAI(apiKey, model, messages, systemPrompt) {
    const url = 'https://api.openai.com/v1/chat/completions';
    const msgs = [{ role: 'system', content: systemPrompt }, ...messages];
    const body = { model, messages: msgs, max_tokens: 8192 };
    const res = await fetchWithTimeout(url, {
        method: 'POST',
        headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    const raw = await res.text();
    if (!res.ok) throw new Error(`openai ${res.status}: ${raw.slice(0, 200)}`);
    const json = JSON.parse(raw);
    const text = json.choices?.[0]?.message?.content?.trim();
    if (!text) throw new Error('openai: empty response');
    return { text, provider: 'openai', model };
}

async function callClaude(apiKey, model, messages, systemPrompt, attachments) {
    const url = 'https://api.anthropic.com/v1/messages';
    const claudeMessages = messages.map(m => ({ role: m.role === 'assistant' ? 'assistant' : 'user', content: m.content }));
    if (attachments && attachments.length > 0) {
        const lastMsg = claudeMessages[claudeMessages.length - 1];
        const contentParts = [];
        for (const a of attachments) {
            if (a.mime && (a.mime.startsWith('image/') || a.mime === 'application/pdf')) {
                contentParts.push({
                    type: a.mime === 'application/pdf' ? 'document' : 'image',
                    source: { type: 'base64', media_type: a.mime, data: a.data }
                });
            }
        }
        contentParts.push({ type: 'text', text: lastMsg.content });
        lastMsg.content = contentParts;
    }
    const body = { model, max_tokens: 8192, system: systemPrompt, messages: claudeMessages };
    const res = await fetchWithTimeout(url, {
        method: 'POST',
        headers: { 'x-api-key': apiKey, 'anthropic-version': '2023-06-01', 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    const raw = await res.text();
    if (!res.ok) throw new Error(`claude ${res.status}: ${raw.slice(0, 200)}`);
    const json = JSON.parse(raw);
    const text = (json.content || []).filter(b => b.type === 'text').map(b => b.text).join('').trim();
    if (!text) throw new Error('claude: empty response');
    return { text, provider: 'claude', model };
}

async function tryProvider(provider, messages, systemPrompt, attachments) {
    if (provider === 'gemini') {
        if (!GEMINI_API_KEY) throw new Error('gemini: no key');
        let lastErr;
        for (const model of GEMINI_MODELS) {
            try { return await callGemini(GEMINI_API_KEY, model, messages, systemPrompt, attachments); }
            catch (e) { lastErr = e; }
        }
        throw lastErr;
    }
    if (provider === 'openai') {
        if (!OPENAI_API_KEY) throw new Error('openai: no key');
        return await callOpenAI(OPENAI_API_KEY, OPENAI_MODEL, messages, systemPrompt);
    }
    if (provider === 'claude') {
        if (!CLAUDE_API_KEY) throw new Error('claude: no key');
        return await callClaude(CLAUDE_API_KEY, CLAUDE_MODEL, messages, systemPrompt, attachments);
    }
    throw new Error('unknown provider: ' + provider);
}

// ============================================================================
// 6. Public routes
// ============================================================================
app.get('/', (req, res) => {
    res.json({
        status: 'ok',
        features: {
            firebaseZevorix: firebaseReady,
            firebaseGradiometer: !!gradDb,
            replicate: !!REPLICATE_TOKEN,
            ai: { gemini: !!GEMINI_API_KEY, openai: !!OPENAI_API_KEY, claude: !!CLAUDE_API_KEY },
            license: 'ed25519'
        }
    });
});

app.post('/api/balance', async (req, res) => {
    if (!firebaseReady) return res.status(503).json({ error: 'Service not ready' });
    const { licenseKey, deviceId } = req.body || {};
    if (!isValidLicenseKey(licenseKey) || !isValidDeviceId(deviceId)) return res.status(400).json({ error: 'Invalid request' });
    try {
        const doc = await db.collection('licenses').doc(licenseKey).get();
        if (!doc.exists) return res.status(404).json({ error: 'License not found' });
        const data = doc.data();
        if (data.deviceId && data.deviceId !== deviceId) return res.status(403).json({ error: 'License used on another device' });
        res.json({ credits: data.credits || 0 });
    } catch (e) { res.status(500).json({ error: 'Internal error' }); }
});

// ============================================================================
// 7. 🤖 AI PROXY
// ============================================================================
app.post('/api/ai/chat', async (req, res) => {
    const body = req.body || {};
    const { licenseKey, deviceId, messages, systemPrompt, provider, providers, attachments } = body;
    const cost = typeof body.cost === 'number' ? Math.max(1, Math.min(10, Math.floor(body.cost))) : 1;

    if (!isValidDeviceId(deviceId)) return res.status(400).json({ error: 'Invalid device' });
    if (!Array.isArray(messages) || messages.length === 0) return res.status(400).json({ error: 'Invalid messages' });
    if (!isValidLicenseKey(licenseKey)) return res.status(401).json({ error: 'INVALID_LICENSE' });
    if (!firebaseReady) return res.status(503).json({ error: 'Service not ready' });

    let jobId = null;
    try {
        const deduction = await deductCredits(licenseKey, deviceId, cost, 'chat', String(messages[messages.length - 1].content || '').slice(0, 200));
        jobId = deduction.jobId;
    } catch (e) {
        if (e.message === 'INSUFFICIENT_CREDITS') return res.status(402).json({ error: 'INSUFFICIENT_CREDITS' });
        if (e.message === 'LICENSE_BOUND_TO_OTHER_DEVICE') return res.status(403).json({ error: 'LICENSE_BOUND' });
        if (e.message === 'INVALID_LICENSE') return res.status(401).json({ error: 'INVALID_LICENSE' });
        return res.status(500).json({ error: 'Internal error' });
    }

    const order = Array.isArray(providers) && providers.length > 0
        ? providers
        : (provider ? [provider] : ['gemini', 'openai', 'claude']);

    let lastError = null;
    const started = Date.now();

    for (const p of order) {
        try {
            const result = await tryProvider(p, messages, systemPrompt || '', attachments || []);
            const latencyMs = Date.now() - started;
            
            if (jobId) {
                db.collection('jobs').doc(jobId).update({
                    status: 'completed',
                    completedAt: admin.firestore.FieldValue.serverTimestamp(),
                    provider: result.provider,
                    model: result.model,
                    latencyMs
                }).catch(err => console.error('job update:', err.message));
            }
            return res.json({
                text: result.text,
                provider: result.provider,
                model: result.model,
                latencyMs
            });
        } catch (e) {
            lastError = e;
            console.warn(`provider ${p} failed: ${e.message}`);
        }
    }

    try { await failJob(jobId, `all providers failed: ${lastError?.message || 'unknown'}`); } catch { }
    return res.status(502).json({ error: 'AI_FAILED', message: String(lastError?.message || '').slice(0, 300) });
});

app.post('/api/ai/image', async (req, res) => {
    const body = req.body || {};
    const { licenseKey, deviceId, prompt } = body;
    const cost = 2;

    if (!isValidDeviceId(deviceId)) return res.status(400).json({ error: 'Invalid device' });
    if (typeof prompt !== 'string' || prompt.length < 3 || prompt.length > 1000) return res.status(400).json({ error: 'Invalid prompt' });
    if (!isValidLicenseKey(licenseKey)) return res.status(401).json({ error: 'INVALID_LICENSE' });
    if (!GEMINI_API_KEY) return res.status(503).json({ error: 'AI_NOT_CONFIGURED' });
    if (!firebaseReady) return res.status(503).json({ error: 'Service not ready' });

    let jobId = null;
    try {
        const r = await deductCredits(licenseKey, deviceId, cost, 'image', prompt);
        jobId = r.jobId;
    } catch (e) {
        if (e.message === 'INSUFFICIENT_CREDITS') return res.status(402).json({ error: 'INSUFFICIENT_CREDITS' });
        if (e.message === 'LICENSE_BOUND_TO_OTHER_DEVICE') return res.status(403).json({ error: 'LICENSE_BOUND' });
        return res.status(401).json({ error: 'INVALID_LICENSE' });
    }

    try {
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_IMAGE_MODEL}:generateContent`;
        const payload = {
            contents: [{ role: 'user', parts: [{ text: prompt }] }],
            generationConfig: { responseModalities: ['TEXT', 'IMAGE'] }
        };
        const r = await fetchWithTimeout(url, {
            method: 'POST',
            headers: { 'x-goog-api-key': GEMINI_API_KEY, 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }, 90_000);
        const raw = await r.text();
        if (!r.ok) throw new Error(`gemini image ${r.status}: ${raw.slice(0, 200)}`);
        const json = JSON.parse(raw);
        
        let b64 = null;
        const parts = json.candidates?.[0]?.content?.parts || [];
        for (const p of parts) {
            const inline = p.inlineData || p.inline_data;
            if (inline?.data) { b64 = inline.data; break; }
        }
        
        if (!b64) throw new Error('gemini image: no image in response');
        if (jobId) {
            db.collection('jobs').doc(jobId).update({
                status: 'completed',
                completedAt: admin.firestore.FieldValue.serverTimestamp()
            }).catch(() => { });
        }
        res.json({ image: b64, mime: 'image/png' });
    } catch (e) {
        try { await failJob(jobId, `image failed: ${e.message}`); } catch { }
        return res.status(502).json({ error: 'AI_FAILED', message: String(e.message || '').slice(0, 300) });
    }
});

app.post('/api/ai/tts', async (req, res) => {
    const body = req.body || {};
    const { licenseKey, deviceId, text, voiceId } = body;
    const cleanText = typeof text === 'string' ? text.trim() : '';

    if (!isValidDeviceId(deviceId)) return res.status(400).json({ error: 'Invalid device' });
    if (!cleanText || cleanText.length > 5000) return res.status(400).json({ error: 'Invalid text' });
    if (!isValidLicenseKey(licenseKey)) return res.status(401).json({ error: 'INVALID_LICENSE' });
    if (!GEMINI_API_KEY) return res.status(503).json({ error: 'AI_NOT_CONFIGURED' });
    if (!firebaseReady) return res.status(503).json({ error: 'Service not ready' });

    try {
        const rl = db.collection('tts_rl').doc(licenseKey);
        const now = Date.now();
        await db.runTransaction(async (tx) => {
            const doc = await tx.get(rl);
            const prev = doc.exists ? (doc.data().ts || 0) : 0;
            const count = doc.exists ? (doc.data().count || 0) : 0;
            const windowMs = 60_000;
            const newCount = (now - prev < windowMs) ? count + 1 : 1;
            if (newCount > 60) throw new Error('RATE_LIMIT');
            tx.set(rl, { ts: now, count: newCount });
        });
    } catch (e) {
        if (e.message === 'RATE_LIMIT') return res.status(429).json({ error: 'RATE_LIMIT' });
        console.warn('tts rate-limit check failed:', e.message);
    }

    try {
        const voice = voiceId || 'Kore';
        const url = `https://generativelanguage.googleapis.com/v1beta/models/${GEMINI_TTS_MODEL}:generateContent`;
        const payload = {
            contents: [{ role: 'user', parts: [{ text: cleanText }] }],
            generationConfig: {
                responseModalities: ['AUDIO'],
                speechConfig: {
                    voiceConfig: { prebuiltVoiceConfig: { voiceName: voice } }
                }
            }
        };
        const r = await fetchWithTimeout(url, {
            method: 'POST',
            headers: { 'x-goog-api-key': GEMINI_API_KEY, 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }, 60_000);
        const raw = await r.text();
        if (!r.ok) throw new Error(`tts ${r.status}: ${raw.slice(0, 200)}`);
        const json = JSON.parse(raw);
        const parts = json.candidates?.[0]?.content?.parts || [];
        let b64 = null;
        for (const p of parts) {
            const inline = p.inlineData || p.inline_data;
            if (inline?.data) { b64 = inline.data; break; }
        }
        if (!b64) throw new Error('tts: no audio in response');
        let pcm = Buffer.from(b64, 'base64');
        if (pcm.length > 44 && pcm[0] === 0x52 && pcm[1] === 0x49 && pcm[2] === 0x46 && pcm[3] === 0x46) {
            pcm = pcm.slice(44);
        }
        if (pcm.length % 2 !== 0) pcm = pcm.slice(0, pcm.length - 1);
        res.set('Content-Type', 'application/octet-stream');
        res.set('X-Sample-Rate', '24000');
        res.set('X-Channels', '1');
        res.send(pcm);
    } catch (e) {
        return res.status(502).json({ error: 'TTS_FAILED', message: String(e.message || '').slice(0, 200) });
    }
});

// ============================================================================
// 8. Video / music / edit
// ============================================================================
app.post(['/api/generate-video', '/api/generate-music'], async (req, res) => {
    const body = req.body || {};
    const prompt = typeof body.prompt === 'string' ? body.prompt.trim() : '';
    const { deviceId, licenseKey } = body;
    const type = req.path.endsWith('-video') ? 'video' : 'music';
    if (prompt.length < 3 || prompt.length > 500) return res.status(400).json({ error: 'Invalid prompt' });
    if (!isValidDeviceId(deviceId)) return res.status(400).json({ error: 'Invalid device' });
    const cost = type === 'video' ? 15 : 5;
    try {
        if (!isValidLicenseKey(licenseKey)) return res.status(401).json({ error: 'Invalid license' });
        const { remaining, jobId } = await deductCredits(licenseKey, deviceId, cost, type, prompt);
        res.status(200).json({ status: 'started', remaining });
        triggerReplicateAsync(prompt, deviceId, type, jobId).catch(err => {
            console.error(`Background error (${type}):`, err.message);
            handleFailure(jobId, deviceId, type, `Start failed: ${err.message}`, 'Generation failed to start');
        });
    } catch (e) {
        if (e.message === 'INSUFFICIENT_CREDITS') return res.status(402).json({ error: 'Insufficient credits' });
        if (e.message === 'LICENSE_BOUND_TO_OTHER_DEVICE') return res.status(403).json({ error: 'License used on another device' });
        if (e.message === 'INVALID_LICENSE') return res.status(401).json({ error: 'Invalid license' });
        return res.status(500).json({ error: 'Internal error' });
    }
});

app.post('/api/edit-video', upload.single('video'), async (req, res) => {
    const body = req.body || {};
    const { deviceId, licenseKey } = body;
    const prompt = typeof body.prompt === 'string' ? body.prompt.trim() : '';
    const file = req.file;
    if (!isValidDeviceId(deviceId)) return res.status(400).json({ error: 'Invalid device' });
    if (!file) return res.status(400).json({ error: 'No video file uploaded' });
    if (prompt.length < 3 || prompt.length > 500) return res.status(400).json({ error: 'Invalid prompt' });
    const cost = 15;
    try {
        if (!isValidLicenseKey(licenseKey)) return res.status(401).json({ error: 'Invalid license' });
        const { remaining, jobId } = await deductCredits(licenseKey, deviceId, cost, 'video', prompt);
        res.status(200).json({ status: 'started', remaining });
        processVideoEdit(file, prompt, deviceId, jobId).catch(err => {
            console.error("Edit Video Error:", err.message);
            handleFailure(jobId, deviceId, 'video', `Edit failed: ${err.message}`, 'Edit failed');
        });
    } catch (e) {
        if (e.message === 'INSUFFICIENT_CREDITS') return res.status(402).json({ error: 'Insufficient credits' });
        if (e.message === 'LICENSE_BOUND_TO_OTHER_DEVICE') return res.status(403).json({ error: 'License used on another device' });
        if (e.message === 'INVALID_LICENSE') return res.status(401).json({ error: 'Invalid license' });
        return res.status(500).json({ error: 'Internal error' });
    }
});

app.use((err, req, res, next) => {
    if (err instanceof multer.MulterError) {
        if (err.code === 'LIMIT_FILE_SIZE') return res.status(413).json({ error: 'Video too large (max 100MB)' });
        return res.status(400).json({ error: 'Upload error' });
    }
    return res.status(500).json({ error: 'Internal error' });
});

// ============================================================================
// 9. Replicate + webhook
// ============================================================================
function buildWebhookUrl(deviceId, type, jobId, prompt) {
    return `${BASE_URL}/webhook/replicate?deviceId=${encodeURIComponent(deviceId)}&type=${type}&jobId=${encodeURIComponent(jobId || '')}&token=${webhookToken(deviceId, type, jobId)}&prompt=${encodeURIComponent(prompt)}`;
}
async function triggerReplicateAsync(prompt, deviceId, type, jobId) {
    if (!REPLICATE_TOKEN || !BASE_URL) throw new Error("Missing env vars");
    const configured = type === 'video' ? REPLICATE_VIDEO_VERSION : REPLICATE_MUSIC_VERSION;
    if (!configured) throw new Error(`REPLICATE_${type.toUpperCase()}_VERSION is missing`);
    const version = configured.includes(':') ? configured.split(':').pop() : configured;
    const response = await fetch('https://api.replicate.com/v1/predictions', {
        method: 'POST',
        headers: { 'Authorization': `Token ${REPLICATE_TOKEN}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ version, input: { prompt }, webhook: buildWebhookUrl(deviceId, type, jobId, prompt), webhook_events_filter: ['completed'] })
    });
    if (!response.ok) throw new Error(await response.text());
    console.log(`🚀 ${type} job started for ${deviceId}`);
}
async function processVideoEdit(file, prompt, deviceId, jobId) {
    if (!REPLICATE_TOKEN || !BASE_URL) throw new Error("Missing env vars");
    if (!REPLICATE_EDIT_VIDEO_VERSION) throw new Error("REPLICATE_EDIT_VIDEO_VERSION missing");
    const originalFileName = `originals/${deviceId}/${Date.now()}.mp4`;
    const bucketFile = bucket.file(originalFileName);
    await bucketFile.save(file.buffer, { contentType: file.mimetype || 'video/mp4' });
    const [publicUrl] = await bucketFile.getSignedUrl({ version: 'v4', action: 'read', expires: Date.now() + 3600000 });
    const version = REPLICATE_EDIT_VIDEO_VERSION.includes(':') ? REPLICATE_EDIT_VIDEO_VERSION.split(':').pop() : REPLICATE_EDIT_VIDEO_VERSION;
    const response = await fetch('https://api.replicate.com/v1/predictions', {
        method: 'POST',
        headers: { 'Authorization': `Token ${REPLICATE_TOKEN}`, 'Content-Type': 'application/json' },
        body: JSON.stringify({ version, input: { prompt, video: publicUrl }, webhook: buildWebhookUrl(deviceId, 'video', jobId, prompt), webhook_events_filter: ['completed'] })
    });
    if (!response.ok) throw new Error(await response.text());
    console.log(`🚀 Edit video job started for ${deviceId}`);
}

app.post('/webhook/replicate', async (req, res) => {
    const { deviceId, type, prompt, token } = req.query;
    const jobId = typeof req.query.jobId === 'string' ? req.query.jobId : '';
    if (!isValidDeviceId(deviceId) || !['video', 'music'].includes(type)) return res.status(401).send('Unauthorized');
    if (jobId && !isValidJobId(jobId)) return res.status(401).send('Unauthorized');
    if (!safeEqual(token, webhookToken(deviceId, type, jobId))) return res.status(401).send('Unauthorized');
    const { output, status, error } = req.body || {};
    res.status(200).send('OK');
    if (status !== 'succeeded' || !output) {
        return handleFailure(jobId, deviceId, type, `Replicate status=${status}: ${error || 'no output'}`, 'Generation failed');
    }
    const remoteUrl = Array.isArray(output) ? output[0] : output;
    if (typeof remoteUrl !== 'string' || !remoteUrl.startsWith('https://')) {
        return handleFailure(jobId, deviceId, type, 'Invalid output URL', 'Invalid output');
    }
    if (!firebaseReady) return;
    const ext = type === 'video' ? 'mp4' : 'mp3';
    const fileName = `${type}s/${deviceId}/${Date.now()}.${ext}`;
    try {
        const download = await fetch(remoteUrl);
        if (!download.ok) throw new Error(`Download failed: HTTP ${download.status}`);
        const buffer = Buffer.from(await download.arrayBuffer());
        const bucketFile = bucket.file(fileName);
        await bucketFile.save(buffer, { contentType: type === 'video' ? 'video/mp4' : 'audio/mpeg' });
        const [signedUrl] = await bucketFile.getSignedUrl({
            version: 'v4', action: 'read', expires: Date.now() + 7 * 24 * 3600 * 1000 - 5 * 60 * 1000
        });
        await db.collection(`${type}s`).doc(deviceId).collection('items').add({
            url: signedUrl, prompt: prompt || '', createdAt: admin.firestore.FieldValue.serverTimestamp()
        });
        if (jobId) {
            await db.collection('jobs').doc(jobId).update({
                status: 'completed', completedAt: admin.firestore.FieldValue.serverTimestamp()
            }).catch(e => console.error('Job update error:', e.message));
        }
        await sendNotification(deviceId, `${type}_ready`, { url: signedUrl, prompt: String(prompt || '') });
    } catch (err) {
        console.error(`❌ Upload failed for ${deviceId}:`, err.message);
        await handleFailure(jobId, deviceId, type, `Save failed: ${err.message}`, 'Failed to save file');
    }
});

// ============================================================================
// 10. FCM
// ============================================================================
async function sendNotification(deviceId, type, data) {
    if (!firebaseReady) return;
    try {
        await admin.messaging().send({
            data: { type, ...data },
            topic: `device_${deviceId}`,
            android: { priority: 'high', ttl: 24 * 60 * 60 * 1000 }
        });
        console.log(`📱 FCM (${type}) → device_${deviceId}`);
    } catch (e) { console.error(`FCM error:`, e.message); }
}

async function handleFailure(jobId, deviceId, type, reason, publicMessage) {
    let refunded = false;
    try { refunded = (await failJob(jobId, reason)).refunded; }
    catch (e) { console.error(`failJob (${jobId}):`, e.message); }
    await sendNotification(deviceId, `${type}_error`, { error: publicMessage, refunded: String(refunded) });
}

// ============================================================================
// 11. 👑 Master NOWPayments Webhook (Zevorix + Gradiometer)
// ============================================================================
app.post('/nowpayments/ipn', async (req, res) => {
    try {
        const receivedSig = req.headers['x-nowpayments-sig'];
        const secret = process.env.GRADIOMETER_IPN_SECRET || NOWPAYMENTS_IPN_SECRET;
        
        if (!secret) return res.status(500).send("Config error");
        
        const sortedBody = JSON.stringify(deepSort(req.body));
        const expectedSig = crypto.createHmac('sha512', secret).update(sortedBody).digest('hex');
        
        if (!safeEqual(receivedSig, expectedSig)) {
            console.warn("❌ Invalid IPN signature");
            return res.status(401).send("Invalid signature");
        }

        const { payment_status, order_id, customer_email, price_amount, payment_id } = req.body;

        if (payment_status !== 'finished' && payment_status !== 'confirmed') {
            return res.status(200).send('Not confirmed yet');
        }

        // 1. توجيه دفعات Gradiometer
        if (order_id) {
            if (!gradDb) return res.status(503).send('Gradiometer DB not ready');
            
            await gradDb.collection('purchases').doc(String(order_id)).set({
                paid: true,
                paymentId: String(payment_id),
                confirmedAt: admin.firestore.FieldValue.serverTimestamp()
            }, { merge: true });
            
            console.log(`✅ Gradiometer purchase confirmed: uid=${order_id}`);
            return res.status(200).send('OK');
        } 
        // 2. توجيه دفعات Zevorix
        else if (customer_email) {
            if (!firebaseReady || !payment_id) return res.status(500).send('Database not ready');
            if (!customer_email.includes('@')) return res.status(400).send('Invalid email');
            
            let creditsToAdd = 0;
            const amount = parseFloat(price_amount || 0);
            if (amount >= 130) creditsToAdd = 1800;
            else if (amount >= 65) creditsToAdd = 800;
            else if (amount >= 30) creditsToAdd = 350;
            else if (amount >= 10) creditsToAdd = 100;
            else return res.status(400).send('Amount too low');
            
            let licenseKey = null;
            await db.runTransaction(async (tx) => {
                const orderRef = db.collection('orders').doc(String(payment_id));
                const orderDoc = await tx.get(orderRef);
                if (orderDoc.exists) throw new Error('ALREADY_PROCESSED');
                
                licenseKey = generateLicenseKey();
                tx.set(orderRef, {
                    email: customer_email, licenseKey, amount, credits: creditsToAdd,
                    status: 'issued', createdAt: admin.firestore.FieldValue.serverTimestamp()
                });
                tx.set(db.collection('licenses').doc(licenseKey), {
                    credits: creditsToAdd, email: customer_email,
                    createdAt: admin.firestore.FieldValue.serverTimestamp()
                });
            });
            
            if (SENDGRID_KEY && licenseKey) {
                await sgMail.send({
                    to: customer_email, from: 'tijara6@gmail.com',
                    subject: 'تم تفعيل نسختك المدفوعة من Zevorix AI',
                    html: `<h3>شكراً لشرائك!</h3>
                           <p>كود التفعيل: <strong>${licenseKey}</strong></p>
                           <p>تمت إضافة <strong>${creditsToAdd} نقطة</strong> لرصيدك.</p>`
                }).catch(e => console.error("Email:", e.message));
            }
            return res.status(200).send('License sent successfully');
        }

        return res.status(400).send('Unknown payment type');
    } catch (error) {
        if (error.message === 'ALREADY_PROCESSED') return res.status(200).send('Already processed');
        console.error('Master IPN error:', error.message);
        res.status(500).send('Error');
    }
});

// ============================================================================
// 12. Start
// ============================================================================
const PORT = process.env.PORT || 10000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Server on port ${PORT}`);
    console.log(`🔐 Ed25519 pub: ${Buffer.from(ED25519_PUBLIC_KEY).toString('hex').substring(0, 16)}…`);
});
