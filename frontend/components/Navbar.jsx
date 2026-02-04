'use client'
import { Search, ShoppingCart } from "lucide-react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState, useEffect } from "react";
import { useSelector } from "react-redux";
import UserProfile from "./UserProfile";
import { auth } from "@/lib/auth";
import Image from "next/image";
import { assets } from "@/assets/assets";

const Navbar = () => {

    const router = useRouter();

    const [search, setSearch] = useState('')
    const [user, setUser] = useState(null)
    const [authLoading, setAuthLoading] = useState(true)
    const cartCount = useSelector(state => state.cart.total)

    // Listen for auth changes
    useEffect(() => {
        const checkUser = async () => {
            const currentUser = await auth.getUser();
            setUser(currentUser);
            setAuthLoading(false);
        };

        checkUser();

        const { data: { subscription } } = auth.onAuthStateChange((event, session) => {
            setUser(session?.user || null);
        });

        return () => {
            subscription?.unsubscribe();
        };
    }, []);

    const handleSearch = (e) => {
        e.preventDefault()
        router.push(`/shop?search=${search}`)
    }

    return (
        <nav className="relative bg-white">
            <div className="mx-2">
                <div className="flex items-center justify-between max-w-7xl mx-auto py-4  transition-all">

                    <Link href="/" className="relative flex items-center -ml-2">
                        <Image
                            src={assets.echo_plus_logo}
                            alt="Echo Plus"
                            width={280}
                            height={100}
                            className="h-20 w-auto object-contain"
                            priority
                        />
                    </Link>


                    {/* Desktop Menu */}
                    <div className="hidden sm:flex items-center gap-4 lg:gap-8 text-slate-600">
                        <Link href="/">Home</Link>
                        <Link href="/shop">Shop</Link>
                        <a href="https://drive.google.com/file/d/1zInuqrx-Crp5_OcYMeIqaDLicIj9UCVW/view?usp=sharing" target="_blank" rel="noopener noreferrer">About</a>
                        <Link href="/">Contact</Link>

                        <form onSubmit={handleSearch} className="hidden xl:flex items-center w-xs text-sm gap-2 bg-slate-100 px-4 py-3 rounded-full">
                            <Search size={18} className="text-slate-600" />
                            <input className="w-full bg-transparent outline-none placeholder-slate-600" type="text" placeholder="Search products" value={search} onChange={(e) => setSearch(e.target.value)} required />
                        </form>

                        <Link href="/cart" className="relative flex items-center gap-2 text-slate-600">
                            <ShoppingCart size={18} />
                            Cart
                            <button className="absolute -top-1 left-3 text-[8px] text-white bg-slate-600 size-3.5 rounded-full">{cartCount}</button>
                        </Link>

                        {/* Auth Section */}
                        {authLoading ? (
                            <div className="w-10 h-10 rounded-full bg-slate-200 animate-pulse"></div>
                        ) : user ? (
                            <UserProfile />
                        ) : (
                            <Link href="/login" className="px-8 py-2 bg-indigo-500 hover:bg-indigo-600 transition text-white rounded-full flex items-center justify-center">
                                Login
                            </Link>
                        )}

                    </div>

                    {/* Mobile User Button  */}
                    <div className="sm:hidden">
                        {authLoading ? (
                            <div className="w-10 h-10 rounded-full bg-slate-200 animate-pulse"></div>
                        ) : user ? (
                            <UserProfile />
                        ) : (
                            <Link href="/login" className="px-7 py-1.5 bg-indigo-500 hover:bg-indigo-600 text-sm transition text-white rounded-full flex items-center justify-center">
                                Login
                            </Link>
                        )}
                    </div>
                </div>
            </div >
            <hr className="border-gray-300" />
        </nav >
    )
}

export default Navbar