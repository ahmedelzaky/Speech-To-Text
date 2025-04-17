import { useEffect, useRef, useState } from "react";
import { Copy, Check, Loader2 } from "lucide-react";
import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { useTypewriter } from "@/hooks/useTypewriter";

interface TranscriptionResultProps {
  text: string;
  isLoading: boolean;
  isStreaming?: boolean;
}

const TranscriptionResult = ({
  text,
  isLoading,
  isStreaming = false,
}: TranscriptionResultProps) => {
  const [copied, setCopied] = useState(false);
  const textRef = useRef<HTMLDivElement>(null);

  // Use typewriter hook to progressively show text
  const animatedText = useTypewriter(text, isLoading, 15);

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (err) {
      console.error("Copy failed:", err);
    }
  };

  return (
    <Card className="p-6 w-full max-w-4xl mx-auto mt-10">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-medium">Transcription Result</h2>
        {text && !isLoading && (
          <Button
            variant="outline"
            size="sm"
            onClick={handleCopy}
            className="flex items-center gap-1"
          >
            {copied ? (
              <>
                <Check className="h-4 w-4" /> Copied
              </>
            ) : (
              <>
                <Copy className="h-4 w-4" /> Copy
              </>
            )}
          </Button>
        )}
      </div>

      <div
        ref={textRef}
        className="bg-muted rounded-lg p-4 min-h-[200px] max-h-[400px] overflow-y-auto whitespace-pre-wrap text-left"
      >
        {isLoading ? (
          <div className="h-full flex flex-col items-center justify-center text-muted-foreground">
            <Loader2 className="h-8 w-8 animate-spin mb-4" />
            <p>Processing your audio...</p>
            <p className="text-sm">This may take a moment</p>
          </div>
        ) : text ? (
          <p className="text-muted-foreground">{animatedText}</p>
        ) : (
          <div className="h-full flex items-center justify-center text-muted-foreground">
            <p>Your transcribed text will appear here</p>
          </div>
        )}
      </div>
    </Card>
  );
};

export default TranscriptionResult;
