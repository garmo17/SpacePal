"use client";

import { useAuth } from "@/contexts/AuthContext";
import { useForm } from "react-hook-form";
import { z } from "zod";
import { zodResolver } from "@hookform/resolvers/zod";
import axios from "@/lib/axios";
import { useEffect, useState } from "react";
import ProtectedPage from "@/components/ProtectedPage";
import Spinner from "@/components/Spinner";
import Header from "@/components/Header";
import { Card, CardHeader, CardTitle, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form";
import Footer from "@/components/Footer";
import { toast } from "react-hot-toast";

// Esquema para el nombre de usuario
const profileSchema = z.object({
  username: z.string().min(3, { message: "El nombre de usuario es requerido" }),
});

// Esquema para cambiar la contraseña
const passwordSchema = z.object({
  newPassword: z.string().min(6, { message: "La nueva contraseña debe tener al menos 6 caracteres" }),
});

export default function ProfilePage() {
  const { userId, isAuthenticated, loading, login } = useAuth();
  const [email, setEmail] = useState("");

  const form = useForm<z.infer<typeof profileSchema>>({
    resolver: zodResolver(profileSchema),
    defaultValues: { username: "" },
  });

  const passwordForm = useForm<z.infer<typeof passwordSchema>>({
    resolver: zodResolver(passwordSchema),
    defaultValues: { newPassword: "" },
  });

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const { data } = await axios.get("/users/me", {
          headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
        });
        form.reset({ username: data.username });
        setEmail(data.email);
      } catch (err) {
        console.error("Error al obtener el usuario:", err);
      }
    };

    if (!loading && isAuthenticated) fetchUserData();
  }, [loading, isAuthenticated, form]);

  // Handler para actualizar nombre de usuario
  const onSubmitProfile = async (values: z.infer<typeof profileSchema>) => {
    try {
      await axios.put(`/users/${userId}`, values, {
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
      });

      // Obtener datos actualizados
      const { data: userData } = await axios.get("/users/me", {
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
      });

      login(localStorage.getItem("access_token")!, userData.username, userData.id);

      toast.success("¡Perfil actualizado correctamente!");
    } catch (err) {
      console.error("Error al actualizar perfil:", err);
      toast.error("Error al actualizar el perfil.");
    }
  };

  // Handler para cambiar la contraseña
  const onSubmitPassword = async (values: z.infer<typeof passwordSchema>) => {
    try {
      await axios.put(`/users/${userId}`, {
        password: values.newPassword,
      }, {
        headers: { Authorization: `Bearer ${localStorage.getItem("access_token")}` },
      });

      toast.success("¡Contraseña cambiada correctamente!");
      passwordForm.reset();
    } catch (err) {
      console.error("Error al cambiar contraseña:", err);
      toast.error("Error al cambiar la contraseña.");
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen bg-background">
        <Spinner />
      </div>
    );
  }

  return (
    <ProtectedPage>
      <div className="flex flex-col min-h-screen bg-background text-foreground">
        <Header />
        <main className="flex flex-col items-center justify-center p-8 gap-6">
          <Card className="w-full max-w-md shadow-lg">
            <CardHeader>
              <CardTitle className="text-center text-2xl font-bold">Mi Perfil</CardTitle>
            </CardHeader>
            <CardContent className="flex flex-col gap-6">

              {/* Mostrar el email */}
              <div>
                <p className="text-sm text-muted-foreground">Correo electrónico:</p>
                <p className="font-semibold">{email}</p>
              </div>

              {/* Formulario para actualizar nombre de usuario */}
              <Form {...form}>
                <form onSubmit={form.handleSubmit(onSubmitProfile)} className="flex flex-col gap-4">
                  <FormField
                    control={form.control}
                    name="username"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Nombre de usuario</FormLabel>
                        <FormControl>
                          <Input
                            type="text"
                            placeholder="Introduce tu nombre de usuario"
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
                    Actualizar nombre de usuario
                  </Button>
                </form>
              </Form>

              {/* Formulario para cambiar la contraseña */}
              <Form {...passwordForm}>
                <form onSubmit={passwordForm.handleSubmit(onSubmitPassword)} className="flex flex-col gap-4">
                  <FormField
                    control={passwordForm.control}
                    name="newPassword"
                    render={({ field }) => (
                      <FormItem>
                        <FormLabel>Nueva contraseña</FormLabel>
                        <FormControl>
                          <Input
                            type="password"
                            placeholder="Introduce la nueva contraseña"
                            {...field}
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
                    Cambiar contraseña
                  </Button>
                </form>
              </Form>
            </CardContent>
          </Card>
        </main>
        <Footer />
      </div>
    </ProtectedPage>
  );
}
