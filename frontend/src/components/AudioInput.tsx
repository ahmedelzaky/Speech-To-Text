
import { useState, useRef, useCallback, DragEvent } from "react";
import { Upload, Link, Mic, Loader2, FileAudio, X } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface AudioInputProps {
  onFileSelect: (file: File) => void;
  onUrlSubmit: (url: string) => void;
  onRecordingComplete: (blob: Blob) => void;
}

const AudioInput = ({ onFileSelect, onUrlSubmit, onRecordingComplete }: AudioInputProps) => {
  const [isDragging, setIsDragging] = useState(false);
  const [url, setUrl] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const [recordingTime, setRecordingTime] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  
  const fileInputRef = useRef<HTMLInputElement>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunksRef = useRef<BlobPart[]>([]);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  
  // Handle file drop
  const handleDragOver = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(true);
  }, []);
  
  const handleDragLeave = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
  }, []);
  
  const handleDrop = useCallback((e: DragEvent<HTMLDivElement>) => {
    e.preventDefault();
    setIsDragging(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files.length > 0) {
      const file = e.dataTransfer.files[0];
      if (file.type.startsWith("audio/")) {
        setSelectedFile(file);
        onFileSelect(file);
      }
    }
  }, [onFileSelect]);
  
  // Handle file select via input
  const handleFileSelect = useCallback(() => {
    if (fileInputRef.current?.files && fileInputRef.current.files.length > 0) {
      const file = fileInputRef.current.files[0];
      setSelectedFile(file);
      onFileSelect(file);
    }
  }, [onFileSelect]);
  
  // Handle URL input
  const handleUrlSubmit = useCallback(() => {
    if (url.trim()) {
      setIsLoading(true);
      // Simulating a loading state - in a real app, you'd validate the URL
      setTimeout(() => {
        onUrlSubmit(url);
        setIsLoading(false);
      }, 1500);
    }
  }, [url, onUrlSubmit]);
  
  // Handle recording
  const startRecording = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];
      
      mediaRecorder.ondataavailable = (e) => {
        audioChunksRef.current.push(e.data);
      };
      
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/wav" });
        onRecordingComplete(audioBlob);
        
        // Stop all tracks of the stream
        stream.getTracks().forEach(track => track.stop());
      };
      
      // Start the timer
      let seconds = 0;
      timerRef.current = setInterval(() => {
        seconds += 1;
        setRecordingTime(seconds);
      }, 1000);
      
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error starting recording:", error);
    }
  }, [onRecordingComplete]);
  
  const stopRecording = useCallback(() => {
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
      mediaRecorderRef.current.stop();
      setIsRecording(false);
      
      // Clear the timer
      if (timerRef.current) {
        clearInterval(timerRef.current);
        timerRef.current = null;
      }
      
      setRecordingTime(0);
    }
  }, []);
  
  // Reset selected file
  const clearSelectedFile = useCallback(() => {
    setSelectedFile(null);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  }, []);
  
  // Format recording time
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, "0")}:${secs.toString().padStart(2, "0")}`;
  };
  
  return (
    <div className="w-full max-w-4xl mx-auto">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Drag & Drop Area */}
        <Card className="md:col-span-2 overflow-hidden">
          <div
            className={cn(
              "drag-area flex flex-col items-center justify-center h-64",
              isDragging && "drag-active",
              selectedFile && "border-blue bg-blue-light/10"
            )}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            {!selectedFile ? (
              <>
                <Upload className="h-12 w-12 text-muted-foreground mb-4 animate-wave" />
                <h3 className="text-lg font-medium mb-2">Drag & Drop Audio Files</h3>
                <p className="text-muted-foreground mb-4 text-center">
                  or browse from your computer
                </p>
                <input
                  type="file"
                  accept="audio/*"
                  ref={fileInputRef}
                  onChange={handleFileSelect}
                  className="hidden"
                  id="audio-file-input"
                />
                <Button 
                  onClick={() => fileInputRef.current?.click()}
                  variant="outline"
                >
                  Choose File
                </Button>
              </>
            ) : (
              <div className="flex flex-col items-center">
                <FileAudio className="h-12 w-12 text-blue mb-4" />
                <p className="font-medium mb-2 break-all text-center">{selectedFile.name}</p>
                <p className="text-sm text-muted-foreground mb-4">
                  {(selectedFile.size / (1024 * 1024)).toFixed(2)} MB
                </p>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={clearSelectedFile}
                  className="flex items-center gap-1"
                >
                  <X className="h-4 w-4" /> Remove
                </Button>
              </div>
            )}
          </div>
        </Card>
        
        {/* URL and Recording */}
        <Card className="p-6 space-y-6">
          {/* URL Input */}
          <div>
            <h3 className="text-lg font-medium mb-3 flex items-center gap-2">
              <Link className="h-5 w-5" /> Paste URL
            </h3>
            <div className="flex gap-2">
              <Input
                type="url"
                placeholder="https://example.com/audio.mp3"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isLoading}
              />
              <Button 
                onClick={handleUrlSubmit} 
                disabled={!url.trim() || isLoading}
              >
                {isLoading ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  "Go"
                )}
              </Button>
            </div>
          </div>
          
          {/* Recording */}
          <div>
            <h3 className="text-lg font-medium mb-3 flex items-center gap-2">
              <Mic className="h-5 w-5" /> Record Audio
            </h3>
            <div className="flex flex-col items-center gap-3">
              <div className="relative">
                <Button
                  onClick={isRecording ? stopRecording : startRecording}
                  className={cn(
                    "btn-record h-16 w-16 rounded-full flex items-center justify-center",
                    isRecording && "bg-destructive hover:bg-destructive/90"
                  )}
                >
                  {isRecording ? (
                    <span className="h-6 w-6 bg-white rounded-sm" />
                  ) : (
                    <Mic className="h-6 w-6" />
                  )}
                  
                  {isRecording && (
                    <span className="absolute inset-0 rounded-full border-4 border-destructive animate-pulse-ring" />
                  )}
                </Button>
              </div>
              
              {isRecording && (
                <div className="text-destructive font-medium">
                  {formatTime(recordingTime)}
                </div>
              )}
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default AudioInput;
