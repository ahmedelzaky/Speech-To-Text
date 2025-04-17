import { useState } from "react";
import Header from "@/components/Header";
import Hero from "@/components/Hero";
import AudioInput from "@/components/AudioInput";
import TranscriptionResult from "@/components/TranscriptionResult";
import Features from "@/components/Features";
import HowItWorks from "@/components/HowItWorks";
import Footer from "@/components/Footer";

const Index = () => {
  const [transcribedText, setTranscribedText] = useState("");
  const [isProcessing, setIsProcessing] = useState(false);

  const processAudio = async (audio: File) => {
    setTranscribedText("");
    const ws = new WebSocket("ws://localhost:8000/ws/transcribe");
    ws.binaryType = "arraybuffer";

    ws.onopen = () => {
      console.log("WebSocket connection established");

      // Step 1: send filename
      ws.send(JSON.stringify({ filename: audio.name }));

      // Step 2: send audio data
      audio.arrayBuffer().then((buffer) => {
        ws.send(buffer);
      });
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("WebSocket message:", data);

      if (data.text) {
        setIsProcessing(false);
        setTranscribedText((prev) => prev + " " + data.text);
      }
      if (data.status) {
        console.log(`Status: ${data.status}`);
        if (data.status === "complete") {
          ws.close(); // Only close here after processing is done
        }
      }
      if (data.error) {
        setIsProcessing(false);
        setTranscribedText("Error: " + data.error);
        ws.close(); // Also close on error
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setTranscribedText("WebSocket error");
    };

  };

  const processYoutubeUrl = async (url: string) => {
    setTranscribedText("");

    const ws = new WebSocket("ws://localhost:8000/ws/transcribe-youtube");

    ws.onopen = () => {
      ws.send(JSON.stringify({ url }));
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log("WebSocket message:", data);

      if (data.text) {
        setIsProcessing(false);
        setTranscribedText((prev) => prev + " " + data.text);
      }
      if (data.progress) {
        console.log(`Download progress: ${data.progress}`);
      }
      if (data.status) {
        console.log(`Status: ${data.status}`);
        if (data.status === "complete") {
          ws.close(); // Only close here after processing is done
        }
      }
      if (data.error) {
        setIsProcessing(false);
        setTranscribedText("Error: " + data.error);
        ws.close(); // Also close on error
      }
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
      setTranscribedText("WebSocket error");
      setIsProcessing(false);
    };

    ws.onclose = () => {
      setIsProcessing(false);
    };
  };

  const handleFileSelect = (file: File) => {
    console.log("File selected:", file.name);
    setIsProcessing(true);
    processAudio(file);
  };

  const handleUrlSubmit = (url: string) => {
    console.log("URL submitted:", url);
    setIsProcessing(true);
    processYoutubeUrl(url);
  };

  const handleRecordingComplete = (blob: Blob) => {
    const audio = new File(
      [blob],
      `${new Date().getTime()}.${blob.type.split("/")[1]}`,
      {
        type: blob.type,
      }
    );
    setIsProcessing(true);
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
