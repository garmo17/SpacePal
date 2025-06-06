"use client";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import axios from "@/lib/axios";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "react-hot-toast";
import Image from "next/image";

const loginSchema = z.object({
  username: z.string().min(3, { message: "El nombre de usuario es requerido" }),
  password: z.string().min(6, { message: "La contraseña debe tener al menos 6 caracteres" }),
});

export default function LoginPage() {
  const { login } = useAuth();
  const router = useRouter();
  const form = useForm<z.infer<typeof loginSchema>>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      username: "",
      password: "",
    },
  });

  const onSubmit = async (values: z.infer<typeof loginSchema>) => {
    try {
      const formData = new URLSearchParams();
      formData.append("username", values.username);
      formData.append("password", values.password);

      // Solicitud para obtener el token
      const response = await axios.post("/auth/token", formData, {
        headers: {
          "Content-Type": "application/x-www-form-urlencoded",
        },
      });

      const accessToken = response.data.access_token;

      // Obtener datos del usuario autenticado
      const meResponse = await axios.get("/users/me", {
        headers: {
          Authorization: `Bearer ${accessToken}`,
        },
      });

      const { username, id } = meResponse.data;

      login(accessToken, username, id);

      toast.success("¡Inicio de sesión exitoso!");
      form.reset();

      setTimeout(() => {
        router.push("/");
      }, 1000);
    } catch (err) {
      console.error(err);
      toast.error("Usuario o contraseña incorrectos");
    }
  };

  return (
    <div className="flex flex-col min-h-screen">
      <Header>
        <Button asChild className="bg-camel text-black border border-white hover:bg-white hover:[color:var(--camel)] transition-colors">
          <Link href="/register">Registrarse</Link>
        </Button>
      </Header>

      <main className="flex flex-1 flex-col items-center justify-center p-8 gap-6">
        <Image src="/Logo2.png" alt="Logo SpacePal" className="h-24" width={100} height={200}/>

        <Card className="w-full max-w-md shadow-lg">
          <CardHeader>
            <CardTitle className="text-center text-2xl font-bold">Iniciar Sesión en SpacePal</CardTitle>
          </CardHeader>

          <CardContent className="flex flex-col gap-6">
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="flex flex-col gap-6 w-full">
                <FormField
                  control={form.control}
                  name="username"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Nombre de usuario</FormLabel>
                      <FormControl>
                        <Input
                          placeholder="Introduce tu nombre de usuario"
                          {...field}
                          className="focus-visible:ring-camel"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Contraseña</FormLabel>
                      <FormControl>
                        <Input
                          type="password"
                          placeholder="Introduce tu contraseña"
                          {...field}
                          className="focus-visible:ring-camel"
                        />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button
                  type="submit"
                  className="bg-camel text-black border-2 border-black hover:bg-white hover:[color:var(--camel)] font-bold py-2 px-6 rounded transition-colors"
                >
                  Iniciar sesión
                </Button>
              </form>
            </Form>
          </CardContent>
        </Card>
      </main>

      <Footer />
    </div>
  );
}
