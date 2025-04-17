import { Headphones } from "lucide-react";

const Header = () => {
  return (
    <header className="container mx-auto py-6 px-4">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Headphones className="h-8 w-8 text-blue" />
          <h1 className="text-2xl font-bold bg-gradient-to-r from-blue via-purple to-teal bg-clip-text text-transparent">
            SpeakText
          </h1>
        </div>
        <nav>
          <ul className="flex items-center gap-6">
            <li>
              <a
                href="#features"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                Features
              </a>
            </li>
            <li>
              <a
                href="#how-it-works"
                className="text-muted-foreground hover:text-foreground transition-colors"
              >
                How It Works
              </a>
            </li>
            <li>
              <button
                className="btn-primary"
                onClick={() => (window.location.href = "#get-started")}
              >
                Get Started
              </button>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
};

export default Header;
