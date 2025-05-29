import { Home, Info, Phone } from "lucide-react";
import { Button } from "@/components/ui/button";
import Link from "next/link";

export default function Header({children}: {children: React.ReactNode}) {
    return (
            <header className="flex justify-between items-center p-4 bg-neutral-800 text-white">
                <div className="flex items-center gap-4">
                    <img src="/logo.png" alt="Logo" className="h-8" />
                    <div className="flex gap-2 items-center">
                        <Button asChild variant="ghost" className="p-0 flex items-center justify-center group">
                            <Link href="/">
                                <Home className="!h-7 !w-7 text-white group-hover:text-black transition-colors" />
                            </Link>
                        </Button>
                        <Button variant="ghost" className="p-0 flex items-center justify-center group">
                            <Info className="!h-7 !w-7 text-white group-hover:text-black transition-colors" />
                        </Button>
                        <Button variant="ghost" className="p-0 flex items-center justify-center group">
                            <Phone className="!h-7 !w-7 text-white group-hover:text-black transition-colors" />
                        </Button>
                    </div>
                </div>

                {children}
            </header>
    );
}