
import { FileAudio, Mic, Link2, Zap, FileText, Repeat } from "lucide-react";
import { Card } from "@/components/ui/card";

const features = [
  {
    icon: FileAudio,
    title: "Upload Audio Files",
    description: "Drag & drop or select audio files from your device for instant transcription."
  },
  {
    icon: Mic,
    title: "Record Audio",
    description: "Record speech directly in your browser and convert it to text immediately."
  },
  {
    icon: Link2,
    title: "Transcribe from URL",
    description: "Enter a URL to an audio file online and transcribe it without downloading."
  },
  {
    icon: Zap,
    title: "Fast Processing",
    description: "Advanced AI technology converts your speech to text with exceptional speed."
  },
  {
    icon: FileText,
    title: "Accurate Results",
    description: "High-quality transcriptions with support for multiple languages and accents."
  },
  {
    icon: Repeat,
    title: "Easy Editing",
    description: "Copy and edit your transcribed text as needed for your projects."
  }
];

const Features = () => {
  return (
    <section id="features" className="container mx-auto py-20 px-4">
      <div className="text-center mb-12">
        <h2 className="text-3xl font-bold mb-4">Powerful Features</h2>
        <p className="text-muted-foreground max-w-2xl mx-auto">
          Our speech-to-text converter offers a wide range of features to make transcription simple and efficient.
        </p>
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((feature, index) => (
          <Card 
            key={index} 
            className="p-6 card-hover flex flex-col items-center text-center"
          >
            <div className="h-12 w-12 rounded-full bg-primary/10 flex items-center justify-center mb-4">
              <feature.icon className="h-6 w-6 text-blue" />
            </div>
            <h3 className="text-xl font-medium mb-2">{feature.title}</h3>
            <p className="text-muted-foreground">{feature.description}</p>
          </Card>
        ))}
      </div>
    </section>
  );
};

export default Features;
