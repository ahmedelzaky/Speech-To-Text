import { useEffect, useRef, useState } from "react";

export const useTypewriter = (text: string, isLoading: boolean, speed = 50) => {
  const [displayed, setDisplayed] = useState("");
  const indexRef = useRef(0);
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    // Reset on new transcription start
    if (isLoading) {
      setDisplayed("");
      indexRef.current = 0;
      if (intervalRef.current) clearInterval(intervalRef.current);
      return;
    }

    if (intervalRef.current) clearInterval(intervalRef.current);

    intervalRef.current = setInterval(() => {
      setDisplayed((prev) => {
        if (indexRef.current >= text.length) {
          clearInterval(intervalRef.current!);
          return prev;
        }
        const nextChar = text.charAt(indexRef.current);
        indexRef.current += 1;
        return prev + nextChar;
      });
    }, speed);

    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [text, isLoading, speed]);

  return displayed;
};
