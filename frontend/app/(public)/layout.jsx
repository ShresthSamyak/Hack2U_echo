'use client'
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

export default function PublicLayout({ children }) {

    return (
        <>
            <Navbar />
            {children}
            <Footer />
        </>
    );
}
