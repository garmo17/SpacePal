"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/contexts/AuthContext";
import axios from "@/lib/axios";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import Spinner from "@/components/Spinner";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import ProtectedPage from "@/components/ProtectedPage";
import { toast } from "react-hot-toast";


interface CartItem {
  product_id: string;
  quantity: number;
  product?: {
    name: string;
    description: string;
    price: number;
    purchase_link: string;
    image_url: string;
  };
}

function CartPageContent() {
  const { user } = useAuth();
  const [cart, setCart] = useState<CartItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [success, setSuccess] = useState<string>("");

  const token =
    typeof window !== "undefined" ? localStorage.getItem("access_token") : null;

  useEffect(() => {
    const fetchCart = async () => {
      if (!token) return;
      try {
        const { data } = await axios.get("/users/me/cart", {
          headers: { Authorization: `Bearer ${token}` },
        });

        const detailedCart = await Promise.all(
          data.map(async (item: CartItem) => {
            const product = await axios.get(`/products/${item.product_id}`);
            return { ...item, product: product.data };
          })
        );

        setCart(detailedCart);
      } catch (err) {
        console.error("Error fetching cart:", err);
      } finally {
        setLoading(false);
      }
    };

    if (token) fetchCart();
  }, [token]);

  const updateQuantity = async (productId: string, quantity: number) => {
    if (!token) return;
    try {
      await axios.patch(
        `/users/me/cart/${productId}`,
        { quantity },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setCart((prev) =>
        prev.map((item) =>
          item.product_id === productId ? { ...item, quantity } : item
        )
      );
      toast.success("¡Cantidad actualizada!");
    } catch (err) {
      console.error("Error updating quantity:", err);
      toast.error("Error al actualizar la cantidad.");
    }
  };

  const removeFromCart = async (productId: string) => {
    if (!token) return;
    try {
      await axios.delete(`/users/me/cart/${productId}`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setCart((prev) => prev.filter((item) => item.product_id !== productId));
      toast.success("Producto eliminado del carrito.");
    } catch (err) {
      console.error("Error removing product:", err);
      toast.error("Error al eliminar el producto.");
    }
  };

  const clearCart = async () => {
    if (!token) return;
    try {
      await axios.delete(`/users/me/cart/clear`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setCart([]);
      toast.success("Carrito vaciado correctamente.");
    } catch (err) {
      console.error("Error clearing cart:", err);
      toast.error("Error al vaciar el carrito.");
    }
  };

  const totalPrice = cart.reduce(
    (acc, item) => acc + (item.product?.price || 0) * item.quantity,
    0
  );

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen bg-background">
        <Spinner />
      </div>
    );
  }

  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      <Header />
      <main className="flex flex-col md:flex-row flex-1 p-8 gap-8">
        <div className="flex-1 flex flex-col gap-4">
          <h1 className="text-3xl font-bold">
            🛒 Carrito de {user ?? "Invitado"}
          </h1>
          {cart.length === 0 ? (
            <p className="text-gray-500 text-center">¡Tu carrito está vacío!</p>
          ) : (
            cart.map((item) => (
              <Card
                key={item.product_id}
                className="flex flex-col md:flex-row gap-4 p-4 shadow-md"
              >
                <img
                  src={item.product?.image_url}
                  alt={item.product?.name}
                  className="w-full md:w-40 h-40 object-cover rounded"
                />
                <div className="flex-1 flex flex-col justify-between">
                  <div>
                    <div className="flex justify-between items-center">
                      <h2 className="font-bold text-lg">{item.product?.name}</h2>
                      <p className="font-semibold text-camel">
                        ${item.product?.price}
                      </p>
                    </div>
                    <p className="text-sm text-muted-foreground">
                      {item.product?.description}
                    </p>
                  </div>
                  <div className="flex justify-between items-center mt-2">
                    <div className="flex items-center gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          updateQuantity(item.product_id, item.quantity - 1)
                        }
                        disabled={item.quantity <= 1}
                      >
                        -
                      </Button>
                      <span>{item.quantity}</span>
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() =>
                          updateQuantity(item.product_id, item.quantity + 1)
                        }
                      >
                        +
                      </Button>
                    </div>
                    <Button
                      variant="ghost"
                      className="text-red-500 hover:text-red-700"
                      onClick={() => removeFromCart(item.product_id)}
                    >
                      🗑️
                    </Button>
                  </div>
                </div>
              </Card>
            ))
          )}
        </div>

        <div className="md:w-72 w-full sticky top-4 self-start">
          <Card className="p-4 shadow-lg">
            <h2 className="text-xl font-bold mb-2">Resumen</h2>
            <p className="text-sm">Total ({cart.length} productos)</p>
            <p className="text-lg font-semibold mb-2">
              ${totalPrice.toFixed(2)}
            </p>
            <div className="flex flex-col gap-1 mb-4">
              {cart.map((item) => (
                <a
                  key={item.product_id}
                  href={item.product?.purchase_link}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="text-blue-500 underline text-sm truncate"
                >
                  {item.product?.name}
                </a>
              ))}
            </div>
            <Button
              className="bg-camel text-black border-2 border-black hover:bg-white hover:[color:var(--camel)] font-bold py-2 px-6 rounded transition-colors w-full"
              onClick={() =>
                alert("¡Comprar todo aún no está implementado!")
              }
            >
              Comprar todo
            </Button>
            <Button
              variant="ghost"
              className="mt-2 text-red-500 hover:text-red-700 w-full"
              onClick={clearCart}
            >
              Vaciar Carrito
            </Button>
          </Card>
        </div>
      </main>
      <Footer />
    </div>
  );
}

export default function CartPageWrapper() {
  return (
    <ProtectedPage>
      <CartPageContent />
    </ProtectedPage>
  );
}
