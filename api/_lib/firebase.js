import { getApps, initializeApp, cert } from 'firebase-admin/app';
import { getFirestore, FieldValue } from 'firebase-admin/firestore';
import { getAuth } from 'firebase-admin/auth';
const app=getApps()[0]||initializeApp({credential:cert({projectId:process.env.FIREBASE_PROJECT_ID,clientEmail:process.env.FIREBASE_CLIENT_EMAIL,privateKey:process.env.FIREBASE_PRIVATE_KEY?.replace(/\\n/g,'\n')})});
export const db=getFirestore(app);export const auth=getAuth(app);export {FieldValue};
export async function user(req){const m=/^Bearer (.+)$/.exec(req.headers.authorization||'');if(!m)throw Object.assign(new Error('Sign in required'),{status:401});try{return await auth.verifyIdToken(m[1])}catch{throw Object.assign(new Error('Invalid session'),{status:401})}}
