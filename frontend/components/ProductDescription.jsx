'use client'
import { ArrowRight } from "lucide-react"
import Image from "next/image"
import Link from "next/link"

const ProductDescription = ({ product }) => {

    return (
        <div className="my-18 text-sm text-slate-600">

            {/* Description Header */}
            <div className="mb-6">
                <h3 className="text-lg font-semibold text-slate-800 mb-4">Product Description</h3>
            </div>

            {/* Description */}
            <p className="max-w-2xl leading-relaxed">{product.description}</p>

            {/* Store Page */}
            <div className="flex gap-3 mt-14">
                <Image src={product.store.logo} alt="" className="size-11 rounded-full ring ring-slate-400" width={100} height={100} />
                <div>
                    <p className="font-medium text-slate-600">Product by {product.store.name}</p>
                    <Link href={`/shop/${product.store.username}`} className="flex items-center gap-1.5 text-green-500">view store <ArrowRight size={14} /></Link>
                </div>
            </div>
        </div>
    )
}

export default ProductDescription