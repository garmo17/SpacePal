"use client";

import { useSelection } from "@/contexts/SelectionContext";
import axios from "@/lib/axios";
import { useRouter } from "next/navigation";
import React, { useEffect, useState } from "react";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import Link from "next/link";
import Image from "next/image";

export default function Seleccion() {
  type Espacio = {
    id: string;
    name: string;
    description: string;
    image: string;
  };

  type Estilo = {
    id: string;
    name: string;
    description: string;
    image: string;
  };

  const {
    espacioElegido,
    estiloElegido,
    setEspacioElegido,
    setEstiloElegido,
  } = useSelection();

  const router = useRouter();

  const [espacios, setEspacios] = useState<Espacio[]>([]);
  const [estilos, setEstilos] = useState<Estilo[]>([]);

  useEffect(() => {
    const fetchEspacios = async () => {
      try {
        const response = await axios.get("/spaces?range=[0,20]");
        setEspacios(response.data);
      } catch (error) {
        console.error("Error al obtener los espacios:", error);
      }
    };

    const fetchEstilos = async () => {
      try {
        const response = await axios.get("/styles?range=[0,20]");
        setEstilos(response.data);
      } catch (error) {
        console.error("Error al obtener los estilos:", error);
      }
    };

    fetchEspacios();
    fetchEstilos();
  }, []);

  const handleContinuar = () => {
    if (espacioElegido && estiloElegido) {
      router.push("/catalogue");
    }
  };

  const espacioSeleccionado = espacios.find((e) => e.id === espacioElegido);
  const estiloSeleccionado = estilos.find((e) => e.id === estiloElegido);

  return (
    <div className="flex flex-col min-h-screen">
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

      <main className="flex-1 flex flex-col items-center px-6 py-6">
        <h1 className="text-3xl font-bold mb-6">Selecciona tu espacio y estilo</h1>

        <div className="flex w-full max-w-6xl h-[700px] gap-8">
          <div className="flex-1 flex flex-col border-r overflow-y-auto pr-4">
            <h2 className="text-center text-xl font-semibold mb-4">Espacios</h2>
            <div className="grid grid-cols-1 gap-4">
              {espacios.map((espacio) => (
                <div
                  key={espacio.id}
                  onClick={() => setEspacioElegido(espacio.id)}
                  className={`rounded-xl overflow-hidden shadow-md border-2 transition-all cursor-pointer hover:scale-[1.01] ${
                    espacioElegido === espacio.id
                      ? "border-[#c19073] bg-[#fdf7f4]"
                      : "border-gray-200 bg-white"
                  }`}
                >
                  <Image
                    src={espacio.image}
                    alt={espacio.name}
                    className="w-full h-40 object-cover"
                    width={300} height={160}
                  />
                  <div className="p-2 text-center">
                    <h3 className="text-base font-bold">{espacio.name}</h3>
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div className="flex-1 flex flex-col overflow-y-auto pl-4">
            <h2 className="text-center text-xl font-semibold mb-4">Estilos</h2>
            <div className="grid grid-cols-1 gap-4">
              {estilos.map((estilo) => (
                <div
                  key={estilo.id}
                  onClick={() => setEstiloElegido(estilo.id)}
                  className={`rounded-xl overflow-hidden shadow-md border-2 transition-all cursor-pointer hover:scale-[1.01] ${
                    estiloElegido === estilo.id
                      ? "border-[#c19073] bg-[#fdf7f4]"
                      : "border-gray-200 bg-white"
                  }`}
                >
                  <Image
                    src={estilo.image}
                    alt={estilo.name}
                    className="w-full h-40 object-cover"
                    width={300} height={160}
                  />
                  <div className="p-2 text-center">
                    <h3 className="text-base font-bold">{estilo.name}</h3>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        <p className="text-sm text-gray-600 mt-6">
          Espacio: <span className="font-mono">{espacioSeleccionado?.name || "ninguno"}</span> | 
          Estilo: <span className="font-mono">{estiloSeleccionado?.name || "ninguno"}</span>
        </p>

        <Button
          onClick={handleContinuar}
          disabled={!espacioElegido || !estiloElegido}
          className={`mt-3 bg-camel hover:bg-white text-black font-bold py-3 px-8 text-lg rounded-xl border-2 border-black transition-colors hover:[color:var(--camel)] ${
            !espacioElegido || !estiloElegido ? "opacity-50 cursor-not-allowed" : ""
          }`}
        >
          Ver catálogo
        </Button>
      </main>

      <Footer />
    </div>
  );
}
