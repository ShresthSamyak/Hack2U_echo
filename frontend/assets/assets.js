import gs_logo from "./gs_logo.jpg"
import echo_plus_logo from "./echo_plus_logo.png"
import happy_store from "./happy_store.webp"
import upload_area from "./upload_area.svg"
import hero_model_img from "./hero_model_img.png"
import hero_product_img1 from "./hero_product_img1.png"
import hero_product_img2 from "./hero_product_img2.png"
import product_img1 from "./product_img1.jpg"
import product_img2 from "./product_img2.png"
import product_img3 from "./product_img3.jpg"
import product_img4 from "./product_img4.jpg"
import product_img5 from "./product_img5.jpg"
import product_img6 from "./product_img6.jpg"
import product_img7 from "./product_img7.jpg"
import product_img8 from "./product_img8.png"
import product_img9 from "./product_img9.jpg"
import product_img10 from "./product_img10.jpg"
import product_img11 from "./product_img11.jpg"
import product_img12 from "./product_img12.jpg"
import { ClockFadingIcon, HeadsetIcon, SendIcon } from "lucide-react";
import profile_pic1 from "./profile_pic1.jpg"
import profile_pic2 from "./profile_pic2.jpg"
import profile_pic3 from "./profile_pic3.jpg"

export const assets = {
    upload_area, hero_model_img,
    hero_product_img1, hero_product_img2, gs_logo, echo_plus_logo,
    product_img1, product_img2, product_img3, product_img4, product_img5, product_img6,
    product_img7, product_img8, product_img9, product_img10, product_img11, product_img12,
}

export const categories = ["Washing Machine", "Refrigerator", "Headphones"];

export const dummyStoreData = {
    id: "store_1",
    userId: "user_1",
    name: "Tech Appliances Store",
    description: "Your trusted source for premium home appliances and electronics. We specialize in washing machines, refrigerators, and audio equipment with comprehensive support and warranty services.",
    username: "techappliances",
    address: "Patiala, Punjab, India",
    status: "approved",
    isActive: true,
    logo: happy_store,
    email: "shresthsamyak@gmail.com",
    contact: "+91 62********",
    createdAt: "2026-02-03T00:00:00.000Z",
    updatedAt: "2026-02-03T00:00:00.000Z",
    user: {
        id: "user_1",
        name: "Tech Appliances",
        email: "shresthsamyak@gmail.com",
        image: gs_logo,
    }
}

// Your actual products from RAG database
export const productDummyData = [
    {
        id: "AT-WM-9KG-BLACK",
        name: "AquaTech Pro 9000 (Matte Black)",
        description: "Front-load automatic washing machine for household use with 9kg capacity, inverter motor technology, and smart connectivity features. Includes steam wash, WiFi connectivity, and auto detergent dispenser. Energy rating A++ with ultra-quiet operation at 52dB.",
        mrp: 499,
        price: 420,
        images: [product_img1, product_img2],
        category: "Washing Machine",
        storeId: "store_1",
        inStock: true,
        store: dummyStoreData,
        rating: [],
        createdAt: '2026-02-03T00:00:00.000Z',
        updatedAt: '2026-02-03T00:00:00.000Z',
    },
    {
        id: "AT-WM-9KG-WHITE",
        name: "AquaTech Pro 9000 (Pearl White)",
        description: "Front-load automatic washing machine for household use with 9kg capacity, inverter motor technology, and smart connectivity features. Includes steam wash, WiFi connectivity, and auto detergent dispenser. Energy rating A++ with ultra-quiet operation at 52dB.",
        mrp: 499,
        price: 420,
        images: [product_img3, product_img4],
        category: "Washing Machine",
        storeId: "store_1",
        inStock: true,
        store: dummyStoreData,
        rating: [],
        createdAt: '2026-02-03T00:00:00.000Z',
        updatedAt: '2026-02-03T00:00:00.000Z',
    },
    {
        id: "AT-WM-9KG-SILVER",
        name: "AquaTech Pro 9000 (Brushed Silver)",
        description: "Front-load automatic washing machine for household use with 9kg capacity, inverter motor technology, and smart connectivity features. Premium brushed silver finish. Includes steam wash, WiFi connectivity, and auto detergent disp enser. Energy rating A++.",
        mrp: 529,
        price: 450,
        images: [product_img5, product_img6],
        category: "Washing Machine",
        storeId: "store_1",
        inStock: true,
        store: dummyStoreData,
        rating: [],
        createdAt: '2026-02-03T00:00:00.000Z',
        updatedAt: '2026-02-03T00:00:00.000Z',
    },
    {
        id: "CM-FF-360-BLACK",
        name: "CoolMax FrostFree 360 (Matte Black)",
        description: "360L frost-free refrigerator with inverter compressor technology, digital temperature control, and energy-efficient cooling system. Features LED lighting, door alarm, and advanced temperature management. Energy rating A+++ with whisper-quiet 38dB operation.",
        mrp: 749,
        price: 650,
        images: [product_img7, product_img8],
        category: "Refrigerator",
        storeId: "store_1",
        inStock: true,
        store: dummyStoreData,
        rating: [],
        createdAt: '2026-02-03T00:00:00.000Z',
        updatedAt: '2026-02-03T00:00:00.000Z',
    },
    {
        id: "CM-FF-360-STEEL",
        name: "CoolMax FrostFree 360 (Stainless Steel)",
        description: "360L frost-free refrigerator with inverter compressor technology, digital temperature control, and energy-efficient cooling system. Premium stainless steel finish. Features LED lighting, door alarm, and advanced temperature management. Energy rating A+++.",
        mrp: 799,
        price: 680,
        images: [product_img9, product_img10],
        category: "Refrigerator",
        storeId: "store_1",
        inStock: true,
        store: dummyStoreData,
        rating: [],
        createdAt: '2026-02-03T00:00:00.000Z',
        updatedAt: '2026-02-03T00:00:00.000Z',
    },
    {
        id: "SP-ANC-BLACK",
        name: "SoundPro ANC Elite (Midnight Black)",
        description: "Premium over-ear wireless headphones with active noise cancellation, 40-hour battery life, and multipoint Bluetooth 5.2 connectivity. Features fast charging, custom EQ via app, and premium comfort earpads. Perfect for work, travel, and entertainment.",
        mrp: 329,
        price: 280,
        images: [product_img11, product_img12],
        category: "Headphones",
        storeId: "store_1",
        inStock: true,
        store: dummyStoreData,
        rating: [],
        createdAt: '2026-02-03T00:00:00.000Z',
        updatedAt: '2026-02-03T00:00:00.000Z',
    },
];

export const ourSpecsData = [
    { title: "Free Shipping", description: "Enjoy fast, free delivery on every order no conditions, just reliable doorstep.", icon: SendIcon, accent: '#05DF72' },
    { title: "2-Year Warranty", description: "All appliances come with comprehensive warranty coverage and support.", icon: ClockFadingIcon, accent: '#FF8904' },
    { title: "24/7 Customer Support", description: "We're here for you. Get expert help with our customer support.", icon: HeadsetIcon, accent: '#A684FF' }
]

export const addressDummyData = {
    id: "addr_1",
    userId: "user_1",
    name: "John Doe",
    email: "johndoe@example.com",
    street: "123 Main St",
    city: "New York",
    state: "NY",
    zip: "10001",
    country: "USA",
    phone: "1234567890",
    createdAt: '2026-02-03T00:00:00.000Z',
}

export const couponDummyData = []

export const dummyUserData = {
    id: "user_1",
    name: "Demo User",
    email: "demo@techappliances.com",
    image: gs_logo,
    cart: {}
}

export const orderDummyData = []

export const storesDummyData = [dummyStoreData]

export const dummyAdminDashboardData = {
    "orders": 0,
    "stores": 1,
    "products": 6,
    "revenue": "0",
    "allOrders": []
}

export const dummyStoreDashboardData = {
    "ratings": [],
    "totalOrders": 0,
    "totalEarnings": 0,
    "totalProducts": 6
}