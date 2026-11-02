const express = require('express');
const admin = require('firebase-admin');

// تهيئة Firebase Admin باستخدام ملف الاعتمادات (سنضيفه لاحقاً أو نعتمد البيئة)
admin.initializeApp({
  credential: admin.credential.applicationDefault()
});

const db = admin.firestore();
const app = express();
app.use(express.json());

app.post('/webhook', async (req, res) => {
  try {
    const paymentData = req.body;
    const paymentStatus = paymentData.payment_status;
    const orderId = paymentData.order_id; // معرف المستخدم (UID)

    if (paymentStatus === 'finished' || paymentStatus === 'confirmed') {
      await db.collection('purchases').doc(orderId).set({
        paid: true,
        paymentId: paymentData.payment_id,
        updatedAt: admin.firestore.FieldValue.serverTimestamp()
      }, { merge: true });

      console.log(`Payment success for user: ${orderId}`);
    }

    res.status(200).send('OK');
  } catch (error) {
    console.error('Webhook error:', error);
    res.status(500).send('Error');
  }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
