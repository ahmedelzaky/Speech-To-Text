import { ArrowRight } from "lucide-react";

const Hero = () => {
  return (
    <section className="container mx-auto py-12 px-4 flex flex-col items-center text-center">
      <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold max-w-3xl mb-6">
        Convert Speech to Text in{" "}
        <span className="bg-gradient-to-r from-blue via-purple to-teal bg-clip-text text-transparent">
          Seconds
        </span>
      </h1>
      <p className="text-lg text-muted-foreground max-w-2xl mb-8">
        Easily transcribe audio files, record your voice, or enter a URL. Our
        advanced AI ensures accurate and fast transcriptions for all your needs.
      </p>
      <div className="flex flex-col sm:flex-row gap-4">
        <button
          className="btn-primary flex items-center gap-2 text-lg"
          onClick={() => (window.location.href = "#get-started")}
        >
          Try Now <ArrowRight className="h-5 w-5" />
        </button>
        <a href="#how-it-works" className="btn-secondary">
          Learn More
        </a>
      </div>
    </section>
  );
};

export default Hero;
