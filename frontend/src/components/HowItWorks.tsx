
import { ArrowRight } from "lucide-react";

const steps = [
  {
    number: "01",
    title: "Upload, Record, or Paste URL",
    description: "Choose how you want to provide your audio - upload a file, record directly, or paste a URL."
  },
  {
    number: "02",
    title: "Process Your Audio",
    description: "Our AI engine analyzes your audio and converts speech patterns into accurate text."
  },
  {
    number: "03",
    title: "Get Your Transcription",
    description: "Review your transcribed text, copy it, and use it for your projects or documents."
  }
];

const HowItWorks = () => {
  return (
    <section id="how-it-works" className="container mx-auto py-20 px-4 relative">
      <div className="absolute inset-0 gradient-bg opacity-5 rounded-3xl -z-10" />
      
      <div className="text-center mb-16">
        <h2 className="text-3xl font-bold mb-4">How It Works</h2>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Converting speech to text has never been easier. Follow these simple steps to get started.
        </p>
      </div>
      
      <div className="max-w-4xl mx-auto">
        {steps.map((step, index) => (
          <div key={index} className="relative mb-12 last:mb-0">
            {index < steps.length - 1 && (
              <div className="absolute left-10 top-20 h-20 w-px bg-border hidden sm:block" />
            )}
            
            <div className="flex flex-col sm:flex-row items-start sm:items-center gap-6">
              <div className="h-20 w-20 rounded-full gradient-bg flex items-center justify-center text-white text-2xl font-bold shrink-0">
                {step.number}
              </div>
              
              <div className="flex-1">
                <h3 className="text-xl font-medium mb-2">{step.title}</h3>
                <p className="text-muted-foreground">{step.description}</p>
              </div>
              
              {index < steps.length - 1 && (
                <ArrowRight className="h-6 w-6 text-muted-foreground hidden sm:block" />
              )}
            </div>
          </div>
        ))}
      </div>
    </section>
  );
};

export default HowItWorks;
