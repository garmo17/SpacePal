export default function Footer() {
    return (
        <footer className="w-full bg-camel py-4 mt-auto">
            <div className="container mx-auto flex justify-center items-center">
                <p className="text-black text-sm text-center">
                    © {new Date().getFullYear()} SpacePal. Todos los derechos reservados.
                </p>
            </div>
        </footer>
    );
}
