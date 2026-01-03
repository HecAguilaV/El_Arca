import { initializeApp } from "firebase/app";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";

const firebaseConfig = {
    apiKey: "AIzaSyAvBZjttSBsX1FDOCvc8AZiGtMsku424Vo",
    authDomain: "el-arca-auth.firebaseapp.com",
    projectId: "el-arca-auth",
    storageBucket: "el-arca-auth.firebasestorage.app",
    messagingSenderId: "1096851086854",
    appId: "1:1096851086854:web:63cfd89a394e185b742d87",
    measurementId: "G-5R2GYX42ED"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Services
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();
googleProvider.setCustomParameters({
    prompt: "select_account"
});
export const analytics = typeof window !== "undefined" ? getAnalytics(app) : null;

// Auth Functions
export const loginWithGoogle = async () => {
    try {
        const result = await signInWithPopup(auth, googleProvider);
        return result.user;
    } catch (error) {
        console.error("Error login:", error);
        throw error;
    }
};

export const logout = async () => {
    try {
        await signOut(auth);
    } catch (error) {
        console.error("Error logout:", error);
        throw error;
    }
};
