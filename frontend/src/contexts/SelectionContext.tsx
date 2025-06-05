"use client";
import React, {
  createContext,
  useState,
  useContext,
  useEffect,
  PropsWithChildren,
} from "react";

// Tipo del contexto
type SelectionContextType = {
  espacioElegido: string;
  estiloElegido: string;
  setEspacioElegido: (espacio: string) => void;
  setEstiloElegido: (estilo: string) => void;
};

// Contexto real tipado
const SelectionContext = createContext<SelectionContextType | null>(null);

// Hook personalizado
export const useSelection = () => {
  const context = useContext(SelectionContext);
  if (!context) throw new Error("useSelection debe usarse dentro de <SelectionProvider>");
  return context;
};

export const SelectionProvider = ({ children }: PropsWithChildren) => {
  const [espacioElegido, setEspacioElegido] = useState('');
  const [estiloElegido, setEstiloElegido] = useState('');

  useEffect(() => {
    const espacioGuardado = localStorage.getItem('espacioElegido');
    const estiloGuardado = localStorage.getItem('estiloElegido');
    if (espacioGuardado) setEspacioElegido(espacioGuardado);
    if (estiloGuardado) setEstiloElegido(estiloGuardado);
  }, []);

  useEffect(() => {
    localStorage.setItem('espacioElegido', espacioElegido);
  }, [espacioElegido]);

  useEffect(() => {
    localStorage.setItem('estiloElegido', estiloElegido);
  }, [estiloElegido]);

  return (
    <SelectionContext.Provider
      value={{ espacioElegido, estiloElegido, setEspacioElegido, setEstiloElegido }}
    >
      {children}
    </SelectionContext.Provider>
  );
};
