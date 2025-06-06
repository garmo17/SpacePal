// src/app/page.tsx
import { Button } from "@/components/ui/button";
import Header from "@/components/Header";
import Link from "next/link";
import Footer from "@/components/Footer";
import Image from "next/image";

export default function Page() {
  return (
    <div className="flex flex-col min-h-screen bg-background text-foreground">
      {/* Barra superior con íconos y botones */}
      <Header>
        <div className="flex gap-2">
          <Link href="/login">
            <Button
              variant="outline"
              className="bg-camel text-black border border-white hover:bg-white hover:[color:var(--camel)!important]"
            >
              Iniciar sesión
            </Button>
          </Link>
          <Link href="/register">
            <Button
              variant="outline"
              className="bg-camel text-black border border-white hover:bg-white hover:[color:var(--camel)!important]"
            >
              Registrarse
            </Button>
          </Link>
        </div>
      </Header>

      <main className="flex flex-col md:flex-row flex-1 px-12 py-16 gap-16 items-center">
        <div className="flex-1 flex justify-center">
          <Image
            src="/imagen_pantalla_principal.png"
            alt="Decoración"
            className="max-w-lg w-full rounded-xl shadow-xl"
            width={300} height={160}
          />
        </div>

        <div className="flex-1 flex flex-col justify-center space-y-8 max-w-2xl pr-4">
          <h1 className="text-5xl font-bold leading-tight">
            Encuentra el estilo perfecto para tu espacio
          </h1>
          <p className="text-xl leading-relaxed">
            Te ayudamos a encontrar los mejores productos de decoración según tu estilo, espacio y necesidades.
          </p>
          <Link href="/selection">
            <Button className="self-start bg-camel hover:bg-white text-black text-lg font-bold py-3 px-8 rounded-xl border-2 border-black transition-colors hover:[color:var(--camel)] shadow-md">
              Comenzar
            </Button>
          </Link>
        </div>
      </main>

      <Footer />
    </div>
  );
}
