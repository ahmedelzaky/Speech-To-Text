import { useState } from "react";
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import AudioInput from "@/components/AudioInput";
import TranscriptionResult from "@/components/TranscriptionResult";
import Features from "@/components/Features";
import HowItWorks from "@/components/HowItWorks";
import Footer from "@/components/Footer";
import axios from "axios";
import { set } from "date-fns";

const Index = () => {
  const [transcribedText, setTranscribedText] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  // Simulated processing function - in a real app this would call an API
  const processAudio = async (audio: File) => {
    setIsProcessing(true);
    try {
      const formData = new FormData();
      formData.append("file", audio, audio.name);
      const response = await axios.post(
        "http://localhost:8000/transcribe",
        formData,
        {
          headers: {
            Accept: "application/json",
          },
        }
      );
      console.log("Transcription response:", response.data);
      setTranscribedText(response.data.transcription);
    } catch (error) {
      console.error("Error during transcription:", error);
      setTranscribedText("Error during transcription");
    }
    setIsProcessing(false);
  };

  const processAudioUrl = async (url: string) => {
    setIsProcessing(true);

    try {
      const response = await axios.post(
        "http://localhost:8000/transcribe-youtube",
        {
          url: url,
        },
        {
          headers: {
            Accept: "application/json",
          },
        }
      );
      console.log("Transcription response:", response.data);
      setTranscribedText(response.data.transcription);
    } catch (error) {
      console.error("Error during transcription:", error);

      setTranscribedText(
        error.response
          ? error.response.data.detail
          : "Error during transcription"
      );
    }

    setIsProcessing(false);
  };

  const handleFileSelect = (file: File) => {
    console.log("File selected:", file.name);
    processAudio(file);
  };

  const handleUrlSubmit = (url: string) => {
    console.log("URL submitted:", url);
    processAudioUrl(url);
  };

  const handleRecordingComplete = (blob: Blob) => {
    const audio = new File(
      [blob],
      `${new Date().getTime()}.${blob.type.split("/")[1]}`,
      {
        type: blob.type,
      }
    );
    processAudio(audio);
  };

  return (
    <div className="min-h-screen flex flex-col">
      <Header />

      <main className="flex-1">
        <Hero />

        <section className="container mx-auto py-16 px-4">
          <AudioInput
            onFileSelect={handleFileSelect}
            onUrlSubmit={handleUrlSubmit}
            onRecordingComplete={handleRecordingComplete}
          />

          <TranscriptionResult
            text={transcribedText}
            isLoading={isProcessing}
          />
        </section>

        <Features />
        <HowItWorks />
      </main>

      <Footer />
    </div>
  );
};

export default Index;
