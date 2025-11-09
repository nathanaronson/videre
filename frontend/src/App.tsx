import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import Index from "./pages/Index";
import GenerateVideo from "./pages/GenerateVideo";
import VideoDisplay from "./pages/VideoDisplay";
import History from "./pages/History";
import NotFound from "./pages/NotFound";
import { useState } from "react";

const queryClient = new QueryClient();

const App = () => {
  const [topic, setTopic] = useState<string>('');
  const [videoURL, setVideoURL] = useState<string>('');

  return (
    <QueryClientProvider client={queryClient}>
      <TooltipProvider>
        <Toaster />
        <Sonner />
        <BrowserRouter>
          <Routes>
            <Route path="/" element={<Index topic={topic} setTopic={setTopic} />} />
            <Route path="/generate" element={<GenerateVideo topic={topic} setVideoURL={setVideoURL} />} />
            <Route path="/video" element={<VideoDisplay topic={topic} videoURL={videoURL} />} />
            <Route path="/history" element={<History setTopic={setTopic} setVideoURL={setVideoURL} />} />
            {/* ADD ALL CUSTOM ROUTES ABOVE THE CATCH-ALL "*" ROUTE */}
            <Route path="*" element={<NotFound />} />
          </Routes>
        </BrowserRouter>
      </TooltipProvider>
    </QueryClientProvider>
  );
};

export default App;
