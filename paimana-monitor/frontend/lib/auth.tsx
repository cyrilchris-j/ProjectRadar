/**
 * Auth context — Firebase-backed sign in / sign out.
 *
 * Flow:
 *  1. signInWithEmailAndPassword() → Firebase ID token
 *  2. POST /api/auth/verify with the ID token → backend upserts user row
 *  3. onAuthStateChanged keeps the session alive; token auto-refreshes via Firebase SDK
 */
"use client";

import React, { createContext, useContext, useEffect, useState } from "react";
import {
  signInWithEmailAndPassword,
  signOut as firebaseSignOut,
  onAuthStateChanged,
  type User as FirebaseUser,
} from "firebase/auth";
import { auth } from "@/lib/firebase";
import { verifyToken, type CurrentUser } from "@/lib/api";

interface AuthContextType {
  user: CurrentUser | null;
  firebaseUser: FirebaseUser | null;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<CurrentUser | null>(null);
  const [firebaseUser, setFirebaseUser] = useState<FirebaseUser | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    // Listen for Firebase auth state changes (handles page refresh, token expiry, etc.)
    const unsubscribe = onAuthStateChanged(auth, async (fbUser) => {
      setFirebaseUser(fbUser);
      if (fbUser) {
        try {
          const idToken = await fbUser.getIdToken();
          const profile = await verifyToken(idToken);
          setUser(profile);
        } catch {
          // Token valid but no matching user in DB yet — will be created on next verify call
          setUser(null);
        }
      } else {
        setUser(null);
      }
      setIsLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const login = async (email: string, password: string) => {
    // Step 1: Firebase sign-in
    const credential = await signInWithEmailAndPassword(auth, email, password);
    // Step 2: Get ID token and call backend /verify (upserts user row, returns profile)
    const idToken = await credential.user.getIdToken();
    const profile = await verifyToken(idToken);
    setUser(profile);
    setFirebaseUser(credential.user);
  };

  const logout = async () => {
    await firebaseSignOut(auth);
    setUser(null);
    setFirebaseUser(null);
    window.location.href = "/login";
  };

  return (
    <AuthContext.Provider value={{ user, firebaseUser, isLoading, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
