import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Paperclip, Camera, Video, Search } from 'lucide-react';
import { toast } from 'sonner';

const Index = () => {
  const [topic, setTopic] = useState('');
  const [inputMode, setInputMode] = useState<'text' | 'file' | 'screenshot'>('text');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const screenshotInputRef = useRef<HTMLInputElement>(null);

  // Cycling placeholder animation
  const [placeholderText, setPlaceholderText] = useState('');
  const [isTyping, setIsTyping] = useState(true);
  const topics = [
    "Dijkstra's algorithm",
    'calculus derivatives',
    'binary search trees',
    'linear algebra',
    'merge sort',
    'graph theory',
    'neural networks',
    'dynamic programming'
  ];
  const [currentTopicIndex, setCurrentTopicIndex] = useState(0);

  useEffect(() => {
    if (topic) return; // Don't show placeholder animation if user is typing

    let typingTimer: NodeJS.Timeout;
    let currentIndex = 0;
    const currentTopic = topics[currentTopicIndex];
    const prefix = 'Teach me about ';

    if (isTyping) {
      // Typing forward
      if (currentIndex < currentTopic.length) {
        const typeChar = () => {
          if (currentIndex < currentTopic.length) {
            setPlaceholderText(prefix + currentTopic.slice(0, currentIndex + 1));
            currentIndex++;
            typingTimer = setTimeout(typeChar, 80);
          } else {
            // Pause at end before deleting
            setTimeout(() => setIsTyping(false), 2000);
          }
        };
        typeChar();
      }
    } else {
      // Deleting
      currentIndex = currentTopic.length;
      const deleteChar = () => {
        if (currentIndex > 0) {
          setPlaceholderText(prefix + currentTopic.slice(0, currentIndex - 1));
          currentIndex--;
          typingTimer = setTimeout(deleteChar, 50);
        } else {
          // Move to next topic
          setCurrentTopicIndex((prev) => (prev + 1) % topics.length);
          setIsTyping(true);
        }
      };
      deleteChar();
    }

    return () => {
      clearTimeout(typingTimer);
    };
  }, [currentTopicIndex, isTyping, topic]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, mode: 'file' | 'screenshot') => {
    const file = e.target.files?.[0];
    if (file) {
      setSelectedFile(file);
      setInputMode(mode);
      setTopic(file.name);
      toast.success(`${mode === 'screenshot' ? 'Screenshot' : 'File'} selected: ${file.name}`);
    }
  };

  const handleGenerate = async () => {
    if (inputMode === 'text' && !topic.trim()) {
      toast.error('Please enter a topic to learn about');
      return;
    }
    if (inputMode === 'file' && !selectedFile) {
      toast.error('Please select a file');
      return;
    }
    if (inputMode === 'screenshot' && !selectedFile) {
      toast.error('Please upload a screenshot');
      return;
    }

    // Navigate to loading screen with the topic/file data
    navigate('/generate', {
      state: {
        topic: inputMode === 'text' ? topic : selectedFile?.name,
        inputMode,
        file: selectedFile
      }
    });
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center px-4 relative overflow-hidden">
      {/* Mathematical grid background */}
      <div className="absolute inset-0 opacity-[0.06] pointer-events-none">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
              <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" strokeWidth="0.5"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#grid)" />
        </svg>
      </div>

      {/* Subtle dots pattern */}
      <div className="absolute inset-0 opacity-[0.08] pointer-events-none">
        <svg width="100%" height="100%" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <pattern id="dots" width="20" height="20" patternUnits="userSpaceOnUse">
              <circle cx="1" cy="1" r="1" fill="currentColor"/>
            </pattern>
          </defs>
          <rect width="100%" height="100%" fill="url(#dots)" />
        </svg>
      </div>

      {/* Background gradient spots */}
      <div className="absolute top-0 left-0 w-96 h-96 bg-gradient-to-br from-primary/15 via-primary/8 to-transparent rounded-full blur-3xl pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-gradient-to-tl from-secondary/12 via-secondary/6 to-transparent rounded-full blur-3xl pointer-events-none" />

      <div className="max-w-2xl w-full text-center relative z-10">
        {/* Title */}
        <h1 className="text-6xl md:text-7xl font-bold mb-3">
          <span className="text-gradient">Videre,</span>
          <span className="text-foreground"> Teach Me...</span>
        </h1>

        {/* Subtitle below Videre */}
        <p className="text-sm text-muted-foreground mb-12">
          One click, one video.
        </p>

        {/* Main Input Box - Similar to original design */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="relative group">
            {/* Gradient overlay */}
            <div className="absolute -inset-1 bg-gradient-primary rounded-2xl blur opacity-25 group-hover:opacity-40 transition duration-300 pointer-events-none" />

            <div className="relative flex flex-col p-6 sm:p-8 rounded-2xl border border-border/50 backdrop-blur-sm shadow-elevated bg-sky-800">
              {/* Top-left input with icon */}
              <div className="flex items-center gap-2 mb-8">
                <Search className="w-5 h-5 text-muted-foreground flex-shrink-0" />
                <input
                  type="text"
                  value={topic}
                  onChange={(e) => {
                    setTopic(e.target.value);
                    if (inputMode !== 'text') {
                      setInputMode('text');
                      setSelectedFile(null);
                    }
                  }}
                  onKeyDown={(e) => {
                    if (e.key === 'Enter') handleGenerate();
                  }}
                  placeholder={topic ? '' : placeholderText}
                  className="flex-1 bg-transparent text-sm italic text-foreground outline-none placeholder:text-muted-foreground"
                  autoFocus
                />
              </div>

              {/* Bottom row: icons on left, button on right */}
              <div className="flex items-center justify-between pt-2">
                {/* Icon buttons on the left */}
                <div className="flex items-center gap-2">
                  {/* Hidden file inputs */}
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

                  {/* Camera icon button */}
                  <button
                    onClick={() => screenshotInputRef.current?.click()}
                    className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                    title="Upload screenshot"
                  >
                    <Camera className="w-5 h-5 text-muted-foreground hover:text-foreground transition-colors" />
                  </button>

                  {/* Paperclip icon button */}
                  <button
                    onClick={() => fileInputRef.current?.click()}
                    className="p-2 rounded-lg hover:bg-white/10 transition-colors"
                    title="Upload file"
                  >
                    <Paperclip className="w-5 h-5 text-muted-foreground hover:text-foreground transition-colors" />
                  </button>
                </div>

                {/* Create Video button on the right */}
                <Button
                  variant="hero"
                  size="sm"
                  onClick={handleGenerate}
                  className="px-5 py-2 flex items-center gap-2"
                >
                  <Video className="w-4 h-4" />
                  Create Video
                </Button>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Caption */}
        <p className="text-sm text-muted-foreground italic">
          Personal STEM visual tutor; the forefront of education in the age of AI.
        </p>
      </div>
    </div>
  );
};

export default Index;
