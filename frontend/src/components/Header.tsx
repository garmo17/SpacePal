"use client";
import { Home, Info, Phone, ShoppingCart } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import { useAuth } from "@/contexts/AuthContext";
import Spinner from "@/components/Spinner";

export default function Header({ children }: { children?: React.ReactNode }) {
  const { isAuthenticated, isAdmin, logout, loading } = useAuth();

  if (loading) {
    return (
      <header className="flex justify-between items-center p-4 bg-neutral-800 text-white">
        <div className="flex items-center gap-4">
          <img src="/logo.png" alt="Logo" className="h-8" />
          <div className="flex gap-2 items-center">
            <Spinner />
          </div>
        </div>
        <div className="flex gap-4">
          <Spinner />
        </div>
      </header>
    );
  }

  return (
    <header className="flex justify-between items-center p-4 bg-neutral-800 text-white">
      <div className="flex items-center gap-4">
        <img src="/logo.png" alt="Logo" className="h-8" />
        <div className="flex gap-2 items-center">
          <Button asChild variant="ghost" className="p-0 flex items-center justify-center group">
            <Link href="/">
              <Home className="!h-7 !w-7 text-white group-hover:text-black transition-colors" />
            </Link>
          </Button>
          <Button variant="ghost" className="p-0 flex items-center justify-center group">
            <Info className="!h-7 !w-7 text-white group-hover:text-black transition-colors" />
          </Button>
          <Button variant="ghost" className="p-0 flex items-center justify-center group">
            <Phone className="!h-7 !w-7 text-white group-hover:text-black transition-colors" />
          </Button>
        </div>
      </div>
      <div className="flex gap-4">
        {isAuthenticated ? (
          <>
            {/* Botón para el admin solo si es admin */}
            {isAdmin && (
              <Button asChild variant="outline" className="bg-camel text-black border border-white hover:bg-white hover:[color:var(--camel)!important]">
                <Link href="/admin">Admin</Link>
              </Button>
            )}
            <Button asChild variant="ghost" className="p-0 flex items-center justify-center group">
              <Link href="/profile/cart">
                <ShoppingCart className="!h-7 !w-7 text-white group-hover:text-black transition-colors" />
              </Link>
            </Button>
            <Button asChild variant="outline" className="bg-camel text-black border border-white hover:bg-white hover:[color:var(--camel)!important]">
              <Link href="/profile">Mi perfil</Link>
            </Button>
            <Button
              onClick={logout}
              className="bg-red-500 hover:bg-red-700 text-white border border-red-700 font-bold py-2 px-4 rounded transition-colors"
            >
              Cerrar sesión
            </Button>
          </>
        ) : (
          children
        )}
      </div>
    </header>
  );
}
