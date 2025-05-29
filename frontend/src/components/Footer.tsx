

export default function Footer() {
    return (
        <footer className="bg-camel h-8 flex items-center justify-center">
            <p className="text-black text-sm">
                © {new Date().getFullYear()} SpacePal. Todos los derechos reservados.
            </p>
        </footer>
    );
}