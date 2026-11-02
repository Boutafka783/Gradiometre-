// ══════════════════════════════════════════════════════════════════════════════
// Zevorix AI & Gradiometer Combined Backend (v5, latest Gemini models)
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
// 2. Firebase Admin
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
        console.log("🔥 Firebase ready.");
    } else { console.warn("⚠️ Firebase key missing."); }
} catch (e) { console.error("❌ Firebase init failed:", e.message); }

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
const isValidDeviceId = (id) => typeof id === 'string' && /^[A-Za-z0-9_-]{6,64}$/.test(id);
const isValidJobId = (id) => typeof id === 'string' && /^[A-Za-z0-9]{10,40}$/.test(id);
const webhookToken = (d, t, j) => crypto.createHmac('sha256', LICENSE_SECRET).update(`WH|${d}|${t}|${j || ''}`).digest('hex').substring(0, 32);

// ============================================================================
// 4. Credits & Deductions
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
// 5. Public & Gradiometer Routes
// ============================================================================
app.get('/', (req, res) => {
    res.json({
        status: 'ok',
        features: {
            firebase: firebaseReady,
            replicate: !!REPLICATE_TOKEN,
            ai: { gemini: !!GEMINI_API_KEY, openai: !!OPENAI_API_KEY, claude: !!CLAUDE_API_KEY },
            license: 'ed25519'
        }
    });
});

// 🟢 مسارات تطبيق Gradiometer الجديدة
app.post('/api/gradiometer/verify-payment', async (req, res) => {
    try {
        if (!firebaseReady) return res.status(503).json({ error: 'Database not ready' });
        const { deviceId, paymentId } = req.body || {};
        if (!deviceId) return res.status(400).json({ error: 'Invalid device' });

        await db.collection('gradiometer_purchases').doc(deviceId).set({
            paid: true,
            paymentId: paymentId || 'manual_verify',
            updatedAt: admin.firestore.FieldValue.serverTimestamp()
        }, { merge: true });

        return res.json({ success: true, message: 'Device unlocked successfully' });
    } catch (e) {
        console.error('Gradiometer verify error:', e.message);
        return res.status(500).json({ error: 'Internal error' });
    }
});

app.post('/api/gradiometer/check-status', async (req, res) => {
    try {
        if (!firebaseReady) return res.status(503).json({ error: 'Database not ready' });
        const { deviceId } = req.body || {};
        if (!deviceId) return res.status(400).json({ error: 'Invalid device' });

        const doc = await db.collection('gradiometer_purchases').doc(deviceId).get();
        if (!doc.exists) {
            return res.json({ paid: false });
        }
        return res.json({ paid: doc.data().paid === true });
    } catch (e) {
        return res.status(500).json({ error: 'Internal error' });
    }
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
// 6. NOWPayments Webhook (Zevorix)
// ============================================================================
app.post('/paymentWebhook', async (req, res) => {
    try {
        const receivedSig = req.headers['x-nowpayments-sig'];
        const sortedBody = JSON.stringify(deepSort(req.body));
        if (!NOWPAYMENTS_IPN_SECRET) return res.status(500).send("Config error");
        const expectedSig = crypto.createHmac('sha512', NOWPAYMENTS_IPN_SECRET).update(sortedBody).digest('hex');
        if (!safeEqual(receivedSig, expectedSig)) return res.status(401).send("Invalid signature");
        const { payment_status, customer_email, price_amount } = req.body;
        const paymentId = req.body.payment_id ? String(req.body.payment_id) : null;
        if (payment_status !== 'finished' && payment_status !== 'confirmed') return res.status(200).send('Not confirmed yet');
        if (!firebaseReady || !paymentId) return res.status(500).send('Database not ready');
        if (!customer_email || !customer_email.includes('@')) return res.status(400).send('Invalid email');
        let creditsToAdd = 0;
        const amount = parseFloat(price_amount || 0);
        if (amount >= 130) creditsToAdd = 1800;
        else if (amount >= 65) creditsToAdd = 800;
        else if (amount >= 30) creditsToAdd = 350;
        else if (amount >= 10) creditsToAdd = 100;
        else return res.status(400).send('Amount too low');
        let licenseKey = null;
        await db.runTransaction(async (tx) => {
            const orderRef = db.collection('orders').doc(paymentId);
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
        res.status(200).send('License sent successfully');
    } catch (error) {
        if (error.message === 'ALREADY_PROCESSED') return res.status(200).send('Already processed');
        console.error('Payment webhook error:', error.message);
        res.status(500).send('Error');
    }
});

// ============================================================================
// 7. Start Server
// ============================================================================
const PORT = process.env.PORT || 10000;
app.listen(PORT, '0.0.0.0', () => {
    console.log(`🚀 Server on port ${PORT}`);
    console.log(`🔐 Ed25519 pub: ${Buffer.from(ED25519_PUBLIC_KEY).toString('hex').substring(0, 16)}…`);
});

