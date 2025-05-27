// src/app/register/page.tsx
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";

export default function RegisterPage() {
  return (
    <div className="flex flex-col min-h-screen">
      {/* Barra superior */}
      <Header>
          <Button asChild className="bg-camel text-black border border-white hover:bg-white hover:[color:var(--camel)] transition-colors">
            <Link href="/login">
                Iniciar sesión
            </Link>
          </Button>
      </Header>

      {/* Contenido principal */}
      <main className="flex flex-1 flex-col items-center justify-center p-8 gap-6">
        <img src="/Logo2.png" alt="Logo SpacePal" className="h-24" />

        <Card className="w-full max-w-md shadow-lg">
          <CardHeader>
            <CardTitle className="text-center text-2xl font-bold">
              Crea tu cuenta en SpacePal
            </CardTitle>
          </CardHeader>
          <CardContent className="flex flex-col gap-6">
            <form className="flex flex-col gap-6 w-full">
              <div className="flex flex-col gap-2">
                <Label htmlFor="username" className="font-semibold">
                  Nombre de usuario
                </Label>
                <Input
                  id="username"
                  type="text"
                  placeholder="Introduce tu nombre"
                  className="focus-visible:ring-camel"
                />
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="email" className="font-semibold">
                  Correo electrónico
                </Label>
                <Input
                  id="email"
                  type="email"
                  placeholder="Introduce tu correo"
                  className="focus-visible:ring-camel"
                />
              </div>

              <div className="flex flex-col gap-2">
                <Label htmlFor="password" className="font-semibold">
                  Contraseña
                </Label>
                <Input
                  id="password"
                  type="password"
                  placeholder="Crea una contraseña"
                  className="focus-visible:ring-camel"
                />
              </div>

              <Button
                type="submit"
                className="bg-camel text-black border-2 border-black hover:bg-white hover:[color:var(--camel)] font-bold py-2 px-6 rounded transition-colors"
              >
                Registrarse
              </Button>
            </form>
          </CardContent>
        </Card>
      </main>

      <Footer/>
    </div>
  );
}
