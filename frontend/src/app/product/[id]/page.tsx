"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import toast from "react-hot-toast";
import Link from "next/link";
import { Star } from "lucide-react";
import Image from "next/image";
import axios from "@/lib/axios";

interface Review {
  id: string;
  user_id: string;
  username: string;
  rating: number;
  comment?: string;
  timestamp?: string;
}

interface Product {
  id: string;
  name: string;
  description: string;
  price: number;
  image_url: string;
  rating: number;
  category: string;
  purchase_link: string;
  reviews?: Review[];
}

export default function ProductPage() {
  const { id } = useParams();
  const { isAuthenticated, userId } = useAuth();
  const [product, setProduct] = useState<Product | null>(null);
  const [recommendations, setRecommendations] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [newRating, setNewRating] = useState<number>(0);
  const [newComment, setNewComment] = useState("");

  useEffect(() => {
    const fetchProduct = async () => {
      try {
        const res = await axios.get(`/products/${id}`);
        setProduct(res.data);
      } catch {
        toast.error("Producto no encontrado");
      } finally {
        setLoading(false);
      }
    };

    const fetchRecommendations = async () => {
      try {
        const res = await axios.get(`/products/${id}/recomendations`, {
          params: { top_n: 4 },
        });
        setRecommendations(res.data);
      } catch (e) {
        console.error(e);
      }
    };

    if (id) {
      fetchProduct();
      fetchRecommendations();
    }
  }, [id]);

  const handleAddToCart = async () => {
    if (!isAuthenticated || !product) return;
    try {
      await axios.post(
        "/users/me/cart",
        { product_id: product.id, quantity: 1 },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      );
      toast.success("Producto añadido al carrito");
    } catch {
      toast.error("Error al añadir al carrito");
    }
  };

  const handleSubmitReview = async () => {
    if (!newRating || newRating < 1 || newRating > 5) {
      toast.error("La puntuación debe estar entre 1 y 5");
      return;
    }

    try {
      const res = await axios.post(
        `/products/${id}/reviews`,
        {
          rating: newRating,
          comment: newComment,
        },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem("access_token")}`,
          },
        }
      );

      const review = res.data;
      setProduct(prev =>
        prev ? { ...prev, reviews: [review, ...(prev.reviews || [])] } : prev
      );
      toast.success("Reseña enviada correctamente");
      setNewRating(0);
      setNewComment("");
    } catch {
      toast.error("Error al enviar la reseña");
    }
  };

  const handleDeleteReview = async (reviewId: string) => {
    if (!product) return;

    try {
      await axios.delete(`/products/${product.id}/reviews/${reviewId}`, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });

      toast.success("Reseña eliminada");
      setProduct(prev =>
        prev ? { ...prev, reviews: prev.reviews?.filter(r => r.id !== reviewId) } : prev
      );
    } catch {
      toast.error("Error al eliminar la reseña");
    }
  };

  const renderStars = () => {
    const stars = [];
    for (let i = 1; i <= 10; i++) {
      const value = i / 2;
      stars.push(
        <Star
          key={value}
          size={24}
          strokeWidth={1}
          fill={newRating >= value ? "#facc15" : "none"}
          onClick={() => setNewRating(value)}
          className="cursor-pointer"
        />
      );
    }
    return stars;
  };

  if (loading || !product) return <div className="p-6">Cargando producto...</div>;

  return (
    <>
      <Header>
        <div className="flex gap-2">
          <Link href="/login">
            <Button variant="outline" className="bg-camel text-black border border-white hover:bg-white hover:[color:var(--camel)!important]">
              Iniciar sesión
            </Button>
          </Link>
          <Link href="/register">
            <Button variant="outline" className="bg-camel text-black border border-white hover:bg-white hover:[color:var(--camel)!important]">
              Registrarse
            </Button>
          </Link>
        </div>
      </Header>

      <main className="p-6 max-w-5xl mx-auto space-y-10">
        <section className="flex flex-col md:flex-row gap-6">
          <Image src={product.image_url} alt={product.name} className="w-full md:w-1/2 object-contain rounded bg-white" width={300} height={160}/>
          <div className="flex flex-col gap-4">
            <h1 className="text-3xl font-bold">{product.name}</h1>
            <p className="text-gray-600">{product.category}</p>
            <p className="text-xl text-black">{product.price.toFixed(2)} €</p>
            <p className="text-yellow-500">⭐ {product.rating?.toFixed(1) || "0.0"}</p>
            <p className="text-gray-800">{product.description}</p>
            <a href={product.purchase_link} target="_blank" rel="noopener noreferrer" className="text-blue-500 underline w-fit">
              Ir al enlace de compra
            </a>
            {isAuthenticated && (
              <Button onClick={handleAddToCart} className="mt-4 w-fit">
                Añadir al carrito
              </Button>
            )}
          </div>
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-2">Reseñas</h2>
          <div className="max-h-60 overflow-y-auto border rounded p-4 space-y-3 bg-gray-50">
            {product.reviews && product.reviews.length > 0 ? (
              product.reviews.map((review, i) => (
                <div key={i} className="border-b pb-2">
                  <p className="text-sm text-gray-700">Usuario: {review.username}</p>
                  <p className="text-yellow-500">⭐ {review.rating}</p>
                  {review.comment && <p>{review.comment}</p>}

                  {isAuthenticated && userId === review.user_id && (
                    <Button
                      variant="ghost"
                      size="sm"
                      onClick={() => handleDeleteReview(review.id)}
                      className="text-red-500 hover:underline"
                    >
                      Eliminar
                    </Button>
                  )}
                </div>
              ))
            ) : (
              <p>No hay reseñas aún.</p>
            )}
          </div>

          {isAuthenticated && (
            <div className="mt-6 space-y-4">
              <h3 className="text-lg font-medium">Deja tu reseña</h3>
              <div className="flex gap-1">
                {renderStars()}
              </div>
              <textarea
                value={newComment}
                onChange={(e) => setNewComment(e.target.value)}
                placeholder="Comentario (opcional)"
                className="w-full border rounded p-2"
              ></textarea>
              <Button onClick={handleSubmitReview}>Enviar reseña</Button>
            </div>
          )}
        </section>

        <section>
          <h2 className="text-2xl font-semibold mb-2">Productos recomendados</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {recommendations.map((rec) => (
              <Link href={`/product/${rec.id}`} key={rec.id} className="border rounded p-4 bg-white shadow hover:shadow-lg transition">
                <Image src={rec.image_url} alt={rec.name} className="h-40 w-full object-contain mb-2" width={300} height={160}/>
                <h3 className="font-bold">{rec.name}</h3>
                <p className="text-sm text-gray-600">{rec.category}</p>
                <p className="text-sm text-yellow-500">⭐ {rec.rating?.toFixed(1)}</p>
                <p className="text-black font-semibold">{rec.price.toFixed(2)} €</p>
              </Link>
            ))}
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
}
