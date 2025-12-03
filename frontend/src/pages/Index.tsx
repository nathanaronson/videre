import { useState, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { ArrowRight, Paperclip, Image } from 'lucide-react';
import { toast } from 'sonner';

const Index = ({ topic, setTopic }: { topic: string, setTopic: (topic: string) => void }) => {
  const [inputMode, setInputMode] = useState<'text' | 'file' | 'screenshot'>('text');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const screenshotInputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, mode: 'file' | 'screenshot') => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setInputMode(mode);
      setTopic(file.name);
      toast.success(`File attached: ${file.name}`);
    }
  };

  const handleGenerate = async () => {
    if (inputMode === "text" && !topic.trim()) {
      toast.error("Enter a topic first");
      return;
    }
    if ((inputMode === "file" || inputMode === "screenshot") && !selectedFile) {
      toast.error("Select a file first");
      return;
    }

    navigate("/generate", {
      state: {
        topic: inputMode === "text" ? topic : selectedFile?.name,
        inputMode,
        file: selectedFile,
      },
    });
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      {/* Header */}
      <header className="p-6 flex justify-between items-center">
        <span className="text-sm font-medium tracking-tight">P2P</span>
        <button
          onClick={() => navigate('/history')}
          className="text-sm text-muted-foreground hover:text-foreground transition-colors"
        >
          History
        </button>
      </header>

      {/* Main */}
      <main className="flex-1 flex flex-col items-center justify-center px-6 pb-24">
        <div className="w-full max-w-xl">
          {/* Title */}
          <h1 className="text-4xl font-semibold tracking-tight mb-2">
            Prompt to Professor
          </h1>
          <p className="text-muted-foreground mb-10">
            Describe any mathematical topic and get a video explanation.
          </p>

          {/* Input */}
          <div className="relative">
            <textarea
              value={topic}
              onChange={(e) => {
                setTopic(e.target.value);
                if (inputMode !== 'text') {
                  setInputMode('text');
                  setSelectedFile(null);
                }
              }}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleGenerate();
                }
              }}
              placeholder="e.g., How does Dijkstra's algorithm work?"
              className="w-full min-h-[120px] p-4 bg-card border border-border rounded-lg resize-none text-foreground placeholder:text-muted-foreground focus:outline-none focus:ring-1 focus:ring-foreground/20"
              autoFocus
            />

            {/* Bottom bar */}
            <div className="flex items-center justify-between mt-3">
              <div className="flex items-center gap-1">
                <input
                  ref={screenshotInputRef}
                  type="file"
                  accept="image/*"
                  onChange={(e) => handleFileChange(e, 'screenshot')}
                  className="hidden"
                />
                <input
                  ref={fileInputRef}
                  type="file"
                  onChange={(e) => handleFileChange(e, 'file')}
                  className="hidden"
                />
                <button
                  onClick={() => screenshotInputRef.current?.click()}
                  className="p-2 text-muted-foreground hover:text-foreground transition-colors"
                  title="Add image"
                >
                  <Image className="w-4 h-4" />
                </button>
                <button
                  onClick={() => fileInputRef.current?.click()}
                  className="p-2 text-muted-foreground hover:text-foreground transition-colors"
                  title="Add file"
                >
                  <Paperclip className="w-4 h-4" />
                </button>
              </div>

              <button
                onClick={handleGenerate}
                className="flex items-center gap-2 px-4 py-2 bg-foreground text-background rounded-lg text-sm font-medium hover:opacity-90 transition-opacity"
              >
                Generate
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      </main>

      {/* Logo bottom left */}
      <img src="/logo.png" alt="P2P" className="fixed bottom-6 left-6 h-12" />
    </div>
  );
};

export default Index;
