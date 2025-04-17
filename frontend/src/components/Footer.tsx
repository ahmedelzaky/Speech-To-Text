
import { Headphones, Github, Twitter, Linkedin } from "lucide-react";

const Footer = () => {
  return (
    <footer className="bg-muted/30 py-12">
      <div className="container mx-auto px-4">
        <div className="flex flex-col md:flex-row justify-between items-center mb-8">
          <div className="flex items-center gap-2 mb-4 md:mb-0">
            <Headphones className="h-6 w-6 text-blue" />
            <h2 className="text-xl font-bold">SpeakText</h2>
          </div>
          
          <div className="flex items-center gap-4">
            <a 
              href="#" 
              className="h-10 w-10 rounded-full bg-background flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors"
            >
              <Github className="h-5 w-5" />
            </a>
            <a 
              href="#" 
              className="h-10 w-10 rounded-full bg-background flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors"
            >
              <Twitter className="h-5 w-5" />
            </a>
            <a 
              href="#" 
              className="h-10 w-10 rounded-full bg-background flex items-center justify-center text-muted-foreground hover:text-foreground transition-colors"
            >
              <Linkedin className="h-5 w-5" />
            </a>
          </div>
        </div>
        
        <div className="border-t border-border pt-8">
          <div className="flex flex-col md:flex-row justify-between items-center gap-4">
            <p className="text-muted-foreground text-sm">
              © {new Date().getFullYear()} SpeakText. All rights reserved.
            </p>
            
            <div className="flex flex-wrap justify-center gap-4 md:gap-8">
              <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Privacy Policy
              </a>
              <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Terms of Service
              </a>
              <a href="#" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
                Contact Us
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
