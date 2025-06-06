"use client";

import { useEffect, useRef, useState } from "react";
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
  category: string;
}

const category_labels = [
  "lighting",
  "home decor and accessories",
  "storage and organization",
  "tables and chairs",
  "desks and desk chairs",
  "home textiles",
  "sofas and armchairs",
  "flooring, rugs and mats",
  "outdoor",
  "plants and gardening",
  "beds and mattresses",
  "smart home and technology",
  "kitchen and tableware",
];

export default function CataloguePage() {
  const { isAuthenticated } = useAuth();
  const { espacioElegido, estiloElegido, setEspacioElegido, setEstiloElegido } = useSelection();
  const [products, setProducts] = useState<Product[]>([]);
  const [originalProducts, setOriginalProducts] = useState<Product[]>([]);
  const [sortOrder, setSortOrder] = useState<'original' | 'asc' | 'desc'>('original');
  const [addedToCart, setAddedToCart] = useState<string | null>(null);
  const [offset, setOffset] = useState(0);
  const [hasMore, setHasMore] = useState(true);
  const [categoriasSeleccionadas, setCategoriasSeleccionadas] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const loaderRef = useRef<HTMLDivElement>(null);
  const router = useRouter();
  const skipNextScroll = useRef(false);
  const [espacios, setEspacios] = useState<{ id: string; name: string }[]>([]);
  const [estilos, setEstilos] = useState<{ id: string; name: string }[]>([]);

  useEffect(() => {
    const fetchFiltros = async () => {
      const [resEspacios, resEstilos] = await Promise.all([
        fetch("http://localhost:8000/api/v1/spaces/"),
        fetch("http://localhost:8000/api/v1/styles/"),
      ]);
      if (resEspacios.ok) setEspacios(await resEspacios.json());
      if (resEstilos.ok) setEstilos(await resEstilos.json());
    };
    fetchFiltros();
  }, []);

  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true);

      const token = localStorage.getItem("access_token");
      const headers: HeadersInit = { "Content-Type": "application/json" };
      if (token) headers["Authorization"] = `Bearer ${token}`;

      const espacioNombre = espacios.find(e => e.id === espacioElegido)?.name ?? "";
      const estiloNombre = estilos.find(e => e.id === estiloElegido)?.name ?? "";

      if (!espacioNombre || !estiloNombre) {
        setIsLoading(false);
        return;
      }

      const url = new URL("http://localhost:8000/api/v1/recommendations/user");
      url.searchParams.append("space", espacioNombre);
      url.searchParams.append("style", estiloNombre);
      url.searchParams.append("limit", "12");
      url.searchParams.append("offset", offset.toString());
      if (categoriasSeleccionadas.length > 0) {
        categoriasSeleccionadas.forEach(cat => url.searchParams.append("categories", cat));
      }

      const res = await fetch(url.toString(), { headers });

      if (!res.ok) {
        setHasMore(false);
        setIsLoading(false);
        return;
      }

      const data = await res.json();
      if (data.length === 0) {
        setHasMore(false);
        setIsLoading(false);
        return;
      }

      setProducts(prev => {
        const nuevos = data.filter((p: Product) => !prev.some(existing => existing.id === p.id));
        return [...prev, ...nuevos];
      });

      setOriginalProducts(prev => {
        const nuevos = data.filter((p: Product) => !prev.some(existing => existing.id === p.id));
        return [...prev, ...nuevos];
      });

      setIsLoading(false);
      skipNextScroll.current = false;
    };

    if (
      espacioElegido &&
      estiloElegido &&
      espacios.length > 0 &&
      estilos.length > 0 &&
      !isLoading
    ) {
      fetchData();
    }
  }, [offset, espacioElegido, estiloElegido, categoriasSeleccionadas, espacios, estilos]);


  useEffect(() => {
    skipNextScroll.current = true;
    setOffset(0);
    setProducts([]);
    setOriginalProducts([]);
    setHasMore(true);

    setTimeout(() => {
      skipNextScroll.current = false;
      setOffset(0);
    }, 50);
  }, [espacioElegido, estiloElegido, categoriasSeleccionadas]);

  useEffect(() => {
    const observer = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && hasMore && !isLoading && !skipNextScroll.current) {
        setOffset(prev => prev + 12);
      }
    });
    if (loaderRef.current) observer.observe(loaderRef.current);
    return () => observer.disconnect();
  }, [hasMore, isLoading]);

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

  const handleClearCategories = () => {
    setCategoriasSeleccionadas([]);
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

      <main className="flex-grow p-6">
        <div className="flex items-center justify-between mb-6">
          <h1 className="text-3xl font-semibold">Catálogo recomendado</h1>
          <button
            className="text-sm border px-4 py-2 rounded hover:bg-gray-100"
            onClick={handleSortChange}
          >
            Ordenar por precio ({sortOrder === 'original' ? 'sin orden' : sortOrder === 'asc' ? 'ascendente' : 'descendente'})
          </button>
        </div>

        <div className="mb-4">
          <label className="block font-medium mb-2">Filtrar por categoría:</label>
          <div className="flex flex-wrap gap-2 mb-2">
            {category_labels.map(categoria => (
              <button
                key={categoria}
                onClick={() => {
                  setCategoriasSeleccionadas(prev =>
                    prev.includes(categoria)
                      ? prev.filter(cat => cat !== categoria)
                      : [...prev, categoria]
                  );
                }}
                className={`px-3 py-1 border rounded text-sm ${
                  categoriasSeleccionadas.includes(categoria)
                    ? "bg-black text-white"
                    : "bg-white text-black"
                }`}
              >
                {categoria}
              </button>
            ))}
            <button
              onClick={handleClearCategories}
              className="px-3 py-1 border rounded text-sm bg-red-100 text-red-800 hover:bg-red-200"
            >
              Limpiar filtros
            </button>
          </div>
        </div>

        <div className="mb-6">
          <h2 className="text-xl font-semibold mb-4">Filtrar por espacio y estilo</h2>
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex flex-col">
              <label className="text-sm font-medium mb-1" htmlFor="espacio-select">Espacio:</label>
              <select
                id="espacio-select"
                value={espacioElegido}
                onChange={(e) => setEspacioElegido(e.target.value)}
                className="border border-gray-300 rounded px-3 py-2 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-camel"
              >
                <option value="">Selecciona un espacio</option>
                {espacios.map((espacio) => (
                  <option key={espacio.id} value={espacio.id}>{espacio.name}</option>
                ))}
              </select>
            </div>

            <div className="flex flex-col">
              <label className="text-sm font-medium mb-1" htmlFor="estilo-select">Estilo:</label>
              <select
                id="estilo-select"
                value={estiloElegido}
                onChange={(e) => setEstiloElegido(e.target.value)}
                className="border border-gray-300 rounded px-3 py-2 bg-white shadow-sm focus:outline-none focus:ring-2 focus:ring-camel"
              >
                <option value="">Selecciona un estilo</option>
                {estilos.map((estilo) => (
                  <option key={estilo.id} value={estilo.id}>{estilo.name}</option>
                ))}
              </select>
            </div>
          </div>
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
      </main>

      <Footer />
    </>
  );
}
