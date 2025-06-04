"use client";

import { useEffect, useRef, useState, useCallback } from "react";
import { useAuth } from "@/contexts/AuthContext";
import { useSelection } from "@/contexts/SelectionContext";
import { useRouter } from "next/navigation";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import toast from "react-hot-toast";

interface Product {
  id: string;
  name: string;
  price: number;
  image_url: string;
  rating: number;
}

export default function CataloguePage() {
  const { isAuthenticated } = useAuth();
  const { espacioElegido, estiloElegido } = useSelection();
  const [products, setProducts] = useState<Product[]>([]);
  const [originalProducts, setOriginalProducts] = useState<Product[]>([]);
  const [sortOrder, setSortOrder] = useState<'original' | 'asc' | 'desc'>('original');
  const [addedToCart, setAddedToCart] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const loaderRef = useRef<HTMLDivElement>(null);
  const router = useRouter();

  const fetchProducts = useCallback(async () => {
    const token = localStorage.getItem("access_token");
    const headers: HeadersInit = { "Content-Type": "application/json" };
    if (token) headers["Authorization"] = `Bearer ${token}`;

    const res = await fetch(
      `http://localhost:8000/api/v1/recommendations/user?space=${espacioElegido}&style=${estiloElegido}&limit=12&offset=${offset}`,
      { headers }
    );

    if (!res.ok) {
      setHasMore(false);
      return;
    }

    const data = await res.json();
    if (data.length === 0) setHasMore(false);
    setProducts(prev => [...prev, ...data]);
    setOriginalProducts(prev => [...prev, ...data]);
  }, [espacioElegido, estiloElegido, offset]);

  useEffect(() => {
    if (espacioElegido && estiloElegido) {
      setOffset(0);
      setProducts([]);
      setOriginalProducts([]);
      setHasMore(true);
    }
  }, [espacioElegido, estiloElegido]);

  useEffect(() => {
    if (espacioElegido && estiloElegido && offset === 0) fetchProducts();
  }, [fetchProducts, espacioElegido, estiloElegido, offset]);

  useEffect(() => {
    const observer = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore) {
        setOffset(prev => prev + 12);
      }
    });
    if (loaderRef.current) observer.observe(loaderRef.current);
    return () => observer.disconnect();
  }, [hasMore]);

  useEffect(() => {
    if (offset !== 0) fetchProducts();
  }, [offset, fetchProducts]);

  const handleSortChange = () => {
    if (sortOrder === 'original') {
      setSortOrder('asc');
      setProducts([...products].sort((a, b) => a.price - b.price));
    } else if (sortOrder === 'asc') {
      setSortOrder('desc');
      setProducts([...products].sort((a, b) => b.price - a.price));
    } else {
      setSortOrder('original');
      setProducts(originalProducts);
    }
  };

  const handleAddToCart = async (productId: string) => {
    if (!isAuthenticated) return;
    const res = await fetch("http://localhost:8000/api/v1/users/me/cart", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${localStorage.getItem("access_token")}`,
      },
      body: JSON.stringify({ product_id: productId, quantity: 1 }),
    });

    if (res.ok) {
      toast.success("Producto añadido al carrito");
      setAddedToCart(productId);
      setTimeout(() => setAddedToCart(null), 1500);
    } else {
      toast.error("No se pudo añadir al carrito");
    }
  };

  const handleProductClick = async (productId: string) => {
    if (isAuthenticated) {
      await fetch("http://localhost:8000/api/v1/user_history/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ product_id: productId, action: "click" }),
      });
    }
    router.push(`/product/${productId}`);
  };

  return (
    <>
      <Header>
        <div className="flex gap-2">
          <Link href="/login">
            <Button variant="outline" className="bg-camel text-black border border-white hover:bg-white hover:[color:var(--camel)!important]">Iniciar sesión</Button>
          </Link>
          <Link href="/register">
            <Button variant="outline" className="bg-camel text-black border border-white hover:bg-white hover:[color:var(--camel)!important]">Registrarse</Button>
          </Link>
        </div>
      </Header>

      <div className="p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-semibold">Catálogo recomendado</h1>
          <button
            className="text-sm border px-4 py-2 rounded hover:bg-gray-100"
            onClick={handleSortChange}
          >
            Ordenar por precio ({sortOrder === 'original' ? 'sin orden' : sortOrder === 'asc' ? 'ascendente' : 'descendente'})
          </button>
        </div>

        <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
          {products.map(product => (
            <div
              key={product.id}
              className="border rounded-xl shadow hover:shadow-lg cursor-pointer overflow-hidden"
              onClick={() => handleProductClick(product.id)}
            >
              <img src={product.image_url} alt={product.name} className="w-full h-40 object-contain bg-white" />
              <div className="p-4">
                <h2 className="text-lg font-semibold mb-2">{product.name}</h2>
                <p className="text-gray-700 mb-1">{product.price.toFixed(2)} €</p>
                <p className="text-yellow-500">⭐ {product.rating?.toFixed(1) || '0.0'}</p>
                {isAuthenticated && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleAddToCart(product.id);
                    }}
                    className={`mt-3 w-full py-2 rounded transition-all ${
                      addedToCart === product.id ? "bg-green-600 text-white" : "bg-black text-white hover:bg-gray-800"
                    }`}
                  >
                    {addedToCart === product.id ? "Añadido ✓" : "Añadir al carrito"}
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>

        {hasMore && <div ref={loaderRef} className="text-center py-4">Cargando más...</div>}
      </div>

      <Footer />
    </>
  );
}
