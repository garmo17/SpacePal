"use client";

import { zodResolver } from "@hookform/resolvers/zod";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import Link from "next/link";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import axios from "@/lib/axios";
import { useRouter } from "next/navigation";
import { useAuth } from "@/contexts/AuthContext";
import { toast } from "react-hot-toast";
import Image from "next/image";

// 1️⃣ Esquema de validación con zod
const formSchema = z.object({
  username: z.string().min(2, { message: "El nombre debe tener al menos 2 caracteres" }),
  email: z.string().email({ message: "Correo no válido" }),
  password: z.string().min(6, { message: "La contraseña debe tener al menos 6 caracteres" }),
});

export default function RegisterPage() {
  const { login } = useAuth();
  const router = useRouter();

  // 2️⃣ Configura react-hook-form con zod
  const form = useForm<z.infer<typeof formSchema>>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      username: "",
      email: "",
      password: "",
    },
  });

  // 3️⃣ Handler del formulario
  async function onSubmit(values: z.infer<typeof formSchema>) {
    try {
      await axios.post("/users/", values);

      const formData = new URLSearchParams();
      formData.append("username", values.username);
      formData.append("password", values.password);

      const response = await axios.post("/auth/token", formData, {
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
      });

      const meResponse = await axios.get("/users/me", {
        headers: { Authorization: `Bearer ${response.data.access_token}` },
      });

      login(response.data.access_token, values.username, meResponse.data.id);

      toast.success("Usuario creado correctamente. Redirigiendo...");
      form.reset();

      setTimeout(() => {
        router.push("/");
      }, 1000);
    } catch (err) {
      if (err instanceof Error) {
        console.error(err.message);
      } else {
        console.error('Unknown error');
      }
      toast.error("Error al crear el usuario. El nombre de usuario o correo ya están en uso.");
    }
  }

  return (
    <div className="flex flex-col min-h-screen">
      {/* Barra superior */}
      <Header>
        <Button asChild className="bg-camel text-black border border-white hover:bg-white hover:[color:var(--camel)] transition-colors">
          <Link href="/login">Iniciar sesión</Link>
        </Button>
      </Header>

      {/* Contenido principal */}
      <main className="flex flex-1 flex-col items-center justify-center p-8 gap-6">
        <Image src="/Logo2.png" alt="Logo SpacePal" className="h-24" width={100} height={200}/>

        <Card className="w-full max-w-md shadow-lg">
          <CardHeader>
            <CardTitle className="text-center text-2xl font-bold">
              Crea tu cuenta en SpacePal
            </CardTitle>
          </CardHeader>
          <CardContent>
            <Form {...form}>
              <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
                {/* Username */}
                <FormField
                  control={form.control}
                  name="username"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Nombre de usuario</FormLabel>
                      <FormControl>
                        <Input placeholder="Introduce tu nombre" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Email */}
                <FormField
                  control={form.control}
                  name="email"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Correo electrónico</FormLabel>
                      <FormControl>
                        <Input placeholder="Introduce tu correo" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                {/* Password */}
                <FormField
                  control={form.control}
                  name="password"
                  render={({ field }) => (
                    <FormItem>
                      <FormLabel>Contraseña</FormLabel>
                      <FormControl>
                        <Input type="password" placeholder="Crea una contraseña" {...field} />
                      </FormControl>
                      <FormMessage />
                    </FormItem>
                  )}
                />

                <Button
                  type="submit"
                  className="bg-camel text-black border-2 border-black hover:bg-white hover:[color:var(--camel)] font-bold py-2 px-6 rounded transition-colors w-full"
                >
                  Registrarse
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
