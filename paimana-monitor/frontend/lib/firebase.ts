/**
 * Firebase client-side initialisation.
 *
 * Fill in the values below from:
 *   Firebase Console → Project Settings → General → Your apps → Web app → SDK setup and configuration
 *
 * Or set them via environment variables in frontend/.env.local (recommended).
 */
import { getApps, initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey:            process.env.NEXT_PUBLIC_FIREBASE_API_KEY || "AIzaSyBZaFZmPGUNq41AlAz0hBR20NoNwbmVVKY",
  authDomain:        process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || "paimana.firebaseapp.com",
  projectId:         process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "paimana",
  storageBucket:     process.env.NEXT_PUBLIC_FIREBASE_STORAGE_BUCKET || "paimana.firebasestorage.app",
  messagingSenderId: process.env.NEXT_PUBLIC_FIREBASE_MESSAGING_SENDER_ID || "288929193818",
  appId:             process.env.NEXT_PUBLIC_FIREBASE_APP_ID || "1:288929193818:web:30fd3d4333b5823586dd63",
  measurementId:     process.env.NEXT_PUBLIC_FIREBASE_MEASUREMENT_ID || "G-KHHXLT7K9G",
};

// Prevent duplicate app initialisation during Next.js hot-reloads
const app = getApps().length === 0 ? initializeApp(firebaseConfig) : getApps()[0];

export const auth = getAuth(app);
export const analytics = typeof window !== "undefined" ? getAnalytics(app) : undefined;
export default app;
