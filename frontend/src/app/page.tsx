// src/app/page.tsx
import { Button } from "@/components/ui/button";
import Header from "@/components/Header";
import Link from "next/link";
import Footer from "@/components/Footer";

export default function Page() {
  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      {/* Barra superior con íconos y botones */}
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

      {/* Contenido principal */}
      <main className="flex flex-col md:flex-row flex-1 p-8 gap-12 items-center">
        {/* Imagen */}
        <div className="flex-1 flex justify-center">
          <img
            src="/imagen_pantalla_principal.png"
            alt="Decoración"
            className="max-w-md w-full rounded shadow-lg"
          />
        </div>

        {/* Texto */}
        <div className="flex-1 flex flex-col justify-center space-y-6 max-w-xl">
          <h1 className="text-4xl font-bold leading-tight">
            Encuentra el estilo perfecto para tu espacio
          </h1>
          <p className="text-lg leading-relaxed">
            Te ayudamos a encontrar los mejores productos de decoración según tu estilo, espacio y necesidades.
          </p>
          <Link href="/selection">
            <Button className="just self-start bg-camel hover:bg-white text-black font-bold py-2 px-6 rounded border-2 border-black transition-colors hover:[color:var(--camel)]">
              Comenzar
            </Button>
          </Link>
        </div>
      </main>

      <Footer/>
    </div>
  );
}
